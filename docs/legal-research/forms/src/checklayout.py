# -*- coding: utf-8 -*-
"""生成した .docx の表が版面からはみ出していないかを調べる。

この環境では LibreOffice が動かず、レイアウトを画面で確認できない。
そこで document.xml を直接読み、各セクションの版面の幅（用紙幅 － 左右余白）と、
その中にある表の列幅の合計を突き合わせる。

はみ出しの原因でいちばん多いのは、横向きセクションの用紙寸法の取り違え。
docx パッケージは LANDSCAPE のとき width と height を入れ替えて書き出すので、
size には A4 縦の寸法（11906 × 16838）をそのまま渡す。入れ替え済みの値を渡すと
二重に入れ替わり、orient だけ landscape・紙幅は A4 縦という版面ができる。

使い方:  python3 src/checklayout.py
"""
import glob
import os
import re
import sys
import zipfile


def attr(tag, name):
    m = re.search(r'w:%s="(-?\d+)"' % name, tag)
    return int(m.group(1)) if m else None


def sections(xml):
    """(用紙幅, 用紙高, 向き, 版面の幅) を本文の登場順に返す。"""
    out = []
    for s in re.findall(r"<w:sectPr[^>]*>.*?</w:sectPr>", xml, re.S):
        pg = re.search(r"<w:pgSz([^/]*)/>", s)
        mg = re.search(r"<w:pgMar([^/]*)/>", s)
        if not pg or not mg:
            continue
        w, h = attr(pg.group(1), "w"), attr(pg.group(1), "h")
        o = re.search(r'w:orient="(\w+)"', pg.group(1))
        left, right = attr(mg.group(1), "left"), attr(mg.group(1), "right")
        out.append((w, h, o.group(1) if o else "portrait", w - left - right))
    return out


def check(path):
    xml = zipfile.ZipFile(path).read("word/document.xml").decode("utf-8")
    secs = sections(xml)
    print("== %s" % os.path.basename(path))
    for i, (w, h, o, u) in enumerate(secs):
        # 向きと紙幅が食い違っていないか（横向きなら幅 > 高さ のはず）
        warn = ""
        if o == "landscape" and w < h:
            warn = "   ← 横向きなのに紙幅が縦のまま。size の width/height を見直すこと"
        print("   sec%d: %d x %d %s 版面の幅=%d%s" % (i, w, h, o, u, warn))

    parts = re.split(r"(<w:sectPr[^>]*>.*?</w:sectPr>)", xml, flags=re.S)
    sec = 0
    bad = 0
    for part in parts:
        if part.startswith("<w:sectPr"):
            sec += 1
            continue
        for ti, t in enumerate(re.findall(r"<w:tbl>.*?</w:tbl>", part, re.S)):
            usable = secs[min(sec, len(secs) - 1)][3]
            grid = sum(int(m) for m in re.findall(r'<w:gridCol w:w="(\d+)"', t))
            if grid > usable:
                print("   !! sec%d 表%d 列幅の合計=%d > 版面=%d（%dはみ出し）"
                      % (sec, ti, grid, usable, grid - usable))
                bad += 1
            for ri, r in enumerate(re.findall(r"<w:tr>.*?</w:tr>", t, re.S)):
                cw = sum(int(m) for m in re.findall(r'<w:tcW w:w="(\d+)"', r))
                if cw > usable:
                    print("   !! sec%d 表%d 行%d セル幅の合計=%d > 版面=%d"
                          % (sec, ti, ri, cw, usable))
                    bad += 1
    print("   はみ出し %d" % bad)
    return bad


if __name__ == "__main__":
    d = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files = sys.argv[1:] or sorted(glob.glob(os.path.join(d, "*.docx")))
    total = sum(check(f) for f in files)
    print()
    print("合計 はみ出し %d" % total)
    sys.exit(1 if total else 0)
