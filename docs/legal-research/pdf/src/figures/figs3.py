# -*- coding: utf-8 -*-
F = {}
TONE = {'g':('#eaf5ee','#186b3f','gr'),'a':('#fdf4e2','#8a6100','am'),
        'r':('#fbecea','#a8261c','rd'),'n':('#f2f5f8','#98a5b0','gy'),
        'b':('#e6edf4','#2a5c8a','n2')}

# ---------- 図11  社会保険の加入ライン ----------
AX, AW = 300, 690
def hx(h): return AX + h*(AW/40.0)
def hrow(y, label, sub, segs):
    s = ['<text class="b nv" x="8" y="%d" font-size="14">%s</text>' % (y+17, label),
         '<text class="gy" x="8" y="%d" font-size="11.5">%s</text>' % (y+33, sub)]
    for h1, h2, fill, hatch, txt, tc in segs:
        x1, x2 = hx(h1), hx(h2)
        f = 'url(#hat2)' if hatch else fill
        s.append('<rect x="%.1f" y="%d" width="%.1f" height="30" rx="2" fill="%s" stroke="%s" stroke-width="0.8"/>' % (x1, y, x2-x1, f, fill))
        if txt:
            s.append('<text class="%s" x="%.1f" y="%d" font-size="12" text-anchor="middle">%s</text>' % (tc, (x1+x2)/2, y+20, txt))
    return '\n    '.join(s)

F['fig11'] = '''<figure class="fig">
  <div class="figt">図11　週の所定労働時間と、加入する保険のライン（労働者と評価された場合）</div>
  <svg viewBox="0 0 1000 256" role="img" aria-label="社会保険の加入ライン">
    <defs><pattern id="hat2" width="7" height="7" patternTransform="rotate(45)" patternUnits="userSpaceOnUse">
      <rect width="7" height="7" fill="#f2f5f8"/><line x1="0" y1="0" x2="0" y2="7" stroke="#98a5b0" stroke-width="2.2"/></pattern></defs>
    ''' + '\n    '.join(
      ['<line x1="%.1f" y1="30" x2="%.1f" y2="236" stroke="#e3e9ee"/>' % (hx(h), hx(h)) for h in (0,10,20,30,40)] +
      ['<text class="gy" x="%.1f" y="24" font-size="12.5" text-anchor="middle">%s</text>' % (hx(h), t)
       for h,t in ((0,'0時間'),(10,'10時間'),(20,'20時間'),(30,'30時間 ＝ 4分の3'))]
      + ['<text class="gy" x="1000" y="24" font-size="12.5" text-anchor="end">40時間</text>']) + '''
    <text class="gy" x="8" y="24" font-size="12.5">週の所定労働時間</text>
    ''' + hrow(40, '労災保険', '保険料は全額事業主負担', [(0, 40, '#186b3f', False, '時間要件なし ― 労働者なら当然適用', 'w')]) + '''
    ''' + hrow(92, '雇用保険', '31日以上の雇用見込みが必要', [(10, 20, '#98a5b0', True, '2028年10月〜', 'gy'), (20, 40, '#16395c', False, '週20時間以上で加入', 'w')]) + '''
    ''' + hrow(144, '健康保険・厚生年金', '当社の判定はこの1本だけ', [(30, 40, '#16395c', False, '通常の労働者の4分の3以上', 'w')]) + '''
    ''' + hrow(196, '短時間労働者の特例', '週20時間＋月8.8万円＋学生でない', [(20, 30, '#98a5b0', True, '特定適用事業所のみ', 'gy')]) + '''
    <text class="rd" x="%.1f" y="244" font-size="12">↑ ハッチは特定適用事業所（厚年の被保険者が常時51人超）だけの話です。当社は対象外</text>
    <line x1="%.1f" y1="30" x2="%.1f" y2="236" stroke="#a8261c" stroke-width="1.4" stroke-dasharray="4 3"/>
  </svg>
  <div class="figc">よくある「週20時間以上は社会保険」は<strong>特定適用事業所（厚年の被保険者51人以上）の話</strong>です。当社はこれに当たらないので、健保・厚年は<strong>4分の3基準だけ</strong>で判定します（健保法3条1項9号・厚年法12条5号）。適用拡大は2027年10月に36人以上へ下がるので、従業員が30名台後半に近づいたら再判定してください。</div>
</figure>
''' % (float(AX), hx(30), hx(30))

