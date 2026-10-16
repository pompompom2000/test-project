# -*- coding: utf-8 -*-
"""残土処分請負契約書（PDF）― Word版と同じ src/keiyaku.json から作る。

内容を直すときは keiyaku.json を直して、Word版（残土処分請負契約書.gen.js）と
この両方を作り直すこと。ずれていないかは src/checkkeiyaku.py で確かめられる。

使い方:  python3 src/残土処分請負契約書.gen.py
"""
import html as H
import json
import pathlib

from playwright.sync_api import sync_playwright

D = pathlib.Path(__file__).parent
OUT_HTML = D / "keiyaku.html"
OUT_PDF = D.parent / "残土処分請負契約書.pdf"
data = json.loads((D / "keiyaku.json").read_text(encoding="utf-8"))

KANSUJI = ["", "", "２", "３", "４", "５", "６", "７", "８", "９", "10"]


def e(s):
    return H.escape(str(s)).replace("\n", "<br>")


def lines(xs, cls=""):
    return "\n".join('<p class="%s">%s</p>' % (cls, e(t) if t else "&nbsp;") for t in xs)


CSS = """
@page { size: A4; margin: 20mm 20mm 18mm; }
* { box-sizing: border-box; }
body { font-family: "Noto Serif CJK JP","Noto Serif JP",serif; font-size: 10.5pt;
       line-height: 1.72; color: #16202b; margin: 0; }
h1 { font-family: "Noto Sans CJK JP",sans-serif; font-size: 19pt; text-align: center;
     letter-spacing: .3em; margin: 0 0 3mm; }
.sub { font-family: "Noto Sans CJK JP",sans-serif; font-size: 9.5pt; text-align: center;
       margin: 0 0 11mm; }
.pre { text-indent: 1em; margin: 0 0 7mm; }
h2 { font-family: "Noto Sans CJK JP",sans-serif; font-size: 11pt; margin: 5mm 0 1.5mm;
     break-after: avoid; }
.art p { margin: 0 0 .6mm; padding-left: 1em; text-indent: -1em; }
.art p.item { padding-left: 2em; text-indent: -1em; font-size: 10pt; }
.close { text-indent: 1em; margin: 8mm 0 5mm; }
.date { margin: 0 0 6mm; }
.sign { border: none; width: auto; margin: 0 0 6mm; }
.sign td { border: none; padding: .8mm 2mm .8mm 0; font-size: 10pt; vertical-align: bottom; }
.sign td.m { font-family: "Noto Sans CJK JP",sans-serif; font-weight: 700; width: 12mm; }
.sign td.l { width: 22mm; }
.sign td.v { border-bottom: .4pt solid #9aa6b2; min-width: 90mm; }
table { width: 100%; border-collapse: collapse; margin: 0 0 4mm; }
th, td { border: .4pt solid #9aa6b2; padding: 1.5mm 2mm; font-size: 9.5pt; vertical-align: top; }
th { background: #e8ecf0; font-family: "Noto Sans CJK JP",sans-serif; font-weight: 700; }
td p, th p { margin: 0; line-height: 1.6; }
.a1 th { text-align: center; }
.a1 td.c { text-align: center; }
.a1 tr.total th, .a1 tr.total td { background: #e8ecf0; text-align: center; }
.a2 th { width: 46mm; text-align: left; font-size: 9pt; }
.a2 td { font-size: 9pt; }
h3 { font-family: "Noto Sans CJK JP",sans-serif; font-size: 14pt; margin: 0 0 3mm;
     padding-bottom: 1.5mm; border-bottom: 1.6pt solid #16395c; break-after: avoid; }
.band { background: #16395c; color: #fff; font-family: "Noto Sans CJK JP",sans-serif;
        font-weight: 700; font-size: 10pt; padding: 1.3mm 2.5mm; margin: 0 0 2mm;
        break-after: avoid; }
.box { border: .4pt solid #9aa6b2; padding: 2.5mm 3mm; margin: 0 0 4mm; }
.box.warn { background: #fdf4e2; border-color: #8a6100; }
.box p { margin: 0; font-size: 9pt; line-height: 1.65; }
.box.warn.lead p { font-family: "Noto Sans CJK JP",sans-serif; font-weight: 700; font-size: 9.5pt; }
.memo p { margin: 0 0 1mm; padding-left: 1em; text-indent: -1em; font-size: 9.5pt; line-height: 1.7; }
.memo { margin: 0 0 3.5mm; }
.sheet { page-break-before: always; }
.box, table, .sign { break-inside: avoid; }
"""

