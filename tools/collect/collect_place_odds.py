#!/usr/bin/env python3
"""秋G1検証セットの各レースについて確定複勝オッズ(全馬)を収集する。

netkeiba の api_get_jra_odds.html?type=2 は決着済みレースでも
status="result" で全馬の複勝オッズ範囲 [low, high, rank] を返す。
全馬が範囲表示のまま返るため、着順による非対称性は入らない。

私的利用の範囲。netkeiba ToS 第16条12号(サーバ負荷)に配慮し
リクエスト間隔を空ける。
"""
import json, glob, os, re, sys, time, urllib.request

INTERVAL = 0.8
OUT = 'data/validation-g1-place-odds.json'
API = ('https://race.netkeiba.com/api/api_get_jra_odds.html'
       '?type=2&race_id={rid}&action=init')


def fetch(rid):
    req = urllib.request.Request(
        API.format(rid=rid),
        headers={'User-Agent': 'Mozilla/5.0',
                 'Referer': f'https://race.netkeiba.com/odds/index.html?race_id={rid}'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode('utf-8'))


def main():
    ids = []
    for p in sorted(glob.glob('data/validation-g1/*.json')):
        m = re.search(r'(\d{12})\.json$', os.path.basename(p))
        if m:
            ids.append(m.group(1))

    out = json.load(open(OUT)) if os.path.exists(OUT) else {}
    todo = [r for r in ids if r not in out]
    print(f'{len(ids)}レース中 {len(todo)}件を取得', flush=True)

    for i, rid in enumerate(todo, 1):
        try:
            d = fetch(rid)
            status = d.get('status')
            odds = (d.get('data') or {}).get('odds', {}).get('2')
            if status == 'result' and odds:
                out[rid] = {'status': status, 'odds': odds,
                            'at': d['data'].get('official_datetime')}
            else:
                out[rid] = {'status': status, 'odds': None}
                print(f'  [{i}] {rid} status={status} 複勝オッズなし', flush=True)
        except Exception as e:
            print(f'  [{i}] {rid} ERROR {e}', flush=True)
        if i % 20 == 0:
            json.dump(out, open(OUT, 'w'), ensure_ascii=False)
            print(f'  [{i}/{len(todo)}] 保存', flush=True)
        time.sleep(INTERVAL)

    json.dump(out, open(OUT, 'w'), ensure_ascii=False)
    ok = sum(1 for v in out.values() if v.get('odds'))
    print(f'完了: {ok}/{len(out)}レースで複勝オッズ取得')


if __name__ == '__main__':
    main()