# ---------- 図12  ゼッケンとナンバープレート ----------
F['fig12'] = '''<figure class="fig">
  <div class="figt">図12　ナンバープレートと表示番号（ゼッケン）は、まったく別の制度です</div>
  <svg viewBox="0 0 1000 238" role="img" aria-label="ナンバープレートとゼッケンの対比">
    <rect x="0" y="0" width="490" height="236" rx="3" fill="#ffffff" stroke="#c9d3dc"/>
    <rect x="0" y="0" width="490" height="30" rx="3" fill="#2a5c8a"/><rect x="0" y="16" width="490" height="14" fill="#2a5c8a"/>
    <text class="b w" x="13" y="21" font-size="16">自動車登録番号標（ナンバープレート）</text>
    <rect x="145" y="46" width="200" height="100" rx="6" fill="#186b3f" stroke="#0f4f2e" stroke-width="2"/>
    <rect x="153" y="54" width="184" height="84" rx="4" fill="none" stroke="#ffffff" stroke-width="1.6"/>
    <text class="b w" x="245" y="86" font-size="20" text-anchor="middle">盛岡 100 あ</text>
    <text class="b w" x="245" y="126" font-size="30" text-anchor="middle">12-34</text>
    <text x="16" y="170" font-size="13">・根拠は<tspan class="b nv">道路運送車両法</tspan>。地名は<tspan class="b nv">「盛岡」「平泉」</tspan></text>
    <text x="16" y="190" font-size="13">・<tspan class="b gr">緑地＝事業用</tspan>、白地＝自家用。ここで緑／白が分かる</text>
    <text x="16" y="210" font-size="13">・付いている位置は<tspan class="b nv">車両の前後</tspan>（2面）</text>
    <text class="gy" x="16" y="228" font-size="11.5">※車検証の「自家用・事業用の別」欄と一致します</text>
    <rect x="510" y="0" width="490" height="236" rx="3" fill="#ffffff" stroke="#c9d3dc"/>
    <rect x="510" y="0" width="490" height="30" rx="3" fill="#8a6100"/><rect x="510" y="16" width="490" height="14" fill="#8a6100"/>
    <text class="b w" x="523" y="21" font-size="16">表示番号（ゼッケン）</text>
    <rect x="600" y="58" width="300" height="76" rx="2" fill="#ffffff" stroke="#1b1b1b" stroke-width="2.2"/>
    <text class="b" x="750" y="108" font-size="34" text-anchor="middle" fill="#1b1b1b">岩手（営）12345</text>
    <text x="526" y="170" font-size="13">・根拠は<tspan class="b am">ダンプ規制法3条・4条</tspan>。地名文字は<tspan class="b am">「岩手」のみ</tspan></text>
    <text x="526" y="190" font-size="13">・<tspan class="b rd">白ナンバーの自家用ダンプにも付いています</tspan>（3条1項）</text>
    <text x="526" y="210" font-size="13">・付いている位置は<tspan class="b am">荷台の両側面と後面</tspan>（3面）</text>
    <text class="gy" x="526" y="228" font-size="11.5">※文字は黒・地は白。高さ200mm（規則別表第一）。後面の脱落・かすれが最多の指摘</text>
  </svg>
  <div class="figc"><strong>ゼッケンの有無は、緑ナンバーかどうかの判断材料になりません。</strong>沢口砂利店（白）・熊谷砂利店（白）のダンプにも表示番号は付いています。</div>
</figure>
'''

# ---------- 図13  表示番号の構造 ----------
def chip(x, y, lab, desc, on):
    f, st, tc = ('#186b3f', '#186b3f', 'w') if on else ('#ffffff', '#c9d3dc', 'nv')
    return ('<rect x="%d" y="%d" width="62" height="34" rx="3" fill="%s" stroke="%s" stroke-width="1.2"/>\n    '
            '<text class="b %s" x="%d" y="%d" font-size="15" text-anchor="middle">%s</text>\n    '
            '<text class="gy" x="%d" y="%d" font-size="11.5" text-anchor="middle">%s</text>') % (
            x, y, f, st, tc, x+31, y+23, lab, x+31, y+50, desc)

F['fig13'] = '''<figure class="fig">
  <div class="figt">図13　表示番号の中身 ― 3つをこの順で組み合わせます（施行規則6条）</div>
  <svg viewBox="0 0 1000 286" role="img" aria-label="表示番号の構造">
    <rect x="150" y="8" width="700" height="80" rx="3" fill="#ffffff" stroke="#1b1b1b" stroke-width="2.2"/>
    <text class="b" x="290" y="66" font-size="40" text-anchor="middle" fill="#1b1b1b">岩手</text>
    <text class="b" x="500" y="66" font-size="40" text-anchor="middle" fill="#1b1b1b">（営）</text>
    <text class="b" x="720" y="66" font-size="40" text-anchor="middle" fill="#1b1b1b">12345</text>
    <path d="M190,96 L190,104 L390,104 L390,96" fill="none" stroke="#2a5c8a" stroke-width="1.4"/>
    <path d="M410,96 L410,104 L590,104 L590,96" fill="none" stroke="#2a5c8a" stroke-width="1.4"/>
    <path d="M610,96 L610,104 L830,104 L830,96" fill="none" stroke="#2a5c8a" stroke-width="1.4"/>
    <text class="b n2" x="290" y="124" font-size="14" text-anchor="middle">① 運輸支局を表示する文字</text>
    <text class="gy" x="290" y="142" font-size="12" text-anchor="middle">別表第二。岩手県は「岩手」だけ</text>
    <text class="gy" x="290" y="159" font-size="12" text-anchor="middle">ナンバーが盛岡・平泉でも「岩手」</text>
    <text class="b n2" x="500" y="124" font-size="14" text-anchor="middle">② 経営する事業の種類</text>
    <text class="gy" x="500" y="142" font-size="12" text-anchor="middle">別表第三。7種類がすべて</text>
    <text class="b gr" x="500" y="159" font-size="12" text-anchor="middle">当社は（営）＝自動車運送事業</text>
    <text class="b n2" x="720" y="124" font-size="14" text-anchor="middle">③ 5けた以下のアラビア数字</text>
    <text class="gy" x="720" y="142" font-size="12" text-anchor="middle">指定を受けた番号</text>
    ''' + '\n    '.join(chip(30 + i*138, 182, lab, desc, lab == '（営）') for i, (lab, desc) in enumerate(
        [('（営）', '自動車運送事業'), ('（石）', '採石業'), ('（砕）', '砕石業'), ('（砂）', '砂利採取業'),
         ('（販）', '砂利販売業'), ('（建）', '建設業'), ('（他）', 'その他')])) + '''
    <rect x="0" y="244" width="1000" height="42" rx="3" fill="#fdf4e2" stroke="#8a6100" stroke-width="1.2"/>
    <text class="b am" x="14" y="263" font-size="14">よくある誤解 ― 「砕石を運ぶから（砕）」は誤りです</text>
    <text class="gy" x="14" y="280" font-size="12">規則6条2号は「経営する事業の種類」と定めており、運ぶ物ではなく営んでいる事業で決まります。（砕）は砕石プラントを持つ者の記号で、親会社・株式会社石名坂（真荷主）の側です。</text>
  </svg>
</figure>
'''

