#!/usr/bin/env python3
"""VRS18の予測は、市場に対して上乗せの情報を持っているか。

対数損失の単独比較（市場0.4317 vs VRS18正規化0.4414）は「VRS18だけを使うと
市場に劣る」ことしか言わない。劣る予測でも、市場と独立な成分があれば
混ぜて改善することはありうる。それを測る。

モデル: logit(p) = a + b*logit(市場) + c*[logit(VRS18) - logit(市場)]
  c = 0  → VRS18は上乗せを持たない（市場だけで十分）
  c > 0  → VRS18の方向に寄せると改善する
b を1に固定した市場オフセット版も併せて出す。

同じデータで係数を推定して評価すると、c はほぼ必ず正に出る。
この企画の基準（調教評価のときと同じ）に合わせ、前期で推定して
後期で検証する前向きの形を主とし、in-sample の値は参考として併記する。

    python3 tools/vrs18_increment_test.py
"""
import glob, json, math, random

TRACK = 'data/tracking'
EPS = 1e-4


def logit(p):
    p = min(max(p, EPS), 1 - EPS)
    return math.log(p / (1 - p))


def load(with_date=False):
    rows = []
    for fp in sorted(glob.glob(f'{TRACK}/2026-*.json')):
        d = json.load(open(fp))
        if 'races' not in d or 'swan' in fp:
            continue
        for r in d['races']:
            if 'result' not in r or r.get('oddsStatus') != 'middle':
                continue
            money = set(r['result']['inTheMoney'])
            for h in r['horses']:
                rec = (logit(h['market'] / 100), logit(h['vrs18Norm'] / 100),
                       1 if h['no'] in money else 0)
                rows.append(rec + (d['date'],) if with_date else rec)
    return rows


def fit(rows, free_b, iters=600, lr=0.05):
    a, b, c = 0.0, 1.0, 0.0
    n = len(rows)
    for _ in range(iters):
        ga = gb = gc = 0.0
        for lm, lv, y in rows:
            z = a + b * lm + c * (lv - lm)
            p = 1 / (1 + math.exp(-max(-30, min(30, z))))
            e = p - y
            ga += e; gb += e * lm; gc += e * (lv - lm)
        a -= lr * ga / n
        if free_b:
            b -= lr * gb / n
        c -= lr * gc / n
    return a, b, c


def nll(rows, a, b, c):
    s = 0.0
    for lm, lv, y in rows:
        z = a + b * lm + c * (lv - lm)
        p = 1 / (1 + math.exp(-max(-30, min(30, z))))
        p = min(max(p, EPS), 1 - EPS)
        s -= y * math.log(p) + (1 - y) * math.log(1 - p)
    return s / len(rows)


def forward(split_date):
    """前期で推定し、後期で検証する。"""
    allrows = load(with_date=True)
    early = [r[:3] for r in allrows if r[3] < split_date]
    late = [r[:3] for r in allrows if r[3] >= split_date]
    print(f'前期（{split_date}より前） {len(early)}頭 / 後期 {len(late)}頭\n')
    for free_b, label in ((False, 'b=1に固定'), (True, 'b も推定')):
        a, b, c = fit(early, free_b)
        base = nll(late, a, b, 0.0)
        full = nll(late, a, b, c)
        half = nll(late, a, b, c / 2)      # 収縮版
        print(f'{label}  前期で推定した c={c:+.4f}')
        print(f'  後期の対数損失  c=0 {base:.4f} / c {full:.4f} ({base-full:+.4f}) '
              f'/ c半分 {half:.4f} ({base-half:+.4f})')
        print(f'  判定: {"後期でも改善" if full < base else "後期では改善しない"}\n')


def main():
    rows = load()
    print(f'{len(rows)}頭（締切前オッズのレースのみ）\n')
    print('=== 前向き検証（主）: 10/12-10/18 で推定 → 11/01 で検証 ===')
    forward('2026-11-01')
    print('=== 同一データでの当てはめ（参考。cは構造上ほぼ必ず正に出る）===')
    for free_b, label in ((False, 'b=1に固定（市場オフセット）'), (True, 'b も推定')):
        a, b, c = fit(rows, free_b)
        base = nll(rows, a, b, 0.0)
        full = nll(rows, a, b, c)
        # c のブートストラップ区間
        cs = []
        rnd = random.Random(0)
        for _ in range(300):
            s = [rows[rnd.randrange(len(rows))] for _ in range(len(rows))]
            cs.append(fit(s, free_b)[2])      # 本推定と同じ反復回数で揃える
        cs.sort()
        lo, hi = cs[int(.025 * len(cs))], cs[int(.975 * len(cs))]
        print(f'{label}')
        print(f'  a={a:+.3f}  b={b:.3f}  c={c:+.4f}  95%CI [{lo:+.4f}, {hi:+.4f}]')
        print(f'  対数損失  c=0 のとき {base:.4f} → c を入れて {full:.4f}  '
              f'（{base-full:+.4f}）')
        print(f'  判定: {"VRS18に上乗せの情報がある" if lo > 0 else "上乗せは検出できない"}\n')


if __name__ == '__main__':
    main()
