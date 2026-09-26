# -*- coding: utf-8 -*-
F = {}
TONE = {'g':('#eaf5ee','#186b3f','gr'),'a':('#fdf4e2','#8a6100','am'),
        'r':('#fbecea','#a8261c','rd'),'n':('#f2f5f8','#98a5b0','gy'),
        'b':('#e6edf4','#2a5c8a','n2')}

# ---------- 図5  親会社が登録した場合・しない場合 ----------
def cmp_panel(px, hdrfill, hdr, nodes, notes, vtitle, vlines, vtone):
    t = TONE[vtone]
    s = ['<rect x="%d" y="0" width="490" height="314" rx="3" fill="#ffffff" stroke="#c9d3dc"/>' % px,
         '<rect x="%d" y="0" width="490" height="30" rx="3" fill="%s"/>' % (px, hdrfill),
         '<rect x="%d" y="16" width="490" height="14" fill="%s"/>' % (px, hdrfill),
         '<text class="b w" x="%d" y="21" font-size="16">%s</text>' % (px+13, hdr)]
    ys = [40, 96, 152]
    for i, (l1, l2, fill, stroke, cls) in enumerate(nodes):
        y = ys[i]
        s.append('<rect x="%d" y="%d" width="228" height="42" rx="3" fill="%s" stroke="%s" stroke-width="1.4"/>' % (px+13, y, fill, stroke))
        s.append('<text class="b %s" x="%d" y="%d" font-size="14.5" text-anchor="middle">%s</text>' % (cls, px+127, y+18, l1))
        s.append('<text class="%s" x="%d" y="%d" font-size="12" text-anchor="middle">%s</text>' % (cls, px+127, y+34, l2))
        if i < 2:
            s.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#2a5c8a" stroke-width="1.4" marker-end="url(#fa5)"/>' % (px+127, y+42, px+127, y+52))
    for i, nt in enumerate(notes):
        s.append('<text class="gy" x="%d" y="%d" font-size="12.5">%s</text>' % (px+250, 62+i*56, nt[0]))
        s.append('<text class="gy" x="%d" y="%d" font-size="12.5">%s</text>' % (px+250, 78+i*56, nt[1]))
    s.append('<rect x="%d" y="204" width="464" height="98" rx="3" fill="%s" stroke="%s" stroke-width="1.2"/>' % (px+13, t[0], t[1]))
    s.append('<text class="b %s" x="%d" y="224" font-size="15">%s</text>' % (t[2], px+26, vtitle))
    for i, ln in enumerate(vlines):
        s.append('<text x="%d" y="%d" font-size="12.5">・%s</text>' % (px+26, 245+i*18, ln))
    return '\n    '.join(s)

F['fig5'] = '''<figure class="fig">
  <div class="figt">図5　親会社が第一種登録を取ると、何が変わるか</div>
  <svg viewBox="0 0 1000 316" role="img" aria-label="親会社の登録の有無による比較">
    <defs><marker id="fa5" markerWidth="9" markerHeight="7" refX="8.5" refY="3.5" orient="auto">
      <path d="M0,0 L9,3.5 L0,7 z" fill="#2a5c8a"/></marker></defs>
    ''' + cmp_panel(0, '#186b3f', '登録しない（現状のまま）',
        [('株式会社石名坂', '真荷主（運送業の許可なし）', '#ffffff', '#2a5c8a', 'n2'),
         ('有限会社石名坂商事（緑）', '元請運送事業者', '#16395c', '#16395c', 'w'),
         ('丸幸運輸（緑）・高新建材（緑）', '実運送（1次請け）', '#ffffff', '#186b3f', 'gr')],
        [('運送契約', '法12条・書面の相互交付'), ('利用運送契約', '法24条2項・一方向交付')],
        '親会社のコストはゼロ',
        ['管理簿・書面の作成義務者は当社（元請）のまま',
         '親会社は荷主として法12条・64条・65条・65条の2の対象',
         '運送人としての責任は負わない（売買上の引渡義務のみ）',
         '事業報告書・事業実績報告書の提出義務もない'], 'g') + '''
    ''' + cmp_panel(510, '#a8261c', '登録する（＝貨物利用運送事業者になる）',
        [('株式会社石名坂', '第一種貨物利用運送事業者', '#fbecea', '#a8261c', 'rd'),
         ('有限会社石名坂商事（緑）', '実運送（下請）', '#16395c', '#16395c', 'w'),
         ('丸幸運輸（緑）・高新建材（緑）', '実運送（2次請け）', '#ffffff', '#186b3f', 'gr')],
        [('運送契約（親会社が運送人）', '法37条→24条2項の一方向交付'), ('', '')],
        '得るものがなく、体制が崩れます',
        ['登録免許税9万円／基準資産300万円以上／標準処理期間2〜3か月',
         '親会社に法24条2項の書面交付・実運送体制管理簿の義務が発生',
         '親会社は真荷主でなくなり、真荷主のいない取引になる（12条2項）',
         '運送人として一次責任。貨物賠償責任保険（利用運送特約）が必須'], 'r') + '''
  </svg>
  <div class="figc">自社の砕石を届けるために運送を委託する行為は、<strong>登録がなくても利用運送事業に当たりません</strong>。登録は推奨しません。</div>
</figure>
'''

