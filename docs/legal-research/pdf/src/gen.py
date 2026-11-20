from playwright.sync_api import sync_playwright
import pathlib
d = pathlib.Path(__file__).parent
out = d / "傭車の考え方と利用運送の登録判断.pdf"
hdr = '<div></div>'
ftr = ('<div style="width:100%;font-family:sans-serif;font-size:7pt;color:#5c6873;'
       'padding:0 14mm;display:flex;justify-content:space-between;">'
       '<span>傭車の考え方と利用運送の登録判断 ｜ 有限会社石名坂商事・株式会社石名坂 ｜ 2026年9月30日改訂</span>'
       '<span class="pageNumber"></span></div>')
def chromium_path():
    """同梱のChromiumを探す。バージョン番号は環境が作り直されると変わるので直書きしない。
    （以前 chromium-1194 を直書きしていて、1243 に変わったときに全部動かなくなった）"""
    import glob
    import os
    # ディレクトリ名も環境で変わる（chrome-linux → chrome-linux64 の実績あり）
    for pat in ("/opt/pw-browsers/chromium-*/chrome-linux*/chrome",
                "/opt/pw-browsers/chromium/chrome-linux*/chrome"):
        hit = sorted(glob.glob(pat))
        if hit:
            return hit[-1]
    raise SystemExit("Chromiumが見つかりません。playwright install は実行しないこと。"
                     "/opt/pw-browsers を確認してください。")

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=chromium_path())
    pg = b.new_page()
    pg.goto((d/"body.html").as_uri(), wait_until="networkidle")
    # フォントの読み込みとレイアウト確定を待つ。待たずにpdf()を呼ぶと
    # 末尾の数ページが欠けたPDFが出ることがある。
    pg.evaluate("document.fonts.ready")
    pg.wait_for_timeout(3000)
    pg.pdf(path=str(out), format="A4", print_background=True,
           display_header_footer=True, header_template=hdr, footer_template=ftr,
           margin={"top":"14mm","bottom":"16mm","left":"14mm","right":"14mm"})
    b.close()
print("wrote", out)
