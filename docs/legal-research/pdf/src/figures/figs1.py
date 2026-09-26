# -*- coding: utf-8 -*-
F = {}

# ---------- 図1  3軸の正常配置 ----------
def row(y, num, title, sub, owner, l1, l2, col):
    cols = {1:(248,240,368), 2:(500,240,620), 3:(752,240,872)}
    c = {'g':('#eaf5ee','#186b3f','gr'),'n':('#e6edf4','#2a5c8a','n2')}[col]
    s = ['<rect x="0" y="%d" width="236" height="66" rx="3" fill="#ffffff" stroke="#c9d3dc"/>' % y,
         '<text class="b nv" x="14" y="%d" font-size="17">%s　%s</text>' % (y+26, num, title),
         '<text class="gy" x="14" y="%d" font-size="13.5">%s</text>' % (y+48, sub)]
    for k,(x,w,cx) in cols.items():
        if k == owner:
            s.append('<rect x="%d" y="%d" width="%d" height="54" rx="3" fill="%s" stroke="%s" stroke-width="1.4"/>' % (x, y+6, w, c[0], c[1]))
            s.append('<text class="b %s" x="%d" y="%d" font-size="16" text-anchor="middle">%s</text>' % (c[2], cx, y+29, l1))
            s.append('<text class="%s" x="%d" y="%d" font-size="13" text-anchor="middle">%s</text>' % (c[2], cx, y+48, l2))
        else:
            s.append('<rect x="%d" y="%d" width="%d" height="54" rx="3" fill="#fafbfc" stroke="#e6ebf0"/>' % (x, y+6, w))
            s.append('<text class="gy" x="%d" y="%d" font-size="15" text-anchor="middle">―</text>' % (cx, y+39))
    return '\n    '.join(s)

F['fig1'] = '''<figure class="fig">
  <div class="figt">図1　適法な傭車の形 ― 「①は自社／②③は相手方」で完全に揃っている</div>
  <svg viewBox="0 0 1000 374" role="img" aria-label="傭車の3軸配置図">
    <defs><marker id="fa1" markerWidth="10" markerHeight="8" refX="9.5" refY="4" orient="auto">
      <path d="M0,0 L10,4 L0,8 z" fill="#2a5c8a"/></marker></defs>
    <rect x="0" y="0" width="236" height="48" rx="3" fill="#f2f5f8" stroke="#c9d3dc"/>
    <text class="b nv" x="118" y="30" font-size="18" text-anchor="middle">3つの軸</text>
    <rect x="248" y="0" width="240" height="48" rx="3" fill="#ffffff" stroke="#2a5c8a" stroke-width="1.4"/>
    <text class="b n2" x="368" y="21" font-size="17" text-anchor="middle">真荷主（発注者）</text>
    <text class="gy" x="368" y="39" font-size="13.5" text-anchor="middle">株式会社石名坂（運送業なし）</text>
    <rect x="500" y="0" width="240" height="48" rx="3" fill="#16395c"/>
    <text class="b w" x="620" y="21" font-size="17" text-anchor="middle">当社（元請）</text>
    <text class="w" x="620" y="39" font-size="13.5" text-anchor="middle" opacity="0.88">有限会社石名坂商事（緑）</text>
    <rect x="752" y="0" width="240" height="48" rx="3" fill="#ffffff" stroke="#186b3f" stroke-width="1.4"/>
    <text class="b gr" x="872" y="21" font-size="17" text-anchor="middle">傭車先（実運送）</text>
    <text class="gy" x="872" y="39" font-size="13.5" text-anchor="middle">丸幸運輸（緑）・高新建材（緑）</text>
    <text class="n2" x="494" y="70" font-size="13.5" text-anchor="middle">運送契約（法12条・書面の相互交付）</text>
    <line x1="380" y1="84" x2="606" y2="84" stroke="#2a5c8a" stroke-width="1.6" marker-end="url(#fa1)"/>
    <text class="n2" x="748" y="70" font-size="13.5" text-anchor="middle">利用運送契約（法24条2項・一方向交付）</text>
    <line x1="632" y1="84" x2="858" y2="84" stroke="#2a5c8a" stroke-width="1.6" marker-end="url(#fa1)"/>
    ''' + row(102, '①', '運送責任', '荷主に運送債務を負うのは誰か', 2, '当社が負う', '＝これが「利用運送」', 'n') + '''
    ''' + row(176, '②', '指揮命令・運行管理', '運転者に指示を出すのは誰か', 3, '傭車先が行う', '点呼・日報・労働時間の管理', 'g') + '''
    ''' + row(250, '③', '車両の使用権原', '車検証の使用者は誰か', 3, '傭車先の緑ナンバー', '運行供用者も傭車先', 'g') + '''
    <rect x="0" y="328" width="324" height="46" rx="3" fill="#fbecea" stroke="#a8261c"/>
    <text class="b rd" x="162" y="347" font-size="14.5" text-anchor="middle">② が当社にずれる</text>
    <text class="rd" x="162" y="365" font-size="13" text-anchor="middle">→ 偽装請負・労働者供給</text>
    <rect x="338" y="328" width="324" height="46" rx="3" fill="#fbecea" stroke="#a8261c"/>
    <text class="b rd" x="500" y="347" font-size="14.5" text-anchor="middle">③ が当社にずれる</text>
    <text class="rd" x="500" y="365" font-size="13" text-anchor="middle">→ 名義貸し（貨運法28条）</text>
    <rect x="676" y="328" width="324" height="46" rx="3" fill="#fdf4e2" stroke="#8a6100"/>
    <text class="b am" x="838" y="347" font-size="14.5" text-anchor="middle">① が傭車先にずれる</text>
    <text class="am" x="838" y="365" font-size="13" text-anchor="middle">→ 単なる紹介（無規制）</text>
  </svg>
  <div class="figc">3つのうち<strong>どれか一つでも本来と違う側にある</strong>と、別の法律関係に変わります。現場で確認するのはこの3点だけです。</div>
</figure>
'''