# ---------- 図6  着手スケジュール ----------
X0, XW = 352, 640          # timeline area
def mx(m): return X0 + m*(XW/6.0)
def gbar(y, m1, m2, fill, hatch=False, op=1.0):
    x1, x2 = mx(m1), mx(m2)
    f = 'url(#hat)' if hatch else fill
    return '<rect x="%.1f" y="%d" width="%.1f" height="17" rx="2" fill="%s" opacity="%.2f"/>' % (x1, y, max(x2-x1, 5), f, op)

def grow(i, label, bars, note=''):
    y = 60 + i*32
    s = ['<text x="14" y="%d" font-size="13.5">%s</text>' % (y+13, label)]
    s += bars
    if note:
        s.append('<text class="gy" x="%.1f" y="%d" font-size="11.5">%s</text>' % (note[0], y+13, note[1]))
    return '\n    '.join(s)

F['fig6'] = '''<figure class="fig">
  <div class="figt">図6　着手スケジュール ― 不足が起きてからでは間に合いません</div>
  <svg viewBox="0 0 1000 332" role="img" aria-label="着手スケジュール">
    <defs><pattern id="hat" width="7" height="7" patternTransform="rotate(45)" patternUnits="userSpaceOnUse">
      <rect width="7" height="7" fill="#dfe7ee"/><line x1="0" y1="0" x2="0" y2="7" stroke="#16395c" stroke-width="2.4"/></pattern></defs>
    <line x1="%d" y1="46" x2="1000" y2="46" stroke="#c9d3dc"/>
    %s
    ''' % (X0, '\n    '.join(
        ['<line x1="%.1f" y1="40" x2="%.1f" y2="304" stroke="#e3e9ee"/>' % (mx(m), mx(m)) for m in range(7)] +
        ['<text class="gy" x="%.1f" y="34" font-size="12.5" text-anchor="%s">%s</text>'
         % (mx(m), 'end' if m == 6 else 'middle', ['今すぐ','1か月','2か月','3か月','4か月','5か月','6か月'][m]) for m in range(7)])) + '''
    ''' + grow(0, '① 傭車先の許可証を徴求　② 事業計画の確認', [gbar(60, 0, 0.3, '#a8261c')], (mx(0.35), '罰則リスクが最大')) + '''
    ''' + grow(1, '③ 運送約款の確認', [gbar(92, 0, 0.4, '#8a6100'), gbar(92, 0.4, 2.4, '', True)], (mx(2.5), '独自約款なら変更認可2か月')) + '''
    ''' + grow(2, '④ 運輸支局へ照会（Q1〜Q12）', [gbar(124, 0, 0.5, '#8a6100')], (mx(0.6), 'Q5は事業継続に直結')) + '''
    ''' + grow(3, '⑤ 傭車先と基本契約書を締結（様式2）', [gbar(156, 0.3, 1.0, '#2a5c8a')], (mx(1.1), '様式1の必須添付書類')) + '''
    ''' + grow(4, '⑥ 事業計画変更認可を申請（様式1）', [gbar(188, 1.0, 1.3, '#16395c')], '') + '''
    ''' + grow(5, '⑦ 標準処理期間 1〜4か月　★ここが読めない', [gbar(220, 1.3, 2.3, '#16395c'), gbar(220, 2.3, 5.3, '', True)], '') + '''
    ''' + grow(6, '⑧ 法定書面の運用開始（様式3・4・5）', [gbar(252, 5.3, 6.0, '#186b3f')], '') + '''
    ''' + grow(7, '⑩⑪ ダンプ5台の点検・過積載防止体制', [gbar(284, 0, 3.0, '#186b3f', op=0.55)], '') + '''
    <line x1="%.1f" y1="216" x2="%.1f" y2="304" stroke="#a8261c" stroke-width="1.6" stroke-dasharray="4 3"/>
    <text class="b rd" x="%.1f" y="324" font-size="13" text-anchor="end">← 認可が下りるまで傭車は出せません</text>
  </svg>
  <div class="figc">事業計画に「貨物自動車利用運送＝行う」の記載がなければ、<strong>相手が緑ナンバーでも明日は出せません</strong>。標準処理期間は1〜4か月で、その日に間に合わせる方法はありません。</div>
</figure>
''' % (mx(5.3), mx(5.3), mx(5.25))

