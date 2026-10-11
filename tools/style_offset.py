#!/usr/bin/env python3
"""市場の複勝価格をオフセットに置き、脚質が追加情報を持つか検定する。

logit(p_i) = a + b*logit(m_i) + Σ β_k * style_k

m_i は確定複勝オッズから逆算した市場の3着内確率（レース内でΣ=3に正規化）。
b を1に固定すれば「市場価格を所与として脚質に残差情報があるか」の検定、
b を推定すれば市場の校正そのものの検定になる。
numpy非依存のIRLS実装。
"""
import json, glob, math, os, re, sys


def load():
    po = json.load(open('data/validation-g1-place-odds.json'))
    rows = []
    for p in sorted(glob.glob('data/validation-g1/*.json')):
        rid = re.search(r'(\d{12})\.json$', os.path.basename(p)).group(1)
        e = po.get(rid)
        if not e or not e.get('odds'):
            continue
        d = json.load(open(p))
        top3 = set(d['finish'][:3])
        hs = d['horses']
        if len(hs) < 16:
            continue
        raw = {}
        for h in hs:
            v = e['odds'].get(f"{h['no']:02d}")
            if v:
                raw[h['no']] = 2.0 / (float(v[0]) + float(v[1]))
        if len(raw) < len(hs) - 1:
            continue
        S = sum(raw.values())
        for h in hs:
            if h['no'] not in raw:
                continue
            m = raw[h['no']] / S * 3.0
            if not (1e-4 < m < 0.9999):
                continue
            rows.append({'m': m, 'y': 1 if h['no'] in top3 else 0,
                         'style': h.get('style')})
    return rows


def solve(A, b):
    n = len(b)
    M = [A[i][:] + [b[i]] for i in range(n)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c]))
        if abs(M[p][c]) < 1e-12:
            raise ValueError('singular')
        M[c], M[p] = M[p], M[c]
        for r in range(n):
            if r == c:
                continue
            f = M[r][c] / M[c][c]
            for k in range(c, n + 1):
                M[r][k] -= f * M[c][k]
    return [M[i][n] / M[i][i] for i in range(n)]


def inv(A):
    n = len(A)
    cols = []
    for j in range(n):
        e = [1.0 if i == j else 0.0 for i in range(n)]
        cols.append(solve([r[:] for r in A], e))
    return [[cols[j][i] for j in range(n)] for i in range(n)]


def logit(p):
    return math.log(p / (1 - p))


def fit(rows, names, feat, fix_b=True):
    """fix_b=True なら logit(m) の係数を1に固定（オフセット）。"""
    cols = ['(切片)'] + (['logit(市場)'] if not fix_b else []) + names
    X, off, y = [], [], []
    for r in rows:
        f = feat(r)
        lm = logit(r['m'])
        X.append([1.0] + ([lm] if not fix_b else []) + f)
        off.append(lm if fix_b else 0.0)
        y.append(float(r['y']))
    n, k = len(X), len(cols)
    beta = [0.0] * k
    for _ in range(60):
        XtWX = [[0.0] * k for _ in range(k)]
        XtWz = [0.0] * k
        for i in range(n):
            eta = off[i] + sum(X[i][j] * beta[j] for j in range(k))
            eta = max(-30.0, min(30.0, eta))
            mu = 1 / (1 + math.exp(-eta))
            w = max(mu * (1 - mu), 1e-9)
            z = (eta - off[i]) + (y[i] - mu) / w
            for a in range(k):
                XtWz[a] += X[i][a] * w * z
                for b2 in range(a, k):
                    XtWX[a][b2] += X[i][a] * w * X[i][b2]
        for a in range(k):
            for b2 in range(a):
                XtWX[a][b2] = XtWX[b2][a]
        nb = solve([r[:] for r in XtWX], XtWz)
        if max(abs(nb[j] - beta[j]) for j in range(k)) < 1e-9:
            beta = nb
            break
        beta = nb
    C = inv(XtWX)
    se = [math.sqrt(max(C[j][j], 0.0)) for j in range(k)]
    print(f'   {"項":<14}{"係数":>9}{"SE":>8}{"z":>7}{"p":>9}')
    for j, nm in enumerate(cols):
        z = beta[j] / se[j] if se[j] else 0.0
        p = 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))
        print(f'   {nm:<14}{beta[j]:>+9.3f}{se[j]:>8.3f}{z:>7.2f}{p:>9.3f}')
    return beta, se


def main():
    rows = load()
    print(f'対象 {len(rows)}頭（16頭以上のレース）\n')

    print('■ モデル1: 市場価格をオフセット（係数1固定）+ 逃げ・追込ダミー')
    fit(rows, ['逃げ', '追込'],
        lambda r: [1.0 if r['style'] == '逃げ' else 0.0,
                   1.0 if r['style'] == '追込' else 0.0])

    print('\n■ モデル2: logit(市場)の係数も推定（市場の校正を検定）')
    fit(rows, ['逃げ', '追込'],
        lambda r: [1.0 if r['style'] == '逃げ' else 0.0,
                   1.0 if r['style'] == '追込' else 0.0], fix_b=False)

    print('\n■ モデル3: 逃げ・追込をまとめた1ダミー（オフセット固定）')
    fit(rows, ['逃げ or 追込'],
        lambda r: [1.0 if r['style'] in ('逃げ', '追込') else 0.0])

    print('\n■ 参考: 予測確率20%以上に限定（軸候補の範囲）')
    sub = [r for r in rows if r['m'] >= 0.20]
    print(f'   n={len(sub)}')
    fit(sub, ['逃げ', '追込'],
        lambda r: [1.0 if r['style'] == '逃げ' else 0.0,
                   1.0 if r['style'] == '追込' else 0.0])


if __name__ == '__main__':
    main()
