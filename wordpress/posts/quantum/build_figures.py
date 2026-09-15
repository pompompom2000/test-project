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
import re
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
        (u'いま', u'IBM・Google の主力部品に', u'2025年のノーベル物理学賞は、この線の出発点に贈られた'),
    ]
    x_line = 150
    x_text = 176
    y0, step = 78, 92
    h = y0 + step * (len(rows) - 1) + 70

    p = []
    p.append(u'<svg viewBox="0 0 640 %d" role="img" aria-label="1984年から85年のジョセフソン接合の実験、'
             u'1999年のNECによる量子ビットの世界初実現、2007年のトランズモンの提案、'
             u'現在のIBMとGoogleの主力部品までを並べた年表。1984年から現在までが40年。" '
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
# ---------------------------------------------------------------- 図A ビットと量子ビット
def fig_bit_vs_qubit():
    """ふつうのビットと量子ビットの違いを、一枚にする。

    記事のいちばん大事な一歩なのに、ここだけ図がなかった。
    「0か1か」と「向きのある矢印」を、並べて見せる。
    """
    p = []
    p.append(u'<svg viewBox="0 0 700 340" role="img" aria-label="ふつうのビットは0か1の'
             u'どちらか一方であるのに対し、量子ビットは長さと向きを持つ矢印で表される。'
             u'長さはその答えの出やすさ、向きは位相を表す。長さが同じでも向きが違えば'
             u'別のものになる。" style="max-width:100%;height:auto;display:block;margin:0 auto">')
    p.append(u'<defs><marker id="qb-ah" viewBox="0 0 10 10" refX="9" refY="5" '
             u'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
             u'<polygon points="0,1 10,5 0,9" fill="%s"></polygon></marker></defs>' % COPPER)

    # まんなかの仕切り
    p.append(u'<line x1="350" y1="24" x2="350" y2="316" stroke="currentColor" '
             u'stroke-width="1" opacity="0.2"></line>')

    # 左：ふつうのビット
    p.append(u'<text x="175" y="42" text-anchor="middle" font-size="17" '
             u'font-weight="bold" fill="currentColor">ふつうのビット</text>')
    for i, (x, lab, on) in enumerate([(85, u'0', False), (180, u'1', True)]):
        fill = COPPER if on else 'none'
        tx = '#FFFFFF' if on else 'currentColor'
        p.append(u'<rect x="%d" y="78" width="85" height="85" rx="8" fill="%s" '
                 u'stroke="currentColor" stroke-width="2" opacity="%s"></rect>'
                 % (x, fill, '1' if on else '0.55'))
        p.append(u'<text x="%d" y="135" text-anchor="middle" font-size="40" '
                 u'font-weight="bold" fill="%s">%s</text>' % (x + 42, tx, lab))
    p.append(u'<text x="175" y="205" text-anchor="middle" font-size="15" '
             u'fill="currentColor">どちらか一方。必ず、どちらか</text>')
    p.append(u'<text x="175" y="232" text-anchor="middle" font-size="15" '
             u'fill="currentColor" opacity="0.7">スイッチと同じです</text>')

    # 右：量子ビット
    p.append(u'<text x="525" y="42" text-anchor="middle" font-size="17" '
             u'font-weight="bold" fill="currentColor">量子ビット</text>')
    p.append(u'<circle cx="525" cy="130" r="56" fill="none" stroke="currentColor" '
             u'stroke-width="1.5" opacity="0.25"></circle>')
    p.append(u'<circle cx="525" cy="130" r="4" fill="currentColor" opacity="0.5"></circle>')
    p.append(u'<line x1="525" y1="130" x2="566" y2="92" stroke="%s" stroke-width="3" '
             u'marker-end="url(#qb-ah)"></line>' % COPPER)
    # 角度がどこのことか分かるように、基準の線と弧を描く
    p.append(u'<line x1="525" y1="130" x2="596" y2="130" stroke="currentColor" '
             u'stroke-width="1.5" stroke-dasharray="4 4" opacity="0.35"></line>')
    p.append(u'<path d="M 565 130 A 40 40 0 0 0 554 103" fill="none" stroke="%s" '
             u'stroke-width="2" opacity="0.7"></path>' % COPPER)
    p.append(u'<text x="604" y="100" font-size="13" font-weight="bold" fill="%s">長さ</text>' % COPPER)
    p.append(u'<text x="604" y="118" font-size="12" fill="currentColor" opacity="0.75">出やすさ</text>')
    p.append(u'<text x="604" y="150" font-size="13" font-weight="bold" fill="%s">向き</text>' % COPPER)
    p.append(u'<text x="604" y="168" font-size="12" fill="currentColor" opacity="0.75">位相</text>')

    # 同じ長さで向きだけ違う三本
    for i, (cx, dx, dy) in enumerate([(425, 30, -18), (525, 0, -35), (625, -30, -18)]):
        p.append(u'<line x1="%d" y1="272" x2="%d" y2="%d" stroke="%s" stroke-width="3" '
                 u'marker-end="url(#qb-ah)"></line>' % (cx, cx + dx, 272 + dy, COPPER))
        p.append(u'<circle cx="%d" cy="272" r="3" fill="currentColor" opacity="0.4"></circle>' % cx)
    p.append(u'<text x="525" y="306" text-anchor="middle" font-size="15" '
             u'fill="currentColor">長さが同じでも、向きが違えば別のもの</text>')
    p.append(u'</svg>')
    return wrap(u'\n'.join(p),
                u'ふつうのビットは0か1。量子ビットは、長さと向きを持つ矢印です。'
                u'この「向き」が、普通の確率にはないものです。')


# ---------------------------------------------------------------- 図B 矢印の数が倍になる
def fig_doubling():
    """量子ビットが1個増えるごとに矢印が倍になることを、実際に描いて見せる。"""
    rows = [(1, 2), (2, 4), (3, 8)]
    p = []
    p.append(u'<svg viewBox="0 0 700 390" role="img" aria-label="量子ビットが1個のとき'
             u'矢印は2本、2個で4本、3個で8本と、1個増えるごとに倍になる。50個では'
             u'約1126兆本になり、絵に描くことはできない。" '
             u'style="max-width:100%;height:auto;display:block;margin:0 auto">')
    p.append(u'<defs><marker id="dbl-ah" viewBox="0 0 10 10" refX="9" refY="5" '
             u'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
             u'<polygon points="0,1 10,5 0,9" fill="%s"></polygon></marker></defs>' % COPPER)

    p.append(u'<text x="350" y="34" text-anchor="middle" font-size="16" '
             u'font-weight="bold" fill="currentColor">1個増えるごとに、矢印の数は倍になります</text>')
    p.append(u'<text x="108" y="70" text-anchor="end" font-size="12" '
             u'fill="currentColor" opacity="0.6">量子ビット</text>')
    p.append(u'<text x="140" y="70" font-size="12" fill="currentColor" opacity="0.6">矢印</text>')

    y = 108
    for qubits, arrows in rows:
        p.append(u'<text x="108" y="%d" text-anchor="end" font-size="17" '
                 u'font-weight="bold" fill="currentColor">%d個</text>' % (y + 6, qubits))
        for i in range(arrows):
            x = 140 + i * 30
            p.append(u'<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" '
                     u'stroke-width="2.5" marker-end="url(#dbl-ah)"></line>'
                     % (x, y + 14, x + 12, y - 12, COPPER))
        p.append(u'<text x="%d" y="%d" font-size="15" fill="currentColor" '
                 u'opacity="0.8">%d本</text>' % (140 + arrows * 30 + 10, y + 6, arrows))
        y += 58

    # 途中を省く
    p.append(u'<text x="150" y="%d" font-size="20" fill="currentColor" opacity="0.4">⋮</text>' % (y + 4))

    # 50個
    y += 44
    p.append(u'<line x1="60" y1="%d" x2="640" y2="%d" stroke="currentColor" '
             u'stroke-width="1" opacity="0.2"></line>' % (y - 22, y - 22))
    p.append(u'<text x="108" y="%d" text-anchor="end" font-size="17" '
             u'font-weight="bold" fill="currentColor">50個</text>' % (y + 6))
    p.append(u'<text x="140" y="%d" font-size="20" font-weight="bold" fill="%s">'
             u'約 1,126 兆本</text>' % (y + 8, COPPER))
    p.append(u'<text x="140" y="%d" font-size="13" fill="currentColor" opacity="0.7">'
             u'ここまで来ると、もう描けません</text>' % (y + 32))
    p.append(u'</svg>')
    return wrap(u'\n'.join(p),
                u'矢印の本数は、量子ビットが1個増えるごとに倍になります。'
                u'ただしこれは「その本数のデータをしまえる」という意味ではありません。')


# ---------------------------------------------------------------- 図C 温度のものさし
def fig_temperature():
    """冷やす話。ただし「全部が冷たいわけではない」まで含めて一枚にする。

    札は線の上下に振り分ける。横に並べると、目盛りの間隔が狭いところで
    文字どうしが重なって読めなくなるため。
    """
    # (x, 温度, 見出し, 補足, 線の上に置くか)
    marks = [
        (90, u'0 K', u'絶対零度', u'到達できません', False),
        (235, u'0.01 K', u'超電導方式の冷凍機', u'絶対零度の100分の1度ほど', True),
        (390, u'2.7 K', u'宇宙のかすかな熱', u'冷凍機の中は、宇宙より冷たい', False),
        (600, u'300 K', u'室温', u'およそ27度', True),
    ]
    p = []
    p.append(u'<svg viewBox="0 0 700 348" role="img" aria-label="絶対零度0ケルビン、'
             u'超電導方式の冷凍機が0.01ケルビン、宇宙のかすかな熱が2.7ケルビン、'
             u'室温が300ケルビン。冷凍機の中は宇宙より冷たい。'
             u'中性原子方式・イオン方式・光方式は、この冷凍機を必要としない。" '
             u'style="max-width:100%;height:auto;display:block;margin:0 auto">')

    p.append(u'<text x="350" y="34" text-anchor="middle" font-size="16" '
             u'font-weight="bold" fill="currentColor">冷やすのは、矢印の向きが壊れないように</text>')
    p.append(u'<text x="640" y="56" text-anchor="end" font-size="11" '
             u'fill="currentColor" opacity="0.5">目盛りは等間隔ではありません</text>')
    p.append(u'<line x1="70" y1="158" x2="640" y2="158" stroke="currentColor" '
             u'stroke-width="2" opacity="0.35"></line>')

    for x, k, title, sub, above in marks:
        hot = (k == u'300 K')
        col = 'currentColor' if hot else COPPER
        p.append(u'<line x1="%d" y1="146" x2="%d" y2="170" stroke="%s" '
                 u'stroke-width="2"></line>' % (x, x, col))
        ys = (136, 108, 88) if above else (188, 212, 232)
        p.append(u'<text x="%d" y="%d" text-anchor="middle" font-size="16" '
                 u'font-weight="bold" fill="%s">%s</text>' % (x, ys[0], col, k))
        p.append(u'<text x="%d" y="%d" text-anchor="middle" font-size="14" '
                 u'font-weight="bold" fill="currentColor">%s</text>' % (x, ys[1], title))
        p.append(u'<text x="%d" y="%d" text-anchor="middle" font-size="12" '
                 u'fill="currentColor" opacity="0.7">%s</text>' % (x, ys[2], sub))

    # 冷やさない方式
    p.append(u'<rect x="70" y="258" width="570" height="74" rx="6" fill="none" '
             u'stroke="currentColor" stroke-width="1.5" opacity="0.35"></rect>')
    p.append(u'<text x="92" y="288" font-size="15" font-weight="bold" '
             u'fill="currentColor">この冷凍機が要らない作り方もあります</text>')
    p.append(u'<text x="92" y="313" font-size="13" fill="currentColor" opacity="0.8">'
             u'中性原子方式／イオン方式／光方式。光の方式は、量子ビットそのものが常温です</text>')
    p.append(u'</svg>')
    return wrap(u'\n'.join(p),
                u'超電導方式の冷凍機の中は、宇宙のかすかな熱よりも冷たい世界です。'
                u'ただし、すべての量子コンピュータがこうではありません。')


# ---------------------------------------------------------------- 図D 量子もつれ
def fig_entangle():
    """「必ず揃う」のに「通信はできない」を、一枚で並べる。

    ここは記事のなかでいちばん誤解の多いところ。文章だけだと
    「揃うなら送れるのでは」と読まれてしまう。
    """
    p = []
    p.append(u'<svg viewBox="0 0 700 372" role="img" aria-label="離れた二つの量子ビットは'
             u'測るたびに必ず同じ目が出るが、その目はどちらの側でも選べないでたらめな値'
             u'であるため、合図として使えず、量子もつれで通信はできない。" '
             u'style="max-width:100%;height:auto;display:block;margin:0 auto">')

    p.append(u'<line x1="350" y1="46" x2="350" y2="282" stroke="currentColor" '
             u'stroke-width="1" opacity="0.22"></line>')

    # 左：必ず揃う
    p.append(u'<text x="190" y="40" text-anchor="middle" font-size="16" '
             u'font-weight="bold" fill="currentColor">測ると、必ず揃う</text>')
    for cx, lab in [(95, u'A'), (285, u'B')]:
        p.append(u'<circle cx="%d" cy="86" r="21" fill="none" stroke="currentColor" '
                 u'stroke-width="2"></circle>' % cx)
        p.append(u'<text x="%d" y="92" text-anchor="middle" font-size="15" '
                 u'font-weight="bold" fill="currentColor">%s</text>' % (cx, lab))
    p.append(u'<line x1="120" y1="86" x2="260" y2="86" stroke="%s" stroke-width="2" '
             u'stroke-dasharray="5 5" opacity="0.8"></line>' % COPPER)
    p.append(u'<text x="190" y="120" text-anchor="middle" font-size="12" '
             u'fill="currentColor" opacity="0.7">どんなに離れていても</text>')

    for i, v in enumerate([('0', '0'), ('1', '1'), ('0', '0')]):
        y = 158 + i * 34
        p.append(u'<text x="95" y="%d" text-anchor="middle" font-size="19" '
                 u'font-weight="bold" fill="%s">%s</text>' % (y, COPPER, v[0]))
        p.append(u'<text x="190" y="%d" text-anchor="middle" font-size="14" '
                 u'fill="currentColor" opacity="0.6">＝</text>' % y)
        p.append(u'<text x="285" y="%d" text-anchor="middle" font-size="19" '
                 u'font-weight="bold" fill="%s">%s</text>' % (y, COPPER, v[1]))
    p.append(u'<text x="190" y="268" text-anchor="middle" font-size="13" '
             u'fill="currentColor">何度測っても、二人の目は同じ</text>')

    # 右：でも選べない
    p.append(u'<text x="520" y="40" text-anchor="middle" font-size="16" '
             u'font-weight="bold" fill="currentColor">でも、出る目は選べない</text>')
    p.append(u'<rect x="470" y="72" width="100" height="100" rx="14" fill="none" '
             u'stroke="currentColor" stroke-width="2"></rect>')
    p.append(u'<text x="520" y="141" text-anchor="middle" font-size="58" '
             u'font-weight="bold" fill="%s">?</text>' % COPPER)
    p.append(u'<text x="520" y="200" text-anchor="middle" font-size="13" '
             u'fill="currentColor">「1を出そう」と思っても</text>')
    p.append(u'<text x="520" y="222" text-anchor="middle" font-size="13" '
             u'fill="currentColor">出る目は、毎回でたらめ</text>')
    p.append(u'<text x="520" y="268" text-anchor="middle" font-size="13" '
             u'fill="currentColor">どちらの側でも決められない</text>')

    # まとめ
    p.append(u'<rect x="60" y="298" width="580" height="54" rx="6" fill="none" '
             u'stroke="%s" stroke-width="2"></rect>' % COPPER)
    p.append(u'<text x="350" y="331" text-anchor="middle" font-size="16" '
             u'font-weight="bold" fill="currentColor">'
             u'決められないものは、合図に使えません</text>')
    p.append(u'</svg>')
    return wrap(u'\n'.join(p),
                u'揃うことと、伝えられることは別です。'
                u'相関はありますが、合図は送れません（通信不可能定理）。')


# ---------------------------------------------------------------- 図E 物理と論理
def fig_logical_qubit():
    """「何量子ビット」の数字が、どちらを指しているかを見せる。"""
    p = []
    p.append(u'<svg viewBox="0 0 700 372" role="img" aria-label="壊れやすい物理量子ビットを'
             u'千から万の単位で束ねて、ようやく確かに計算できる論理量子ビットが1個できる。'
             u'ニュースで見る量子ビットの数は、たいてい物理量子ビットのほうである。" '
             u'style="max-width:100%;height:auto;display:block;margin:0 auto">')
    p.append(u'<defs><marker id="lq-ah" viewBox="0 0 10 10" refX="9" refY="5" '
             u'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
             u'<polygon points="0,1 10,5 0,9" fill="%s"></polygon></marker></defs>' % COPPER)

    p.append(u'<text x="350" y="36" text-anchor="middle" font-size="16" '
             u'font-weight="bold" fill="currentColor">'
             u'ニュースの「◯◯量子ビット」は、どちらの数でしょう</text>')

    # 左：物理量子ビット（たくさんの粒）
    for r in range(6):
        for c in range(12):
            p.append(u'<circle cx="%d" cy="%d" r="5" fill="none" stroke="currentColor" '
                     u'stroke-width="1.5" opacity="0.65"></circle>'
                     % (66 + c * 20, 88 + r * 22))
    p.append(u'<text x="176" y="252" text-anchor="middle" font-size="16" '
             u'font-weight="bold" fill="currentColor">物理量子ビット</text>')
    p.append(u'<text x="176" y="276" text-anchor="middle" font-size="13" '
             u'fill="currentColor" opacity="0.75">壊れやすい部品。これを数えた数</text>')

    # 矢印
    p.append(u'<line x1="322" y1="154" x2="392" y2="154" stroke="%s" stroke-width="3" '
             u'marker-end="url(#lq-ah)"></line>' % COPPER)
    p.append(u'<text x="357" y="134" text-anchor="middle" font-size="15" '
             u'font-weight="bold" fill="%s">千〜万個</text>' % COPPER)
    p.append(u'<text x="357" y="180" text-anchor="middle" font-size="13" '
             u'fill="currentColor">束ねて</text>')

    # 右：論理量子ビット（ひとつ）
    p.append(u'<circle cx="530" cy="154" r="52" fill="none" stroke="%s" '
             u'stroke-width="3"></circle>' % COPPER)
    p.append(u'<text x="530" y="164" text-anchor="middle" font-size="30" '
             u'font-weight="bold" fill="%s">1個</text>' % COPPER)
    p.append(u'<text x="530" y="252" text-anchor="middle" font-size="16" '
             u'font-weight="bold" fill="currentColor">論理量子ビット</text>')
    p.append(u'<text x="530" y="276" text-anchor="middle" font-size="13" '
             u'fill="currentColor" opacity="0.75">誤りを打ち消して、確かに使える1個</text>')

    p.append(u'<line x1="60" y1="300" x2="640" y2="300" stroke="currentColor" '
             u'stroke-width="1" opacity="0.25"></line>')
    p.append(u'<text x="350" y="326" text-anchor="middle" font-size="14" '
             u'fill="currentColor">ニュースの数字は、たいてい<tspan font-weight="bold">左</tspan>のほうです</text>')
    p.append(u'<text x="350" y="352" text-anchor="middle" font-size="13" '
             u'fill="currentColor" opacity="0.75">'
             u'IBMは1,121個の機械から、133個の機械に主力を移しました</text>')
    p.append(u'</svg>')
    return wrap(u'\n'.join(p),
                u'「256量子ビット」と「論理量子ビット256個」は、まったく違う話です。')


# ---------------------------------------------------------------- 図F 応酬
def fig_claim_rebuttal():
    """「できた」と「普通のパソコンでもできた」の応酬を、三つ並べる。

    本文が「この分野を理解するのにいちばん大事」と言っている節なのに、
    図がなかった。見出しだけ読むと左半分しか目に入らないことを見せる。

    改行は手で決める。文字数で折ると、枠からはみ出したり
    変なところで切れたりするため。
    """
    rows = [
        (u'2019', u'Google',
         [u'スパコンで1万年かかる計算を', u'200秒で解いた'],
         [u'IBM「工夫すれば2日半でできる」。', u'2022年、別の研究チームが',
          u'普通のコンピュータで実際に解いた']),
        (u'2023', u'IBM',
         [u'誤り訂正の前の段階でも', u'役に立つ証拠だ'],
         [u'数週間のうちに複数のチームが再現。', u'ひとつはノートパソコンの1コアで動き、',
          u'量子の実機より桁違いに速かった']),
        (u'2025', u'D-Wave',
         [u'科学誌に成果を発表'],
         [u'数日のうちに二つの研究機関が', u'「普通のコンピュータで再現できる」。',
          u'同社はさらに反論している']),
    ]
    h = 92 + 112 * len(rows) + 62
    p = []
    p.append(u'<svg viewBox="0 0 700 %d" role="img" aria-label="2019年のGoogle、'
             u'2023年のIBM、2025年のD-Waveの発表に対して、いずれも普通のコンピュータで'
             u'再現できるという反論が続いた。発表と検証と議論がくり返されている。" '
             u'style="max-width:100%%;height:auto;display:block;margin:0 auto">' % h)
    p.append(u'<defs><marker id="cr-ah" viewBox="0 0 10 10" refX="9" refY="5" '
             u'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
             u'<polygon points="0,1 10,5 0,9" fill="currentColor" opacity="0.5">'
             u'</polygon></marker></defs>')

    p.append(u'<text x="180" y="42" text-anchor="middle" font-size="16" '
             u'font-weight="bold" fill="%s">「できた」という発表</text>' % COPPER)
    p.append(u'<text x="502" y="42" text-anchor="middle" font-size="16" '
             u'font-weight="bold" fill="currentColor">'
             u'「普通のパソコンでもできた」</text>')
    p.append(u'<line x1="338" y1="58" x2="338" y2="%d" stroke="currentColor" '
             u'stroke-width="1" opacity="0.2"></line>' % (h - 76))

    y = 96
    for year, who, claim, back in rows:
        box_h = 34 + 19 * len(claim)
        p.append(u'<text x="30" y="%d" font-size="13.5" font-weight="bold" '
                 u'fill="currentColor" opacity="0.5">%s</text>' % (y + 22, year))
        p.append(u'<rect x="76" y="%d" width="250" height="%d" rx="6" fill="none" '
                 u'stroke="%s" stroke-width="2"></rect>' % (y, box_h, COPPER))
        p.append(u'<text x="90" y="%d" font-size="14" font-weight="bold" fill="%s">%s</text>'
                 % (y + 22, COPPER, who))
        for k, ln in enumerate(claim):
            p.append(u'<text x="90" y="%d" font-size="12.5" fill="currentColor">%s</text>'
                     % (y + 42 + k * 19, ln))
        p.append(u'<line x1="334" y1="%d" x2="358" y2="%d" stroke="currentColor" '
                 u'stroke-width="2" opacity="0.5" marker-end="url(#cr-ah)"></line>'
                 % (y + box_h / 2, y + box_h / 2))
        for k, ln in enumerate(back):
            p.append(u'<text x="370" y="%d" font-size="12.5" fill="currentColor">%s</text>'
                     % (y + 22 + k * 19, ln))
        y += 112

    p.append(u'<rect x="30" y="%d" width="640" height="44" rx="6" fill="none" '
             u'stroke="currentColor" stroke-width="1.5" opacity="0.4"></rect>' % (h - 58))
    p.append(u'<text x="350" y="%d" text-anchor="middle" font-size="14" '
             u'fill="currentColor">見出しに出るのは'
             u'<tspan font-weight="bold">左だけ</tspan>。'
             u'数週間後の右は、まず届きません</text>' % (h - 30))
    p.append(u'</svg>')
    return wrap(u'\n'.join(p),
                u'発表があり、検証があり、議論がある。'
                u'不正でも失敗でもなく、科学が正常に働いている姿です。')


# ---------------------------------------------------------------- 図G 実用化の見通し
def fig_when():
    """「いつ実用化されるのか」の答えの幅を、そのまま見せる。"""
    p = []
    p.append(u'<svg viewBox="0 0 700 330" role="img" aria-label="実用化の見通しは、'
             u'IBMとGoogleの目標が2029年、日本政府の暗号切り替えの目処が2035年、'
             u'国の研究目標ムーンショットが2050年、そして そもそも実現しないという'
             u'反対論まで、大きく開いている。" '
             u'style="max-width:100%;height:auto;display:block;margin:0 auto">')
    p.append(u'<text x="350" y="36" text-anchor="middle" font-size="16" '
             u'font-weight="bold" fill="currentColor">'
             u'「いつ実用化されるのか」の答えは、これだけ開いています</text>')

    marks = [(130, u'2029年', u'IBM・Googleの目標', u'会社の目標であって、予定ではない'),
             (330, u'2035年', u'国が暗号を切り替える目処', u'内閣官房。2026年度中に工程表'),
             (530, u'2050年', u'ムーンショット', u'誤りに強い汎用の機械の実現')]
    p.append(u'<line x1="90" y1="126" x2="600" y2="126" stroke="currentColor" '
             u'stroke-width="2" opacity="0.35"></line>')
    for x, yr, title, sub in marks:
        p.append(u'<line x1="%d" y1="114" x2="%d" y2="138" stroke="%s" '
                 u'stroke-width="2"></line>' % (x, x, COPPER))
        p.append(u'<text x="%d" y="104" text-anchor="middle" font-size="18" '
                 u'font-weight="bold" fill="%s">%s</text>' % (x, COPPER, yr))
        p.append(u'<text x="%d" y="162" text-anchor="middle" font-size="13.5" '
                 u'font-weight="bold" fill="currentColor">%s</text>' % (x, title))
        p.append(u'<text x="%d" y="182" text-anchor="middle" font-size="11.5" '
                 u'fill="currentColor" opacity="0.7">%s</text>' % (x, sub))

    p.append(u'<text x="628" y="132" font-size="22" fill="currentColor" '
             u'opacity="0.45">…</text>')
    p.append(u'<rect x="90" y="212" width="510" height="48" rx="6" fill="none" '
             u'stroke="currentColor" stroke-width="1.5" opacity="0.45"></rect>')
    p.append(u'<text x="345" y="242" text-anchor="middle" font-size="15" '
             u'fill="currentColor">そして「<tspan font-weight="bold">そもそも実現しない'
             u'</tspan>」とする物理学者の反対論もあります</text>')
    p.append(u'<text x="350" y="294" text-anchor="middle" font-size="13" '
             u'fill="currentColor">NVIDIAの最高経営責任者は、'
             u'<tspan font-weight="bold" fill="%s">2か月で見方を撤回</tspan>しました</text>'
             % COPPER)
    p.append(u'<text x="350" y="316" text-anchor="middle" font-size="12" '
             u'fill="currentColor" opacity="0.7">'
             u'「何年に実用化」と書いてある記事は、そのつもりで読んでください</text>')
    p.append(u'</svg>')
    return wrap(u'\n'.join(p),
                u'2029年から2050年、そして「来ない」まで。これが、いまの見通しの幅です。')


# ---------------------------------------------------------------- 図H いま盗んで、あとで読む
def fig_harvest_now():
    """なぜ機械がまだないのに、いま暗号を切り替えるのかを三つの段で見せる。"""
    steps = [
        (140, u'いま', u'鍵のかかった通信を、\nそのまま記録して保存する'),
        (350, u'何年も', u'解ける機械ができるまで、\n寝かせておく'),
        (560, u'そのあと', u'さかのぼって、\n中身を読む'),
    ]
    p = []
    p.append(u'<svg viewBox="0 0 700 300" role="img" aria-label="暗号化された通信を'
             u'いまのうちに記録して保存し、解読できる機械ができた時点でさかのぼって読む、'
             u'という考え方。だから機械がまだなくても、暗号の切り替えがすでに始まっている。" '
             u'style="max-width:100%;height:auto;display:block;margin:0 auto">')
    p.append(u'<defs><marker id="hn-ah" viewBox="0 0 10 10" refX="9" refY="5" '
             u'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
             u'<polygon points="0,1 10,5 0,9" fill="%s"></polygon></marker></defs>' % COPPER)
    p.append(u'<text x="350" y="36" text-anchor="middle" font-size="16" '
             u'font-weight="bold" fill="currentColor">'
             u'「いま盗んで、あとで読む」</text>')

    for i, (x, when, what) in enumerate(steps):
        p.append(u'<circle cx="%d" cy="104" r="34" fill="none" stroke="%s" '
                 u'stroke-width="2.5"></circle>' % (x, COPPER))
        p.append(u'<text x="%d" y="112" text-anchor="middle" font-size="24" '
                 u'font-weight="bold" fill="%s">%d</text>' % (x, COPPER, i + 1))
        p.append(u'<text x="%d" y="166" text-anchor="middle" font-size="14" '
                 u'font-weight="bold" fill="%s">%s</text>' % (x, COPPER, when))
        for k, ln in enumerate(what.split('\n')):
            p.append(u'<text x="%d" y="%d" text-anchor="middle" font-size="13" '
                     u'fill="currentColor">%s</text>' % (x, 190 + k * 20, ln))
        if i < len(steps) - 1:
            p.append(u'<line x1="%d" y1="104" x2="%d" y2="104" stroke="%s" '
                     u'stroke-width="2.5" marker-end="url(#hn-ah)"></line>'
                     % (x + 44, x + 166, COPPER))

    p.append(u'<line x1="60" y1="244" x2="640" y2="244" stroke="currentColor" '
             u'stroke-width="1" opacity="0.25"></line>')
    p.append(u'<text x="350" y="272" text-anchor="middle" font-size="15" '
             u'fill="currentColor">だから、機械がまだなくても'
             u'<tspan font-weight="bold">いま切り替えが始まっています</tspan>'
             u'（目処 2035年）</text>')
    p.append(u'</svg>')
    return wrap(u'\n'.join(p),
                u'解ける機械ができるのを待って、あとから読む。'
                u'この手口があるので、国はもう動き始めています。')


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
    ('article-01.html',
     u'<p class="has-medium-font-size">よく「0でもあり1でもある、不思議な状態」と説明されますが、この言い方だと<strong>向きの話がまるごと抜け落ちます。</strong>そして向きが抜けると、量子コンピュータが速い理由も、まるごと消えてしまうのです。</p>\n<!-- /wp:paragraph -->',
     fig_bit_vs_qubit),
    ('article-01.html',
     u'<p class="has-medium-font-size">正しくはこうです。<strong>その状態を普通のコンピュータで書き留めようとすると、それだけの本数の矢印を並べる必要がある</strong>、ということです。</p>\n<!-- /wp:paragraph -->',
     fig_doubling),
    ('article-01.html',
     u'<p class="has-medium-font-size">「量子コンピュータは絶対零度に冷やす機械です」と言い切ってしまうと、それは嘘になります。<strong>あの写真は、超電導方式のものです。</strong></p>\n<!-- /wp:paragraph -->',
     fig_temperature),
    ('article-01.html',
     u'<p class="has-medium-font-size">理由は単純です。離れた2つの量子ビットを測ると、必ず示し合わせたような結果になります。ところが<strong>その結果は、どちらの側でも決められない、でたらめな値</strong>なのです。決められないものは、合図に使えません。<strong>二人の目が揃っていたとわかるのは、あとで電話やメールなど普通の方法で結果を見せ合ったとき</strong>です。</p>\n<!-- /wp:paragraph -->',
     fig_entangle),
    ('article-01.html',
     u'<p class="has-medium-font-size">それを示す出来事があります。IBMは2023年に1,121量子ビットの機械を発表しましたが、その後、<strong>133量子ビットの機械を主力に切り替えました。</strong>数を減らしたのに、性能は上がっています。数ではなく質に舵を切ったのです。</p>\n<!-- /wp:paragraph -->',
     fig_logical_qubit),
    ('article-02.html',
     u'<p class="has-medium-font-size">誤解のないように申し添えます。<strong>これは不正でも失敗でもありません。科学が正常に働いている姿です。</strong>発表があり、検証があり、議論がある。そうやって確かなことが積み上がっていきます。</p>\n<!-- /wp:paragraph -->',
     fig_claim_rebuttal),
    ('article-02.html',
     u'<p class="has-medium-font-size">業界の第一人者ですら、2か月で見方が変わります。<strong>「何年に実用化」と書いてある記事は、そのつもりで読んでください。</strong></p>\n<!-- /wp:paragraph -->',
     fig_when),
    ('article-02.html',
     u'<p class="has-medium-font-size">そして2025年11月20日、内閣官房の国家サイバー統括室が、政府機関などの暗号を新しい方式（<strong>耐量子計算機暗号</strong>）へ切り替える方針をまとめました。<strong>目処は、原則2035年。</strong>2026年度中に工程表を作るとされています。</p>\n<!-- /wp:paragraph -->',
     fig_harvest_now),
]

for fname, anchor, maker in INSERTS:
    path = os.path.join(HERE, fname)
    t = io.open(path, encoding='utf-8').read()
    block = maker()
    # 二度流しても重ねない。図ごとの読み上げ文の頭を目印にする。
    # 先に「もう入っているか」を見ること。差し込み先の文はあとから
    # 言い換えることがあり、入っているのに止まってしまうため。
    key = block[block.index('aria-label="') + 12:][:40]
    if key in t:
        print(u'－ %s には、この図がすでにあります（何もしません）' % fname)
        continue
    if t.count(anchor) != 1:
        sys.stderr.write('× 差し込み先が %d 件（1件でないと止めます）: %s\n'
                         % (t.count(anchor), fname))
        sys.exit(1)
    t = t.replace(anchor, anchor + u'\n\n' + block)
    io.open(path, 'w', encoding='utf-8').write(t)
    print(u'○ %s に図を1枚 差し込みました' % fname)
