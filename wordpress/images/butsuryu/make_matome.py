# -*- coding: utf-8 -*-
u"""記事を読まない人向けの「1枚まとめ図」を描く。

  手本は、気候変動シリーズ最終回で使われている図
  （Gemini_Generated_Image_758tfp758tfp758t.jpg）。
  上に見出し帯、左右2つの箱を色分けし、矢印を中央の結論に集める。
  いちばん下に灰色の帯で、補足を横並び。

  文字はコードで描くので崩れない。数字が変わっても1行直せば描き直せる。

    python3 make_matome.py
"""
from __future__ import print_function
import os, io

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 2400, 1350

ORANGE = '#E8761E'; ORANGE_BG = '#FCEBDA'
BLUE   = '#1F6FB2'; BLUE_BG   = '#DCEBF8'
GREEN  = '#2E9E4F'; GREEN_BG  = '#DFF0DC'
GREY   = '#E7E7E4'
INK    = '#1A1A1A'


def icon_truck(c, s=86):
    return (u'<svg width="%d" height="%d" viewBox="0 0 100 100" fill="none">'
            u'<rect x="6" y="34" width="52" height="34" rx="5" fill="%s"/>'
            u'<path d="M60 44h18l14 15v9H60z" fill="%s" opacity=".55"/>'
            u'<circle cx="26" cy="74" r="10" fill="#333"/><circle cx="26" cy="74" r="4" fill="#fff"/>'
            u'<circle cx="74" cy="74" r="10" fill="#333"/><circle cx="74" cy="74" r="4" fill="#fff"/>'
            u'</svg>' % (s, s, c, c))


def icon_box(c, s=80):
    return (u'<svg width="%d" height="%d" viewBox="0 0 100 100" fill="none">'
            u'<rect x="16" y="28" width="68" height="52" rx="5" fill="%s"/>'
            u'<rect x="44" y="28" width="12" height="52" fill="#fff" opacity=".75"/>'
            u'<rect x="16" y="28" width="68" height="13" fill="#000" opacity=".12"/>'
            u'</svg>' % (s, s, c))


def icon_clock(c, s=80):
    return (u'<svg width="%d" height="%d" viewBox="0 0 100 100" fill="none">'
            u'<circle cx="50" cy="54" r="30" fill="%s"/>'
            u'<path d="M50 34v22h17" stroke="#fff" stroke-width="7" stroke-linecap="round"/>'
            u'</svg>' % (s, s, c))


def icon_yen(c, s=80):
    return (u'<svg width="%d" height="%d" viewBox="0 0 100 100" fill="none">'
            u'<circle cx="50" cy="52" r="31" fill="%s"/>'
            u'<path d="M36 34l14 18 14-18M38 56h24M38 66h24M50 52v22" stroke="#fff" '
            u'stroke-width="7" stroke-linecap="round" fill="none"/>'
            u'</svg>' % (s, s, c))


def icon_person(c, s=84):
    return (u'<svg width="%d" height="%d" viewBox="0 0 100 100" fill="none">'
            u'<path d="M24 40a26 26 0 0152 0z" fill="%s"/>'
            u'<rect x="18" y="40" width="64" height="7" rx="3" fill="%s"/>'
            u'<circle cx="50" cy="58" r="13" fill="#333"/>'
            u'<path d="M24 92c0-15 12-22 26-22s26 7 26 22z" fill="#333"/>'
            u'</svg>' % (s, s, c, c))


def bullet(color, head, sub=u''):
    s = (u'<li style="display:flex;gap:18px;align-items:flex-start">'
         u'<span style="flex:none;width:20px;height:20px;border-radius:50%%;'
         u'background:%s;margin-top:16px"></span><div>'
         u'<div style="font-size:47px;font-weight:900;line-height:1.35">%s</div>' % (color, head))
    if sub:
        s += u'<div style="font-size:32px;font-weight:700;line-height:1.4;opacity:.82">%s</div>' % sub
    return s + u'</div></li>'