# ---------- 図7  配車の組み立て ----------
def truck(x, y, col, fill, cross=False):
    g = ['<g transform="translate(%d,%d)">' % (x, y),
         '<rect x="0" y="2" width="56" height="24" rx="2" fill="%s" stroke="%s" stroke-width="1.5"/>' % (fill, col),
         '<path d="M58,9 L76,9 L84,19 L84,26 L58,26 z" fill="%s" stroke="%s" stroke-width="1.5"/>' % (fill, col),
         '<circle cx="17" cy="31" r="6" fill="#ffffff" stroke="%s" stroke-width="1.6"/>' % col,
         '<circle cx="44" cy="31" r="6" fill="#ffffff" stroke="%s" stroke-width="1.6"/>' % col,
         '<circle cx="72" cy="31" r="6" fill="#ffffff" stroke="%s" stroke-width="1.6"/>' % col]
    if cross:
        g.append('<path d="M6,4 L80,36 M80,4 L6,36" stroke="#a8261c" stroke-width="2.6" opacity="0.85"/>')
    g.append('</g>')
    return ''.join(g)

def fleet(x0, n, col, fill, cross=False):
    return '\n    '.join(truck(x0 + i*96, 88, col, fill, cross) for i in range(n))

def grp(x1, x2, title, sub, cls):
    cx = (x1+x2)/2.0
    return '\n    '.join([
      '<path d="M%d,76 L%d,70 L%d,70 L%d,76" fill="none" stroke="#98a5b0" stroke-width="1.2"/>' % (x1, x1, x2, x2),
      '<text class="b %s" x="%.1f" y="62" font-size="15" text-anchor="middle">%s</text>' % (cls, cx, title),
      '<text class="gy" x="%.1f" y="146" font-size="12.5" text-anchor="middle">%s</text>' % (cx, sub)])