# ---------- 図14  ダンプ車両の点検ポイント ----------
F['fig14'] = '''<figure class="fig">
  <div class="figt">図14　大型ダンプで見るべき4か所</div>
  <svg viewBox="0 0 1000 300" role="img" aria-label="ダンプの点検ポイント">
    <rect x="52" y="60" width="252" height="40" rx="2" fill="none" stroke="#a8261c" stroke-width="2" stroke-dasharray="6 4"/>
    <text class="b rd" x="178" y="86" font-size="15" text-anchor="middle">さし枠（かさ上げ）</text>
    <path d="M60,100 L60,110 M296,100 L296,110" stroke="#a8261c" stroke-width="3"/>
    <rect x="52" y="104" width="252" height="86" rx="3" fill="#dbe3ea" stroke="#16395c" stroke-width="2"/>
    <rect x="96" y="128" width="164" height="42" rx="2" fill="#ffffff" stroke="#1b1b1b" stroke-width="1.8"/>
    <text class="b" x="178" y="157" font-size="19" text-anchor="middle" fill="#1b1b1b">岩手（営）12345</text>
    <path d="M308,120 L376,120 L410,166 L410,190 L308,190 z" fill="#dbe3ea" stroke="#16395c" stroke-width="2"/>
    <rect x="322" y="130" width="46" height="30" rx="2" fill="#ffffff" stroke="#16395c" stroke-width="1.4"/>
    <circle cx="345" cy="176" r="9" fill="#fdf4e2" stroke="#8a6100" stroke-width="1.8"/>
    <text class="b am" x="345" y="181" font-size="11" text-anchor="middle">計</text>
    <circle cx="100" cy="200" r="19" fill="#ffffff" stroke="#16395c" stroke-width="2.4"/>
    <circle cx="228" cy="200" r="19" fill="#ffffff" stroke="#16395c" stroke-width="2.4"/>
    <circle cx="272" cy="200" r="19" fill="#ffffff" stroke="#16395c" stroke-width="2.4"/>
    <circle cx="378" cy="200" r="19" fill="#ffffff" stroke="#16395c" stroke-width="2.4"/>
    <rect x="30" y="226" width="400" height="30" rx="3" fill="#f2f5f8" stroke="#c9d3dc"/>
    <text class="nv" x="230" y="246" font-size="13" text-anchor="middle">最大積載量 ÷ 荷台容積 ＜ 1.5t／m³ の荷台は備えてはならない</text>
    <path d="M304,80 L470,80" stroke="#a8261c" stroke-width="1.2" stroke-dasharray="3 3"/>
    <path d="M264,149 L470,149" stroke="#98a5b0" stroke-width="1.2" stroke-dasharray="3 3"/>
    <path d="M354,176 L470,176" stroke="#8a6100" stroke-width="1.2" stroke-dasharray="3 3"/>
    <path d="M430,241 L470,241" stroke="#98a5b0" stroke-width="1.2" stroke-dasharray="3 3"/>
    <rect x="480" y="56" width="520" height="52" rx="3" fill="#fbecea" stroke="#a8261c" stroke-width="1.2"/>
    <text class="b rd" x="494" y="76" font-size="14">さし枠は「取付金具があるだけ」でも違反</text>
    <text x="494" y="96" font-size="12.5">保安基準27条2項・細目告示193条2項。枠を外していても金具が残っていれば違反です</text>
    <rect x="480" y="120" width="520" height="52" rx="3" fill="#f2f5f8" stroke="#98a5b0" stroke-width="1.2"/>
    <text class="b nv" x="494" y="140" font-size="14">表示番号は荷台の両側面と後面の3面</text>
    <text x="494" y="160" font-size="12.5">ダンプ規制法4条・規則6条。後面の脱落・かすれが最も多い指摘事項です</text>
    <rect x="480" y="184" width="520" height="52" rx="3" fill="#fdf4e2" stroke="#8a6100" stroke-width="1.2"/>
    <text class="b am" x="494" y="204" font-size="14">自重計（ダンプ規制法6条）</text>
    <text x="494" y="224" font-size="12.5">技術基準適合証で確認。計量法の検定対象ではありません。故障放置は法21条1号の罰金</text>
    <rect x="480" y="248" width="520" height="52" rx="3" fill="#fbecea" stroke="#a8261c" stroke-width="1.2"/>
    <text class="b rd" x="494" y="268" font-size="14">土砂禁ダンプで砕石を運んではいけない</text>
    <text x="494" y="288" font-size="12.5">車検証備考欄の「土砂等運搬禁止車両」の記載がないことを5台すべてで確認してください</text>
  </svg>
  <div class="figc">砕石はダンプ規制法2条1項の「土砂等」に明記されています。土砂禁ダンプで運ぶと、①保安基準27条2項違反　②表示番号なしでの運搬＝法4条違反　③満載すれば構造上必ず過積載、の3つが同時に成立します。</div>
</figure>
'''

