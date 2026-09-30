# -*- coding: utf-8 -*-
"""白ダンプの早見表（単独PDF）

本編 body.html の「付録：白ダンプ早見表」（65〜69章）をそのまま切り出し、
専用の表紙を付けて1冊にする。本編を直せば、このPDFも自動で追随する。
"""
import io, pathlib, re
from playwright.sync_api import sync_playwright

D = pathlib.Path(__file__).parent
OUT_HTML = D / "hayami.html"
OUT_PDF = D / "白ダンプの早見表.pdf"

body = io.open(D / "body.html", encoding="utf-8").read()

MARK = "<!-- ============ 付録：白ダンプ早見表 ============ -->"
i = body.index(MARK)
# 次のパート区切りがあればそこまで。なければ本文の終わりまで。
nxt = body.find("<!-- ============ ", i + len(MARK))
j = nxt if nxt != -1 else body.index("</body></html>")
part = body[i:j].strip()
# 早見表パートの <div class="part"> を閉じ直す（次のパートを切り落としたため）
if part.count("<div") > part.count("</div>"):
    part += "\n</div>"

# 本編のパートヘッダ（APPENDIX / 見出し / リード）は表紙に置き換える
part = re.sub(
    r'<div class="part-head">.*?</div>\s*</div>\s*',
    "", part, count=1, flags=re.S)
# 開いたままの <div class="part"> を閉じ直す
part = part.replace('<div class="part">', '<div class="part">', 1)

COVER = """
<div class="cover">
  <div class="top">
    <div class="sub">社内実務資料　―　現場用</div>
    <h1>白ダンプの早見表</h1>
    <h2>ケース別・品目別　―　使ってよい形と、使えない形<br>
    ― 有限会社石名坂商事・株式会社石名坂 ―</h2>
  </div>

  <div style="margin-top:12mm">
    <div class="box danger">
      <div class="t">この早見表の使い方</div>
      <ol>
        <li><strong>65章</strong>で、白ダンプに効く<strong>4つの関門</strong>（貨運法・ダンプ規制法・労働／社会保険・廃掃法）を確認する。<span class="ng">1つでも落ちれば違法です。</span></li>
        <li><strong>66章</strong>で、その荷物が<strong>「土砂等」か／「産業廃棄物」か</strong>を判定する。<strong>この2つは別の軸</strong>です。どちらか一方だけを見て決めないでください。</li>
        <li><strong>67章</strong>の表で、当てはまるケースを探す。<strong>全24ケース</strong>をⅠ〜Ⅴに分けてあります。</li>
        <li>判定が<strong>▲</strong>なら<strong>69章</strong>の手引きへ。<strong>①何が条件か ②○にする手順 ③×になる典型 ④残す書面</strong>の4点が書いてあります。</li>
        <li><strong>68章の「現場の1枚」は、運転席と配車室に貼ってください。</strong>積込み前に上から順に見る6項目です。</li>
      </ol>
      <p class="sm" style="margin:3mm 0 0"><strong>記号：</strong><span class="ok">○</span>＝そのまま可　／　<span class="warn">▲</span>＝条件付き（書いてある要件を<strong>全部</strong>満たせば可）　／　<span class="ng">×</span>＝不可・違法　／　―＝その法律はかからない。<br>
      <strong>▲の右肩の数字は69章の手引きの番号です。</strong>▲3 なら「▲3　労働 ― 持込み運転者を日雇いで雇う」を見てください。</p>
    </div>

    <div class="box note">
      <div class="t">会社名の後ろの表記について</div>
      <p style="margin-bottom:0">運送事業者の名前に<span class="pg">（緑）</span>＝一般貨物自動車運送事業の許可あり（事業用・緑ナンバー）、<span class="pw">（白）</span>＝許可なし（自家用・白ナンバー）を付けています。<br>
      <strong>株式会社石名坂</strong>は運送業の許可を持たない発注者なので、ナンバーではなく<span class="pn">（真荷主）</span>と表記しています（貨運法12条2項の「真荷主」）。</p>
    </div>
  </div>

  <div class="meta">
    <table>
      <tr><td>作成日</td><td>2026年（令和8年）9月28日　／　<strong>改訂 9月29日</strong></td></tr>
      <tr><td>法令基準日</td><td><strong>2026年9月29日</strong>現在の施行法令（e-Gov法令検索の現行版）</td></tr>
      <tr><td>出典</td><td>本編『傭車の考え方と利用運送の登録判断』<strong>第65〜69章</strong>（図25〜図28）を抜き出したものです。<br>
        章番号・図番号は本編と同じです。Word版は <code>docs/legal-research/forms/白ダンプの早見表.docx</code></td></tr>
    </table>
    <p class="sm" style="margin-top:3mm">
      <strong class="ng">2026年9月29日 訂正：▲11（緑ダンプに日雇い運転者を乗せる）。</strong>
      輸送安全規則3条2項により<strong>日雇いの運転者は事業用自動車の選任運転者にできません</strong>。
      9月28日版をお持ちの方は差し替えてください。<span class="sm">白ダンプ（▲3）は日雇いで構いません。経緯は verify6/I_早見表の再検証.md</span><br>
      本資料は社内検討用に法令・省庁公表資料を整理したものです。個別事案の最終判断、とくに「照会事項」と記した項目は、
      岩手運輸支局・東北運輸局・岩手県・労働基準監督署への確認を経てください。
    </p>
  </div>
</div>
"""

html = (
    '<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8">\n'
    "<title>白ダンプの早見表</title>\n"
    '<link rel="stylesheet" href="style.css"></head><body>\n'
    + COVER + "\n" + part + "\n</body></html>\n"
)
io.open(OUT_HTML, "w", encoding="utf-8").write(html)

hdr = "<div></div>"
ftr = ('<div style="width:100%;font-family:sans-serif;font-size:7pt;color:#5c6873;'
       'padding:0 14mm;display:flex;justify-content:space-between;">'
       '<span>白ダンプの早見表 ｜ 有限会社石名坂商事・株式会社石名坂 ｜ 2026年9月29日改訂</span>'
       '<span class="pageNumber"></span></div>')

with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
    pg = b.new_page()
    pg.goto(OUT_HTML.as_uri(), wait_until="networkidle")
    # フォントの読み込みとレイアウト確定を待つ（末尾ページの欠落を防ぐ）
    pg.evaluate("document.fonts.ready")
    pg.wait_for_timeout(3000)
    pg.pdf(path=str(OUT_PDF), format="A4", print_background=True,
           display_header_footer=True, header_template=hdr, footer_template=ftr,
           margin={"top": "14mm", "bottom": "16mm", "left": "14mm", "right": "14mm"})
    b.close()
print("wrote", OUT_PDF)
