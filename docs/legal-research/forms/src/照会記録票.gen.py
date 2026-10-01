# -*- coding: utf-8 -*-
"""照会記録票（PDF）― Word版（照会記録票.gen.js）と同じ中身を印刷用に。

社内限り。運輸局等への照会の回答を、その場で書き留めるための2枚。
印刷して配るだけならこちらが早い。Wordで書き込むなら .docx を使う。

Word版と文言がずれていないかは src/checkmatch.py で確かめられる。

使い方:  python3 src/照会記録票.gen.py
"""
import html as H
import pathlib

from playwright.sync_api import sync_playwright

D = pathlib.Path(__file__).parent
OUT_HTML = D / "kiroku.html"
OUT_PDF = D.parent / "照会記録票.pdf"

e = H.escape


def rows(pairs):
    return "".join("<tr><th>%s</th><td>%s</td></tr>"
                   % (e(l), "".join("<p>%s</p>" % (e(t) if t else "&nbsp;") for t in v))
                   for l, v in pairs)


def blanklines(n):
    return "".join('<p class="bl">&nbsp;</p>' for _ in range(n))


CSS = """
@page { size: A4; margin: 12mm 16mm 12mm; }
* { box-sizing: border-box; }
body { font-family: "Noto Serif CJK JP","Noto Serif JP",serif; font-size: 10pt;
       line-height: 1.6; color: #16202b; margin: 0; }
.naibu { font-family: "Noto Sans CJK JP",sans-serif; font-size: 9pt; font-weight: 700;
         text-align: right; letter-spacing: .3em; margin: 0 0 1mm; }
h1 { font-family: "Noto Sans CJK JP",sans-serif; font-size: 17pt; text-align: center;
     letter-spacing: .3em; margin: 0 0 2mm; }
.sub { font-size: 9pt; text-align: center; color: #4a5663; margin: 0 0 4mm; }
table { width: 100%; border-collapse: collapse; margin: 0 0 3mm; break-inside: avoid; }
th, td { border: .4pt solid #9aa6b2; padding: .9mm 2mm; font-size: 9.5pt; vertical-align: top; }
th { background: #e8ecf0; font-family: "Noto Sans CJK JP",sans-serif; font-weight: 700;
     white-space: nowrap; width: 24mm; }
td p, th p { margin: 0; line-height: 1.6; }
.band { background: #16395c; color: #fff; font-family: "Noto Sans CJK JP",sans-serif;
        font-weight: 700; font-size: 10.5pt; padding: 1.2mm 2.5mm; margin: 0 0 1.5mm;
        break-after: avoid; }
.write { border: .4pt solid #9aa6b2; padding: 1.5mm 3mm; margin: 0 0 2.5mm; break-inside: avoid; }
.write p.bl { margin: 0; border-bottom: .3pt dotted #c3ccd4; height: 5.4mm; }
.write p.lead { margin: 0 0 1mm; font-size: 8.5pt; color: #4a5663; }
.cast th { text-align: center; width: auto; }
.cast td { text-align: center; font-size: 9pt; }
.cast td.l { text-align: left; }
.cast td.no { font-family: "Noto Sans CJK JP",sans-serif; font-weight: 700; width: 13mm; }
.box { border: .4pt solid #8a6100; background: #fdf4e2; padding: 2.5mm 3mm; margin: 0 0 3mm;
       break-inside: avoid; }
.box p { margin: 0; font-size: 8.5pt; line-height: 1.6; }
.next td { font-size: 9pt; }
.next td.c { text-align: center; width: 10mm; }
.foot { font-size: 8.5pt; color: #4a5663; margin: 1.5mm 0 0; }
.mini { font-size: 8.5pt; color: #4a5663; margin: 0 0 2mm; }
.pb { page-break-before: always; }
"""

h = ['<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8">',
     "<title>照会記録票</title><style>%s</style></head><body>" % CSS]

h.append('<div class="naibu">社 内 限 り</div>')
h.append("<h1>照 会 記 録 票</h1>")
h.append('<div class="sub">運輸局・運輸支局・労働基準監督署・県への照会と、その回答の記録</div>')

h.append("<table>%s</table>" % rows([
    ("整理番号", ["（例：A-1、B-3　※21_運輸局への照会事例集の番号）"]),
    ("照会日時", ["　　　　年　　月　　日（　）　　　時　　分　〜　　　時　　分"]),
    ("方法", ["□ 電話　　□ 窓口で対面　　□ 書面（FAX・メール）　　□ その他（　　　　　　　）"]),
    ("照会先", ["□ 東北運輸局 自動車交通部 貨物課（022-791-7531）",
                "□ 岩手運輸支局 輸送・監査部門（019-638-2154 音声案内【3】）",
                "□ 岩手運輸支局 登録部門　　□ 盛岡労働基準監督署　　□ ハローワーク盛岡",
                "□ 岩手県 資源循環推進課 廃棄物対策担当（019-629-5366）　　□ 年金事務所",
                "□ その他（　　　　　　　　　　　　　　　　　　　　　　　　　　　　）",
                "※運輸支局の電話受付は平日 8:30〜11:45／13:00〜17:00。昼休みは出ません"]),
    ("応対者", ["部署：　　　　　　　　　役職：　　　　　　　　　氏名："]),
    ("当社担当", ["氏名："]),
    ("この照会の当事者", ["□ 甲社〔緑〕　　□ 乙社〔白〕　　□ 丙社〔白〕　　□ 丁社　　□ 戊〔白〕",
                          "□ その他（　　　　　　　　　　　　　　　　　　　　　　　　　　　）"]),
]))