# ---------- 図15  積込み前の30秒チェック ----------
def gate(i, q, sub, ng1, ng2):
    y = i*86
    out = [
      '<rect x="0" y="%d" width="440" height="68" rx="4" fill="#e6edf4" stroke="#2a5c8a" stroke-width="1.5"/>' % y,
      '<text class="b n2" x="14" y="%d" font-size="13">CHECK %d</text>' % (y+20, i+1),
      '<text class="b nv" x="14" y="%d" font-size="15">%s</text>' % (y+41, q),
      '<text class="gy" x="14" y="%d" font-size="11.5">%s</text>' % (y+59, sub),
      '<line x1="440" y1="%d" x2="528" y2="%d" stroke="#a8261c" stroke-width="1.6" marker-end="url(#fa15r)"/>' % (y+34, y+34),
      '<text class="b rd" x="484" y="%d" font-size="12" text-anchor="middle">いいえ</text>' % (y+26),
      '<rect x="540" y="%d" width="460" height="68" rx="4" fill="#fbecea" stroke="#a8261c" stroke-width="1.2"/>' % y,
      '<text class="b rd" x="554" y="%d" font-size="14.5">%s</text>' % (y+28, ng1),
      '<text x="554" y="%d" font-size="12">%s</text>' % (y+50, ng2)]
    if i < 2:
        out.append('<line x1="220" y1="%d" x2="220" y2="%d" stroke="#186b3f" stroke-width="1.8" marker-end="url(#fa15g)"/>' % (y+68, y+84))
        out.append('<text class="b gr" x="232" y="%d" font-size="12">はい</text>' % (y+81))
    return '\n    '.join(out)

F['fig15'] = '''<figure class="fig">
  <div class="figt">図15　積込み前の30秒チェック ― 3つ揃って初めて「傭車」</div>
  <svg viewBox="0 0 1000 424" role="img" aria-label="積込み前チェック">
    <defs>
      <marker id="fa15r" markerWidth="10" markerHeight="8" refX="9.5" refY="4" orient="auto"><path d="M0,0 L10,4 L0,8 z" fill="#a8261c"/></marker>
      <marker id="fa15g" markerWidth="10" markerHeight="8" refX="9.5" refY="4" orient="auto"><path d="M0,0 L10,4 L0,8 z" fill="#186b3f"/></marker>
    </defs>
    ''' + gate(0, '相手は緑ナンバーか', '許可証の写しを台帳で確認。ゼッケンの有無では判断できない', '積ませない', '貨運法65条の2／100万円以下の罰金（75条14号）・両罰80条') + '''
    ''' + gate(1, '指示を出すのは相手方の運行管理者か', '自社の配車が運転者に直接指示していないか', '偽装請負＝労働者供給・労働者派遣', '職安法44条／昭61労働省告示37号') + '''
    ''' + gate(2, '車検証の使用者は相手方か', '「自家用・事業用の別」欄もあわせて確認', '名義貸し・事業の貸渡し', '貨運法28条／事業停止30日、3年内の再違反で許可取消') + '''
    <line x1="220" y1="240" x2="220" y2="258" stroke="#186b3f" stroke-width="1.8" marker-end="url(#fa15g)"/>
    <text class="b gr" x="232" y="255" font-size="12">はい</text>
    <rect x="0" y="262" width="1000" height="44" rx="4" fill="#eaf5ee" stroke="#186b3f" stroke-width="1.5"/>
    <text class="b gr" x="14" y="290" font-size="16">3つ揃って初めて傭車。そのうえで、その日のうちに次の4点を回してください。</text>
    ''' + '\n    '.join(
      ['<rect x="%d" y="322" width="238" height="72" rx="3" fill="#ffffff" stroke="#2a5c8a" stroke-width="1.2"/>\n    '
       '<text class="b n2" x="%d" y="344" font-size="13.5">%s</text>\n    '
       '<text x="%d" y="364" font-size="11.5">%s</text>\n    '
       '<text class="gy" x="%d" y="382" font-size="11.5">%s</text>' % (i*254, i*254+12, a, i*254+12, b, i*254+12, c)
       for i, (a, b, c) in enumerate([
         ('① 真荷主への事前通知', '利用運送を行う旨', '標準約款17条'),
         ('② 法24条2項書面の交付', '往復方式は不可。一方向で交付', '貨運法24条2項'),
         ('③ 元請連絡事項の通知', '連絡先・真荷主の商号・請負階層', '貨運法24条の5第2項'),
         ('④ 実運送体制管理簿に記載', '砕石は全運行が1.5トン基準超', '貨運法24条の5第1項')])]) + '''
    <text class="b rd" x="0" y="416" font-size="12.5">積む物が廃棄物なら、これに加えて排出事業者の事前の書面承諾が必要です（廃掃法14条16項・令6条の12第1号 → 54章）。</text>
  </svg>
</figure>
'''

