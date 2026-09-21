"""騎手別の成績と回収率を集計する。

リーディング（勝利数の順位表）は公表されているが、回収率までは載らない。
「よく勝つ騎手」と「買って得な騎手」は別物なので、両方を並べて出す。

    python3 tools/jockey_leading.py jockey_ev.csv [最低騎乗数]

単勝回収率 = Σ(勝った騎乗の単勝オッズ×100) ÷ (騎乗数×100)
複勝回収率 = Σ(3着内の複勝払戻) ÷ (騎乗数×100)
"""
import csv, sys, math
from collections import defaultdict


def ci(values, z=1.96):
    """平均の95%信頼区間。回収率は分散が大きいので幅を必ず見る。"""
    n = len(values)
    if n < 2:
        return (0.0, 0.0)
    m = sum(values) / n
    var = sum((x - m) ** 2 for x in values) / (n - 1)
    se = math.sqrt(var / n)
    return (m - z * se, m + z * se)


def main(path, min_rides=100):
    rows = list(csv.DictReader(open(path)))
    st = defaultdict(lambda: dict(rides=0, win=0, place=0, win_ret=[], place_ret=[]))
    for r in rows:
        j = (r.get('jockey') or '').strip()
        if not j:
            continue
        s = st[j]
        s['rides'] += 1
        won = r['place'] == '1'
        s['win'] += won
        s['place'] += int(r['placed'])
        s['win_ret'].append(float(r['win_odds']) * 100 if won else 0)
        s['place_ret'].append(int(r['place_payout']) if int(r['placed']) else 0)

    elig = {j: s for j, s in st.items() if s['rides'] >= min_rides}
    print(f'全騎手 {len(st)}名 / {min_rides}騎乗以上 {len(elig)}名 / 延べ {len(rows):,}騎乗\n')

    print('■ リーディング（勝利数順）')
    print('順 騎手           騎乗   勝利   勝率   3着内率  単回収   複回収')
    for i, (j, s) in enumerate(sorted(elig.items(), key=lambda x: -x[1]['win'])[:25], 1):
        wr = sum(s['win_ret']) / (s['rides'] * 100)
        pr = sum(s['place_ret']) / (s['rides'] * 100)
        print(f"{i:>2} {j:<13}{s['rides']:>5}  {s['win']:>5}  {s['win']/s['rides']*100:>5.1f}%  "
              f"{s['place']/s['rides']*100:>6.1f}%  {wr*100:>6.1f}%  {pr*100:>6.1f}%")

    print('\n■ 単勝回収率の高い順（買って得な騎手）')
    print('順 騎手           騎乗   勝利   勝率   単回収   95%信頼区間')
    ranked = sorted(elig.items(), key=lambda x: -sum(x[1]['win_ret']) / x[1]['rides'])
    for i, (j, s) in enumerate(ranked[:15], 1):
        wr = sum(s['win_ret']) / (s['rides'] * 100)
        lo, hi = ci(s['win_ret'])
        print(f"{i:>2} {j:<13}{s['rides']:>5}  {s['win']:>5}  {s['win']/s['rides']*100:>5.1f}%  "
              f"{wr*100:>6.1f}%  [{lo/100*100:>6.1f}〜{hi/100*100:>6.1f}%]")

    print('\n■ 単勝回収率の低い順（買うと損な騎手）')
    for i, (j, s) in enumerate(ranked[-5:], 1):
        wr = sum(s['win_ret']) / (s['rides'] * 100)
        print(f"   {j:<13}{s['rides']:>5}騎乗  勝率{s['win']/s['rides']*100:>5.1f}%  単回収{wr*100:>6.1f}%")

    # 100%を超える騎手が偶然かどうか
    over = [j for j, s in elig.items() if sum(s['win_ret']) / (s['rides'] * 100) > 1]
    print(f'\n単勝回収率が100%を超えた騎手: {len(over)}/{len(elig)}名')
    sig = []
    for j, s in elig.items():
        lo, _ = ci(s['win_ret'])
        if lo / 100 > 1:
            sig.append(j)
    print(f'うち信頼区間の下限も100%を超えた騎手: {len(sig)}名 {sig if sig else ""}')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'jockey_ev.csv',
         int(sys.argv[2]) if len(sys.argv) > 2 else 100)
