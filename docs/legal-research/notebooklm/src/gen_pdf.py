# -*- coding: utf-8 -*-
"""読ませる原稿.md から PDF を作る。

NotebookLM は Markdown のテキストファイルも読めるが、環境によってはファイル選択で
拡張子ではじかれることがある。PDF なら確実に上がるので、同じ中身で用意しておく。

使い方:  python3 src/gen_pdf.py
"""
import pathlib
import markdown
from playwright.sync_api import sync_playwright

D = pathlib.Path(__file__).parent.parent
md = (D / "読ませる原稿.md").read_text(encoding="utf-8")
html_body = markdown.markdown(md, extensions=["tables"])

CSS = """
@page { size: A4; margin: 20mm 18mm; }
body { font-family:"Noto Serif CJK JP","Noto Serif JP",serif; font-size:10.5pt;
       line-height:1.85; color:#16202b; margin:0; }
h1 { font-family:"Noto Sans CJK JP",sans-serif; font-size:19pt; margin:0 0 6mm;
     padding-bottom:3mm; border-bottom:2pt solid #16395c; }
h2 { font-family:"Noto Sans CJK JP",sans-serif; font-size:13.5pt; margin:9mm 0 3mm;
     padding-left:3mm; border-left:4pt solid #16395c; break-after:avoid; }
p { margin:0 0 3.5mm; }
table { border-collapse:collapse; width:100%; margin:0 0 5mm; break-inside:avoid; font-size:9.5pt; }
th,td { border:.4pt solid #9aa6b2; padding:1.5mm 2.5mm; vertical-align:top; }
th { background:#e8ecf0; font-family:"Noto Sans CJK JP",sans-serif; }
blockquote { margin:0 0 4mm; padding:2.5mm 4mm; background:#f2f4f7;
             border-left:3pt solid #8a6100; break-inside:avoid; }
blockquote p { margin:0; }
strong { font-family:"Noto Sans CJK JP",sans-serif; }
hr { border:0; border-top:.6pt solid #c3ccd4; margin:7mm 0; }
"""
page = ('<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8">'
        '<title>白ナンバーのダンプは、どこまで使えるのか</title>'
        '<style>%s</style></head><body>%s</body></html>' % (CSS, html_body))
tmp = D / "src" / "_src.html"
tmp.write_text(page, encoding="utf-8")

out = D / "読ませる原稿.pdf"
ftr = ('<div style="width:100%;font-family:sans-serif;font-size:7pt;color:#5c6873;'
       'padding:0 18mm;display:flex;justify-content:space-between;">'
       '<span>白ナンバーのダンプは、どこまで使えるのか（社名はすべて仮称）</span>'
       '<span class="pageNumber"></span></div>')
with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
    pg = b.new_page()
    pg.goto(tmp.as_uri(), wait_until="networkidle")
    pg.evaluate("document.fonts.ready")
    pg.wait_for_timeout(2500)
    pg.pdf(path=str(out), format="A4", print_background=True,
           display_header_footer=True, header_template="<div></div>", footer_template=ftr,
           margin={"top": "14mm", "bottom": "14mm", "left": "0", "right": "0"})
    b.close()
print("wrote", out)
