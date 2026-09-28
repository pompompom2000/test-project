# -*- coding: utf-8 -*-
F = {}

# ---------- 図25  白ダンプに効く4つの関門 ----------
def _gate(y, no, tone, law, q, lines):
    bg, st, cl = tone
    h = 26 + 19*len(lines)
    s = ['<rect x="96" y="%d" width="904" height="%d" rx="3" fill="%s" stroke="%s" stroke-width="1.3"/>' % (y, h, bg, st),
         '<rect x="0" y="%d" width="84" height="%d" rx="3" fill="%s"/>' % (y, h, st),
         '<text class="b w" x="42" y="%d" font-size="22" text-anchor="middle">%s</text>' % (y + h//2 + 8, no),
         '<text class="b %s" x="110" y="%d" font-size="14.5">%s</text>' % (cl, y+20, law),
         '<text class="gy" x="%d" y="%d" font-size="12.5">%s</text>' % (110 + len(law)*15 + 14, y+20, q)]
    yy = y + 41
    for t in lines:
        s.append('<text x="110" y="%d" font-size="12.5">%s</text>' % (yy, t)); yy += 19
    return '\n    '.join(s), h

_g = [
 ('1', ('#e6edf4','#2a5c8a','n2'), '貨物自動車運送事業法', '― 誰の荷物を、誰が、有償で運ぶか',
  ['自分の荷物を自分で運ぶ　または　生業と密接不可分で付帯し、運送の対価がない',
   'どちらにも当たらず有償なら許可が必要。委託した側も65条の2（100万円以下の罰金＋公表）']),
 ('2', ('#fdf4e2','#8a6100','am'), 'ダンプ規制法', '― その荷物は「土砂等」か',
  ['土砂等なら、荷台3面の表示番号（ゼッケン）と自重計が必要。無表示は3万円以下の罰金＋両罰',
   '表示番号は「使用者が経営する事業」に対応。挙証書類を出して取得し、車検証に記載される']),
 ('3', ('#eaf5ee','#186b3f','gr'), '労働法・社会保険', '― 運転者と誰が雇用関係にあるか',
  ['白ダンプを適法に動かせるのは「雇用」だけ。労働条件通知書と車両使用通知書を交付する',
   '許可不要でも改善基準告示は適用。労基法32・35・37条違反はダンプ規制法8条1項で車が止まる']),
 ('4', ('#fbecea','#a8261c','rd'), '廃棄物処理法', '― その荷物は産業廃棄物か',
  ['産廃なら収集運搬業許可が要る。建設工事は元請が排出事業者（21条の3）',
   '受託したものをさらに他社へ回すことはできない（14条16項）']),
]
def _b25():
    parts=['<rect x="0" y="0" width="1000" height="38" rx="3" fill="#16395c"/>',
           '<text class="b w" x="500" y="25" font-size="16" text-anchor="middle">白ナンバーのダンプを1台動かすのに、通さなければならない関門は4つあります</text>']
    y=50
    for no,tone,law,q,lines in _g:
        blk,h=_gate(y,no,tone,law,q,lines); parts.append(blk); y+=h+10
    parts.append('<rect x="0" y="%d" width="1000" height="30" rx="3" fill="#16395c"/>'%y)
    parts.append('<text class="b w" x="14" y="%d" font-size="13.5">4つ全部を通って、はじめて適法です。1つでも落ちれば、残り3つが完璧でも違法になります。</text>'%(y+20))
    return '\n    '.join(parts), y+34
_b,_h = _b25()
F['fig25'] = '''
<figure class="fig">
  <div class="figt">図25　白ダンプに効く4つの関門</div>
  <svg viewBox="0 0 1000 %d" role="img" aria-label="白ダンプに効く4つの法律">
    %s
  </svg>
  <div class="figc">よくある間違いは、<strong>関門1だけを見て「許可が要らないから大丈夫」と考えること</strong>です。許可が不要でも、ゼッケンがなければ土砂等は運べませんし、雇用関係が実態を伴わなければ関門1に戻って無許可運送になります。</div>
</figure>
''' % (_h, _b)

# ---------- 図26  品目の2軸マトリクス ----------
def _quad(x, y, w, h, tone, head, sub, items, mark):
    bg, st, cl = tone
    s = ['<rect x="%d" y="%d" width="%d" height="%d" rx="3" fill="%s" stroke="%s" stroke-width="1.5"/>' % (x,y,w,h,bg,st),
         '<rect x="%d" y="%d" width="%d" height="28" rx="3" fill="%s"/>' % (x,y,w,st),
         '<rect x="%d" y="%d" width="%d" height="14" fill="%s"/>' % (x,y+14,w,st),
         '<text class="b w" x="%d" y="%d" font-size="13.5" text-anchor="middle">%s</text>' % (x+w//2, y+19, head),
         '<text class="b %s" x="%d" y="%d" font-size="20">%s</text>' % (cl, x+12, y+52, mark),
         '<text class="b %s" x="%d" y="%d" font-size="12">%s</text>' % (cl, x+44, y+51, sub)]
    yy = y + 74
    for t in items:
        s.append('<text x="%d" y="%d" font-size="12.5">・%s</text>' % (x+12, yy, t)); yy += 19
    return '\n    '.join(s)

F['fig26'] = '''
<figure class="fig">
  <div class="figt">図26　品目で何が変わるか ― ダンプ規制法と廃棄物処理法は、まったく別の軸です</div>
  <svg viewBox="0 0 1000 466" role="img" aria-label="品目の2軸マトリクス">
    <text class="b nv" x="0" y="16" font-size="13.5">↑ ダンプ規制法の「土砂等」に当たる（ゼッケン・自重計が要る）</text>
    <text class="b nv" x="1000" y="462" font-size="13.5" text-anchor="end">廃棄物処理法の「産業廃棄物」に当たる →</text>
    ''' + _quad(0, 26, 486, 196, ('#eaf5ee','#186b3f','gr'), 'ゼッケンは要る／産廃ではない', '貨運法とダンプ規制法だけ',
        ['土・建設発生土（残土）　― 法2条1項「土」', '砕石・砂利・砂・玉石　― 法2条1項',
         '石灰石（砂利状・砕石状）・けい砂　― 令1条4号', '再生砕石（RC-40等）　※有価物性は個別判断'], '○') + '''
    ''' + _quad(514, 26, 486, 196, ('#fbecea','#a8261c','rd'), 'ゼッケンも産廃も ― 三階建て', '貨運法＋ダンプ規制法＋廃掃法',
        ['アスファルト・コンクリート（アスがら）― 令1条1号', 'コンクリート・れんが・モルタル・しっくいのくず ― 令1条3号',
         'がれき類は、この2つが中心です', '鉱さい・廃鉱・石炭がら　― 令1条2号'], '×') + '''
    ''' + _quad(0, 240, 486, 196, ('#f2f5f8','#98a5b0','gy'), 'どちらもかからない', '貨運法だけ見ればよい',
        ['アスファルト合材・生コン　― 製品', '鉄筋・二次製品・リース機械',
         '有価スクラップ（鉄くず等）　― 専ら物', '水（散水車）'], '―') + '''
    ''' + _quad(514, 240, 486, 196, ('#fdf4e2','#8a6100','am'), '産廃だが、ゼッケンは要らない', '貨運法＋廃掃法',
        ['汚泥・建設汚泥', '木くず・廃プラスチック類', '廃石膏ボード', '廃油・廃酸・廃アルカリ'], '△') + '''
    <line x1="500" y1="26" x2="500" y2="436" stroke="#16395c" stroke-width="1.6" stroke-dasharray="6 4"/>
    <line x1="0" y1="231" x2="1000" y2="231" stroke="#16395c" stroke-width="1.6" stroke-dasharray="6 4"/>
  </svg>
  <div class="figc">現場では「産廃だからゼッケンが要る」「有価物だから要らない」と言われがちですが、<strong>この2つは無関係です</strong>。
  <strong>がれき類は産廃であり、同時に土砂等でもあります</strong>（施行令1条1号・3号）。逆に<strong>汚泥は産廃ですが土砂等ではありません</strong>。砕石・砂利は産廃ではありませんが土砂等です。</div>
</figure>
'''

# ---------- 図27  積込み前の1枚（白ダンプ用） ----------
def _chk(y, no, tone, q, ok, ng):
    bg, st, cl = tone
    s = ['<rect x="0" y="%d" width="1000" height="56" rx="3" fill="%s" stroke="%s" stroke-width="1.1"/>' % (y, bg, st),
         '<rect x="0" y="%d" width="46" height="56" rx="3" fill="%s"/>' % (y, st),
         '<text class="b w" x="23" y="%d" font-size="15" text-anchor="middle">%s</text>' % (y+35, no),
         '<text class="b %s" x="60" y="%d" font-size="13.5">%s</text>' % (cl, y+23, q),
         '<text class="gr" x="60" y="%d" font-size="12">○ %s</text>' % (y+44, ok),
         '<text class="rd" x="560" y="%d" font-size="12">× %s</text>' % (y+44, ng)]
    return '\n    '.join(s)

F['fig27'] = '''
<figure class="fig">
  <div class="figt">図27　白ダンプを使う日の、積込み前チェック</div>
  <svg viewBox="0 0 1000 424" role="img" aria-label="白ダンプの積込み前チェック">
    <rect x="0" y="0" width="1000" height="36" rx="3" fill="#16395c"/>
    <text class="b w" x="500" y="24" font-size="15.5" text-anchor="middle">上から順に。1つでも × なら、その車に積ませない</text>
    ''' + _chk(46, '1', ('#e6edf4','#2a5c8a','n2'), 'この荷物は誰のものか', '運転者側の会社が所有者。または自分の工事で出た残土', '当社の荷物を、当社以外が運ぶ ＝ 委託。白なら65条の2違反') + '''
    ''' + _chk(110, '2', ('#e6edf4','#2a5c8a','n2'), '運送の対価を払っていないか', '着地渡しの商品代に含まれている。運賃としては動いていない', '運賃・傭車代・手間賃・応援代。名目を変えても同じ') + '''
    ''' + _chk(174, '3', ('#eaf5ee','#186b3f','gr'), '運転者は誰に雇われているか', '荷物の所有者と雇用関係がある（日雇い可）。本人所有の荷なら不要', '委託契約・請負契約。他社が雇った人が当社の荷を運ぶ') + '''
    ''' + _chk(238, '4', ('#fdf4e2','#8a6100','am'), '車検証に表示番号があるか', '備考欄に記載。券面になければ記録事項かアプリで確認', '記載なし＝指定を受けていない。土砂等は積めない') + '''
    ''' + _chk(302, '5', ('#fdf4e2','#8a6100','am'), '荷台3面のゼッケンと自重計', '両側面と後面の3面。車検証の番号と一致。自重計が作動する', '後面の脱落・かすれ。マグネットでの仮表示') + '''
    ''' + _chk(366, '6', ('#fbecea','#a8261c','rd'), 'その荷物は産業廃棄物か', 'がれき類・汚泥なら収集運搬業許可とマニフェストを確認', '「残土」と言われたが、実はコンクリートがらが混ざっている') + '''
  </svg>
  <div class="figc">1〜3が<strong>貨運法</strong>、4〜5が<strong>ダンプ規制法</strong>、6が<strong>廃棄物処理法</strong>です。運転席と配車室に貼って使ってください。</div>
</figure>
'''

# ---------- 図28  労働時間の通算と管理モデル ----------
F['fig28'] = '''
<figure class="fig">
  <div class="figt">図28　1日に複数事業者の荷を運ばせる日 ― 労働時間の通算と「管理モデル」</div>
  <svg viewBox="0 0 1000 418" role="img" aria-label="労働時間の通算と管理モデル">
    <rect x="0" y="0" width="1000" height="36" rx="3" fill="#16395c"/>
    <text class="b w" x="500" y="24" font-size="15.5" text-anchor="middle">労基法38条1項「労働時間は、事業場を異にする場合においても……通算する」</text>
    <text class="gy" x="0" y="58" font-size="12.5">※「事業場を異にする場合」とは<tspan class="b nv">事業主を異にする場合をも含む</tspan>（昭和23年5月14日 基発第769号）</text>

    <rect x="0" y="72" width="1000" height="112" rx="3" fill="#fbecea" stroke="#a8261c" stroke-width="1.4"/>
    <text class="b rd" x="14" y="94" font-size="14">そのままだと ― 誰も割増賃金を払わないまま37条違反になりかねない</text>
    <rect x="14" y="106" width="300" height="34" rx="2" fill="#e6edf4" stroke="#2a5c8a"/>
    <text class="b n2" x="164" y="128" font-size="13" text-anchor="middle">午前　A社　所定4時間</text>
    <rect x="322" y="106" width="374" height="34" rx="2" fill="#e6edf4" stroke="#2a5c8a"/>
    <text class="b n2" x="509" y="128" font-size="13" text-anchor="middle">午後　B社　所定5時間</text>
    <rect x="704" y="106" width="92" height="34" rx="2" fill="#fbecea" stroke="#a8261c" stroke-width="1.6"/>
    <text class="b rd" x="750" y="128" font-size="13" text-anchor="middle">1時間</text>
    <text class="rd" x="806" y="128" font-size="12.5">← 通算9時間。8時間を超える部分</text>
    <text x="14" y="160" font-size="12.5">割増賃金を払うのは<tspan class="b rd">時間的に後から労働契約を締結した使用者（B社）</tspan>。自ら労働させた時間について支払う</text>
    <text class="gy" x="14" y="177" font-size="12">基発0901第3号 第3の2・第4の1。率は自社の就業規則等で定めた率（2割5分以上）</text>

    <rect x="0" y="196" width="1000" height="90" rx="3" fill="#fdf4e2" stroke="#8a6100" stroke-width="1.4"/>
    <text class="b am" x="14" y="218" font-size="14">まず ― 申告させる仕組みを作る（第2・第3の1(2)）</text>
    <text x="14" y="240" font-size="12.5">・就業規則や労働契約に<tspan class="b am">副業・兼業の届出制</tspan>を定め、他社での勤務を申告させる</text>
    <text x="14" y="259" font-size="12.5">・<tspan class="b nv">「労働者からの申告等がなかった場合には労働時間の通算は要せず」</tspan>、申告内容が事実と異なっていても</text>
    <text x="14" y="278" font-size="12.5">　申告により把握した労働時間で通算していれば足りる ― <tspan class="b am">申告制を作ることが、そのまま防御になります</tspan></text>

    <rect x="0" y="298" width="1000" height="120" rx="3" fill="#eaf5ee" stroke="#186b3f" stroke-width="1.4"/>
    <text class="b gr" x="14" y="320" font-size="14">実務の答え ― 「管理モデル」（第5）</text>
    <text x="14" y="342" font-size="12.5">・副業・兼業の<tspan class="b gr">開始前に</tspan>、A社の法定外労働時間とB社の労働時間の合計が単月100時間未満・複数月平均80時間以内と</text>
    <text x="14" y="361" font-size="12.5">　なる範囲で、<tspan class="b gr">各社の労働時間の上限をあらかじめ設定</tspan>しておく</text>
    <text x="14" y="380" font-size="12.5">・A社は自社の法定外労働時間、B社は<tspan class="b gr">自社の労働時間すべて</tspan>について割増賃金を払う</text>
    <text x="14" y="399" font-size="12.5">・こうすれば<tspan class="b gr">「他の使用者の事業場における実労働時間の把握を要することなく法を遵守できる」</tspan>（第5の2）</text>
  </svg>
  <div class="figc">通算されるのは<strong>法定労働時間（32条・40条）</strong>と、36条6項2号・3号の単月100時間未満・複数月平均80時間以内の要件です。
  <strong>休憩（34条）・休日（35条）・年次有給休暇（39条）は通算されません。</strong>36協定の限度時間も事業場ごとです（第1の3）。</div>
</figure>
'''
