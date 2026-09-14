# -*- coding: utf-8 -*-
"""量子記事の図（SVG）を作り、記事に差し込む。

3枚とも文字・数字が入るため、画像生成AIには任せられないもの。
 図2：1984年からの40年の流れ（前編）
 図3：50量子ビットを、普通のコンピュータと量子コンピュータで比べる（前編）
 図4：工場と根粒菌の条件くらべ（後編）

配色は currentColor（本文の文字色）と銅色 #C1803A のみ。
明るい画面でも暗い画面でも読めるようにするため。
"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
COPPER = '#C1803A'


def wrap(svg, caption):
    return (u'<!-- wp:html -->\n'
            u'<figure style="margin:0;padding:0">\n'
            + svg + u'\n'
            u'<figcaption style="font-size:0.85em;text-align:center;'
            u'margin-top:8px;opacity:0.8">' + caption + u'</figcaption>\n'
            u'</figure>\n'
            u'<!-- /wp:html -->')


# ---------------------------------------------------------------- 図2 年表
def fig_timeline():
    rows = [
        (u'1984-85', u'ジョセフソン接合の実験', u'2025年のノーベル物理学賞の対象'),
        (u'1999', u'NECが量子ビットを世界初実現', u'「クーパー対箱」。Nature の表紙に'),
        (u'2007', u'トランズモンの提案', u'論文の題名は「クーパー対箱から導かれた設計」'),
        (u'いま', u'IBM・Google の主力部品に', u''),
        (u'2026', u'NECが実機開発を中止と報じられる', u'同じ月に理研・阪大が144量子ビットを稼働'),
    ]
    x_line = 150
    x_text = 176
    y0, step = 78, 92
    h = y0 + step * (len(rows) - 1) + 70

    p = []
    p.append(u'<svg viewBox="0 0 640 %d" role="img" aria-label="1984年から85年のジョセフソン接合の実験、'
             u'1999年のNECによる量子ビットの世界初実現、2007年のトランズモンの提案、現在のIBMとGoogleの'
             u'主力部品、2026年のNECの実機開発中止の報道までを並べた年表。1984年から現在までが40年。" '
             u'style="max-width:100%%;height:auto;display:block;margin:0 auto">' % h)

    # 40年のかっこ（1984 → いま）
    y_top, y_bot = y0, y0 + step * 3
    p.append(u'<path d="M 112 %d L 100 %d L 100 %d L 112 %d" fill="none" '
             u'stroke="%s" stroke-width="2"></path>' % (y_top, y_top, y_bot, y_bot, COPPER))
    p.append(u'<text x="100" y="%d" text-anchor="middle" font-size="15" '
             u'font-weight="bold" fill="%s">40年</text>' % (y_top - 18, COPPER))

    # 縦線
    p.append(u'<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="currentColor" '
             u'stroke-width="2" opacity="0.3"></line>'
             % (x_line, y0, x_line, y0 + step * (len(rows) - 1)))

    for i, (year, title, sub) in enumerate(rows):
        y = y0 + step * i
        p.append(u'<circle cx="%d" cy="%d" r="6" fill="%s"></circle>' % (x_line, y, COPPER))
        p.append(u'<text x="%d" y="%d" font-size="13" font-weight="bold" fill="%s">%s</text>'
                 % (x_text, y - 12, COPPER, year))
        p.append(u'<text x="%d" y="%d" font-size="15" font-weight="bold" fill="currentColor">%s</text>'
                 % (x_text, y + 10, title))
        if sub:
            p.append(u'<text x="%d" y="%d" font-size="13" fill="currentColor" opacity="0.75">%s</text>'
                     % (x_text, y + 32, sub))

    y_end = y0 + step * (len(rows) - 1)
    p.append(u'<text x="320" y="%d" text-anchor="middle" font-size="13" fill="currentColor">'
             u'基礎研究が形になるまでに、40年かかりました</text>' % (y_end + 62))
    p.append(u'</svg>')
    return wrap(u'\n  '.join(p),
                u'1984年の実験から、いまの機械まで。一本の線でつながっています。')


# ------------------------------------------------- 図3 50量子ビットの比べ方
def fig_compare():
    p = []
    p.append(u'<svg viewBox="0 0 700 400" role="img" aria-label="50量子ビットを扱うとき、'
             u'普通のコンピュータは約1126兆本の矢印を一本ずつ記憶する必要があり1ペタバイトを超える'
             u'メモリを要するが、量子コンピュータにとっては部品が50個あるだけである、という比較。" '
             u'style="max-width:100%;height:auto;display:block;margin:0 auto">')
    p.append(u'<defs><pattern id="qc-dots" width="11" height="11" patternUnits="userSpaceOnUse">'
             u'<circle cx="5.5" cy="5.5" r="1.5" fill="currentColor" opacity="0.6"></circle>'
             u'</pattern></defs>')

    p.append(u'<text x="350" y="30" text-anchor="middle" font-size="15" font-weight="bold" '
             u'fill="currentColor">どちらも「50量子ビット」を扱う</text>')

    # 仕切り
    p.append(u'<line x1="350" y1="52" x2="350" y2="352" stroke="currentColor" '
             u'stroke-width="1" opacity="0.25"></line>')

    # 左：普通のコンピュータ
    p.append(u'<text x="180" y="78" text-anchor="middle" font-size="16" font-weight="bold" '
             u'fill="currentColor">普通のコンピュータ</text>')
    p.append(u'<rect x="42" y="98" width="276" height="176" fill="url(#qc-dots)" '
             u'stroke="currentColor" stroke-width="1.5" opacity="0.9"></rect>')
    p.append(u'<text x="180" y="300" text-anchor="middle" font-size="14" fill="currentColor">'
             u'この点が 約1,126兆個</text>')
    p.append(u'<text x="180" y="324" text-anchor="middle" font-size="14" fill="currentColor">'
             u'一本ずつ、記憶しておく</text>')
    p.append(u'<text x="180" y="356" text-anchor="middle" font-size="16" font-weight="bold" '
             u'fill="%s">メモリ 1ペタバイト超</text>' % COPPER)

    # 右：量子コンピュータ（50個）
    cols, rowsn, sp = 10, 5, 26
    x_start = 520 - (cols - 1) * sp / 2.0
    y_start = 118
    p.append(u'<text x="520" y="78" text-anchor="middle" font-size="16" font-weight="bold" '
             u'fill="currentColor">量子コンピュータ</text>')
    for r in range(rowsn):
        for c in range(cols):
            p.append(u'<circle cx="%.0f" cy="%d" r="6" fill="none" stroke="%s" '
                     u'stroke-width="2"></circle>'
                     % (x_start + c * sp, y_start + r * sp, COPPER))
    p.append(u'<text x="520" y="300" text-anchor="middle" font-size="14" fill="currentColor">'
             u'部品が 50個 あるだけ</text>')
    p.append(u'<text x="520" y="324" text-anchor="middle" font-size="14" fill="currentColor">'
             u'矢印は物理が持っている</text>')
    p.append(u'<text x="520" y="356" text-anchor="middle" font-size="16" font-weight="bold" '
             u'fill="%s">記憶しなくてよい</text>' % COPPER)

    p.append(u'<text x="350" y="390" text-anchor="middle" font-size="13" fill="currentColor">'
             u'1量子ビット増えるごとに、左の点の数は倍になります</text>')
    p.append(u'</svg>')
    return wrap(u'\n  '.join(p),
                u'速さではなく、扱える量の桁が違います。ここが量子コンピュータの強みです。')


# ----------------------------------------------- 図4 工場と根粒菌の条件くらべ
def fig_ammonia():
    p = []
    p.append(u'<svg viewBox="0 0 700 380" role="img" aria-label="アンモニアを作るのに、'
             u'工場では400から500度・数百気圧を要し人類の全エネルギーの数パーセントを使う一方、'
             u'マメ科の根につく根粒では常温・常圧で同じことが行われており、そのしくみは未解明である、'
             u'という比較。" style="max-width:100%;height:auto;display:block;margin:0 auto">')

    p.append(u'<text x="350" y="30" text-anchor="middle" font-size="15" font-weight="bold" '
             u'fill="currentColor">どちらも、空気の窒素からアンモニアを作っている</text>')
    p.append(u'<line x1="350" y1="52" x2="350" y2="330" stroke="currentColor" '
             u'stroke-width="1" opacity="0.25"></line>')

    # 左：工場
    p.append(u'<text x="175" y="80" text-anchor="middle" font-size="16" font-weight="bold" '
             u'fill="currentColor">工場</text>')
    g = []
    g.append(u'<rect x="108" y="150" width="46" height="70"></rect>')
    g.append(u'<rect x="162" y="128" width="34" height="92"></rect>')
    g.append(u'<rect x="204" y="162" width="40" height="58"></rect>')
    g.append(u'<line x1="120" y1="150" x2="120" y2="112"></line>')
    g.append(u'<line x1="142" y1="150" x2="142" y2="122"></line>')
    g.append(u'<line x1="108" y1="220" x2="244" y2="220"></line>')
    p.append(u'<g fill="none" stroke="currentColor" stroke-width="2">%s</g>' % u''.join(g))
    p.append(u'<text x="175" y="256" text-anchor="middle" font-size="17" font-weight="bold" '
             u'fill="%s">400〜500度</text>' % COPPER)
    p.append(u'<text x="175" y="282" text-anchor="middle" font-size="17" font-weight="bold" '
             u'fill="%s">数百気圧</text>' % COPPER)
    p.append(u'<text x="175" y="314" text-anchor="middle" font-size="13" fill="currentColor">'
             u'人類が使う全エネルギーの数パーセント</text>')

    # 右：根粒
    p.append(u'<text x="525" y="80" text-anchor="middle" font-size="16" font-weight="bold" '
             u'fill="currentColor">マメ科の根</text>')
    r = []
    r.append(u'<line x1="525" y1="104" x2="525" y2="150"></line>')
    r.append(u'<path d="M 525 150 C 500 172 486 196 478 222"></path>')
    r.append(u'<path d="M 525 150 C 545 176 556 200 560 224"></path>')
    r.append(u'<path d="M 525 150 C 522 180 520 202 516 226"></path>')
    p.append(u'<g fill="none" stroke="currentColor" stroke-width="2">%s</g>' % u''.join(r))
    for cx, cy in [(506, 172), (488, 203), (543, 178), (556, 208), (521, 190), (518, 216)]:
        p.append(u'<circle cx="%d" cy="%d" r="6.5" fill="%s"></circle>' % (cx, cy, COPPER))
    p.append(u'<text x="525" y="256" text-anchor="middle" font-size="17" font-weight="bold" '
             u'fill="%s">常温</text>' % COPPER)
    p.append(u'<text x="525" y="282" text-anchor="middle" font-size="17" font-weight="bold" '
             u'fill="%s">常圧</text>' % COPPER)
    p.append(u'<text x="525" y="314" text-anchor="middle" font-size="13" fill="currentColor">'
             u'根粒菌の酵素が、土の中で</text>')

    p.append(u'<text x="350" y="360" text-anchor="middle" font-size="14" font-weight="bold" '
             u'fill="currentColor">このしくみは、まだ解明されていません</text>')
    p.append(u'</svg>')
    return wrap(u'\n  '.join(p),
                u'同じことを、工場は高温高圧で、根粒は常温常圧で行っています。')


# ---------------------------------------------------------------- 差し込み
INSERTS = [
    ('article-01.html',
     u'<p class="has-medium-font-size"><strong>そして現在。</strong>このトランズモンが、IBMやGoogleの量子コンピュータの主力部品になっています。1984年の実験から数えて、40年。基礎研究が形になるまでに、それだけの時間がかかっています。</p>\n<!-- /wp:paragraph -->',
     fig_timeline),
    ('article-01.html',
     u'<p class="has-medium-font-size">一方、量子コンピュータにとって50量子ビットは<strong>50個の部品</strong>です。1,126兆本の矢印を「覚えておく」必要がありません。物理が勝手に持っていてくれるからです。</p>\n<!-- /wp:paragraph -->',
     fig_compare),
    ('article-02.html',
     u'<p class="has-medium-font-size">もし解明されれば、常温常圧で肥料を作る道が開けるかもしれません。<strong>これが、量子コンピュータに期待されていることの、いちばんわかりやすい形です。</strong></p>\n<!-- /wp:paragraph -->',
     fig_ammonia),
]

for fname, anchor, maker in INSERTS:
    path = os.path.join(HERE, fname)
    t = io.open(path, encoding='utf-8').read()
    if t.count(anchor) != 1:
        sys.stderr.write('× 差し込み先が %d 件（1件でないと止めます）: %s\n'
                         % (t.count(anchor), fname))
        sys.exit(1)
    t = t.replace(anchor, anchor + u'\n\n' + maker())
    io.open(path, 'w', encoding='utf-8').write(t)
    print(u'○ %s に図を1枚 差し込みました' % fname)
