# -*- coding: utf-8 -*-
"""docx が何ページになるか、どこで改ページされるかを行数から見積もる。

この環境では LibreOffice が動かず、レイアウトを画面で見られない。
記入用の書式では「回答欄が改ページで上下に割れる」のが一番困るので、
段落と表の行数から高さを積み上げて、どの見出しが何ページ目に来るかを出す。

あくまで見積もりで、実際の折返しまでは見ていない。
Word で開いたときの答え合わせに使うこと。

使い方:  python3 src/checkpages.py [ファイル.docx ...]
"""
import glob
import html
import os
import re
import sys
import zipfile

LINE = 260      # 表のセル1行あたりの高さ（line=260 で組んでいる）
CELLPAD = 120   # セルの上下マージン合計


def sections(xml):
    out = []
    for s in re.findall(r"<w:sectPr[^>]*>.*?</w:sectPr>", xml, re.S):
        pg = re.search(r"<w:pgSz([^/]*)/>", s)
        mg = re.search(r"<w:pgMar([^/]*)/>", s)
        if not pg or not mg:
            continue
        g = lambda t, k: int(re.search(r'w:%s="(-?\d+)"' % k, t).group(1))
        out.append(g(pg.group(1), "h") - g(mg.group(1), "top") - g(mg.group(1), "bottom"))
    return out


def check(path):
    xml = zipfile.ZipFile(path).read("word/document.xml").decode("utf-8")
    usable = sections(xml)[0]
    body = re.search(r"<w:body>(.*)</w:body>", xml, re.S).group(1)
    print("== %s（1ページの高さ %d twips）" % (os.path.basename(path), usable))
    run, page = 0, 1
    for m in re.finditer(r"<w:tbl>.*?</w:tbl>|<w:p [^>]*>.*?</w:p>|<w:p>.*?</w:p>", body, re.S):
        t = m.group(0)
        forced = "pageBreakBefore" in t
        if t.startswith("<w:tbl>"):
            h = 0
            for r in re.findall(r"<w:tr>.*?</w:tr>", t, re.S):
                cells = re.findall(r"<w:tc>.*?</w:tc>", r, re.S)
                h += max(len(re.findall(r"<w:p[ >]", c)) for c in cells) * LINE + CELLPAD
        else:
            sp = re.search(r'w:line="(\d+)"', t)
            h = int(sp.group(1)) if sp else 290
        label = html.unescape(re.sub(r"<[^>]+>", "", t))[:38].strip()
        if forced or run + h > usable:
            print("   ---- %dページ目 使用 %d / %d %s" %
                  (page, run, usable, "（明示の改ページ）" if forced else ""))
            page += 1
            run = 0
        run += h
        if label:
            print("   p%d %6d  %s" % (page, run, label))
    print("   ---- %dページ目 使用 %d / %d" % (page, run, usable))
    print("   合計 %d ページ" % page)
    return page


if __name__ == "__main__":
    d = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files = sys.argv[1:] or sorted(glob.glob(os.path.join(d, "*.docx")))
    for f in files:
        check(f)
        print()