# ---------- 図16  二階建て ----------
F['fig16'] = '''<figure class="fig">
  <div class="figt">図16　産廃を他社ダンプに運ばせると、規制が二階建てになる</div>
  <svg viewBox="0 0 1000 356" role="img" aria-label="貨運法と廃掃法の二階建て">
    <path d="M300,6 L640,6 L662,30 L278,30 z" fill="#16395c"/>
    <text class="b w" x="470" y="24" font-size="15" text-anchor="middle">産業廃棄物を他社の大型ダンプに運ばせる</text>
    <rect x="280" y="38" width="380" height="122" rx="3" fill="#fdf4e2" stroke="#8a6100" stroke-width="1.8"/>
    <text class="b am" x="296" y="60" font-size="16">2階　廃棄物処理法</text>
    <text x="296" y="82" font-size="13">再委託（14条16項）― 原則禁止</text>
    <text class="b am" x="296" y="102" font-size="13">令6条の12の基準を全部満たすこと</text>
    <text class="gy" x="296" y="120" font-size="12">核は排出事業者の事前の書面による承諾（1号）</text>
    <text class="rd" x="296" y="138" font-size="12">違反＝法26条1号</text>
    <text class="rd" x="296" y="154" font-size="11.5">3年以下の拘禁刑若しくは300万円以下の罰金、又は併科</text>
    <rect x="280" y="168" width="380" height="122" rx="3" fill="#e6edf4" stroke="#2a5c8a" stroke-width="1.8"/>
    <text class="b n2" x="296" y="190" font-size="16">1階　貨物自動車運送事業法</text>
    <text x="296" y="212" font-size="13">貨物自動車利用運送（2条7項）</text>
    <text class="b n2" x="296" y="232" font-size="13">事業計画変更認可（9条1項）</text>
    <text class="gy" x="296" y="250" font-size="12">ほかに法12条の書面相互交付・法24条の5の管理簿も発生</text>
    <text class="rd" x="296" y="268" font-size="12">違反＝行政処分 初違反10日車</text>
    <text class="rd" x="296" y="284" font-size="11.5">無認可の事業計画変更は75条2号・100万円以下の罰金</text>
    <rect x="272" y="298" width="396" height="20" rx="2" fill="#16395c"/>
    <rect x="0" y="38" width="262" height="122" rx="3" fill="#ffffff" stroke="#c9d3dc"/>
    <text class="b nv" x="14" y="60" font-size="14">砕石・砂利・砂・残土</text>
    <text class="gr" x="14" y="84" font-size="13">有価物なので1階だけ</text>
    <text class="gy" x="14" y="106" font-size="12">これまでの章はこの前提でした。</text>
    <text class="gy" x="14" y="124" font-size="12">建設発生土も廃棄物ではありません</text>
    <text class="gy" x="14" y="142" font-size="12">（昭46環整43号）</text>
    <rect x="0" y="168" width="262" height="122" rx="3" fill="#eaf5ee" stroke="#186b3f"/>
    <text class="b gr" x="14" y="190" font-size="14">自社ダンプで直行運搬</text>
    <text x="14" y="214" font-size="13">利用運送ではないので</text>
    <text class="b gr" x="14" y="236" font-size="13">1階も2階も不要</text>
    <text class="gy" x="14" y="258" font-size="12">岩手県内で積み、岩手県内で卸す</text>
    <text class="gy" x="14" y="276" font-size="12">かぎり。これが当社の基本形です</text>
    <rect x="680" y="38" width="320" height="252" rx="3" fill="#fbecea" stroke="#a8261c" stroke-width="1.2"/>
    <text class="b rd" x="694" y="62" font-size="15">一方を満たしても</text>
    <text class="b rd" x="694" y="83" font-size="15">他方の違法は治りません</text>
    <text x="694" y="110" font-size="12">「産廃の許可は持っているから大丈夫」も</text>
    <text x="694" y="128" font-size="12">「事業計画に利用運送を入れたから大丈夫」も、</text>
    <text x="694" y="146" font-size="12">どちらも<tspan class="b rd">片方だけ</tspan>です。</text>
    <line x1="694" y1="162" x2="986" y2="162" stroke="#e5c6c2"/>
    <text class="b rd" x="694" y="186" font-size="13">傭車先は緑ナンバーでなければなりません</text>
    <text class="gy" x="694" y="208" font-size="12">令和8年3月16日 国交省 事務連絡</text>
    <text class="gy" x="694" y="226" font-size="12">「収集又は処分を伴わない廃棄物の運搬行為</text>
    <text class="gy" x="694" y="244" font-size="12">のみ」を行う場合には貨運法の許可等が必要</text>
    <text class="gr" x="694" y="266" font-size="12">当社は緑なので、この論点で悩む必要は</text>
    <text class="gr" x="694" y="284" font-size="12">ありません</text>
    <text class="gy" x="0" y="336" font-size="12">※ 許可権者も別です ― 産廃収集運搬業許可は<tspan class="b nv">原則 都道府県知事</tspan>。指定都市・中核市の長になるのは「その市の区域内のみで事業を行う場合」と</text>
    <text class="gy" x="0" y="352" font-size="12">「積替え保管を行う区域」の2類型だけです（令27条1項5号括弧書）。一般貨物の許可権者は国土交通大臣（地方運輸局長）です。</text>
  </svg>
</figure>
'''

