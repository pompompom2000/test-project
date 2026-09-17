from playwright.sync_api import sync_playwright
import pathlib
d = pathlib.Path(__file__).parent
out = d / "傭車の考え方と利用運送の登録判断.pdf"
hdr = '<div></div>'
ftr = ('<div style="width:100%;font-family:sans-serif;font-size:7pt;color:#5c6873;'
       'padding:0 14mm;display:flex;justify-content:space-between;">'
       '<span>傭車の考え方と利用運送の登録判断 ｜ 有限会社石名坂商事・株式会社石名坂 ｜ 2026年9月17日</span>'
       '<span class="pageNumber"></span></div>')
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
    pg = b.new_page()
    pg.goto((d/"body.html").as_uri(), wait_until="networkidle")
    pg.pdf(path=str(out), format="A4", print_background=True,
           display_header_footer=True, header_template=hdr, footer_template=ftr,
           margin={"top":"14mm","bottom":"16mm","left":"14mm","right":"14mm"})
    b.close()
print("wrote", out)
