#!/usr/bin/env python3
"""発走前に記録した追跡ファイルに結果を埋め、通算サマリを更新する。

netkeiba の無料DB(db.netkeiba.com)は当日〜数日は未反映で、確認できた範囲では
約1週間のラグがある（当日の race/result.html は1着のみ公開で2着以降は有料）。
そのため本スクリプトは冪等で、毎日実行して反映済みのものから順に埋める設計。

使い方: python3 tools/collect/vrs18_score.py
"""
import glob, html, json, math, os, re, sys, time, urllib.request

DB = 'https://db.netkeiba.com/race/{rid}/'
UA = {'User-Agent': 'Mozilla/5.0'}
TRACK = 'data/tracking'


_CACHE = {}


def race_result(rid):
    """着順(馬番リスト)と複勝払戻(馬番->円)。未反映なら None。同一実行内でキャッシュ。"""
    if rid in _CACHE:
        return _CACHE[rid]
    with urllib.request.urlopen(urllib.request.Request(DB.format(rid=rid), headers=UA),
                                timeout=40) as r:
        s = r.read().decode('euc-jp', 'replace')
    if '1970年1月01日' in s:
        _CACHE[rid] = None
        return None
    order = []
    for row in re.findall(r'(?is)<tr[^>]*>(.*?)</tr>', s):
        f = [' '.join(html.unescape(re.sub(r'<[^>]+>', ' ', x)).split())
             for x in re.findall(r'(?is)<td[^>]*>(.*?)</td>', row)]
        if len(f) >= 4 and f[0].isdigit() and f[2].isdigit():
            order.append((int(f[0]), int(f[2])))
    if not order:
        _CACHE[rid] = None
        return None

    pay = {}
    for m in re.finditer(r'(?is)<th[^>]*>\s*複勝\s*</th>(.*?)</tr>', s):
        cells = [html.unescape(re.sub(r'<[^>]+>', '|', c))
                 for c in re.findall(r'(?is)<td[^>]*>(.*?)</td>', m.group(1))]
        if len(cells) < 2:
            continue
        nos = [x for x in cells[0].split('|') if x.strip().isdigit()]
        yens = [x.replace(',', '') for x in cells[1].split('|')
                if x.replace(',', '').strip().isdigit()]
        for a, b in zip(nos, yens):
            pay[int(a)] = int(b)
        break

    res = {'order': [no for _, no in sorted(order)], 'placePayout': pay}
    _CACHE[rid] = res
    return res


def finishing_order(rid):
    r = race_result(rid)
    return r['order'] if r else None


def logloss(hs, key, inmoney):
    tot = 0.0
    for h in hs:
        p = h.get(key)
        if p is None:
            return None
        p = min(max(p / 100.0, 1e-6), 1 - 1e-6)
        y = 1.0 if h['no'] in inmoney else 0.0
        tot += -(y * math.log(p) + (1 - y) * math.log(1 - p))
    return round(tot / len(hs), 4)