# ---------- 図2  正常形と3つの崩れ方 ----------
def panel(px, py, hdrfill, hdr, own, v1, v2, vcol):
    """own: dict col->list of (num, ok)  col1=荷主 col2=当社 col3=傭車先"""
    cx = {1: px+86, 2: px+244, 3: px+402}
    s = ['<rect x="%d" y="%d" width="488" height="176" rx="3" fill="#ffffff" stroke="#c9d3dc"/>' % (px, py),
         '<rect x="%d" y="%d" width="488" height="30" rx="3" fill="%s"/>' % (px, py, hdrfill),
         '<rect x="%d" y="%d" width="488" height="14" fill="%s"/>' % (px, py+16, hdrfill),
         '<text class="b w" x="%d" y="%d" font-size="16">%s</text>' % (px+13, py+21, hdr)]
    for k, lab in ((1, '荷主'), (2, '当社（緑）'), (3, '傭車先（緑）')):
        x = px + 12 + (k-1)*158
        s.append('<rect x="%d" y="%d" width="148" height="26" rx="3" fill="#f2f5f8" stroke="#dde4ea"/>' % (x, py+42))
        s.append('<text class="nv" x="%d" y="%d" font-size="13.5" text-anchor="middle">%s</text>' % (cx[k], py+60, lab))
    for k, items in own.items():
        n = len(items)
        for i, (num, ok) in enumerate(items):
            x = cx[k] + (i - (n-1)/2.0)*34
            f, st = ('#16395c', '#16395c') if ok else ('#a8261c', '#a8261c')
            s.append('<circle cx="%.1f" cy="%d" r="13" fill="%s" stroke="%s"/>' % (x, py+92, f, st))
            s.append('<text class="b w" x="%.1f" y="%d" font-size="15" text-anchor="middle">%s</text>' % (x, py+97, num))
    s.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#e0e6ec"/>' % (px+12, py+114, px+476, py+114))
    s.append('<text class="b %s" x="%d" y="%d" font-size="14.5">%s</text>' % (vcol, px+13, py+134, v1))
    s.append('<text class="gy" x="%d" y="%d" font-size="13">%s</text>' % (px+13, py+155, v2))
    return '\n    '.join(s)

F['fig2'] = '''<figure class="fig">
  <div class="figt">図2　正常形と、3つの崩れ方 ― ①②③がどの列にあるか</div>
  <svg viewBox="0 0 1000 374" role="img" aria-label="傭車の4類型">
    ''' + panel(0, 0, '#186b3f', '正常形 ― 貨物自動車利用運送',
                {2: [('1', True)], 3: [('2', True), ('3', True)]},
                '事業計画変更認可だけでよい', '貨運法9条1項。利用運送法の登録は不要（同法19条）', 'gr') + '''
    ''' + panel(512, 0, '#a8261c', '②だけが当社にずれる',
                {2: [('1', True), ('2', False)], 3: [('3', True)]},
                '偽装請負 ＝ 労働者供給・労働者派遣', '当社が傭車先の運転者にルート・出発時刻を直接指示（職安法44条）', 'rd') + '''
    ''' + panel(0, 198, '#a8261c', '③だけが当社にずれる',
                {2: [('1', True), ('3', False)], 3: [('2', True)]},
                '名義貸し・事業の貸渡し（貨運法28条）', '傭車先の緑ナンバー車を借り、当社の運転者が乗る／事業停止30日', 'rd') + '''
    ''' + panel(512, 198, '#8a6100', '①も傭車先にある',
                {3: [('1', False), ('2', True), ('3', True)]},
                'そもそも傭車ではなく単なる紹介', '荷主と傭車先の直接契約。無規制だが手数料の契約根拠がなくなる', 'am') + '''
  </svg>
  <div class="figc">① 運送責任　② 指揮命令・運行管理　③ 車両の使用権原。<span class="rd" style="font-weight:700">赤い丸</span>が、本来あるべき列からずれている軸です。</div>
</figure>
'''

