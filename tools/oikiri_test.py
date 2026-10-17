#!/usr/bin/env python3
"""調教評価（因子#15）を、事前登録した手順で検定する。

data/analysis/oikiri-prereg.md に、結果を見る前に固定した設計がある。
市場は確定複勝オッズ（data/validation-g1-place-odds.json）。
確定オッズは締切後なので運用には使えないが、因子検証では
「市場が持つ情報をすべて与えたうえで、それでも調教が勝つか」という
最も厳しい基準になる。他の14因子もこの基準で落ちている。
"""
import glob, json, math, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from style_offset import fit, logit

GRADES = ['A', 'B', 'C', 'D']
REF = 'B'


def load():
    po = json.load(open('data/validation-g1-place-odds.json'))
    oi = json.load(open('data/analysis/oikiri-g1.json'))
    rows = []
    for p in sorted(glob.glob('data/validation-g1/*.json')):
        rid = re.search(r'(\d{12})\.json$', os.path.basename(p)).group(1)
        e, g = po.get(rid), oi.get(rid)
        if not e or not e.get('odds') or not g:
            continue
        d = json.load(open(p))
        year = int(os.path.basename(p)[:4])
        top3 = set(d['finish'][:3])
        raw = {}
        for h in d['horses']:
            v = e['odds'].get(f"{h['no']:02d}")
            if v:
                raw[h['no']] = 2.0 / (float(v[0]) + float(v[1]))
        if len(raw) < len(d['horses']) - 1:
            continue
        S = sum(raw.values())
        for h in d['horses']:
            if h['no'] not in raw:
                continue
            m = raw[h['no']] / S * 3.0
            gr = (g['grades'].get(str(h['no'])) or {}).get('grade')
            if not (1e-4 < m < 0.9999) or gr not in GRADES:
                continue
            rows.append({'m': m, 'y': 1 if h['no'] in top3 else 0,
                         'g': gr, 'year': year, 'rid': rid})
    return rows


def chi2_sf(x, k):
    """自由度kのカイ二乗上側確率（k<=3のみ使う）。"""
    from math import erf, exp, sqrt, pi
    if k == 1:
        return 2 * (1 - 0.5 * (1 + erf(sqrt(x / 2))))
    if k == 2:
        return exp(-x / 2)
    if k == 3:
        return (2 * (1 - 0.5 * (1 + erf(sqrt(x / 2))))
                + sqrt(2 * x / pi) * exp(-x / 2))
    return float('nan')


def feat(r):
    return [1.0 if r['g'] == g else 0.0 for g in GRADES if g != REF]


def loglik(rows, beta, b=1.0, a=0.0):
    ll = 0.0
    for r in rows:
        z = a + b * logit(r['m']) + sum(c * x for c, x in zip(beta, feat(r)))
        p = 1 / (1 + math.exp(-max(-30, min(30, z))))
        p = min(max(p, 1e-12), 1 - 1e-12)
        ll += math.log(p) if r['y'] else math.log(1 - p)
    return ll


def main():
    rows = load()
    names = [f'評価{g}' for g in GRADES if g != REF]
    print(f'対象 {len(set(r["rid"] for r in rows))}レース {len(rows)}頭  '
          f'（基準=評価{REF}）\n')

    print('【1】生の3着内率')
    for g in GRADES:
        s = [r for r in rows if r['g'] == g]
        if not s:
            continue
        hit = sum(r['y'] for r in s)
        mk = sum(r['m'] for r in s) / len(s)
        print(f'  {g}: {len(s):5d}頭  3着内 {hit:4d}  {hit/len(s)*100:5.1f}%'
              f'   市場の平均予想 {mk*100:5.1f}%   差 {(hit/len(s)-mk)*100:+5.1f}pt')

    print('\n【2】市場オフセット付きロジスティック回帰')
    for fix in (True, False):
        lab = 'b=1に固定（事前登録どおり）' if fix else 'b を推定（頑健性確認）'
        print(f'  -- {lab}')
        beta, se = fit(rows, names, feat, fix_b=fix)
        off = 0 if fix else 1
        a1, b1 = beta[0], (1.0 if fix else beta[1])
        bb = beta[1 + off:]
        ll1 = loglik(rows, bb, b=b1, a=a1)
        beta0, _ = fit(rows, [], lambda r: [], fix_b=fix)
        a0, b0 = beta0[0], (1.0 if fix else beta0[1])
        ll0 = loglik(rows, [], b=b0, a=a0)
        lr = 2 * (ll1 - ll0)
        df = len(names)
        print(f'     尤度比検定: LR={lr:.2f}  df={df}  p={chi2_sf(lr, df):.4f}\n')

    print('\n【3】期間2分割の予測検定（前期2015-2020 / 後期2021-2025）')
    tr = [r for r in rows if r['year'] <= 2020]
    te = [r for r in rows if r['year'] >= 2021]
    print(f'  前期 {len(tr)}頭 / 後期 {len(te)}頭')
    btr, _ = fit(tr, names, feat, fix_b=True)
    base = -loglik(te, [0.0] * len(names), a=btr[0]) / len(te)
    print(f'  市場のみ（β=0）           後期の対数損失 {base:.4f}')
    for k in (1.0, 0.5, 0.25, 0.0):
        beta = [c * k for c in btr[1:]]
        ll = -loglik(te, beta, a=btr[0]) / len(te)
        tag = {1.0: '収縮なし', 0.5: '半分に収縮', 0.25: '1/4に収縮', 0.0: '完全収縮'}[k]
        print(f'  前期のβ×{k:<4} ({tag:<10s}) 後期の対数損失 {ll:.4f}  '
              f'{"改善" if ll < base else "悪化"} {ll-base:+.4f}')


if __name__ == '__main__':
    main()