def main():
    files = sorted(f for f in glob.glob(f'{TRACK}/*.json')
                   if not f.endswith('summary.json'))
    pending, done = [], []
    for fp in files:
        d = json.load(open(fp))
        if 'races' not in d:
            continue
        changed = False
        for r in d['races']:
            if 'result' in r:
                continue
            try:
                order = finishing_order(r['raceId'])
            except Exception as e:
                print(f"  {fp} {r['race']} 取得失敗 {e}")
                order = None
            time.sleep(0.7)
            if not order:
                pending.append(f"{os.path.basename(fp)} {r['race']}")
                continue
            inmoney = set(order[:r['placePositions']])
            hs = r['horses']
            r['result'] = {
                'order': order, 'inTheMoney': sorted(inmoney),
                'marketAxisHit': r['axis']['market']['no'] in inmoney,
                'vrs18AxisHit': r['axis']['vrs18']['no'] in inmoney,
                'logLoss': {'market': logloss(hs, 'market', inmoney),
                            'vrs18Raw': logloss(hs, 'vrs18Raw', inmoney),
                            'vrs18Norm': logloss(hs, 'vrs18Norm', inmoney)}}
            changed = True
            done.append(f"{os.path.basename(fp)} {r['race']}")
        if changed:
            json.dump(d, open(fp, 'w'), ensure_ascii=False, indent=1)

    # 見送り記録の仮想ポートフォリオを採点
    for fp in sorted(glob.glob('data/results/*-pass.json')):
        d = json.load(open(fp))
        cfb = d.get('counterfactual')
        if not cfb or 'result' in cfb:
            continue
        hs = cfb.get('horses', [])
        filled, miss = 0, 0
        for h in hs:
            if 'hit' in h:
                filled += 1
                continue
            try:
                rr = race_result(h['raceId'])
            except Exception as e:
                print(f"  {fp} {h['raceId']} 取得失敗 {e}")
                rr = None
            time.sleep(0.7)
            if not rr:
                miss += 1
                continue
            # 複勝圏は頭数で決まる。払戻に馬番があれば的中
            h['hit'] = h['no'] in rr['placePayout']
            h['payout'] = rr['placePayout'].get(h['no'], 0)
            filled += 1
        if filled and not miss:
            n = len(hs)
            stake = n * 100
            ret = sum(h['payout'] for h in hs)
            cfb['result'] = {
                'bets': n, 'stake': stake, 'hits': sum(1 for h in hs if h['hit']),
                'return': ret, 'profit': ret - stake,
                'roi': round(ret / stake, 3) if stake else None,
                'note': ('実際には買っていない。見送り判断の検証用。'
                         f'{n}点では運の幅が大きく、1日分では判定にならない')}
            print(f"{fp} 仮想ポートフォリオ採点: {cfb['result']['hits']}/{n}的中 "
                  f"回収 {ret}円/{stake}円 = 回収率 {cfb['result']['roi']:.1%}")
        elif miss:
            print(f'{fp} 仮想ポートフォリオ: {miss}/{len(hs)}頭が未反映のため保留')
        json.dump(d, open(fp, 'w'), ensure_ascii=False, indent=1)

    # 通算サマリ
    races, split = [], []
    for fp in files:
        d = json.load(open(fp))
        if 'races' not in d or 'swan' in fp:      # swan-s は京都ファイルと重複
            continue
        for r in d['races']:
            if 'result' not in r:
                continue
            races.append(r)
            if not r['agree']:
                split.append(r)

    def agg(rs):
        if not rs:
            return None
        n = len(rs)
        o = {'races': n,
             'marketAxisHit': sum(r['result']['marketAxisHit'] for r in rs),
             'vrs18AxisHit': sum(r['result']['vrs18AxisHit'] for r in rs)}
        for k in ('market', 'vrs18Raw', 'vrs18Norm'):
            v = [r['result']['logLoss'][k] for r in rs if r['result']['logLoss'][k] is not None]
            o[f'logLoss_{k}'] = round(sum(v) / len(v), 4) if v else None
        return o

    summary = {'updatedAt': time.strftime('%Y-%m-%dT%H:%M:%S'),
               'all': agg(races), 'axisSplitOnly': agg(split),
               'pending': len(pending),
               'note': ('軸が一致したレースでは主指標に差が出ない。'
                        'axisSplitOnly が軸比較の実効サンプル。'
                        '対数損失は全レースで差が出るのでそちらは全件使える。')}
    json.dump(summary, open(f'{TRACK}/summary.json', 'w'), ensure_ascii=False, indent=1)

    print(f'新規に採点 {len(done)}レース / 未反映 {len(pending)}レース')
    if summary['all']:
        a, s = summary['all'], summary['axisSplitOnly']
        print(f"通算 {a['races']}レース  軸的中 市場 {a['marketAxisHit']}/{a['races']} "
              f"VRS18 {a['vrs18AxisHit']}/{a['races']}")
        print(f"  対数損失 市場 {a['logLoss_market']}  "
              f"VRS18生 {a['logLoss_vrs18Raw']}  VRS18正規化 {a['logLoss_vrs18Norm']}")
        if s:
            print(f"軸が割れた {s['races']}レースのみ: 市場 {s['marketAxisHit']}/{s['races']} "
                  f"VRS18 {s['vrs18AxisHit']}/{s['races']}")
    if pending:
        print(f'未反映（db.netkeiba待ち）: {len(pending)}件 例 {pending[:3]}')


if __name__ == '__main__':
    main()
