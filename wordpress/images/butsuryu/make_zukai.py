# -*- coding: utf-8 -*-
u"""総合物流施策大綱の記事用の図解を、石名坂の型どおりに描いて PNG にする。

  型は、トラック許可更新制の連載で使われている図（メディア 5514〜5524）から
  読み取った。2400×1350、白地、上に大きな見出し、角丸のカード、
  強調はオレンジ、いちばん下に濃紺の帯で言いたいこと一行。

    python3 make_zukai.py        3枚とも描く
    python3 make_zukai.py 2      2枚目だけ描き直す

  ％ の書式化は使わない。CSS の中の ％ と衝突するため、__名前__ を置き換える。
"""
from __future__ import print_function
import os, sys, io

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 2400, 1350

# 過去の図から読み取った色
NAVY   = '#14294A'
PALE   = '#E8F0F8'
ORANGE = '#E8761E'
MUTED  = '#5B6B80'

BASE = u'''<meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&display=swap">
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  html,body{width:2400px;height:1350px}
  body{
    background:#fff; color:__NAVY__;
    font-family:"Noto Sans JP","IPAGothic",sans-serif;
    font-weight:700; -webkit-font-smoothing:antialiased;
    display:flex; flex-direction:column;
  }
  .title{font-size:78px; font-weight:900; text-align:center;
         padding:60px 90px 0; line-height:1.3; letter-spacing:.01em}
  .stage{flex:1; display:flex; align-items:center; justify-content:center; padding:0 90px}
  .band{background:__NAVY__; color:#fff; font-size:42px; font-weight:700;
        text-align:center; padding:34px 60px; letter-spacing:.01em}
  .card{background:__PALE__; border-radius:22px;
        display:flex; flex-direction:column; align-items:center; justify-content:center}
  .num{font-weight:900; line-height:1}
  .sub{font-size:44px; margin-top:20px; font-weight:700}
  .muted{color:__MUTED__}
</style>
'''

FIG1 = BASE + u'''
<div class="title">輸送力の34％が、足りなくなるはずだった</div>
<div class="stage">
  <div style="width:100%">
    <div class="muted" style="text-align:center;font-size:40px;margin-bottom:34px">
      対策をしなかった場合に、2030年度に足りなくなるとされた輸送力
    </div>
    <div style="display:flex;height:400px;border-radius:22px;overflow:hidden">
      <div style="flex:14;background:__ORANGE__;color:#fff;display:flex;flex-direction:column;
                  align-items:center;justify-content:center">
        <div class="num" style="font-size:170px">約14％</div>
        <div class="sub">すでに克服した分</div>
      </div>
      <div style="flex:20;background:__PALE__;display:flex;flex-direction:column;
                  align-items:center;justify-content:center">
        <div class="num" style="font-size:170px">残り</div>
        <div class="sub">これからの課題</div>
      </div>
    </div>
    <div class="muted" style="display:flex;justify-content:space-between;
                              font-size:32px;margin-top:24px">
      <span>2024年問題への対応で克服</span><span>2030年度まで 集中改革期間</span>
    </div>
  </div>
</div>
<div class="band">総合物流施策大綱（2026年度〜2030年度）　2026年3月31日 閣議決定</div>
'''

HASHIRA = [
    (u'1', u'とにかく<br>無駄をなくす'),
    (u'2', u'頼む側の<br>意識を変える'),
    (u'3', u'働く人の<br>待遇をよくする'),
    (u'4', u'デジタルと<br>脱炭素'),
    (u'5', u'災害と国際情勢<br>に備える'),
]

FIG2 = BASE + u'''
<div class="title">大綱が、やると決めた5つのこと</div>
<div class="stage"><div style="display:flex;gap:30px;width:100%">__CARDS__</div></div>
<div class="band">運ぶ側だけの話ではない。荷主も消費者も、当事者に名指しされている</div>
'''

MOKUHYO = [
    (u'トラックの積載効率', u'41.3％', u'44％'),
    (u'荷待ち・荷役の時間', u'年 750時間', u'年 625時間'),
    (u'大型ドライバーの年収', u'492万円', u'全産業平均まで'),
    (u'自動運転トラック', u'まだ無い', u'1,000台'),
]

FIG3 = BASE + u'''
<div class="title">2030年度までに、ここを変える</div>
<div class="stage">
  <table style="width:100%;border-collapse:separate;border-spacing:0 26px;font-size:50px">
    <tr class="muted" style="font-size:34px">
      <td style="width:30%"></td><td style="width:28%;text-align:center">いま</td>
      <td style="width:8%"></td><td style="width:34%;text-align:center">2030年度</td>
    </tr>
    __ROWS__
  </table>
</div>
<div class="band">賃金は上げ、労働時間は下げて、どちらも全産業の平均まで</div>
'''


def paint(t):
    return (t.replace('__NAVY__', NAVY).replace('__PALE__', PALE)
             .replace('__ORANGE__', ORANGE).replace('__MUTED__', MUTED))


def fig1():
    return paint(FIG1)


def fig2():
    cards = []
    for no, label in HASHIRA:
        cards.append(
            u'<div class="card" style="flex:1;height:430px;padding:30px">'
            u'<div style="width:88px;height:88px;border-radius:50%;background:__ORANGE__;'
            u'color:#fff;font-size:46px;font-weight:900;display:flex;align-items:center;'
            u'justify-content:center;margin-bottom:30px">' + no + u'</div>'
            u'<div style="font-size:42px;text-align:center;line-height:1.45">' + label + u'</div>'
            u'</div>')
    return paint(FIG2.replace('__CARDS__', u''.join(cards)))


def fig3():
    rows = []
    for name, now, then in MOKUHYO:
        rows.append(
            u'<tr>'
            u'<td style="padding-right:34px">' + name + u'</td>'
            u'<td class="muted" style="background:__PALE__;border-radius:16px;'
            u'padding:28px;text-align:center">' + now + u'</td>'
            u'<td style="text-align:center;font-size:54px;color:__ORANGE__">→</td>'
            u'<td style="background:__ORANGE__;border-radius:16px;padding:28px;'
            u'text-align:center;color:#fff;font-weight:900">' + then + u'</td>'
            u'</tr>')
    return paint(FIG3.replace('__ROWS__', u''.join(rows)))


FIGS = [
    ('butsuryu-01-34percent.png', fig1),
    ('butsuryu-02-five-pillars.png', fig2),
    ('butsuryu-03-targets-2030.png', fig3),
]


def main():
    from playwright.sync_api import sync_playwright
    only = int(sys.argv[1]) if len(sys.argv) > 1 else None
    exe = None
    for c in ('/opt/pw-browsers/chromium-1194/chrome-linux/chrome', '/opt/pw-browsers/chromium'):
        if os.path.exists(c):
            exe = c
            break
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path=exe) if exe else pw.chromium.launch()
        pg = b.new_page(viewport={'width': W, 'height': H}, device_scale_factor=1)
        for i, (name, maker) in enumerate(FIGS, 1):
            if only and i != only:
                continue
            html = maker()
            path = os.path.join(HERE, name)
            io.open(path.replace('.png', '.html'), 'w', encoding='utf-8').write(html)
            pg.set_content(html, wait_until='networkidle')
            pg.wait_for_timeout(700)
            pg.screenshot(path=path)
            print(u'○ %s（%d bytes）' % (name, os.path.getsize(path)))
        b.close()


if __name__ == '__main__':
    main()