# ---------- 図17  令6条の12の4要件 ----------
def req(i, no, title, body, note):
    x = i*254
    return '\n    '.join([
      '<rect x="%d" y="0" width="238" height="158" rx="3" fill="#ffffff" stroke="#2a5c8a" stroke-width="1.3"/>' % x,
      '<rect x="%d" y="0" width="238" height="28" rx="3" fill="#2a5c8a"/><rect x="%d" y="14" width="238" height="14" fill="#2a5c8a"/>' % (x, x),
      '<text class="b w" x="%d" y="20" font-size="14" text-anchor="middle">%s</text>' % (x+119, no),
      '<text class="b nv" x="%d" y="48" font-size="13.5">%s</text>' % (x+12, title),
      ] + ['<text x="%d" y="%d" font-size="11.5">%s</text>' % (x+12, 70+j*17, ln) for j, ln in enumerate(body)]
      + ['<text class="gy" x="%d" y="%d" font-size="11">%s</text>' % (x+12, 70+len(body)*17+j*15, ln) for j, ln in enumerate(note)]
      + ['<path d="M%d,158 L%d,180" stroke="#2a5c8a" stroke-width="1.6" marker-end="url(#fa17)"/>' % (x+119, x+119)])

F['fig17'] = '''<figure class="fig">
  <div class="figt">図17　再委託の要件 ― 令6条の12の4つを「全部」満たしてはじめて適法</div>
  <svg viewBox="0 0 1000 314" role="img" aria-label="令6条の12の4要件">
    <defs><marker id="fa17" markerWidth="10" markerHeight="8" refX="9.5" refY="4" orient="auto">
      <path d="M0,0 L10,4 L0,8 z" fill="#2a5c8a"/></marker></defs>
    ''' + req(0, '1号', '排出事業者の事前の書面承諾', ['あらかじめ再受託者の氏名・名称と、', '再委託が基準に適合することを', '明らかにしたうえで承諾を受ける'], ['記載事項は規則10条の6の6', '★案件ごとに再受託者を特定して', '　取る必要があります']) + '''
    ''' + req(1, '2号', '引渡し時の文書交付', ['排出事業者との委託契約書に記載', 'された令6条の2第4号のイ〜ハ', '及びホを記載した文書を交付'], ['ニ（輸入廃棄物である旨）は', '交付事項に含まれません']) + '''
    ''' + req(2, '3号', '輸入廃棄物の制限', ['法15条の4の5第1項の許可を受けて', '輸入された廃棄物の処分又は再生を', '委託しないこと'], ['「処理終了の通知」は令6条の12には', 'なく、規則8条の4の2第8号です']) + '''
    ''' + req(3, '4号', '委託基準の準用', ['令6条の2の1号・2号・4号・5号の例', '① 再受託者がその産廃の運搬を業と', '　 して行うことができる者であること', '② 書面による委託契約＋許可証の写し'], ['規則8条の4・8条の4の2']) + '''
    <rect x="0" y="186" width="1000" height="44" rx="4" fill="#eaf5ee" stroke="#186b3f" stroke-width="1.5"/>
    <text class="b gr" x="14" y="214" font-size="16">4つ全部を満たして、はじめて再委託できます（廃掃法14条16項ただし書）</text>
    <rect x="0" y="240" width="490" height="72" rx="3" fill="#fbecea" stroke="#a8261c" stroke-width="1.2"/>
    <text class="b rd" x="14" y="260" font-size="14">1つでも欠けたら14条16項違反</text>
    <text x="14" y="280" font-size="12">法26条1号／3年以下の拘禁刑若しくは300万円以下の罰金、又は併科</text>
    <text x="14" y="300" font-size="12">法人には法32条の両罰規定</text>
    <rect x="510" y="240" width="490" height="72" rx="3" fill="#fdf4e2" stroke="#8a6100" stroke-width="1.2"/>
    <text class="b am" x="524" y="260" font-size="14">「緊急時に限る」は法令の要件ではありません</text>
    <text x="524" y="280" font-size="12">令6条の12に緊急性の要件はありません。東京都・大阪府の方針は</text>
    <text x="524" y="300" font-size="12">行政指導上の運用です（岩手県の手引にも記載なし。照会事項Q9）</text>
  </svg>
  <div class="figc">保存義務も分かれます ― <strong>再受託者との委託契約書は当社が5年</strong>（規則8条の4の3）、<strong>承諾書の写しは排出事業者が5年</strong>（令6条の2第6号・規則8条の4の4）。当社にも写しを保存しておくことを勧めます。</div>
</figure>
'''