# ---------- 図3  制度の全体像 ----------
def branch(y, cond, res, src, tone):
    t = {'g':('#eaf5ee','#186b3f','gr'),'a':('#fdf4e2','#8a6100','am'),
         'r':('#fbecea','#a8261c','rd'),'n':('#f2f5f8','#98a5b0','gy')}[tone]
    c = y + 32
    return '\n    '.join([
      '<path d="M290,145 L290,%d L324,%d" fill="none" stroke="#98a5b0" stroke-width="1.4" marker-end="url(#fa3)"/>' % (c, c),
      '<rect x="332" y="%d" width="668" height="64" rx="3" fill="%s" stroke="%s" stroke-width="1.2"/>' % (y, t[0], t[1]),
      '<line x1="592" y1="%d" x2="592" y2="%d" stroke="%s" stroke-width="0.8" opacity="0.5"/>' % (y, y+64, t[1]),
      '<text class="b nv" x="346" y="%d" font-size="15">%s</text>' % (c+5, cond),
      '<text class="b %s" x="606" y="%d" font-size="15.5">%s</text>' % (t[2], c-3, res),
      '<text class="gy" x="606" y="%d" font-size="12.5">%s</text>' % (c+18, src)])

F['fig3'] = '''<figure class="fig">
  <div class="figt">図3　どの制度に当たるかは「委託先が何者か」だけで決まる</div>
  <svg viewBox="0 0 1000 310" role="img" aria-label="制度の全体像">
    <defs><marker id="fa3" markerWidth="10" markerHeight="8" refX="9.5" refY="4" orient="auto">
      <path d="M0,0 L10,4 L0,8 z" fill="#98a5b0"/></marker></defs>
    <rect x="0" y="105" width="250" height="80" rx="3" fill="#16395c"/>
    <text class="b w" x="125" y="133" font-size="16" text-anchor="middle">当社（一般貨物の許可あり）が</text>
    <text class="b w" x="125" y="155" font-size="16" text-anchor="middle">運送を他社に委託する</text>
    <text class="w" x="125" y="174" font-size="12.5" text-anchor="middle" opacity="0.8">＝ 現場で「傭車に出す」と呼ぶ行為</text>
    <line x1="250" y1="145" x2="290" y2="145" stroke="#98a5b0" stroke-width="1.4"/>
    ''' + branch(8,   '緑ナンバーの運送会社（実運送）', '貨物自動車利用運送 ／ 事業計画変更認可', '貨運法2条7項・9条1項。利用運送法は19条で適用除外', 'g') + '''
    ''' + branch(82,  '水屋（利用運送専業者）',       '第一種貨物利用運送事業の登録',        '2条7項の括弧書きで除外され、19条が働かない', 'a') + '''
    ''' + branch(156, '白ナンバー・未届出の軽貨物',   '委託そのものが禁止',                 '貨運法65条の2。100万円以下の罰金（75条14号）・両罰80条', 'r') + '''
    ''' + branch(230, '運送責任を負わない（紹介のみ）', '取次ぎ・マッチング ／ 無規制',        '平成14年法律第77号で貨物取次事業の規制を廃止', 'n') + '''
  </svg>
  <div class="figc">1段目と2段目の分かれ目が、貨運法2条7項の括弧書き「<strong>自動車を使用しないで貨物の運送を行わせることを内容とする契約によるものを除く</strong>」です。</div>
</figure>
'''

# ---------- 図4  判定フローチャート ----------
def qbox(x, y, w, n, q):
    return ('<rect x="%d" y="%d" width="%d" height="62" rx="4" fill="#e6edf4" stroke="#2a5c8a" stroke-width="1.5"/>\n    '
            '<text class="b n2" x="%d" y="%d" font-size="17">%s</text>\n    '
            '<text class="b nv" x="%d" y="%d" font-size="15.5">%s</text>') % (x, y, w, x+14, y+27, n, x+14, y+49, q)

