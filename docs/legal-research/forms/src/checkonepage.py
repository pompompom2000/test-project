# -*- coding: utf-8 -*-
"""照会書が「1件1ページ」になっているかを、できたPDFで確かめる。

照会は窓口で該当ページだけ抜いて使う前提なので、1件が2ページにまたがると
回答欄だけが別の紙に残る。文面を足したときに起きやすい。

checkpages.py は段落の数からの見積もりで、セル内の折返しまでは見ていない。
こちらは実際のPDFのページを読むので正確。文面を直したら両方ではなくこちらを見ること。

使い方:  python3 src/checkonepage.py
"""
import json
import pathlib
import re
import sys

import pypdfium2 as pdfium

SRC = pathlib.Path(__file__).parent
PDF = SRC.parent / "運輸局照会書.pdf"
COVER = 3   # 表紙・登場人物・ことわりで3ページ


def main():
    d = json.loads((SRC / "shokai.json").read_text(encoding="utf-8"))
    nos = [q["no"] for q in d["inquiries"]]
    if not PDF.exists():
        print("  （PDF未生成。先に 運輸局照会書.gen.py を動かすこと）")
        return 1

    doc = pdfium.PdfDocument(str(PDF))
    pages = [doc[i].get_textpage().get_text_range() for i in range(len(doc))]
    bad = []

    want = COVER + len(nos)
    print("  PDF %d頁　表紙%d＋照会%d件 → %d頁が正しい" % (len(pages), COVER, len(nos), want))
    if len(pages) != want:
        bad.append("ページ数が合わない（%d頁。1件が2ページにまたがっている）" % len(pages))

    # 各ページの見出しを拾う。見出しは「【A-1】　…」の形。
    head = {}
    for i, t in enumerate(pages):
        for m in re.findall(r"【([A-C]-\d+)】", t):
            head.setdefault(m, []).append(i + 1)

    for no in nos:
        pg = head.get(no)
        if not pg:
            bad.append("%s の見出しが見つからない" % no)
        elif len(pg) > 1:
            bad.append("%s の見出しが複数ページにある: %s頁" % (no, pg))

    # 見出しのない本文ページ＝前の照会からの溢れ
    for i in range(COVER, len(pages)):
        if not re.search(r"【[A-C]-\d+】", pages[i]):
            first = next((x for x in pages[i].splitlines() if x.strip()), "")
            bad.append("%d頁に見出しがない（前の照会からの溢れ）: %s" % (i + 1, first[:40]))

    # 1ページに2件入っていないか
    for i, t in enumerate(pages):
        got = set(re.findall(r"【([A-C]-\d+)】", t))
        if len(got) > 1:
            bad.append("%d頁に照会が2件以上ある: %s" % (i + 1, sorted(got)))

    print()
    if bad:
        for b in bad:
            print("  NG  %s" % b)
        print("\n  %d 件" % len(bad))
        return 1
    print("  %d件すべて1件1ページ　異常なし" % len(nos))
    return 0


if __name__ == "__main__":
    sys.exit(main())
