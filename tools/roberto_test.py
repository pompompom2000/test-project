#!/usr/bin/env python3
"""長距離×道悪でロベルト系が有利か。設計は data/analysis/roberto-prereg.md。

主張は「良馬場との差」なので、主検定はロベルト系×道悪の交互作用に置く。
標本数を検定の前に出す（事前登録で決めた手順）。
"""
import json, math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from style_offset import solve, inv

DATA = 'data/analysis/longmud-data.json'
SIRES = 'data/analysis/roberto-sires.json'


def load(min_dist):
    sires = json.load(open(SIRES))
    rows = []
    for rid, r in json.load(open(DATA)).items():
        if r['dist'] < min_dist:
            continue
        for h in r['horses']:
            if h.get('finish') is None or h.get('pop') is None:
                continue
            s, b = sires.get(h.get('sire') or ''), sires.get(h.get('bms') or '')
            if s is None or b is None or s.get('roberto') is None or b.get('roberto') is None:
                continue                      # 判定できなかった馬は落とす
            rows.append({'y': 1 if h['finish'] <= 3 else 0,
                         'pop': h['pop'], 'ground': r['ground'],
                         'rob': 1 if (s['roberto'] or b['roberto']) else 0,
                         'sireRob': 1 if s['roberto'] else 0,
                         'dist': r['dist'], 'rid': rid})
    return rows


def irls(rows, cols, feat):
    k = len(cols)
    X = [[1.0] + feat(r) for r in rows]
    y = [float(r['y']) for r in rows]
    beta = [0.0] * k
    for _ in range(80):
        A = [[0.0] * k for _ in range(k)]
        z = [0.0] * k
        for i, xi in enumerate(X):
            eta = max(-30.0, min(30.0, sum(xi[j] * beta[j] for j in range(k))))
            mu = 1 / (1 + math.exp(-eta))
            w = max(mu * (1 - mu), 1e-9)
            t = eta + (y[i] - mu) / w
            for a in range(k):
                z[a] += xi[a] * w * t
                for b in range(a, k):
                    A[a][b] += xi[a] * w * xi[b]
        for a in range(k):
            for b in range(a):
                A[a][b] = A[b][a]
        nb = solve([r[:] for r in A], z)
        if max(abs(nb[j] - beta[j]) for j in range(k)) < 1e-10:
            beta = nb
            break
        beta = nb
    C = inv(A)
    se = [math.sqrt(max(C[j][j], 0.0)) for j in range(k)]
    out = []
    for nm, b, s in zip(cols, beta, se):
        zz = b / s if s else 0.0
        p = 2 * (1 - 0.5 * (1 + math.erf(abs(zz) / math.sqrt(2))))
        out.append((nm, b, s, zz, p))
    return out


def cells(rows, mudset, label):
    print(f'  馬場の分け方: 道悪 = {label}')
    print(f'  {"":12s}{"頭数":>7s}{"3着内":>7s}{"率":>8s}{"平均人気":>9s}')
    for rob in (1, 0):
        for g, gn in ((1, '道悪'), (0, '良+その他')):
            s = [r for r in rows if r['rob'] == rob and (r['ground'] in mudset) == (g == 1)]
            if not s:
                continue
            hit = sum(r['y'] for r in s)
            print(f'  {"ロベルト" if rob else "非ロベルト":<10s}{gn:<6s}{len(s):5d}{hit:7d}'
                  f'{hit/len(s)*100:7.1f}%{sum(r["pop"] for r in s)/len(s):8.1f}')
    print()


def run(min_dist, mudset, label):
    rows = load(min_dist)
    mud = [r for r in rows if r['ground'] in mudset]
    print(f'=== {min_dist}m以上 / 道悪={label} ===')
    print(f'  対象 {len(rows)}頭（うち道悪 {len(mud)}頭、ロベルト系 '
          f'{sum(r["rob"] for r in rows)}頭）')
    if len(mud) < 150:
        print(f'  → 道悪が{len(mud)}頭で事前登録の基準(150頭)を下回る。検定しない。\n')
        cells(rows, mudset, label)
        return
    cells(rows, mudset, label)
    feat = lambda r: [math.log(r['pop']), r['rob'],
                      1.0 if r['ground'] in mudset else 0.0,
                      r['rob'] * (1.0 if r['ground'] in mudset else 0.0)]
    cols = ['(切片)', 'log(人気)', 'ロベルト系', '道悪', 'ロベルト系×道悪']
    print(f'  {"項":<16s}{"係数":>9s}{"SE":>8s}{"z":>7s}{"p":>8s}')
    for nm, b, s, z, p in irls(rows, cols, feat):
        mark = '  ←主検定' if nm.endswith('×道悪') else ''
        print(f'  {nm:<16s}{b:>+9.3f}{s:>8.3f}{z:>7.2f}{p:>8.3f}{mark}')
    print()


if __name__ == '__main__':
    print('ロベルト系 = 父の父系、または母父の父系が Roberto に行き着く\n')
    run(3000, {'重', '不良'}, '重・不良')
    run(2500, {'重', '不良'}, '重・不良')
    run(2500, {'重', '不良', '稍重'}, '重・不良・稍重（感度分析）')
    run(3000, {'重', '不良', '稍重'}, '重・不良・稍重（感度分析）')