def obox(x, y, w, h, tone, l1, l2, l3=None):
    t = {'g':('#eaf5ee','#186b3f','gr'),'a':('#fdf4e2','#8a6100','am'),
         'r':('#fbecea','#a8261c','rd'),'n':('#f2f5f8','#98a5b0','gy')}[tone]
    s = ['<rect x="%d" y="%d" width="%d" height="%d" rx="4" fill="%s" stroke="%s" stroke-width="1.2"/>' % (x,y,w,h,t[0],t[1]),
         '<text class="b %s" x="%d" y="%d" font-size="15.5">%s</text>' % (t[2], x+14, y+25, l1),
         '<text x="%d" y="%d" font-size="13.5">%s</text>' % (x+14, y+45, l2)]
    if l3: s.append('<text class="gy" x="%d" y="%d" font-size="12.5">%s</text>' % (x+14, y+63, l3))
    return '\n    '.join(s)

F['fig4'] = '''<figure class="fig">
  <div class="figt">図4　判定フローチャート ― Q1からQ4までで必ず答えが出ます</div>
  <svg viewBox="0 0 1000 556" role="img" aria-label="登録要否の判定フロー">
    <defs><marker id="fa4" markerWidth="10" markerHeight="8" refX="9.5" refY="4" orient="auto">
      <path d="M0,0 L10,4 L0,8 z" fill="#2a5c8a"/></marker></defs>
    ''' + qbox(20, 8, 330, 'Q1', '荷主に運送責任を負うか') + '''
    <line x1="350" y1="39" x2="588" y2="39" stroke="#2a5c8a" stroke-width="1.4" marker-end="url(#fa4)"/>
    <text class="b n2" x="469" y="31" font-size="13" text-anchor="middle">負わない</text>
    ''' + obox(600, 8, 390, 62, 'n', '取次ぎ・紹介', '登録不要・無規制（判定終了）') + '''
    <line x1="185" y1="70" x2="185" y2="106" stroke="#2a5c8a" stroke-width="1.4" marker-end="url(#fa4)"/>
    <text class="b n2" x="196" y="93" font-size="13">負う</text>
    ''' + qbox(20, 110, 330, 'Q2', '一般貨物の許可を持っているか') + '''
    <line x1="350" y1="141" x2="588" y2="141" stroke="#2a5c8a" stroke-width="1.4" marker-end="url(#fa4)"/>
    <text class="b n2" x="469" y="133" font-size="13" text-anchor="middle">持っていない ＝ 株式会社石名坂</text>
    ''' + qbox(600, 110, 390, 'Q4', 'その貨物は「自社の貨物」か') + '''
    <path d="M795,172 L795,180 L575,180 L575,215 L592,215 M575,180 L575,285 L592,285"
          fill="none" stroke="#2a5c8a" stroke-width="1.4"/>
    <path d="M592,210 L602,215 L592,220 z M592,280 L602,285 L592,290 z" fill="#2a5c8a"/>
    ''' + obox(602, 188, 388, 54, 'g', '自社の貨物', '登録不要（Q&amp;A A1）。自社は「真荷主」として法12条の義務') + '''
    ''' + obox(602, 258, 388, 54, 'a', '他人の貨物', '第一種貨物利用運送事業の登録が必要（利用運送法3条1項）') + '''
    <line x1="185" y1="172" x2="185" y2="208" stroke="#2a5c8a" stroke-width="1.4" marker-end="url(#fa4)"/>
    <text class="b n2" x="196" y="195" font-size="13">持っている ＝ 石名坂商事（緑）</text>
    ''' + qbox(20, 212, 330, 'Q3', '委託先は誰か') + '''
    <path d="M100,274 L100,510 M100,370 L128,370 M100,440 L128,440 M100,510 L128,510" fill="none" stroke="#2a5c8a" stroke-width="1.4"/>
    <path d="M128,365 L138,370 L128,375 z M128,435 L138,440 L128,445 z M128,505 L138,510 L128,515 z" fill="#2a5c8a"/>
    ''' + obox(142, 341, 848, 58, 'g', '緑ナンバーの運送会社', '第一種登録は不要。一般貨物の事業計画変更認可（貨運法9条1項）だけでよい ― 利用運送法19条の適用除外') + '''
    ''' + obox(142, 411, 848, 58, 'a', '水屋（利用運送専業者）', '第一種貨物利用運送事業の登録が必要（貨運法2条7項の括弧書き／利用運送法3条1項）') + '''
    ''' + obox(142, 481, 848, 58, 'r', '白ナンバー・未届出の軽貨物', '委託自体が禁止（貨運法65条の2）／100万円以下の罰金') + '''
  </svg>
  <div class="figc">Q3の3本が、当社が日々迷う分岐です。<strong>委託先の許可証と車検証の「自家用・事業用の別」欄</strong>を見れば、どの行かは必ず確定します。Q4で「他人の貨物」に落ちた場合、無登録営業は1年以下の拘禁刑若しくは100万円以下の罰金、又は併科です（利用運送法62条1号）。</div>
</figure>
'''
