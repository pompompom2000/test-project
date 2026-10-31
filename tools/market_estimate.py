#!/usr/bin/env python3
"""単勝・複勝・ワイド・3連複の4プールから3着内確率を出し、中央値を取る。

なぜ中央値か: 2026-10-17の新潟12Rで、同じ「3着内確率」を複勝が78.6%、
ワイドが40.1%、3連複が47.0%と言った。単勝5.1倍の馬が複勝78.6%になることは
なく、外れていたのは最も厚い複勝プールだった。単独のプールを基準に据えると
その誤りが全組に伝播する（EV>1が143組出た）。3つに同じ量を言わせて中央値を
取ると13組に落ちた。経緯は data/analysis/pool-discrepancy.md。

ペア・3頭組の確率は、3連複プールの依存構造を保ったままIPFで周辺を中央値に
合わせて出す。

    python3 tools/market_estimate.py <race_id> [出力先.json]
"""
import json, itertools, statistics, sys, time, urllib.request

UA = {'User-Agent': 'Mozilla/5.0'}
API = ('https://race.netkeiba.com/api/api_get_jra_odds.html'
       '?type={t}&race_id={rid}&action=init')
RATE = {'win': 0.80, 'place': 0.80, 'wide': 0.775, 'trio': 0.75}


def fetch(t, rid):
    d = json.loads(urllib.request.urlopen(
        urllib.request.Request(API.format(t=t, rid=rid), headers=UA),
        timeout=40).read().decode('utf-8', 'replace'))
    return d.get('data') or {}, d.get('status')


def num(s):
    return float(str(s).replace(',', ''))


def collect(rid, pause=1.0):
    d1, st = fetch(1, rid); time.sleep(pause)
    d5, _ = fetch(5, rid);  time.sleep(pause)
    d7, _ = fetch(7, rid)
    return {
        'at': d7.get('official_datetime'), 'status': st,
        'win': {int(k): num(v[0]) for k, v in d1['odds']['1'].items()},
        'place': {int(k): [num(v[0]), num(v[1])] for k, v in d1['odds']['2'].items()},
        'wide': {f'{min(int(k[:2]),int(k[2:])):02d}{max(int(k[:2]),int(k[2:])):02d}':
                 [num(v[0]), num(v[1])] for k, v in d5['odds']['5'].items()},
        'trio': {''.join(f'{x:02d}' for x in sorted((int(k[:2]), int(k[2:4]), int(k[4:])))):
                 num(v[0]) for k, v in d7['odds']['7'].items() if num(v[0]) > 0},
    }


def estimate(raw):
    win = raw['win']
    place = {int(k): v for k, v in raw['place'].items()}
    wide = {(int(k[:2]), int(k[2:])): v for k, v in raw['wide'].items()}
    trio = {(int(k[:2]), int(k[2:4]), int(k[4:])): v for k, v in raw['trio'].items()}
    N = sorted(win)
    k_place = 3 if len(N) >= 8 else 2

    def scaled(p):
        s = sum(p.values())
        return {n: v * k_place / s for n, v in p.items()}

    # 複勝プール: 下限と上限の中点から
    p_pl = scaled({n: RATE['place'] / ((place[n][0] + place[n][1]) / 2) for n in N})
    # ワイドプール: i が3着内なら i を含む的中ペアはちょうど2つ
    wm = {n: 0.0 for n in N}
    for (a, b), (lo, hi) in wide.items():
        q = RATE['wide'] / ((lo + hi) / 2); wm[a] += q; wm[b] += q
    p_wd = scaled({n: wm[n] / 2 for n in N})
    # 3連複プール: i を含む3頭組の和
    tm = {n: 0.0 for n in N}
    for (a, b, c), o in trio.items():
        q = RATE['trio'] / o; tm[a] += q; tm[b] += q; tm[c] += q
    p_tr = scaled(tm)

    med = scaled({n: statistics.median([p_pl[n], p_wd[n], p_tr[n]]) for n in N})

    # IPF: 3連複プールの依存構造を保ったまま周辺を中央値に合わせる
    base = {k: RATE['trio'] / o for k, o in trio.items()}
    w = {n: 1.0 for n in N}
    t = base
    for it in range(400):
        t = {k: v * w[k[0]] * w[k[1]] * w[k[2]] for k, v in base.items()}
        s = sum(t.values()); t = {k: v / s for k, v in t.items()}
        mg = {n: 0.0 for n in N}
        for (a, b, c), v in t.items():
            mg[a] += v; mg[b] += v; mg[c] += v
        err = max(abs(mg[n] - med[n]) for n in N)
        if err < 1e-10:
            break
        for n in N:
            w[n] *= (med[n] / mg[n]) ** 0.5
    pair = {}
    for (a, b, c), v in t.items():
        for x, y in ((a, b), (a, c), (b, c)):
            pair[(x, y)] = pair.get((x, y), 0.0) + v
    return {'N': N, 'k': k_place, 'win': win, 'place': place, 'wide': wide,
            'trio': trio, 'pl': p_pl, 'wd': p_wd, 'tr': p_tr, 'med': med,
            'joint': t, 'pair': pair, 'ipfIters': it + 1, 'ipfErr': err}