F['fig7'] = '''<figure class="fig">
  <div class="figt">図7　8運行をどう割り振るか ― ダンプが3台足りない日</div>
  <svg viewBox="0 0 1000 262" role="img" aria-label="配車の組み立て">
    <rect x="0" y="0" width="1000" height="34" rx="3" fill="#16395c"/>
    <text class="b w" x="14" y="22" font-size="15">株式会社石名坂（真荷主）からの依頼 ― ○○道路改良工事現場へ 砕石 8台分。自社の大型ダンプは5台。3台足りない。</text>
    ''' + fleet(16, 5, '#16395c', '#dbe3ea') + '''
    ''' + fleet(524, 2, '#186b3f', '#eaf5ee') + '''
    ''' + fleet(716, 1, '#186b3f', '#eaf5ee') + '''
    ''' + grp(16, 484, '有限会社石名坂商事（緑）　5運行', '元請＝自社実運送。利用運送ではない', 'nv') + '''
    ''' + grp(524, 704, '丸幸運輸（緑）　2運行', '1次請け＝貨物自動車利用運送', 'gr') + '''
    ''' + grp(716, 800, '高新建材（緑）　1運行', '1次請け＝同上', 'gr') + '''
    <line x1="504" y1="52" x2="504" y2="150" stroke="#c9d3dc" stroke-dasharray="3 3"/>
    <rect x="0" y="166" width="1000" height="96" rx="3" fill="#fbecea" stroke="#a8261c" stroke-width="1.2"/>
    ''' + truck(20, 186, '#a8261c', '#f3e3e1', True) + truck(124, 186, '#a8261c', '#f3e3e1', True) + '''
    <text class="gy" x="20" y="250" font-size="12.5">沢口砂利店（白）・熊谷砂利店（白）</text>
    <text class="b rd" x="240" y="196" font-size="16">0運行 ― 白ナンバーには委託できません</text>
    <text class="rd" x="240" y="218" font-size="13.5">貨運法65条の2。違反は100万円以下の罰金（75条14号）、法人にも両罰（80条）</text>
    <text class="gy" x="240" y="240" font-size="13">判断材料は社名ではなく、①一般貨物自動車運送事業許可書　②車検証の「自家用・事業用の別」欄の2つだけです。</text>
  </svg>
  <div class="figc">「建材」と付いていても緑ナンバー、「運輸」と付いていても白ナンバーということがあります。<strong>社名からは判断できません。</strong></div>
</figure>
'''

# ---------- 図8  その日に交わす書面 ----------
LX = {1: 168, 2: 500, 3: 832}
def msg(y, a, b, label, sub, tone='b', back=False):
    t = TONE[tone]
    x1, x2 = LX[a], LX[b]
    d = -1 if x2 < x1 else 1
    s = ['<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="1.6" marker-end="url(#fa8%s)"/>' % (x1+12*d, y, x2-14*d, y, t[1], t[2])]
    cx = (x1+x2)/2.0
    s.append('<text class="b %s" x="%.1f" y="%d" font-size="14" text-anchor="middle">%s</text>' % (t[2], cx, y-9, label))
    s.append('<text class="gy" x="%.1f" y="%d" font-size="12" text-anchor="middle">%s</text>' % (cx, y+17, sub))
    return '\n    '.join(s)

