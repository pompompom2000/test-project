# -*- coding: utf-8 -*-
"""運輸局照会書（PDF）― Word版と同じ src/shokai.json から作る。

運輸局にそのまま提出できる形。Wordで開いたときのレイアウト崩れを気にせずに済み、
窓口で書き込んでもらう回答欄もそのまま使える。

中身を直すときは shokai.json を直して、Word版（運輸局照会書.gen.js）と
この両方を作り直すこと。ずれていないかは src/checkmatch.py で確かめられる。

使い方:  python3 src/運輸局照会書.gen.py
"""
import html as H
import json
import pathlib

from playwright.sync_api import sync_playwright

D = pathlib.Path(__file__).parent
OUT_HTML = D / "shokai.html"
OUT_PDF = D.parent / "運輸局照会書.pdf"
data = json.loads((D / "shokai.json").read_text(encoding="utf-8"))


def e(s):
    return H.escape(s).replace("〔緑〕", '<b class="g">〔緑〕</b>').replace("〔白〕", '<b class="w">〔白〕</b>')


def lines(xs, cls=""):
    """配列を1行ずつの段落にする。空文字は余白として残す。"""
    out = []
    for t in xs:
        out.append('<p class="%s">%s</p>' % (cls, e(t) if t else "&nbsp;"))
    return "\n".join(out)


CSS = """
@page { size: A4; margin: 20mm 18mm 18mm; }
* { box-sizing: border-box; }
body { font-family: "Noto Serif CJK JP","Noto Serif JP",serif; font-size: 10pt;
       line-height: 1.66; color: #16202b; margin: 0; }
h1 { font-family: "Noto Sans CJK JP",sans-serif; font-size: 20pt; text-align: center;
     letter-spacing: .4em; margin: 0 0 3mm; }
.sub { font-family: "Noto Sans CJK JP",sans-serif; font-size: 10.5pt; text-align: center; margin: 0 0 10mm; }
.date { text-align: right; margin: 0 0 7mm; }
.to { font-size: 11pt; margin: 0 0 1mm; }
.to2 { font-size: 8.5pt; color: #4a5663; margin: 0 0 8mm; }
table { width: 100%; border-collapse: collapse; margin: 0 0 4mm; }
th, td { border: .4pt solid #9aa6b2; padding: 1.4mm 2mm; font-size: 9.5pt; vertical-align: top; }
th { background: #e8ecf0; font-family: "Noto Sans CJK JP",sans-serif; font-weight: 700;
     white-space: nowrap; width: 26mm; }
td p, th p { margin: 0; line-height: 1.6; }
.cast th { text-align: center; width: auto; }
.cast td { text-align: center; }
.cast td.l { text-align: left; }
.cast td.no { font-family: "Noto Sans CJK JP",sans-serif; font-weight: 700;
              width: 22mm; white-space: nowrap; }
.band { background: #16395c; color: #fff; font-family: "Noto Sans CJK JP",sans-serif;
        font-weight: 700; font-size: 10.5pt; padding: 1.3mm 2.5mm; margin: 0 0 2mm;
        break-after: avoid; }
/* 囲みと表は途中で割らない。見出しだけがページ末に残るのも防ぐ */
.box, table, .ans { break-inside: avoid; }
h2 { break-after: avoid; }
.box { border: .4pt solid #9aa6b2; padding: 2.5mm 3mm; margin: 0 0 4mm; }
.box.warn { background: #fdf4e2; border-color: #8a6100; }
.box p { margin: 0; font-size: 9pt; line-height: 1.65; }
.inq { page-break-before: always; }
.inq:first-of-type { page-break-before: auto; }
h2 { font-family: "Noto Sans CJK JP",sans-serif; font-size: 13pt; margin: 0 0 2mm;
     padding-bottom: 1.5mm; border-bottom: 1.6pt solid #16395c; }
.note { font-size: 8.5pt; color: #4a5663; margin: 0 0 4mm; }
.note p { margin: 0; }
.sec { margin: 0 0 3mm; }
.sec p { margin: 0; padding-left: 3mm; }
.sec.base p { font-size: 9pt; color: #30404f; }
.ans { border: .4pt solid #9aa6b2; height: 26mm; padding: 2mm 3mm; font-size: 8.5pt; color: #4a5663; }
b.g { color: #186b3f; }
b.w { color: #8a6100; }
"""

parts = ['<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8">',
         "<title>運輸局照会書</title><style>%s</style></head><body>" % CSS]

# ---- 表紙 ----
parts.append("<h1>%s</h1>" % e(data["title"]))
parts.append('<div class="sub">%s</div>' % e(data["subtitle"]))
parts.append('<div class="date">年　　月　　日</div>')
parts.append('<div class="to">%s</div>' % e(data["to"]))
parts.append('<div class="to2">%s</div>' % e(data["to_note"]))

rows = "".join("<tr><th>%s</th><td>%s</td></tr>" % (e(l), lines(v)) for l, v in data["sender"])
parts.append("<table>%s</table>" % rows)

parts.append('<div class="band">%s</div>' % e(data["cast_title"]))
head = "".join("<th>%s</th>" % e(h) for h in data["cast_head"])
body = ""
for no, what, kyoka, car in data["cast"]:
    body += ('<tr><td class="no">%s</td><td class="l">%s</td><td>%s</td><td>%s</td></tr>'
             % (e(no), lines(what), lines(kyoka), lines(car)))
parts.append('<table class="cast"><tr>%s</tr>%s</table>' % (head, body))
parts.append('<div class="box warn">%s</div>' % lines(data["cast_note"]))
parts.append('<div class="box">%s</div>' % lines(data["greeting"]))
parts.append('<div class="box warn">%s</div>' % lines(data["scope_note"]))

# ---- 照会本体 ----
for q in data["inquiries"]:
    parts.append('<div class="inq">')
    parts.append("<h2>【%s】　%s</h2>" % (e(q["no"]), e(q["title"])))
    if q["note"]:
        parts.append('<div class="note">%s</div>' % lines(q["note"]))
    for key, band in zip(("fact", "mine", "base", "ask"), data["bands"]):
        parts.append('<div class="band">%s</div>' % e(band))
        parts.append('<div class="sec %s">%s</div>' % (key, lines(q[key])))
    parts.append('<div class="ans">%s</div>' % e(data["answer_box"]))
    parts.append("</div>")

parts.append("</body></html>")
OUT_HTML.write_text("\n".join(parts), encoding="utf-8")

ftr = ('<div style="width:100%;font-family:sans-serif;font-size:7pt;color:#5c6873;'
       'padding:0 18mm;display:flex;justify-content:space-between;">'
       "<span>照会書　貨物自動車運送事業法・ダンプ規制法の適用について</span>"
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