parts = ['<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8">',
         "<title>残土処分請負契約書</title><style>%s</style></head><body>" % CSS]

# ---- 契約書本体 ----
parts.append("<h1>%s</h1>" % e(data["title"]))
parts.append('<div class="sub">%s</div>' % e(data["subtitle"]))
for t in data["preamble"]:
    parts.append('<div class="pre">%s</div>' % e(t))

for a in data["articles"]:
    parts.append("<h2>%s（%s）</h2>" % (e(a["no"]), e(a["title"])))
    parts.append('<div class="art">')
    n = 0
    for x in a["paras"]:
        if isinstance(x, list):
            for t in x:
                parts.append('<p class="item">%s</p>' % e(t))
            continue
        n += 1
        label = "" if n == 1 else KANSUJI[n] + "　"
        parts.append("<p>%s%s</p>" % (e(label), e(x)))
    parts.append("</div>")

for t in data["closing"]:
    parts.append('<div class="close">%s</div>' % e(t))
parts.append('<div class="date">%s</div>' % e(data["sign_date"]))

for row in data["sign_rows"]:
    mark, labels = row[0], row[1:]
    rows = ""
    for i, lab in enumerate(labels):
        v = "　　　　　　　　　　　　　　　　　　　　印" if lab == "代表者" else "&nbsp;"
        rows += ('<tr><td class="m">%s</td><td class="l">%s</td><td class="v">%s</td></tr>'
                 % (e(mark) if i == 0 else "&nbsp;", e(lab), v))
    parts.append('<table class="sign">%s</table>' % rows)

# ---- 別紙１ ----
parts.append('<div class="sheet">')
parts.append("<h3>%s</h3>" % e(data["att1_title"]))
head = "".join("<th>%s</th>" % e(h) for h in data["att1_head"])
body = ""
for r in data["att1_rows"]:
    body += "<tr>" + "".join(
        '<td class="%s">%s</td>' % ("c" if i >= 2 else "", e(v) if v else "&nbsp;")
        for i, v in enumerate(r)) + "</tr>"
tot = "".join("<th>%s</th>" % (e(v) if v else "&nbsp;") for v in data["att1_total"])
parts.append('<table class="a1"><tr>%s</tr>%s<tr class="total">%s</tr></table>' % (head, body, tot))
parts.append('<div class="box warn">%s</div>' % lines(data["att1_note"]))
parts.append("</div>")

# ---- 別紙２ ----
parts.append('<div class="sheet">')
parts.append("<h3>%s</h3>" % e(data["att2_title"]))
rows = "".join("<tr><th>%s</th><td>%s</td></tr>" % (e(k), e(v) if v else "&nbsp;")
               for k, v in data["att2_rows"])
parts.append('<table class="a2">%s</table>' % rows)
parts.append("</div>")

# ---- 社内用メモ ----
parts.append('<div class="sheet">')
parts.append("<h3>%s</h3>" % e(data["memo_title"]))
parts.append('<div class="box warn lead">%s</div>' % lines(data["memo_lead"]))
for s in data["memo_sections"]:
    parts.append('<div class="band">%s</div>' % e(s["h"]))
    parts.append('<div class="memo">%s</div>' % lines(s["ps"]))
parts.append("</div>")

parts.append("</body></html>")
OUT_HTML.write_text("\n".join(parts), encoding="utf-8")

ftr = ('<div style="width:100%;font-family:sans-serif;font-size:7pt;color:#5c6873;'
       'padding:0 20mm;display:flex;justify-content:space-between;">'
       "<span>残土処分請負契約書（ひな型）　※最終頁は社内用</span>"
       '<span class="pageNumber"></span></div>')

with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
    pg = b.new_page()
    pg.goto(OUT_HTML.as_uri(), wait_until="networkidle")
    # フォントの読み込みとレイアウト確定を待つ。待たずに pdf() を呼ぶと末尾が欠ける
    pg.evaluate("document.fonts.ready")
    pg.wait_for_timeout(3000)
    pg.pdf(path=str(OUT_PDF), format="A4", print_background=True,
           display_header_footer=True, header_template="<div></div>", footer_template=ftr,
           margin={"top": "14mm", "bottom": "14mm", "left": "0", "right": "0"})
    b.close()
print("wrote", OUT_PDF)
