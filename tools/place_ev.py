"""複勝の最低払戻（下限）が効いている馬の期待値を、過去データで調べる。

複勝は最低払戻が100円（1.0倍）に決められている。人気が集中しすぎると
オッズがこの下限に張り付き、本来の確率に見合わない安さで止まる。
その結果、抜けた1番人気の複勝は「安すぎるがゆえに割に合う」ことが
起きうる——という仮説を、実際の3着内率と複勝払戻で検証する。

    python3 tools/place_ev.py place_ev.csv

複勝の払戻はプールの分配で決まるため、事前オッズは遡れない。
代わりに単勝オッズを「人気の集中度」の代理指標として使う。
"""
import csv, sys, math
from collections import defaultdict

BUCKETS = [
    ('〜1.2倍', 0, 1.2), ('1.2〜1.5倍', 1.2, 1.5), ('1.5〜2.0倍', 1.5, 2.0),
    ('2.0〜2.5倍', 2.0, 2.5), ('2.5〜3.0倍', 2.5, 3.0), ('3.0〜4.0倍', 3.0, 4.0),
    ('4.0〜5.0倍', 4.0, 5.0), ('5.0〜7.0倍', 5.0, 7.0), ('7.0〜10倍', 7.0, 10.0),
    ('10〜20倍', 10.0, 20.0), ('20〜50倍', 20.0, 50.0), ('50倍〜', 50.0, 1e9),
]


def wilson(k, n, z=1.96):
    """二項比率の信頼区間。標本が少ない上位人気帯でも幅を見誤らないため。"""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    r = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - r) / d, (c + r) / d)


def main(path):
    rows = list(csv.DictReader(open(path)))
    print(f'読み込み: {len(rows):,}頭ぶん')

    stats = defaultdict(lambda: dict(n=0, placed=0, payout=0))
    for r in rows:
        od = float(r['win_odds'])
        for name, lo, hi in BUCKETS:
            if lo <= od < hi:
                s = stats[name]
                s['n'] += 1
                s['placed'] += int(r['placed'])
                s['payout'] += int(r['place_payout'])
                break

    print('\n■ 単勝オッズ帯ごとの複勝成績（全レース）')
    print('オッズ帯         頭数   3着内率   平均複勝配当  回収率   95%信頼区間の回収率')
    for name, _, _ in BUCKETS:
        s = stats[name]
        if not s['n']:
            continue
        rate = s['placed'] / s['n']
        avg = s['payout'] / s['placed'] if s['placed'] else 0
        roi = s['payout'] / (s['n'] * 100)
        lo, hi = wilson(s['placed'], s['n'])
        print(f"{name:<14}{s['n']:>7,}  {rate*100:>6.1f}%  {avg:>9.0f}円  "
              f"{roi*100:>6.1f}%  {lo*avg/100*100:>6.1f}% 〜 {hi*avg/100*100:>5.1f}%")

    # 下限が効いていそうな馬（単勝1.5倍未満）を細かく見る
    print('\n■ 単勝1.5倍未満の馬（下限が効きやすい層）')
    tight = [r for r in rows if float(r['win_odds']) < 1.5]
    if tight:
        n = len(tight)
        placed = sum(int(r['placed']) for r in tight)
        payout = sum(int(r['place_payout']) for r in tight)
        paid = [int(r['place_payout']) for r in tight if int(r['placed'])]
        floor = sum(1 for p in paid if p <= 110)
        print(f'  頭数 {n}　3着内 {placed}（{placed/n*100:.1f}%）')
        print(f'  回収率 {payout/(n*100)*100:.1f}%')
        print(f'  的中時の配当: 最低 {min(paid)}円 / 中央 {sorted(paid)[len(paid)//2]}円 / 最高 {max(paid)}円')
        print(f'  110円以下の配当が {floor}/{len(paid)}（{floor/len(paid)*100:.0f}%）')
        lo, hi = wilson(placed, n)
        avg = payout / placed
        print(f'  回収率の95%信頼区間: {lo*avg/100*100:.1f}% 〜 {hi*avg/100*100:.1f}%')

    # 馬場・距離での違い
    print('\n■ 単勝2.0倍未満の馬を条件別に')
    print('条件            頭数   3着内率   回収率')
    def show(label, sel):
        if not sel:
            return
        n = len(sel)
        placed = sum(int(r['placed']) for r in sel)
        payout = sum(int(r['place_payout']) for r in sel)
        print(f'{label:<14}{n:>7,}  {placed/n*100:>6.1f}%  {payout/(n*100)*100:>6.1f}%')

    fav = [r for r in rows if float(r['win_odds']) < 2.0]
    show('全体', fav)
    show('芝', [r for r in fav if r['surface'] == '芝'])
    show('ダート', [r for r in fav if r['surface'] == 'ダ'])
    show('良馬場', [r for r in fav if r['going'] == '良'])
    show('道悪', [r for r in fav if r['going'] in ('稍', '稍重', '重', '不', '不良')])
    show('少頭数(〜12)', [r for r in fav if int(r['field']) <= 12])
    show('多頭数(13〜)', [r for r in fav if int(r['field']) >= 13])


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'place_ev.csv')
