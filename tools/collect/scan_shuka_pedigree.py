#!/usr/bin/env python3
"""秋華賞20年350頭の血統表を10代前まで展開し、指定の牝馬の有無を集計する。

深さ10は打ち切りなので、未検出が「存在しない」のか「届かなかった」のかを
区別するため、経路上の目印（Bold Ruler＝Miss Discoの子、
Deputy Minister / Mint Copy＝Bunty's Flight側）の世代も記録する。
例: Bold Rulerが10代前なら Miss Disco は11代前で打ち切りの外。

冪等。途中で止めても再実行で続きから。
出力: data/analysis/shuka-sho-pedscan.json
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import expand_pedigree as ep

SRC = 'data/analysis/shuka-sho-weights.json'
OUT = 'data/analysis/shuka-sho-pedscan.json'
DEPTH = 10
MARKS = {"bunty's flight": 'BF', 'miss disco': 'MD',
         'bold ruler': 'BoldRuler', 'deputy minister': 'DeputyMinister',
         'mint copy': 'MintCopy'}


def norm(s):
    return re.sub(r"[’'`]", "'", s).lower()


def main():
    src = json.load(open(SRC))
    out = json.load(open(OUT)) if os.path.exists(OUT) else {}
    todo = [(y, h) for y in sorted(src) for h in src[y]['horses']
            if h.get('horseId') and h['horseId'] not in out]
    print(f'未処理 {len(todo)}頭 / キャッシュ {len(ep._CACHE)}頭', flush=True)
    for i, (y, h) in enumerate(todo, 1):
        try:
            a = ep.ancestors(h['horseId'], DEPTH)
        except Exception as e:
            print(f"  {h['name']} ERROR {e}", flush=True)
            continue
        rec = {'year': int(y), 'name': h['name'], 'place': h['place'],
               'popularity': h.get('popularity'), 'ancestors': len(a)}
        for key, lab in MARKS.items():
            g = [gg for _, (gg, n) in a.items() if key in norm(n)]
            rec[lab] = min(g) if g else None
        out[h['horseId']] = rec
        if i % 10 == 0:
            json.dump(out, open(OUT, 'w'), ensure_ascii=False)
            ep.save_cache()
            print(f'  [{i}/{len(todo)}] {y} {h["name"]} '
                  f'キャッシュ{len(ep._CACHE)} 取得{ep._FETCHED[0]}', flush=True)
    json.dump(out, open(OUT, 'w'), ensure_ascii=False, indent=1)
    ep.save_cache()
    print(f'完了 {len(out)}頭')


if __name__ == '__main__':
    main()