# ---------- 図18  マニフェストの流れ ----------
MX = {1: 160, 2: 500, 3: 840}
def mmsg(y, a, b, no, label, sub):
    x1, x2 = MX[a], MX[b]
    d = -1 if x2 < x1 else 1
    cx = (x1+x2)/2.0
    return '\n    '.join([
      '<text class="b nv" x="14" y="%d" font-size="15">%s</text>' % (y+4, no),
      '<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#16395c" stroke-width="1.8" marker-end="url(#fa18)"/>' % (x1+12*d, y, x2-14*d, y),
      '<text class="b nv" x="%.1f" y="%d" font-size="14" text-anchor="middle">%s</text>' % (cx, y-9, label),
      '<text class="gy" x="%.1f" y="%d" font-size="12" text-anchor="middle">%s</text>' % (cx, y+17, sub)])

F['fig18'] = '''<figure class="fig">
  <div class="figt">図18　再委託のとき、管理票（マニフェスト）はこう回ります</div>
  <svg viewBox="0 0 1000 290" role="img" aria-label="再委託時のマニフェストの流れ">
    <defs><marker id="fa18" markerWidth="10" markerHeight="8" refX="9.5" refY="4" orient="auto">
      <path d="M0,0 L10,4 L0,8 z" fill="#16395c"/></marker></defs>
    <rect x="10" y="0" width="300" height="46" rx="3" fill="#ffffff" stroke="#2a5c8a" stroke-width="1.4"/>
    <text class="b n2" x="160" y="20" font-size="15" text-anchor="middle">排出事業者</text>
    <text class="gy" x="160" y="37" font-size="12" text-anchor="middle">建設工事なら元請業者（法21条の3第1項）</text>
    <rect x="350" y="0" width="300" height="46" rx="3" fill="#16395c"/>
    <text class="b w" x="500" y="20" font-size="15" text-anchor="middle">当社（受託者）</text>
    <text class="w" x="500" y="37" font-size="12" text-anchor="middle" opacity="0.85">有限会社石名坂商事（緑）</text>
    <rect x="690" y="0" width="300" height="46" rx="3" fill="#ffffff" stroke="#186b3f" stroke-width="1.4"/>
    <text class="b gr" x="840" y="20" font-size="15" text-anchor="middle">再受託者</text>
    <text class="gy" x="840" y="37" font-size="12" text-anchor="middle">緑ナンバー＋当該品目・区域の産廃許可</text>
    <line x1="160" y1="46" x2="160" y2="226" stroke="#c9d3dc" stroke-dasharray="4 4"/>
    <line x1="500" y1="46" x2="500" y2="226" stroke="#c9d3dc" stroke-dasharray="4 4"/>
    <line x1="840" y1="46" x2="840" y2="226" stroke="#c9d3dc" stroke-dasharray="4 4"/>
    ''' + mmsg(84, 1, 2, '①', '管理票を交付', '法12条の3第1項') + '''
    ''' + mmsg(134, 2, 3, '②', '交付された管理票をそのまま引き渡す', '当社は運搬受託者欄に記載しません') + '''
    <text class="b nv" x="14" y="188" font-size="15">③</text>
    <rect x="690" y="162" width="300" height="42" rx="3" fill="#eaf5ee" stroke="#186b3f" stroke-width="1.2"/>
    <text class="b gr" x="840" y="180" font-size="13.5" text-anchor="middle">運搬を受託した者の氏名等を訂正</text>
    <text class="gy" x="840" y="197" font-size="12" text-anchor="middle">訂正するのは再受託者です</text>
    ''' + mmsg(232, 3, 1, '④', '運搬終了後、管理票の写しを排出事業者へ送付', '運搬終了の日から10日以内（規則8条の23）') + '''
    <rect x="0" y="258" width="1000" height="32" rx="3" fill="#eaf5ee" stroke="#186b3f" stroke-width="1.2"/>
    <text class="b gr" x="14" y="278" font-size="13">法12条の4第3項（運搬を終了していないのに終了した旨を報告すること）との衝突は起きません ― 写しを送るのは実際に運んだ再受託者だからです。</text>
  </svg>
  <div class="figc">根拠は<strong>平成23年3月17日 環廃産第110317001号「産業廃棄物管理票制度の運用について」第1の3(1)①③</strong>。施行規則を全文走査しても「再受託者」欄は法定されておらず、再委託時に追加で回る票も存在しません。<span class="rd" style="font-weight:700">電子マニフェスト（JWNET）の再委託専用機能は確認できませんでした</span>（「多区間」は積替え保管施設を経由する場合のもの）。電子で扱う運用はJWNETと岩手県に確認してください（照会事項）。虚偽記載・未交付等は法27条の2（1年以下の拘禁刑又は100万円以下の罰金）。</div>
</figure>
'''