def report(e, raw):
    N, med = e['N'], e['med']
    print(f"オッズ確定 {raw['at']}  status={raw['status']}  {len(N)}頭  "
          f"IPF {e['ipfIters']}回 残差 {e['ipfErr']:.1e}\n")
    print('馬番  単勝   複勝由来 ワイド由来 3連複由来  中央値   最大差')
    for n in sorted(N, key=lambda n: -med[n]):
        sp = [e['pl'][n], e['wd'][n], e['tr'][n]]
        print(f'{n:3d}  {e["win"][n]:6.1f}  {sp[0]*100:7.1f}  {sp[1]*100:8.1f}  '
              f'{sp[2]*100:8.1f}  {med[n]*100:7.1f}  {(max(sp)-min(sp))*100:6.1f}pt')
    sp8 = [max(e['pl'][n], e['wd'][n], e['tr'][n]) - min(e['pl'][n], e['wd'][n], e['tr'][n])
           for n in sorted(N, key=lambda n: -med[n])[:8]]
    print(f'\n上位8頭のプール間不一致: 平均 {statistics.mean(sp8)*100:.1f}pt '
          f'最大 {max(sp8)*100:.1f}pt')

    print('\n=== 複勝 EV（下限オッズ）===')
    ev = sorted(((med[n] * e['place'][n][0], n) for n in N), reverse=True)
    for v, n in ev[:5]:
        print(f'  {n:2d}番  p={med[n]*100:5.1f}%  {e["place"][n][0]}-{e["place"][n][1]}倍  EV={v:.3f}')
    print(f'  最高 {ev[0][0]:.3f} / 基準 {RATE["place"]}')

    print('\n=== ワイド EV（下限オッズ）===')
    we = sorted(((e['pair'].get(c, 0) * o[0], c) for c, o in e['wide'].items()), reverse=True)
    for v, c in we[:5]:
        print(f'  {c[0]:2d}-{c[1]:2d}  p={e["pair"].get(c,0)*100:5.2f}%  {e["wide"][c][0]}倍  EV={v:.3f}')
    print(f'  EV>1: {sum(1 for v,_ in we if v>1)}/{len(we)} / 基準 {RATE["wide"]}')

    print('\n=== 3連複 EV ===')
    te = sorted(((e['joint'][k] * o, k) for k, o in e['trio'].items()), reverse=True)
    for v, k in te[:5]:
        print(f'  {k[0]:2d}-{k[1]:2d}-{k[2]:2d}  p={e["joint"][k]*100:5.2f}%  {e["trio"][k]}倍  EV={v:.3f}')
    print(f'  EV>1: {sum(1 for v,_ in te if v>1)}/{len(te)} / 基準 {RATE["trio"]}')
    print('\n  確率帯での分解（EV>1が薄い裾に偏るならアーティファクト）')
    print('   帯         組数  EV中央値  EV>1')
    for nm, lo, hi in [('2%以上',.02,1),('1-2%',.01,.02),('0.5-1%',.005,.01),
                       ('0.1-0.5%',.001,.005),('0.1%未満',0,.001)]:
        g = [e['joint'][k]*e['trio'][k] for k in e['trio'] if lo <= e['joint'][k] < hi]
        if g:
            print(f'   {nm:10s} {len(g):4d}  {statistics.median(g):7.3f}  '
                  f'{sum(1 for x in g if x>1):4d}')


def main():
    rid = sys.argv[1]
    raw = collect(rid)
    e = estimate(raw)
    report(e, raw)
    if len(sys.argv) > 2:
        json.dump({'raceId': rid, 'oddsAt': raw['at'], 'status': raw['status'],
                   'rawOdds': raw,
                   'placeProb': {str(n): round(e['med'][n], 5) for n in e['N']},
                   'byPool': {str(n): {'place': round(e['pl'][n], 5),
                                       'wide': round(e['wd'][n], 5),
                                       'trio': round(e['tr'][n], 5)} for n in e['N']},
                   'trioJoint': {''.join(f'{x:02d}' for x in k): round(v, 8)
                                 for k, v in e['joint'].items()}},
                  open(sys.argv[2], 'w'), ensure_ascii=False)
        print(f'\n{sys.argv[2]} に生オッズごと保存')


if __name__ == '__main__':
    main()