F['fig8'] = '''<figure class="fig">
  <div class="figt">図8　その日に交わす書面 ― ①から⑤までの流れと向き</div>
  <svg viewBox="0 0 1000 322" role="img" aria-label="書面の流れ">
    <defs>
      <marker id="fa8n2" markerWidth="10" markerHeight="8" refX="9.5" refY="4" orient="auto"><path d="M0,0 L10,4 L0,8 z" fill="#2a5c8a"/></marker>
      <marker id="fa8gr" markerWidth="10" markerHeight="8" refX="9.5" refY="4" orient="auto"><path d="M0,0 L10,4 L0,8 z" fill="#186b3f"/></marker>
      <marker id="fa8am" markerWidth="10" markerHeight="8" refX="9.5" refY="4" orient="auto"><path d="M0,0 L10,4 L0,8 z" fill="#8a6100"/></marker>
    </defs>
    <rect x="18" y="0" width="300" height="46" rx="3" fill="#ffffff" stroke="#2a5c8a" stroke-width="1.4"/>
    <text class="b n2" x="168" y="20" font-size="15" text-anchor="middle">株式会社石名坂（真荷主）</text>
    <text class="gy" x="168" y="37" font-size="12" text-anchor="middle">発注者・砕石の売主</text>
    <rect x="350" y="0" width="300" height="46" rx="3" fill="#16395c"/>
    <text class="b w" x="500" y="20" font-size="15" text-anchor="middle">有限会社石名坂商事（緑）</text>
    <text class="w" x="500" y="37" font-size="12" text-anchor="middle" opacity="0.85">元請運送事業者</text>
    <rect x="682" y="0" width="300" height="46" rx="3" fill="#ffffff" stroke="#186b3f" stroke-width="1.4"/>
    <text class="b gr" x="832" y="20" font-size="15" text-anchor="middle">丸幸運輸（緑）・高新建材（緑）</text>
    <text class="gy" x="832" y="37" font-size="12" text-anchor="middle">実運送事業者（1次請け）</text>
    <line x1="168" y1="46" x2="168" y2="300" stroke="#c9d3dc" stroke-dasharray="4 4"/>
    <line x1="500" y1="46" x2="500" y2="300" stroke="#c9d3dc" stroke-dasharray="4 4"/>
    <line x1="832" y1="46" x2="832" y2="300" stroke="#c9d3dc" stroke-dasharray="4 4"/>
    <text class="b n2" x="26" y="84" font-size="15">①</text>
    ''' + msg(84, 1, 2, '運送申込書', '貨運法12条1項／標準約款6条') + '''
    <text class="b n2" x="26" y="134" font-size="15">②</text>
    ''' + msg(134, 2, 1, '運送引受書', '貨運法12条1項／標準約款7条') + '''
    <text class="b am" x="26" y="184" font-size="15">③</text>
    ''' + msg(184, 2, 1, '利用運送を行う旨の事前通知', '標準約款17条（令和6年告示第210号・R6.6.1施行）', 'a') + '''
    <text class="b gr" x="26" y="234" font-size="15">④</text>
    ''' + msg(234, 2, 3, '運送委託書（元請連絡事項を含む）', '貨運法24条2項・24条の5第2項', 'g') + '''
    <text class="b nv" x="26" y="284" font-size="15">⑤</text>
    <path d="M500,272 L572,272 L572,292 L514,292" fill="none" stroke="#16395c" stroke-width="1.6" marker-end="url(#fa8n2)"/>
    <text class="b nv" x="586" y="278" font-size="14">実運送体制管理簿（自社で作成・保存）</text>
    <text class="gy" x="586" y="295" font-size="12">貨運法24条の5第1項。砕石は全運行が1.5トン基準を超えるので全件が対象</text>
    <rect x="18" y="306" width="470" height="16" fill="none"/>
    <text class="gy" x="18" y="318" font-size="12">①② は相互交付なので<tspan class="b nv">往復方式で足ります</tspan>（Q&amp;A 問2-22）</text>
    <text class="gy" x="510" y="318" font-size="12">④ は<tspan class="b rd">往復方式が認められません</tspan>。一方向で法定事項を網羅した書面を交付</text>
  </svg>
</figure>
'''