# ---------- 図19  建設工事の排出事業者 ----------
F['fig19'] = '''<figure class="fig">
  <div class="figt">図19　建設工事に伴う廃棄物 ― 誰が排出事業者か</div>
  <svg viewBox="0 0 1000 302" role="img" aria-label="建設工事の排出事業者の判定">
    <defs><marker id="fa19" markerWidth="10" markerHeight="8" refX="9.5" refY="4" orient="auto">
      <path d="M0,0 L10,4 L0,8 z" fill="#2a5c8a"/></marker></defs>
    <rect x="0" y="0" width="1000" height="40" rx="3" fill="#16395c"/>
    <text class="b w" x="500" y="25" font-size="16" text-anchor="middle">建設工事に伴って生じる廃棄物　―　廃掃法21条の3第1項により、原則として元請業者が排出事業者</text>
    <path d="M500,40 L500,54 M166,54 L834,54 M166,54 L166,68 M500,54 L500,68 M834,54 L834,68" fill="none" stroke="#2a5c8a" stroke-width="1.5"/>
    <path d="M161,68 L166,78 L171,68 z M495,68 L500,78 L505,68 z M829,68 L834,78 L839,68 z" fill="#2a5c8a"/>
    <rect x="0" y="80" width="322" height="158" rx="3" fill="#eaf5ee" stroke="#186b3f" stroke-width="1.4"/>
    <rect x="0" y="80" width="322" height="28" rx="3" fill="#186b3f"/><rect x="0" y="94" width="322" height="14" fill="#186b3f"/>
    <text class="b w" x="161" y="100" font-size="14.5" text-anchor="middle">原則 ― 元請と直接契約する</text>
    <text class="b gr" x="14" y="130" font-size="13.5">排出事業者＝元請業者</text>
    <text x="14" y="152" font-size="12.5">当社は元請から直接受託します。</text>
    <text x="14" y="172" font-size="12.5">委託基準・マニフェスト交付義務を</text>
    <text x="14" y="192" font-size="12.5">負うのは元請です。</text>
    <text class="gy" x="14" y="216" font-size="12">下請から「うちの現場のがれきを運んで」と</text>
    <text class="gy" x="14" y="232" font-size="12">頼まれたら、まず誰が排出事業者かを確認</text>
    <rect x="339" y="80" width="322" height="158" rx="3" fill="#fdf4e2" stroke="#8a6100" stroke-width="1.4"/>
    <rect x="339" y="80" width="322" height="28" rx="3" fill="#8a6100"/><rect x="339" y="94" width="322" height="14" fill="#8a6100"/>
    <text class="b w" x="500" y="100" font-size="14.5" text-anchor="middle">例外 ― 21条の3第4項本文</text>
    <text class="b am" x="353" y="130" font-size="13.5">下請負人を事業者とみなす</text>
    <text x="353" y="152" font-size="12.5">下請が例外的にその運搬又は処分を</text>
    <text x="353" y="172" font-size="12.5">他人に委託せざるを得なくなった場合。</text>
    <text x="353" y="192" font-size="12.5">下請が委託基準・マニフェスト交付</text>
    <text x="353" y="212" font-size="12.5">義務を負います。</text>
    <text class="gr" x="353" y="232" font-size="12">下請から受託する形が一律に違法なのではありません</text>
    <rect x="678" y="80" width="322" height="158" rx="3" fill="#e6edf4" stroke="#2a5c8a" stroke-width="1.4"/>
    <rect x="678" y="80" width="322" height="28" rx="3" fill="#2a5c8a"/><rect x="678" y="94" width="322" height="14" fill="#2a5c8a"/>
    <text class="b w" x="839" y="100" font-size="14.5" text-anchor="middle">同項括弧書 ― 下請が産廃許可を持つ</text>
    <text class="b n2" x="692" y="130" font-size="13.5">「みなし」から外れます</text>
    <text x="692" y="152" font-size="12.5">その下請が元請から受託したものを</text>
    <text x="692" y="172" font-size="12.5">さらに他人に回すときは、</text>
    <text class="b n2" x="692" y="192" font-size="12.5">14条16項の再委託ルートになります。</text>
    <text class="gy" x="692" y="214" font-size="12">＝ 令6条の12の4要件を全部満たすこと</text>
    <text class="gy" x="692" y="230" font-size="12">（54章の図17）</text>
    <rect x="0" y="248" width="1000" height="54" rx="3" fill="#fbecea" stroke="#a8261c" stroke-width="1.2"/>
    <text class="b rd" x="14" y="270" font-size="13.5">当社が受託者として受けたものを、さらに他社へ回すことはできません</text>
    <text x="14" y="290" font-size="12.5">14条16項ただし書は「事業者から委託を受けた」場合に限られるため、再々委託は適用除外の対象外です（53章 #9）。</text>
  </svg>
</figure>
'''