h.append('<div class="band">１　聞いたこと</div>')
h.append('<div class="write">%s</div>' % blanklines(5))
h.append('<div class="band">２　回答（できるだけ言われたとおりに書く）</div>')
h.append('<div class="write">%s</div>' % blanklines(10))

h.append("<table>%s</table>" % rows([
    ("結論", ["□ 当社の理解どおり　　□ 一部異なる　　□ 異なる　　□ 明確な回答は得られず"]),
    ("言質の強さ", ["□ 断定的（「そのとおりです」）",
                    "□ 留保つき（「一般論としては」「個別には実態で」）",
                    "□ 回答不可（「個別具体の判断はできない」「他の窓口へ」）"]),
    ("書面回答", ["□ 依頼した（回答予定：　　月　　日頃）　　□ 依頼したが断られた　　□ 依頼せず"]),
]))

# ---- 2ページ目 ----
h.append('<div class="band">３　前提のどれが変わると結論が変わるか</div>')
h.append('<div class="write"><p class="lead">※ここが一番大事です。必ず聞いて、'
         '聞けなかったときは「聞けなかった」と書いてください。</p>%s</div>' % blanklines(4))

h.append('<div class="band">４　次にやること</div>')
NEXT = ["本編PDFの該当章を直す（章番号：　　　　　）",
        "早見表（PDF・Word）を直す（▲番号：　　　　　）",
        "照会事例集から消し込む",
        "現場・配車室へ周知する",
        "別の窓口へ聞き直す（　　　　　　　　　　　）",
        "　"]
h.append('<table class="next"><tr><th style="width:10mm"></th><th>内容</th>'
         '<th style="width:30mm">期限・担当</th></tr>%s</table>'
         % "".join('<tr><td class="c">□</td><td>%s</td><td>&nbsp;</td></tr>' % e(t) for t in NEXT))

h.append('<div class="band">仮称の対照（照会書と同じ記号で書いてください）</div>')
CAST = [("甲社", "運送事業者（大型ダンプ5両）", "有（一般貨物）", "〔緑〕事業用"),
        ("乙社", "砕石の製造販売業者。甲社の親会社", "無", "〔白〕自家用"),
        ("丙社", "砂利・砕石の販売業者", "無", "〔白〕自家用"),
        ("丁社", "建設業者（元請）", "無", "―"),
        ("戊", "個人。自ら運転する（持込み運転者）", "無", "〔白〕自家用")]
h.append('<table class="cast"><tr><th>仮称</th><th>どのような会社か</th>'
         '<th>運送事業の許可</th><th>ナンバー</th></tr>%s</table>'
         % "".join('<tr><td class="no">%s</td><td class="l">%s</td><td>%s</td><td>%s</td></tr>'
                   % (e(a), e(b), e(c), e(d)) for a, b, c, d in CAST))
h.append('<p class="mini">〔緑〕＝一般貨物の許可あり・事業用自動車　　〔白〕＝許可なし・自家用自動車</p>')
h.append("<table>%s</table>" % rows([("実名の控え（社内限り・任意）",
                                     ["仮称　　　　＝　　　　　　　　　　　　仮称　　　　＝"])]))

h.append('<div class="box">%s</div>' % "".join("<p>%s</p>" % e(t) for t in [
    "書き方の注意",
    "・会社名は仮称（甲社〔緑〕・乙社〔白〕など）で書くこと。聞くときも仮称で聞きます。",
    "　実名で記録すると、実際に話した内容と記録が食い違い、あとで読み返せなくなります。",
    "　仮称と実名の対応表は 21_運輸局への照会事例集.md にあります。この票には書きません。",
    "・応対者の氏名と日付は必ず取ること。後から「誰に聞いたか」が分からない記録は使えません。",
    "・回答は要約せず、言われた言葉のまま書くこと。とくに「一般論としては」「実態によります」",
    "　といった留保は、落とさずに書いてください。留保の有無で使える強さが変わります。",
    "・「個別具体の判断はできない」と言われた場合も、そう言われたこと自体が記録になります。",
    "・重要なものは「書面でいただけますか」と頼むこと。断られても、頼んだ事実を残します。",
    "・この票は事案ごとに1枚。社内限りです。運輸局等に渡さないでください。",
]))
h.append('<p class="foot">※ 記入後は社内リポジトリ docs/legal-research/verify_shokai/ に保存してください。</p>')
h.append("</body></html>")
OUT_HTML.write_text("\n".join(h), encoding="utf-8")

ftr = ('<div style="width:100%;font-family:sans-serif;font-size:7pt;color:#5c6873;'
       'padding:0 18mm;display:flex;justify-content:space-between;">'
       "<span>照会記録票（社内限り）</span><span class=\"pageNumber\"></span></div>")

with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
    pg = b.new_page()
    pg.goto(OUT_HTML.as_uri(), wait_until="networkidle")
    pg.evaluate("document.fonts.ready")
    pg.wait_for_timeout(3000)
    pg.pdf(path=str(OUT_PDF), format="A4", print_background=True,
           display_header_footer=True, header_template="<div></div>", footer_template=ftr,
           margin={"top": "10mm", "bottom": "10mm", "left": "0", "right": "0"})
    b.close()
print("wrote", OUT_PDF)
