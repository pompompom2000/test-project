#!/usr/bin/env python3
"""1頭軸と2頭軸を、点数を揃えて比較する。

設計は data/analysis/axis-count-prereg.md に、データを見る前に固定してある。
人気順位だけで買い目を決めるので、予想の巧拙は入らない。
実際の着順と実際の払戻を使うので、確率推定を介さない。
"""
import json, random, statistics, sys
from itertools import combinations

DATA = 'data/analysis/trio-payouts.json'
MIN_RUNNERS = 12


def one_axis(k):
    """軸=人気1、相手=人気2..k。点数 C(k-1,2)。"""
    partners = set(range(2, k + 1))
    pts = len(list(combinations(partners, 2)))
    def hit(pops):
        if 1 not in pops:
            return False
        rest = [p for p in pops if p != 1]
        return len(rest) == 2 and all(p in partners for p in rest)
    return f'1頭軸(人気1 → 2-{k})', pts, hit, k


def two_axis_a(m):
    """軸=人気1,2、相手=人気3..m。点数 m-2。"""
    partners = set(range(3, m + 1))
    pts = m - 2
    def hit(pops):
        if 1 not in pops or 2 not in pops:
            return False
        rest = [p for p in pops if p not in (1, 2)]
        return len(rest) == 1 and rest[0] in partners
    return f'2頭軸A(人気1,2 → 3-{m})', pts, hit, m


def two_axis_b(pts):
    """軸=人気1,3、相手=それ以外の人気上位から pts 頭。秋華賞の形に近い版。"""
    partners, p = set(), 2
    while len(partners) < pts:
        if p not in (1, 3):
            partners.add(p)
        p += 1
    need = max(partners)
    def hit(pops):
        if 1 not in pops or 3 not in pops:
            return False
        rest = [p for p in pops if p not in (1, 3)]
        return len(rest) == 1 and rest[0] in partners
    return f'2頭軸B(人気1,3 → {sorted(partners)})', pts, hit, need


def run(races, strat):
    name, pts, hit, need = strat
    stake = hits = ret = 0
    per = {}
    for rid, d in races.items():
        if d['runners'] < max(MIN_RUNNERS, need):
            continue
        s = pts * 100
        r = sum(t['pay'] for t in d['trio'] if hit(t['pops']))
        stake += s; ret += r; hits += 1 if r else 0
        per[rid] = r - s
    return {'name': name, 'points': pts, 'races': len(per), 'stake': stake,
            'hits': hits, 'return': ret,
            'roi': ret / stake if stake else 0,
            'hitRate': hits / len(per) if per else 0, 'per': per}


def boot(a, b, n=4000, seed=0):
    """レース単位で対応をとった差（1頭軸 − 2頭軸）のブートストラップ区間。"""
    keys = sorted(set(a['per']) & set(b['per']))
    d = [a['per'][k] - b['per'][k] for k in keys]
    random.seed(seed)
    ms = sorted(statistics.mean(random.choice(d) for _ in d) for _ in range(n))
    return len(d), statistics.mean(d), ms[int(n * 0.025)], ms[int(n * 0.975)]


def main():
    races = json.load(open(DATA))
    races = {k: v for k, v in races.items() if v['runners'] >= MIN_RUNNERS}
    print(f'対象 {len(races)}レース（12頭以上、2025年のJRA）')
    print(f'3連複の払戻率は0.75。これを基準に読む。\n')
    for pts, k, m in [(3, 4, 5), (6, 5, 8), (10, 6, 12)]:
        print(f'=== {pts}点 ===')
        A = run(races, one_axis(k))
        B = run(races, two_axis_a(m))
        C = run(races, two_axis_b(pts))
        for r in (A, B, C):
            print(f"  {r['name']:<28s} {r['races']:5d}レース  "
                  f"的中 {r['hits']:4d} ({r['hitRate']*100:5.2f}%)  "
                  f"回収率 {r['roi']*100:6.2f}%")
        for other in (B, C):
            n, mean, lo, hi = boot(A, other)
            tag = '1頭軸が有利' if lo > 0 else ('2頭軸が有利' if hi < 0 else '差を検出できない')
            print(f"  1頭軸 − {other['name'][:8]}: 1レースあたり {mean:+7.1f}円  "
                  f"95%CI [{lo:+.1f}, {hi:+.1f}]  → {tag}")
        print()


if __name__ == '__main__':
    main()
