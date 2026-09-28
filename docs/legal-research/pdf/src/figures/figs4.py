# -*- coding: utf-8 -*-
F = {}

# ---------- 図20  3本の事務連絡 ----------
def _tsu(x, w, kicker, date, issuer, lines, tone):
    bg, st, cl = tone
    s = ['<rect x="%d" y="52" width="%d" height="168" rx="3" fill="%s" stroke="%s" stroke-width="1.5"/>' % (x, w, bg, st),
         '<rect x="%d" y="52" width="%d" height="30" rx="3" fill="%s"/>' % (x, w, st),
         '<rect x="%d" y="68" width="%d" height="14" fill="%s"/>' % (x, w, st),
         '<text class="b w" x="%d" y="73" font-size="14.5" text-anchor="middle">%s</text>' % (x + w // 2, kicker),
         '<text class="b %s" x="%d" y="104" font-size="15">%s</text>' % (cl, x + 14, date),
         '<text class="gy" x="%d" y="124" font-size="11.5">%s</text>' % (x + 14, issuer)]
    y = 148
    for t in lines:
        s.append('<text x="%d" y="%d" font-size="12.5">%s</text>' % (x + 14, y, t))
        y += 19
    return '\n    '.join(s)

F['fig20'] = '''
<figure class="fig">
  <div class="figt">図20　届いた事務連絡は3本目 ― 何が示され、何が変わらないか</div>
  <svg viewBox="0 0 1000 340" role="img" aria-label="3本の事務連絡の流れ">
    <rect x="0" y="0" width="1000" height="38" rx="3" fill="#16395c"/>
    <text class="b w" x="500" y="25" font-size="16" text-anchor="middle">自家用ダンプカーの貨物自動車運送事業法における取扱い　―　令和8年の事務連絡3本</text>
    ''' + _tsu(0, 316, '① 骨格', '令和8年2月10日', '物流・自動車局 貨物流通事業課長',
               ['許可が不要になる2類型', '　(1) 自ら所有する貨物を自ら運送',
                '　(2) 生業と密接不可分で付帯', '共通の具備要件＝雇用関係'],
               ('#e6edf4', '#2a5c8a', 'n2')) + '''
    ''' + _tsu(342, 316, '② 再周知', '令和8年5月1日', '不動産・建設経済局 建設業課長',
               ['施行1か月で「工事現場におい', 'て十分周知されていない事案', 'が発生している」ため',
                '内容は①のとおり'],
               ('#fdf4e2', '#8a6100', 'am')) + '''
    ''' + _tsu(684, 316, '③ 今回届いたもの', '令和8年8月20日', '不動産・建設経済局 建設業課長',
               ['1. 誰と雇用契約を結ぶのか', '　→ 5つの場面（図21）',
                '2. 1日に複数事業者の荷なら', '　→ 通知書2枚 × 事業者の数'],
               ('#eaf5ee', '#186b3f', 'gr')) + '''
    <path d="M316,136 L342,136 M658,136 L684,136" fill="none" stroke="#98a5b0" stroke-width="2"/>
    <path d="M336,131 L346,136 L336,141 z M678,131 L688,136 L678,141 z" fill="#98a5b0"/>
    <rect x="0" y="234" width="1000" height="106" rx="3" fill="#fbecea" stroke="#a8261c" stroke-width="1.4"/>
    <text class="b rd" x="14" y="258" font-size="14.5">変わらないこと ― ③は前文で自ら確認しています</text>
    <text x="14" y="282" font-size="12.5">・違法な「白トラ」行為に係る<tspan class="b rd">違法性の判断基準は、従前から変わらない</tspan></text>
    <text x="14" y="302" font-size="12.5">・白ナンバーを使ってよいのは<tspan class="b nv">雇用関係にある従業員たる運転者に運送行為を行わせる場合</tspan>だけ（期間雇用・日雇いを含む）</text>
    <text x="14" y="322" font-size="12.5">・<tspan class="b rd">沢口砂利店（白）・熊谷砂利店（白）への傭車は、今回も依然として貨運法65条の2違反です</tspan>（100万円以下の罰金・両罰）</text>
  </svg>
  <div class="figc">3本とも<strong>規制を新設していません</strong>。①が判断の骨格、②が「現場に伝わっていない」ことを受けた再周知、③が①の運用を具体化したものです。<strong>③は物流・自動車局と厚生労働省の両方と調整済み</strong>と本文に明記されています。</div>
</figure>
'''

# ---------- 図21  雇用契約を締結する主体 ----------
def _row(y, h, no, lines, who, hi):
    bg = '#fdf4e2' if hi else '#ffffff'
    st = '#8a6100' if hi else '#c9d3dc'
    s = ['<rect x="0" y="%d" width="1000" height="%d" fill="%s" stroke="%s" stroke-width="0.8"/>' % (y, h, bg, st),
         '<rect x="0" y="%d" width="52" height="%d" fill="%s"/>' % (y, h, '#8a6100' if hi else '#16395c'),
         '<text class="b w" x="26" y="%d" font-size="14" text-anchor="middle">%s</text>' % (y + h // 2 + 5, no),
         '<line x1="640" y1="%d" x2="640" y2="%d" stroke="%s" stroke-width="0.8"/>' % (y, y + h, st)]
    ty = y + (h - (len(lines) - 1) * 19) // 2 + 5
    for t in lines:
        s.append('<text x="66" y="%d" font-size="13">%s</text>' % (ty, t))
        ty += 19
    cl = 'b am' if hi else 'b nv'
    s.append('<text class="%s" x="660" y="%d" font-size="13.5">%s</text>' % (cl, y + h // 2 + 5, who))
    return '\n    '.join(s)

F['fig21'] = '''
<figure class="fig">
  <div class="figt">図21　誰と雇用契約を結ぶのか ― 令和8年8月20日事務連絡の5つの場面</div>
  <svg viewBox="0 0 1000 350" role="img" aria-label="雇用契約を締結する主体の5類型">
    <rect x="0" y="0" width="1000" height="36" rx="3" fill="#16395c"/>
    <text class="b w" x="346" y="24" font-size="14.5" text-anchor="middle">資材等を運搬する場面</text>
    <text class="b w" x="820" y="24" font-size="14.5" text-anchor="middle">雇用契約の締結主体</text>
    <line x1="640" y1="0" x2="640" y2="36" stroke="#ffffff" stroke-width="0.8"/>
    ''' + _row(40, 46, '(1)', ['資材業者が所有する資材等を運搬する'], '運転手と資材業者', False) + '''
    ''' + _row(88, 46, '(2)', ['建設業者が所有する資材等を運搬する'], '運転手と建設業者', False) + '''
    ''' + _row(136, 64, '(3)', ['資材業者が、生業として自ら販売した資材等を、',
                                '販売先の建設業者への引渡しのために運搬する'], '運転手と資材業者', True) + '''
    ''' + _row(202, 64, '(4)', ['建設業者が生業として請け負った建設工事の施工に',
                                '必要な、発注者が支給する資材等を運搬する'], '運転手と建設業者', False) + '''
    ''' + _row(268, 46, '(5)', ['運転手自らが所有する資材等を運搬する'], '雇用契約は不要', False) + '''
    <rect x="0" y="322" width="1000" height="28" rx="3" fill="#16395c"/>
    <text class="b w" x="14" y="341" font-size="13">貫いている原理は1つ　―　荷物を持っている者　＝　運ばせる者　＝　雇う者　を一致させる</text>
  </svg>
  <div class="figc"><strong>(3)が当社の砕石販売に直撃する類型です。</strong>株式会社石名坂<span class="pn">（真荷主）</span>が自分で売った砕石を自分で届けるなら、運転者は<strong>株式会社石名坂が雇う</strong>。石名坂商事<span class="pg">（緑）</span>が雇って親会社の荷を運べば、それは石名坂商事の運送事業であり<strong>緑ナンバー（事業用自動車）が要ります</strong>。(5)は荷物の所有者と運転者が同一人なので、雇う相手がいません。</div>
</figure>
'''

# ---------- 図22  ダンプが足りない日に取りうる3つの形 ----------
def _col(x, w, head, tone, mark, lines, foot):
    bg, st, cl = tone
    s = ['<rect x="%d" y="44" width="%d" height="218" rx="3" fill="%s" stroke="%s" stroke-width="1.5"/>' % (x, w, bg, st),
         '<rect x="%d" y="44" width="%d" height="30" rx="3" fill="%s"/>' % (x, w, st),
         '<rect x="%d" y="60" width="%d" height="14" fill="%s"/>' % (x, w, st),
         '<text class="b w" x="%d" y="65" font-size="13.5" text-anchor="middle">%s</text>' % (x + w // 2, head),
         '<text class="b %s" x="%d" y="98" font-size="20" text-anchor="middle">%s</text>' % (cl, x + w // 2, mark)]
    y = 122
    for t in lines:
        s.append('<text x="%d" y="%d" font-size="11.5">%s</text>' % (x + 11, y, t))
        y += 17
    s.append('<text class="b %s" x="%d" y="250" font-size="11.5">%s</text>' % (cl, x + 11, foot))
    return '\n    '.join(s)

F['fig22'] = '''
<figure class="fig">
  <div class="figt">図22　ダンプが足りない日に取りうる形 ― 事務連絡を踏まえた4択</div>
  <svg viewBox="0 0 1000 300" role="img" aria-label="ダンプ不足の日の4つの選択肢">
    <rect x="0" y="0" width="1000" height="36" rx="3" fill="#16395c"/>
    <text class="b w" x="500" y="24" font-size="15.5" text-anchor="middle">石名坂商事（緑）の5台が埋まっている日に、どの形なら適法か</text>
    ''' + _col(0, 238, '① 緑ナンバーへ傭車', ('#eaf5ee', '#186b3f', 'gr'), '○',
               ['丸幸運輸（緑）・高新建材（緑）', 'に下請に出す。', '',
                '事業計画変更認可（貨運法9条', '1項）の範囲内で行う。', '法12条書面・24条2項書面・',
                '実運送体制管理簿が発生。'], '本命。運賃が自社に立つ') + '''
    ''' + _col(254, 238, '② 親会社が自分で届ける', ('#e6edf4', '#2a5c8a', 'n2'), '○',
               ['株式会社石名坂（真荷主）が、', '自社の砕石を自社従業員または',
                '日雇い運転者に運ばせる。', '', '2/10事務連絡1.(1)＋8/20(3)。',
                '通知書2枚と実費弁償が条件。'], '運賃は立たない。自家輸送') + '''
    ''' + _col(508, 238, '③ 引取販売', ('#e6edf4', '#2a5c8a', 'n2'), '○',
               ['沢口砂利店（白）が砕石を買い、', '現場の元請・施主に自分で売り、',
                '自分で運ぶ。', '', '8/20(3)(5)、建設Q18、資材Q6。', '請求は「運賃込みの砕石代」。'],
               '買い戻しは違法（30章）') + '''
    ''' + _col(762, 238, '④ 白ナンバーへ傭車', ('#fbecea', '#a8261c', 'rd'), '×',
               ['沢口砂利店（白）・熊谷砂利店', '（白）に運送を委託する。', '',
                '貨運法65条の2違反。', '100万円以下の罰金（75条14号）、', '法人にも両罰（80条）。'],
               '事務連絡でも変わらない') + '''
    <rect x="0" y="272" width="1000" height="28" rx="3" fill="#f2f5f8" stroke="#c9d3dc" stroke-width="0.8"/>
    <text x="14" y="291" font-size="12.5">検討の順序は<tspan class="b gr">① → ②・③ → 断る</tspan>。<tspan class="b rd">④に流れないこと</tspan>。②と③は<tspan class="b nv">石名坂商事の売上にはなりません</tspan>が、現場は止まりません。</text>
  </svg>
  <div class="figc">②と③の違いは<strong>誰が砕石の所有者か</strong>です。②は株式会社石名坂<span class="pn">（真荷主）</span>が最後まで売主で、届けるのも自分。③は沢口砂利店<span class="pw">（白）</span>がいったん買主になり、自分の荷物として運びます。どちらも<strong>運送の対価が別建てで動かない</strong>ことが前提です。</div>
</figure>
'''

# ---------- 図23  貨運法とダンプ規制法のずれ ----------
def _side(x, w, head, tone, lines):
    bg, st, cl = tone
    s = ['<rect x="%d" y="44" width="%d" height="214" rx="3" fill="%s" stroke="%s" stroke-width="1.5"/>' % (x, w, bg, st),
         '<rect x="%d" y="44" width="%d" height="30" rx="3" fill="%s"/>' % (x, w, st),
         '<rect x="%d" y="60" width="%d" height="14" fill="%s"/>' % (x, w, st),
         '<text class="b w" x="%d" y="65" font-size="14" text-anchor="middle">%s</text>' % (x + w // 2, head)]
    y = 96
    for t, bold in lines:
        c = ('b ' + cl) if bold else ''
        s.append('<text class="%s" x="%d" y="%d" font-size="12.5">%s</text>' % (c, x + 13, y, t))
        y += 19
    return '\n    '.join(s)

F['fig23'] = '''
<figure class="fig">
  <div class="figt">図23　1日に複数事業者 ― 貨運法は通しても、ダンプ規制法が通らないことがある</div>
  <svg viewBox="0 0 1000 384" role="img" aria-label="貨運法とダンプ規制法のずれ">
    <rect x="0" y="0" width="1000" height="38" rx="3" fill="#16395c"/>
    <text class="b w" x="500" y="25" font-size="16" text-anchor="middle">持込みの白ダンプで、午前はA社・午後はB社の荷を運ぶ日</text>
    ''' + _side(0, 486, '貨運法（令和8年8月20日事務連絡）', ('#eaf5ee', '#186b3f', 'gr'), [
        ('午前　A社と日雇いの労働契約', True),
        ('　　　労働条件通知書＋車両使用通知書', False),
        ('午後　B社と日雇いの労働契約', True),
        ('　　　労働条件通知書＋車両使用通知書', False),
        ('', False),
        ('「個々の事業者ごとに労働契約を締結し、', False),
        ('それぞれが通知を併せて行うことが適切」', False),
        ('', False),
        ('→ 貨運法の許可は不要', True),
    ]) + '''
    ''' + _side(514, 486, 'ダンプ規制法（表示番号）', ('#fbecea', '#a8261c', 'rd'), [
        ('表示番号＝「使用者が経営する事業に', True),
        ('対応した」記号（東北運輸局Q12）', True),
        ('届出時に事業の挙証書類を出して取得し、', False),
        ('車検証に記入される（規則3条3項）', False),
        ('事業の種類が変われば番号の取り直し', True),
        ('（規則3条3項2号。規則4条の反対解釈）', False),
        ('', False),
        ('→ 雇主が替わるたびに付け替える、は', True),
        ('　 制度上できない', True),
    ]) + '''
    <path d="M486,150 L514,150" fill="none" stroke="#98a5b0" stroke-width="2" stroke-dasharray="5 4"/>
    <text class="b rd" x="500" y="140" font-size="18" text-anchor="middle">≠</text>
    <rect x="0" y="266" width="1000" height="118" rx="3" fill="#e6edf4" stroke="#2a5c8a" stroke-width="1.4"/>
    <text class="b nv" x="14" y="290" font-size="14.5">成り立つのは1つの形だけです</text>
    <text x="14" y="314" font-size="12.5">① <tspan class="b n2">車検証上の使用者は運転者本人のまま</tspan>（車両使用通知書も「賃貸借その他の独立した契約関係を構成しない」としています）</text>
    <text x="14" y="334" font-size="12.5">② <tspan class="b n2">運転者本人が、自分の事業（建設業・砂利販売業など）で表示番号の指定を受けている</tspan></text>
    <text x="14" y="354" font-size="12.5">この2つが揃えば、ゼッケンは<tspan class="b nv">1日じゅう本人のもののまま</tspan>で、雇主が替わっても貼り替える必要はありません。</text>
    <text class="rd" x="14" y="374" font-size="12.5">逆に、運転者が事業を営んでおらず挙証書類を出せないなら、<tspan class="b rd">表示番号が取れず、土砂等を運ぶこと自体ができません。</tspan></text>
  </svg>
  <div class="figc">記号が表すのは<strong>その日の荷主の業種ではなく、使用者（車検証上の使用者）の業種</strong>です。だから（販）のダンプが建設業者の残土を運ぶこと自体は、表示番号の問題にはなりません。問題になるのは<strong>使用者そのものを日替わりにしようとしたとき</strong>です。</div>
</figure>
'''
