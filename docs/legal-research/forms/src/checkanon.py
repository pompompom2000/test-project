# -*- coding: utf-8 -*-
"""提出する照会書に、実名や社内限りの情報が紛れ込んでいないかを調べる。

運輸局に渡す書面には取引先の実名を書かない方針にしている。
仮称と実名の対応表は 21_運輸局への照会事例集.md にのみ置く。
照会書を直したあとは、提出前に必ずこれを通すこと。

使い方:  python3 src/checkanon.py
"""
import html
import re
import sys
import zipfile

# 提出する書面に出てはいけない語
NG = ["石名坂", "沢口", "熊谷", "対応表", "仮称と実名"]
TARGET = "運輸局照会書.docx"


def main():
    x = zipfile.ZipFile(TARGET).read("word/document.xml").decode("utf-8")
    t = html.unescape(re.sub(r"<[^>]+>", "", x))
    bad = 0
    print("== %s" % TARGET)
    for w in NG:
        c = t.count(w)
        if c:
            print("   !! 「%s」が %d 箇所" % (w, c))
            bad += c
    # 仮称がちゃんと使われているか（置き換え漏れの裏取り）
    for w in ["甲社", "乙社", "丙社", "〔緑〕", "〔白〕"]:
        if t.count(w) == 0:
            print("   ?? 「%s」が1つもない。置き換えが崩れていないか確認すること" % w)
    print("   %s" % ("提出前チェック OK（実名なし）" if bad == 0 else "提出不可。%d件" % bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
