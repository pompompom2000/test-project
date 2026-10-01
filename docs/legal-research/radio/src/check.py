# -*- coding: utf-8 -*-
"""作った音声を機械で確かめる。耳で聞いた確認の代わりにはならない。

1. 合成に失敗した行がないか（文字数のわりに音が極端に短い行を探す）
2. 二人の声が聞き分けられるだけ離れているか（基本周波数の中央値を比べる）
3. README.md の章立ての時刻が、台本.md（実測）と合っているか

使い方:  python3 src/check.py
"""
import io
import json
import math
import pathlib
import re
import sys
import wave

import numpy as np

D = pathlib.Path(__file__).parent
B = D / "build"


def f0_median(path):
    """有声フレームごとに自己相関で基本周波数を出し、中央値を返す。

    最大ピークのラグをそのまま採るとオクターブ下に落ちることがあるので、
    最大の0.75倍を超えるもののうち最小のラグを採る。
    """
    with wave.open(str(path)) as w:
        sr = w.getframerate()
        d = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float)
    N, H = int(sr * 0.04), int(sr * 0.02)
    lo, hi = int(sr / 350), int(sr / 70)
    vals = []
    for i in range(0, len(d) - N, H):
        s = d[i:i + N]
        if np.sqrt((s ** 2).mean()) < 900:
            continue
        s = s - s.mean()
        ac = np.correlate(s, s, "full")[N - 1:]
        if ac[0] <= 0:
            continue
        seg = ac[lo:hi]
        if not len(seg) or seg.max() / ac[0] < 0.30:
            continue
        cand = np.where(seg >= seg.max() * 0.75)[0]
        vals.append(sr / (lo + cand[0]))
    return float(np.median(vals)) if len(vals) >= 5 else None


def main():
    data = json.loads((D / "radio.json").read_text(encoding="utf-8"))
    lines = [x for x in data["script"] if x["type"] == "line"]
    ng = 0

    # 1. 合成に失敗した行
    bad = []
    for i, x in enumerate(lines):
        p = B / ("l%04d.wav" % i)
        if not p.exists():
            bad.append((i, "ファイルが無い", x["text"][:28]))
            continue
        with wave.open(str(p)) as w:
            dur = w.getnframes() / w.getframerate()
        if dur < len(x["text"]) * 0.045:
            bad.append((i, "%.2f秒 / %d文字" % (dur, len(x["text"])), x["text"][:28]))
    print("1) 合成　セリフ %d行中、失敗の疑い %d行" % (len(lines), len(bad)))
    for i, why, t in bad[:10]:
        print("     !! %d行目 %s  %s" % (i, why, t))
    ng += len(bad)

    # 2. 声の分離
    a, b = [], []
    for i, x in enumerate(lines[:80]):
        v = f0_median(B / ("l%04d.wav" % i))
        if v:
            (a if x["sp"] == "A" else b).append(v)
    ma, mb = np.median(a), np.median(b)
    semi = 12 * math.log2(ma / mb)
    print("2) 声　　%s %.0fHz ／ %s %.0fHz ／ 差 約%.1f半音"
          % (data["speakers"]["A"], ma, data["speakers"]["B"], mb, semi))
    if semi < 3:
        print("     !! 近すぎます。gen.py の TONE を離してください")
        ng += 1

    # 3. READMEの章立てが実測と合っているか
    sc = re.findall(r"^\| (\d+:\d\d) \| (\d+)　", (D.parent / "台本.md").read_text(encoding="utf-8"), re.M)
    rm = re.findall(r"^\| (\d+:\d\d) \| (\d+)　", (D.parent / "README.md").read_text(encoding="utf-8"), re.M)
    same = sc == rm
    print("3) 章立て　台本.md %d章 ／ README.md %d章 ／ %s"
          % (len(sc), len(rm), "一致" if same else "ずれています"))
    if not same:
        for x, y in zip(sc, rm):
            if x != y:
                print("     !! 台本 %s ↔ README %s" % (x, y))
        ng += 1

    print()
    print("問題 %d件" % ng)
    print("※ 耳で聞いた確認はしていません。配る前に一度通しで聞いてください。")
    return 1 if ng else 0


if __name__ == "__main__":
    sys.exit(main())