# ---------- 図9  引取販売 ----------
def trade(px, hdrfill, hdr, n3, money, vt, vl1, vl2, vtone):
    t = TONE[vtone]
    cxs = [px+77, px+245, px+413]
    s = ['<rect x="%d" y="0" width="490" height="316" rx="3" fill="#ffffff" stroke="#c9d3dc"/>' % px,
         '<rect x="%d" y="0" width="490" height="30" rx="3" fill="%s"/>' % (px, hdrfill),
         '<rect x="%d" y="16" width="490" height="14" fill="%s"/>' % (px, hdrfill),
         '<text class="b w" x="%d" y="21" font-size="15.5">%s</text>' % (px+13, hdr)]
    nodes = [('株式会社石名坂', '砕石の売主', '#e6edf4', '#2a5c8a', 'n2'),
             ('沢口砂利店（白）', '白ナンバー・砂利店', '#f2f5f8', '#98a5b0', 'nv'), n3]
    for i, (l1, l2, f, st, cl) in enumerate(nodes):
        x = px + 13 + i*168
        s.append('<rect x="%d" y="52" width="128" height="46" rx="3" fill="%s" stroke="%s" stroke-width="1.4"/>' % (x, f, st))
        s.append('<text class="b %s" x="%d" y="72" font-size="13" text-anchor="middle">%s</text>' % (cl, x+64, l1))
        s.append('<text class="gy" x="%d" y="89" font-size="11" text-anchor="middle">%s</text>' % (x+64, l2))
    for i in (0, 1):
        x1, x2 = cxs[i]+68, cxs[i+1]-68
        s.append('<line x1="%d" y1="75" x2="%d" y2="75" stroke="#16395c" stroke-width="2.2" marker-end="url(#fa9n)"/>' % (x1, x2-2))
        s.append('<text class="b nv" x="%d" y="66" font-size="11" text-anchor="middle">砕石</text>' % ((x1+x2)//2))
    s += money
    s.append('<rect x="%d" y="210" width="464" height="92" rx="3" fill="%s" stroke="%s" stroke-width="1.2"/>' % (px+13, t[0], t[1]))
    s.append('<text class="b %s" x="%d" y="234" font-size="16">%s</text>' % (t[2], px+26, vt))
    s.append('<text x="%d" y="258" font-size="12.5">%s</text>' % (px+26, vl1))
    s.append('<text class="gy" x="%d" y="278" font-size="11.5">%s</text>' % (px+26, vl2))
    s.append('<text class="gy" x="%d" y="294" font-size="11.5">%s</text>' % (px+26, vl2b(vtone)))
    return '\n    '.join(s)

def vl2b(tone):
    return ''

def mflow(x1, x2, y, lab, tone='g'):
    t = TONE[tone]
    return ('<path d="M%d,%d L%d,%d" stroke="%s" stroke-width="1.6" stroke-dasharray="5 3" marker-end="url(#fa9%s)"/>\n    '
            '<text class="b %s" x="%d" y="%d" font-size="11.5" text-anchor="middle">%s</text>') % (
            x1, y, x2, y, t[1], t[2], t[2], (x1+x2)//2, y-7, lab)

F['fig9'] = '''<figure class="fig">
  <div class="figt">図9　引取販売 ― 適法な形と、違法な買い戻し（実線＝物の流れ／破線＝お金の流れ）</div>
  <svg viewBox="0 0 1000 318" role="img" aria-label="引取販売の適法・違法">
    <defs>
      <marker id="fa9n" markerWidth="9" markerHeight="7" refX="8.5" refY="3.5" orient="auto"><path d="M0,0 L9,3.5 L0,7 z" fill="#16395c"/></marker>
      <marker id="fa9gr" markerWidth="9" markerHeight="7" refX="8.5" refY="3.5" orient="auto"><path d="M0,0 L9,3.5 L0,7 z" fill="#186b3f"/></marker>
      <marker id="fa9rd" markerWidth="9" markerHeight="7" refX="8.5" refY="3.5" orient="auto"><path d="M0,0 L9,3.5 L0,7 z" fill="#a8261c"/></marker>
    </defs>
    ''' + trade(0, '#186b3f', 'パターン1 ― 沢口が現場の相手に自分で売る',
        ('現場の元請・施主', '買主', '#eaf5ee', '#186b3f', 'gr'),
        [mflow(237, 85, 134, '仕入代金 2,000円／t'),
         mflow(405, 253, 176, '売買代金（着地渡し）5,100円／t')],
        '○ 適法', '沢口砂利店（白）は自分が買った荷物を自分のダンプで運んでいる',
        '＝自家輸送。貨運法2条1項・2項の「他人の需要に応じ、有償で」に当たらない', 'g') + '''
    ''' + trade(510, '#a8261c', 'パターン2 ― 沢口が石名坂に売り戻す',
        ('石名坂の現場', '納入先は石名坂', '#fbecea', '#a8261c', 'rd'),
        [mflow(747, 595, 134, '仕入代金', 'r'),
         mflow(595, 747, 176, '石名坂から沢口へ支払（差額＝運賃）', 'r')],
        '× 違法', '一周した差額は運賃以外の何物でもない。売主は最初から最後まで石名坂',
        '石名坂＝65条の2（100万円以下の罰金）／沢口＝3条違反（3年以下の拘禁刑等）', 'r') + '''
    <text class="gy" x="253" y="200" font-size="11" text-anchor="middle">代金は現場から沢口へ入る</text>
    <text class="rd" x="763" y="200" font-size="11" text-anchor="middle">現場に納入し請求するのは石名坂のまま</text>
  </svg>
  <div class="figc">見分ける3つのテスト ― <strong>①現場に請求書を出すのは誰か　②石名坂から沢口へお金が流れていないか　③沢口の粗利が運賃表と一致していないか</strong>。差額3,100円／tが運賃単価とぴたり同じなら、それは商売差益ではなく運賃です。</div>
</figure>
'''

# ---------- 図10  労働者性の分水嶺 ----------
def wrow(i, factor, left, right):
    y = 44 + i*50
    return '\n    '.join([
      '<rect x="372" y="%d" width="256" height="44" rx="3" fill="#f2f5f8" stroke="#dde4ea"/>' % y,
      '<text class="b nv" x="500" y="%d" font-size="13.5" text-anchor="middle">%s</text>' % (y+27, factor),
      '<rect x="0" y="%d" width="360" height="44" rx="3" fill="#fbecea" stroke="#e5c6c2"/>' % y,
      '<text class="rd" x="348" y="%d" font-size="13" text-anchor="end">%s</text>' % (y+27, left),
      '<rect x="640" y="%d" width="360" height="44" rx="3" fill="#eaf5ee" stroke="#c4dece"/>' % y,
      '<text class="gr" x="652" y="%d" font-size="13">%s</text>' % (y+27, right)])

F['fig10'] = '''<figure class="fig">
  <div class="figt">図10　車持ち運転手の労働者性 ― どちらに寄っているか</div>
  <svg viewBox="0 0 1000 348" role="img" aria-label="労働者性の判断要素">
    <rect x="0" y="0" width="360" height="34" rx="3" fill="#a8261c"/>
    <text class="b w" x="180" y="22" font-size="15" text-anchor="middle">← 労働者と評価される方向</text>
    <rect x="372" y="0" width="256" height="34" rx="3" fill="#16395c"/>
    <text class="b w" x="500" y="22" font-size="15" text-anchor="middle">判断要素</text>
    <rect x="640" y="0" width="360" height="34" rx="3" fill="#186b3f"/>
    <text class="b w" x="820" y="22" font-size="15" text-anchor="middle">独立の事業者と評価される方向 →</text>
    ''' + wrow(0, '車両の所有名義', '会社名義・会社からのリース', '本人所有') + '''
    ''' + wrow(1, '費用負担', '会社が事後的に求めた／給与天引き', '本人の事業判断で負担') + '''
    ''' + wrow(2, '他社の仕事', 'できない（専属・諾否の自由なし）', 'できる実態がある') + '''
    ''' + wrow(3, '報酬の決め方', '時間単位・日単位（日額○万円）', '出来高（運行あたり・トンあたり）') + '''
    ''' + wrow(4, '指示の範囲', 'ルート・出発時刻・契約外の雑務', '品物・届け先・納入時刻のみ') + '''
    <rect x="0" y="296" width="360" height="46" rx="3" fill="#ffffff" stroke="#a8261c" stroke-width="1.2"/>
    <text class="b rd" x="180" y="315" font-size="13.5" text-anchor="middle">日興運送事件・東陽ガス事件</text>
    <text class="gy" x="180" y="333" font-size="12" text-anchor="middle">東京地判平24.1.27／平25.10.24　いずれも肯定</text>
    <rect x="372" y="296" width="256" height="46" rx="3" fill="#fdf4e2" stroke="#8a6100" stroke-width="1.2"/>
    <text class="b am" x="500" y="315" font-size="13.5" text-anchor="middle">★中間がいちばん危ない</text>
    <text class="am" x="500" y="333" font-size="12" text-anchor="middle">どちらかにはっきり寄せる</text>
    <rect x="640" y="296" width="360" height="46" rx="3" fill="#ffffff" stroke="#186b3f" stroke-width="1.2"/>
    <text class="b gr" x="820" y="315" font-size="13.5" text-anchor="middle">旭紙業事件</text>
    <text class="gy" x="820" y="333" font-size="12" text-anchor="middle">最一小判平8.11.28　否定。ただし一審は肯定した事例判断</text>
  </svg>
  <div class="figc">★運送業特有の決定打 ― <strong>その運転手の車を当社の事業用自動車として事業計画に登載しているか</strong>。登載して運行させれば輸送安全規則7条の点呼対象となり、拘束性と指揮監督を強く裏づけます。</div>
</figure>
'''
