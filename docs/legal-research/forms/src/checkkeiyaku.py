# -*- coding: utf-8 -*-
"""残土処分請負契約書のひな型が、許可不要の組立てを崩していないかを調べる。

この契約書は、令和8年2月10日付け事務連絡 1.(2)の
ⅰ 生業と密接不可分・付帯、ⅱ 同一の者が生業と運送を一貫して行う、
ⅲ 名目の如何を問わず運送の対価としての有償性がない、の三要件と、
同2.の雇用関係の要件に当てはめるために条文の書き方を決めている。
うっかり文言を落とすと、その当てはめが成り立たなくなる。それを機械で見張る。

見ているもの
  1 三要件と2.の雇用関係に対応する必須文言が残っているか
  2 内訳書に運搬を独立費目として立てていないか（通達ⅲ）
  3 単位が立方メートルのままか（台・kmになっていないか）
  4 表の幅が本文幅（A4縦・左右25mm余白＝9072 DXA）を超えていないか
  5 社内用メモが最終頁にあり、相手方に渡す頁に混ざっていないか
  6 当事者のトークン（{甲}など）が差し替えられずに残っていないか

使い方:  python3 src/checkkeiyaku.py
"""
import json
import pathlib
import re
import sys
import unicodedata

import pypdfium2 as pdfium

SRC = pathlib.Path(__file__).parent
PDF = SRC.parent / "残土処分請負契約書.pdf"
W = 9072

# 落とすと通達の当てはめが崩れる文言。どの要件に効くかを添える。
MUST = [
    ("ⅱ 運送が主目的でない", "運搬を目的とするものではない"),
    ("ⅱ 運搬は手段", "処分を完成するために{乙}が自らの手段として行う工程の一部"),
    ("ⅲ 名目を問わない", "名目の如何を問わず"),
    ("ⅲ 距離・回数・台数で決めない", "使用する車両の台数に応じて定めるものではない"),
    ("ⅲ 請求書も同じ名目", "別紙１と同一の区分及び名目"),
    ("ⅰ 処分地を自ら確保", "処分地の確保、維持及び管理は、{乙}の責任と費用において行う"),
    ("ⅰ 受入後の責任を負う", "本件残土の管理及び災害の防止に係る責任は、{乙}が負う"),
    ("ⅰ 工程を一体で行う", "各工程を一体のものとして自ら行う"),
    ("ⅰ 丸投げしない", "第三者に再委託しない"),
    ("補強 積込み時に所有権移転", "所有権は、前項の引渡しと同時に、{甲}から{乙}に移転する"),
    ("2. 雇用関係にある従業員", "{乙}と雇用関係にある従業員"),
    ("2. 雇用関係の実態", "労働条件通知書を交付し、その報酬を給与として支払う"),
    ("ダンプ規制法は外れない", "表示番号"),
    ("廃棄物が混ざれば対象外", "廃棄物に該当しないものに限る"),
]

# 内訳書に立ててはいけない費目（通達ⅲ「名目の如何を問わず」）
NG_ITEM = ["運賃", "運搬費", "横持", "車両費", "回送費", "輸送費", "運送費"]
NG_UNIT = ["台", "km", "ｋｍ", "t", "ｔ", "回"]


def norm(s):
    return re.sub(r"[\s　]", "", unicodedata.normalize("NFKC", str(s)))


def build_tok(raw):
    """当事者の名前のトークン。生成スクリプトと同じ対応表を作る。"""
    tok = {}
    for k, v in raw["parties"].items():
        tok["{%s}" % k] = v["short"]
        for f in ("full", "role", "car"):
            tok["{%s_%s}" % (k, f)] = v[f]
    return tok


def strings(x):
    """入れ子になった値のうち、文字列だけを取り出す。"""
    if isinstance(x, str):
        yield x
    elif isinstance(x, list):
        for i in x:
            yield from strings(i)
    elif isinstance(x, dict):
        for v in x.values():
            yield from strings(v)


def sub(s, tok):
    for k, v in tok.items():
        s = s.replace(k, v)
    return s


def main():
    raw = json.loads((SRC / "keiyaku.json").read_text(encoding="utf-8"))
    tok = build_tok(raw)
    d = json.loads(sub(json.dumps(raw, ensure_ascii=False), tok))
    bad = []
    print("  当事者　甲=%s（%s）／乙=%s（%s）"
          % (raw["parties"]["甲"]["short"], raw["parties"]["甲"]["full"],
             raw["parties"]["乙"]["short"], raw["parties"]["乙"]["full"]))

    # ---- 1 必須文言（当事者名を差し替えたうえで突き合わせる）----
    whole = norm("".join(strings(d)))
    for why, phrase in MUST:
        if norm(sub(phrase, tok)) not in whole:
            bad.append("必須文言が無い（%s）: %s" % (why, sub(phrase, tok)))

    # ---- 6 未置換トークン ----
    # JSON全体を文字列化すると object の波括弧を拾ってしまうので、値の文字列だけを見る。
    left = sorted({t for v in strings(d) for t in re.findall(r"\{[^{}]+\}", v)})
    if left:
        bad.append("差し替えられていないトークンがある: %s" % left)

    # ---- 2 内訳書の費目 ----
    cells = [c for r in d["att1_rows"] for c in r] + d["att1_head"] + d["att1_total"]
    for c in cells:
        for ng in NG_ITEM:
            if ng in str(c):
                bad.append("内訳書に運搬の費目がある: %r に「%s」" % (c, ng))

    # ---- 3 単位 ----
    units = {str(r[3]).strip() for r in d["att1_rows"] if str(r[3]).strip()}
    if units - {"㎥"}:
        bad.append("内訳書の単位が立方メートル以外: %s" % sorted(units - {"㎥"}))
    for u in units:
        if u in NG_UNIT:
            bad.append("内訳書の単位が運搬量になっている: %s" % u)

    # ---- 4 表の幅 ----
    for name in ("atama_cols", "att1_cols", "att2_cols"):
        s = sum(d[name])
        mark = "OK" if s <= W else "はみ出し"
        if s > W:
            bad.append("%s の合計 %d が本文幅 %d を超える" % (name, s, W))
        print("  %-10s 合計 %5d / %d  %s" % (name, s, W, mark))

    # ---- 5 社内用メモの位置 ----
    if PDF.exists():
        doc = pdfium.PdfDocument(str(PDF))
        pages = [norm(doc[i].get_textpage().get_text_range()) for i in range(len(doc))]
        hit = [i + 1 for i, p in enumerate(pages) if "社内用" in p]
        # フッターに「※最終頁は社内用」が入るので、本文に出る頁だけを見る
        body = [i + 1 for i, p in enumerate(pages) if "この契約書の書き方と注意点" in p
                or "相手方に交付する契約書には綴らない" in p]
        print("  PDF %d頁　社内用メモ: %s頁" % (len(pages), body or "なし"))
        stray = sorted({t for pg in pages for t in re.findall(r"\{[^{}]+\}", pg)})
        if stray:
            bad.append("PDFにトークンが残っている: %s" % stray)
        if not body:
            bad.append("社内用メモがPDFに見つからない")
        elif min(body) <= 4:
            bad.append("社内用メモが契約書本体に混ざっている（%s頁）" % body)
    else:
        print("  （PDF未生成。先に 残土処分請負契約書.gen.py を動かすこと）")

    print()
    if bad:
        for b in bad:
            print("  NG  %s" % b)
        print("\n  %d 件" % len(bad))
        return 1
    print("  条 %d・頭書・別紙2・社内用メモ　異常なし" % len(d["articles"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
