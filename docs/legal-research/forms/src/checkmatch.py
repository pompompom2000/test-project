# -*- coding: utf-8 -*-
"""同じ書式の Word版と PDF版の文面がずれていないかを調べる。

照会書は src/shokai.json から両方を作るのでずれない。
記録票は Word と PDF で別々に組んでいるので、直したとき片方を忘れやすい。
文面を直したら、両方を作り直してからこれを通すこと。

行の折返しや空白の入り方は形式ごとに違うので、空白を落とし全角半角をそろえたうえで、
「一方にしかない文字列」を探す。語順の入れ替えまでは見ていない。

使い方:  python3 src/checkmatch.py
"""
import html
import os
import re
import sys
import unicodedata
import zipfile

import pypdfium2 as pdfium

PAIRS = [("運輸局照会書.docx", "運輸局照会書.pdf"),
         ("照会記録票.docx", "照会記録票.pdf"),
         ("残土処分請負契約書.docx", "残土処分請負契約書.pdf")]
# 書式として当然違うものは除く。PDFだけに入るフッター（文言＋ページ番号）と、ページ番号だけの行。
# 正規化後の文字列が、ここに挙げた語で始まるものを落とす。
IGNORE_PREFIX = [
    "照会書貨物自動車運送事業法・ダンプ規制法の適用について",
    "照会記録票(社内限り)",
    "残土処分請負契約書(ひな型)",
]


def norm(s):
    return re.sub(r"[\s　]", "", unicodedata.normalize("NFKC", s))


def docx_text(path):
    x = zipfile.ZipFile(path).read("word/document.xml").decode("utf-8")
    x = re.sub(r"</w:p>", "\n", x)
    return html.unescape(re.sub(r"<[^>]+>", "", x))


def pdf_text(path):
    d = pdfium.PdfDocument(path)
    return "\n".join(d[i].get_textpage().get_text_range() for i in range(len(d)))


def chunks(t):
    """意味のある行だけを、正規化して集合にする。"""
    out = set()
    for line in t.split("\n"):
        n = norm(line)
        if len(n) < 6 or n.isdigit():
            continue
        if any(n.startswith(x) for x in IGNORE_PREFIX):
            continue
        out.add(n)
    return out


def flat(t):
    """フッターなど形式由来の行を落として全文を1本につなぐ。
    1つの段落がページをまたぐと、間にフッターが挟まって部分一致に失敗するため。"""
    keep = [l for l in t.split("\n") if not any(norm(l).startswith(x) for x in IGNORE_PREFIX)]
    return norm("".join(keep))


def main():
    d = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    bad = 0
    for dx, pf in PAIRS:
        dtext, ptext = docx_text(os.path.join(d, dx)), pdf_text(os.path.join(d, pf))
        a, b = chunks(dtext), chunks(ptext)
        # PDFは行の折返し位置が違うので、短い行はつながって一致しないことがある。
        # 片方の全文に部分文字列として含まれていれば一致とみなす。
        fd, fp = flat(dtext), flat(ptext)
        only_d = [s for s in sorted(a - b) if s not in fp]
        only_p = [s for s in sorted(b - a) if s not in fd]
        print("== %s ↔ %s" % (dx, pf))
        for s in only_d:
            print("   Wordにしかない: %s" % s[:62])
        for s in only_p:
            print("   PDFにしかない : %s" % s[:62])
        n = len(only_d) + len(only_p)
        bad += n
        print("   ずれ %d 件" % n)
    print()
    print("合計 ずれ %d 件" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
