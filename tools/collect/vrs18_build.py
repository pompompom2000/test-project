#!/usr/bin/env python3
"""manifest.json + predictions.json を突き合わせて発走前の追跡ファイルを作る。

predictions.json はモデルが画像から読み取った値。形式:
  {"<会場>": {"<N>R": {"<馬番>": {"win": 21.77, "place": 48.25, "odds": 3.8}, ...}}}

市場推定3着内率は 0.8/複勝オッズ中点。レース内正規化はしない
（Σ=3に正規化すると断然人気がいる組で100%を超えるため）。
VRS18は出力が確率分布として正規化されていないので生値と正規化値の両方を持つ。
軸の選択は単調変換なので正規化の有無に依存しない。

使い方: python3 tools/collect/vrs18_build.py YYYY-MM-DD [--force]
"""
import json, os, sys

ROMAJI = {'札幌': 'sapporo', '函館': 'hakodate', '福島': 'fukushima', '新潟': 'niigata',
          '東京': 'tokyo', '中山': 'nakayama', '中京': 'chukyo', '京都': 'kyoto',
          '阪神': 'hanshin', '小倉': 'kokura'}


def build(date, force=False):
    work = f'data/tracking/work/{date}'
    man = json.load(open(f'{work}/manifest.json'))
    preds = json.load(open(f'{work}/predictions.json'))
    written = []

    for v in man['venues']:
        venue = v['venue']
        pv = preds.get(venue)
        if not pv:
            print(f'{venue}: predictions.json に無いのでスキップ')
            continue
        out = f"data/tracking/{date}-{ROMAJI.get(venue, venue)}.json"
        if os.path.exists(out) and not force:
            print(f'{out} は既存のためスキップ（上書きは --force）')
            continue

        races, agree, skipped = [], 0, []
        for r in v['races']:
            pr = pv.get(r['race'])
            if not pr:
                skipped.append(r['race']); continue
            pr = {int(k): x for k, x in pr.items()}
            po = {int(k): val for k, val in r['placeOdds'].items()}
            if set(pr) != set(po):
                skipped.append(f"{r['race']}(馬番不一致)"); continue

            places = r['placePositions']
            mk = {no: 0.8 / ((po[no][0] + po[no][1]) / 2) for no in po}
            sp = sum(x['place'] for x in pr.values())
            hs = [{'no': no,
                   'market': round(mk[no] * 100, 2),
                   'vrs18Raw': pr[no]['place'],
                   'vrs18Norm': round(pr[no]['place'] / sp * places * 100, 2),
                   'vrs18Win': pr[no]['win'],
                   'vrs18Odds': pr[no].get('odds'),
                   'placeOdds': po[no]} for no in sorted(po)]
            ma = max(hs, key=lambda h: h['market'])
            va = max(hs, key=lambda h: h['vrs18Raw'])
            ok = ma['no'] == va['no']; agree += ok
            races.append({**{k: r[k] for k in
                             ('race', 'raceId', 'field', 'placePositions',
                              'oddsStatus', 'oddsAt')},
                          'marketSum': round(sum(mk.values()), 3),
                          'axis': {'market': {'no': ma['no'], 'place': ma['market']},
                                   'vrs18': {'no': va['no'], 'placeNorm': va['vrs18Norm'],
                                             'placeRaw': va['vrs18Raw']}},
                          'agree': ok,
                          'vrs18Sums': {'win': round(sum(x['win'] for x in pr.values()), 2),
                                        'place': round(sp, 2),
                                        'placeTheoretical': places * 100},
                          'horses': hs})

        rec = {'meet': v['title'], 'venue': venue, 'date': date,
               'recordedAt': man['preparedAt'],
               'source': {'article': v['article'], 'publishedAt': v['publishedAt'],
                          'extraction': '予測値は記事内のグラフ画像。モデルが読み取って数値化'},
               'framing': ('運用ルールは「複勝オッズ最安を軸」＝市場そのもの。'
                           '実質「市場 vs VRS18」の比較。'),
               'method': {'market': '複勝オッズ範囲の中点から 0.8/odds。レース内正規化はしない',
                          'vrs18': 'VRS18の出力は未正規化。vrs18Normは理論値へ正規化した値'},
               'prereg': {'主指標': '軸が複勝圏に入ったか（8頭以上は3着まで、5-7頭は2着まで）',
                          '副指標': '全出走馬の複勝予測に対する対数損失'},
               'axisAgreement': f'{agree}/{len(races)}',
               'races': races}
        json.dump(rec, open(out, 'w'), ensure_ascii=False, indent=1)
        written.append(out)
        print(f'{out}  {len(races)}レース  軸の一致 {agree}/{len(races)}'
              + (f'  スキップ {skipped}' if skipped else ''))
        started = [r['race'] for r in races if r['oddsStatus'] != 'middle']
        if started:
            print(f'  注意: 発走済みで記録したレース {started}')
    return written


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('usage: vrs18_build.py YYYY-MM-DD [--force]')
    build(sys.argv[1], '--force' in sys.argv)