HTML = u'''<meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@700;900&display=swap">
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  html,body{width:2400px;height:1350px}
  body{background:#fff;color:__INK__;font-family:"Noto Sans JP","IPAGothic",sans-serif;
       font-weight:900;-webkit-font-smoothing:antialiased;
       display:flex;flex-direction:column;padding:28px 34px 30px}
  .head{font-size:62px;text-align:center;letter-spacing:-.01em;line-height:1.2;
        padding-bottom:24px}
  .row{display:flex;gap:26px;height:600px}
  .panel{flex:1;border:8px solid;border-radius:26px;padding:26px 34px 30px;position:relative;
         display:flex;flex-direction:column}
  .fukidashi{border-radius:22px;padding:12px 38px;font-size:52px;display:inline-block;
             position:relative;margin:0 auto 20px}
  .fukidashi:after{content:"";position:absolute;bottom:-17px;left:50%;transform:translateX(-50%);
                   border:18px solid transparent;border-top-width:20px;border-bottom:0}
  ul{list-style:none;display:flex;flex-direction:column;gap:26px;flex:1;justify-content:center}
  .arrows{display:flex;justify-content:center;gap:520px;margin:8px 0 6px}
  .arrow{width:0;height:0;border:36px solid transparent;border-bottom:0;border-top-width:42px}
  .conclusion{border:8px solid __GREEN__;background:__GREEN_BG__;border-radius:26px;
              padding:34px 30px;display:flex;align-items:center;gap:30px;justify-content:center}
  .strip{background:__GREY__;border-radius:20px;margin-top:22px;padding:24px 30px 28px}
  .strip h3{font-size:42px;text-align:center;margin-bottom:18px}
  .strip .items{display:flex;justify-content:space-around;align-items:center;gap:26px}
  .item{display:flex;align-items:center;gap:18px;font-size:38px}
  .item small{font-size:31px;opacity:.82;font-weight:700}
</style>

<div class="head">総合物流施策大綱 ── 国が決めた、物流の5年計画（2026〜2030年度）</div>

<div class="row">
  <div class="panel" style="border-color:__ORANGE__">
    <div class="fukidashi" style="background:__ORANGE_BG__">荷物が、運べなくなる</div>
    <ul>__L1__</ul>
  </div>
  <div class="panel" style="border-color:__BLUE__">
    <div class="fukidashi" style="background:__BLUE_BG__">運ぶ人が、足りない</div>
    <ul>__L2__</ul>
  </div>
</div>

<div class="arrows">
  <div class="arrow" style="border-top-color:__ORANGE__"></div>
  <div class="arrow" style="border-top-color:__BLUE__"></div>
</div>

<div class="conclusion">
  __ICON_PERSON__
  <div>
    <div style="font-size:58px;line-height:1.25">だから国は、<span style="color:__GREEN__">
      賃金と労働時間を『全産業平均まで』</span>と書いた</div>
    <div style="font-size:36px;font-weight:700;margin-top:10px">
      2030年度までが「集中改革期間」。物流を、続けられる仕事にする5年間</div>
  </div>
  __ICON_TRUCK__
</div>

<div class="strip">
  <h3>受け取る私たちにも、できることがある</h3>
  <div class="items">
    <div class="item">__ICON_BOX__<div>置き配・宅配ボックス<br><small>利用率 25.6％ → 50％程度へ</small></div></div>
    <div class="item">__ICON_TRUCK2__<div>トラックの積載効率<br><small>41.3％ → 44％へ</small></div></div>
    <div class="item">__ICON_CLOCK__<div>荷待ち・荷役の時間<br><small>年750時間 → 年625時間へ</small></div></div>
  </div>
</div>
'''


def build():
    l1 = u''.join([
        bullet(ORANGE, u'2030年度に <span style="color:%s">約34％</span>の輸送力が不足する' % ORANGE,
               u'対策を何もしなかった場合の推計'),
        bullet(ORANGE, u'そのうち <span style="color:%s">約14％</span>は、すでに克服' % ORANGE,
               u'「2024年問題」への官民の取組による'),
        bullet(ORANGE, u'ただし、荷物そのものも約12％減った',
               u'28.4億トン（2019年）→ 25.1億トン（2024年）'),
    ])
    l2 = u''.join([
        bullet(BLUE, u'大型ドライバーの年収 <span style="color:%s">492万円</span>' % BLUE,
               u'全産業の平均は527万円'),
        bullet(BLUE, u'労働時間は年 <span style="color:%s">2,484時間</span>' % BLUE,
               u'全産業の平均は2,052時間。年400時間以上も長い'),
        bullet(BLUE, u'15〜29歳は、わずか <span style="color:%s">10.1％</span>' % BLUE,
               u'若い人が入ってこない'),
    ])
    t = HTML
    for k, v in [('__INK__', INK), ('__ORANGE__', ORANGE), ('__ORANGE_BG__', ORANGE_BG),
                 ('__BLUE__', BLUE), ('__BLUE_BG__', BLUE_BG), ('__GREEN__', GREEN),
                 ('__GREEN_BG__', GREEN_BG), ('__GREY__', GREY),
                 ('__L1__', l1), ('__L2__', l2),
                 ('__ICON_PERSON__', icon_person(BLUE, 128)),
                 ('__ICON_TRUCK__', icon_truck(GREEN, 138)),
                 ('__ICON_TRUCK2__', icon_truck(ORANGE, 84)),
                 ('__ICON_BOX__', icon_box(GREEN, 80)),
                 ('__ICON_CLOCK__', icon_clock(BLUE, 80))]:
        t = t.replace(k, v)
    return t


def main():
    from playwright.sync_api import sync_playwright
    exe = None
    for c in ('/opt/pw-browsers/chromium-1194/chrome-linux/chrome', '/opt/pw-browsers/chromium'):
        if os.path.exists(c):
            exe = c
            break
    html = build()
    io.open(os.path.join(HERE, 'butsuryu-00-matome.html'), 'w', encoding='utf-8').write(html)
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path=exe) if exe else pw.chromium.launch()
        pg = b.new_page(viewport={'width': W, 'height': H}, device_scale_factor=1)
        pg.set_content(html, wait_until='networkidle')
        pg.wait_for_timeout(700)
        path = os.path.join(HERE, 'butsuryu-00-matome.png')
        pg.screenshot(path=path)
        print(u'○ butsuryu-00-matome.png（%d bytes）' % os.path.getsize(path))
        b.close()


if __name__ == '__main__':
    main()
