# -*- coding: utf-8 -*-
"""量子記事の挿絵につける情報（ファイル名・代替テキスト等）の一覧を作る。

画像が上がってくるたび SHOTS の url を埋めて、このスクリプトを流し直す。
"""
import base64
import html
import io
import os
import urllib.request

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'gazou-seo.html')
CACHE = os.path.join(HERE, '.thumb-cache')


def thumb_data_uri(url, width=768):
    """本体を取ってきて、こちらで縮めて data URI にする。

    確認用ページは外部の画像を読み込めないため、埋め込む必要がある。
    サイトが作る縮小版（-768x429 など）の名前は、絵の縦横比で変わる。
    文字の帯を足してから比が変わり、決め打ちの名前では取れなくなったので、
    本体を取って自分で縮める作りに変えた。これなら比が何であれ通る。
    """
    if not url:
        return u''
    if not os.path.isdir(CACHE):
        os.makedirs(CACHE)
    key = os.path.join(CACHE, '%d-%s' % (width, os.path.basename(url)))
    if not os.path.exists(key):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                raw = r.read()
        except Exception as e:
            print('  ! 取得できず（%s）: %s' % (e, url))
            return u''
        im = Image.open(io.BytesIO(raw)).convert('RGB')
        im = im.resize((width, max(1, int(round(width * im.size[1] / float(im.size[0]))))),
                       Image.LANCZOS)
        im.save(key, 'JPEG', quality=80, optimize=True)
    raw = open(key, 'rb').read()
    return u'data:image/jpeg;base64,' + base64.b64encode(raw).decode('ascii')


SHOTS = [
    dict(
        n=1, part=u'前編', where=u'冒頭／アイキャッチ',
        title=u'冷凍機',
        url=u'https://www.ishinazaka.co.jp/common/files/uploads/2026/09/'
            u'01-quantum-computer-dilution-refrigerator.jpg',
        fname=u'01-quantum-computer-dilution-refrigerator.jpg',
        alt=u'超電導方式の量子コンピュータを冷やす希釈冷凍機のイメージ図。'
            u'銅色の円盤が段状に吊り下がり、細い同軸ケーブルの束が下へ伸びている',
        mtitle=u'超電導方式の量子コンピュータの希釈冷凍機（イメージ図）',
        caption=u'超電導方式の量子コンピュータを冷やす装置。すべての方式がこうなっている'
                u'わけではありません。イメージ図（生成AIで作成）',
        desc=u'「量子コンピュータとは何か【前編】」のアイキャッチ。'
             u'生成AIで作成したイメージ図であり、実在の装置の写真ではありません。',
        note=u'<strong>dilution refrigerator</strong> は「希釈冷凍機」の正式な英語名です。',
    ),
    dict(
        n=2, part=u'前編', where=u'「1984年から、一本の線がつながっています」',
        title=u'量子ビットのチップ',
        url=u'https://www.ishinazaka.co.jp/common/files/uploads/2026/09/'
            u'02-superconducting-qubit-chip.jpg',
        fname=u'02-superconducting-qubit-chip.jpg',
        alt=u'超電導方式の量子ビットを載せたチップのイメージ図。十字の形をした電極が'
            u'格子状に並び、チップの縁から細い金線が周囲の基板へ弧を描いている',
        mtitle=u'超電導方式の量子ビットを載せたチップ（イメージ図）',
        caption=u'超電導方式の量子ビットを載せたチップ。1999年にNECが作った回路の'
                u'子孫にあたります。イメージ図（生成AIで作成）',
        desc=u'「量子コンピュータとは何か【前編】」の挿絵。'
             u'生成AIで作成したイメージ図であり、実在の装置の写真ではありません。',
        note=u'表面の十字の形は、実際の超電導量子ビットの電極の形です。'
             u'<strong>qubit</strong> は「量子ビット」の英語です。',
    ),
    dict(
        n=3, part=u'前編', where=u'「もうひとつ、圧倒的に得意なことがあります」',
        title=u'矢印を持った分子',
        url=u'https://www.ishinazaka.co.jp/common/files/uploads/2026/09/'
            u'03-molecule-electron-arrows.jpg',
        fname=u'03-molecule-electron-arrows.jpg',
        alt=u'分子の中の電子を矢印で表したイメージ図。球と棒でできた分子のまわりに'
            u'淡い雲が広がり、その中に向きの異なる小さな矢印が散らばっている',
        mtitle=u'分子の中の電子と「矢印」（イメージ図）',
        caption=u'分子の中の電子も「矢印」を持っています。だから量子の機械と相性が'
                u'よいのです。イメージ図（生成AIで作成）',
        desc=u'「量子コンピュータとは何か【前編】」の挿絵。'
             u'生成AIで作成したイメージ図であり、実在の装置の写真ではありません。',
        note=u'記事の図（矢印の打ち消し合い）と同じ矢印が出るように頼んであります。',
    ),
    dict(
        n=4, part=u'前編', where=u'「なぜ、普通のコンピュータでは追いつけないのか」',
        title=u'スーパーコンピュータの列',
        url=u'https://www.ishinazaka.co.jp/common/files/uploads/2026/09/'
            u'04-supercomputer-server-aisle.jpg',
        fname=u'04-supercomputer-server-aisle.jpg',
        alt=u'スーパーコンピュータの並ぶ通路のイメージ図。同じ形の背の高い装置が'
            u'両側に果てしなく続いている',
        mtitle=u'スーパーコンピュータの並ぶ通路（イメージ図）',
        caption=u'50量子ビットを普通のコンピュータで再現するには、1ペタバイトを超える'
                u'メモリが要りました。イメージ図（生成AIで作成）',
        desc=u'「量子コンピュータとは何か【前編】」の挿絵。'
             u'生成AIで作成したイメージ図であり、実在の装置の写真ではありません。',
        note=u'',
    ),
    dict(
        n=5, part=u'後編', where=u'冒頭／アイキャッチ',
        title=u'四つの違う装置',
        url=u'https://www.ishinazaka.co.jp/common/files/uploads/2026/09/'
            u'05-quantum-computer-four-modalities.jpg',
        fname=u'05-quantum-computer-four-modalities.jpg',
        alt=u'量子コンピュータの四つの方式を並べたイメージ図。冷凍機、レーザーの通る'
            u'真空容器、鏡を並べた光学台、探針の下のシリコンチップが一台ずつ置かれている',
        mtitle=u'量子コンピュータの主な方式（イメージ図）',
        caption=u'作り方は六通りあり、まだ本命が決まっていません。主な方式のイメージ図'
                u'（生成AIで作成）',
        desc=u'「量子コンピュータとは何か【後編】」のアイキャッチ。'
             u'生成AIで作成したイメージ図であり、実在の装置の写真ではありません。',
        note=u'',
    ),
    dict(
        n=6, part=u'後編', where=u'「本命は、分子と材料のシミュレーションです」（7番と対）',
        title=u'アンモニアの工場',
        url=u'https://www.ishinazaka.co.jp/common/files/uploads/2026/09/'
            u'06-ammonia-plant-haber-bosch.jpg',
        fname=u'06-ammonia-plant-haber-bosch.jpg',
        alt=u'アンモニアを作る工場のイメージ図。背の高い反応塔と太い配管が並び、'
            u'蒸気が立ちのぼっている',
        mtitle=u'アンモニアを合成する工場（イメージ図）',
        caption=u'肥料のもとになるアンモニアは、400〜500度・数百気圧で作られています。'
                u'イメージ図（生成AIで作成）',
        desc=u'「量子コンピュータとは何か【後編】」の挿絵。7番（根粒）と対で使います。'
             u'生成AIで作成したイメージ図であり、実在の設備の写真ではありません。',
        note=u'<strong>Haber-Bosch</strong> は「ハーバー・ボッシュ法」の英語表記です。',
    ),
    dict(
        n=7, part=u'後編', where=u'6番のすぐ下。対にして使う',
        title=u'マメ科の根粒',
        url=u'https://www.ishinazaka.co.jp/common/files/uploads/2026/09/'
            u'Gemini_Generated_Image_ck7649ck7649ck76.jpg',
        fname=u'07-soybean-root-nodules.jpg',
        alt=u'マメ科の植物の根と根粒のイメージ図。細い根に沿って丸い粒が連なり、'
            u'土がついたまま持ち上げられている',
        mtitle=u'マメ科の根につく根粒（イメージ図）',
        caption=u'マメ科の根につく根粒。ここでは常温・常圧で、同じことが行われています。'
                u'しくみはまだ解明されていません。イメージ図（生成AIで作成）',
        desc=u'「量子コンピュータとは何か【後編】」の挿絵。6番（工場）と対で使います。'
             u'生成AIで作成したイメージ図であり、実物の写真ではありません。',
        note=u'<strong>root nodule</strong> は「根粒」の英語です。',
    ),
    dict(
        n=8, part=u'後編', where=u'「セキュリティのための機械ではありません」',
        title=u'錠前の付け替え', url=u'',
        fname=u'08-padlock-old-and-new.jpg',
        alt=u'古い真鍮の南京錠と新しい鋼の南京錠を並べたイメージ図。'
            u'左は開いており、右は閉じている',
        mtitle=u'古い錠前と新しい錠前（イメージ図）',
        caption=u'量子コンピュータは暗号を「壊す側」です。国は2035年を目処に、'
                u'錠前の付け替えを進めています。イメージ図（生成AIで作成）',
        desc=u'「量子コンピュータとは何か【後編】」の挿絵。'
             u'生成AIで作成したイメージ図であり、実物の写真ではありません。',
        note=u'',
    ),
]

FIELDS = [
    ('fname', u'ファイル名', u'入れ直すときのファイル名', True),
    ('alt', u'代替テキスト（alt）', u'メディアライブラリ／いちばん効く欄', False),
    ('mtitle', u'タイトル', u'メディアライブラリ', False),
    ('caption', u'キャプション', u'記事の画像の下に出る文', False),
    ('desc', u'説明', u'メディアライブラリ', False),
]

E = html.escape


def card(shot):
    p = []
    up = bool(shot['url'])
    p.append(u'<div class="shot%s">' % (u'' if up else u' pending'))
    p.append(u'<header>')
    p.append(u'<span class="num">%d</span>' % shot['n'])
    p.append(u'<h3>%s</h3>' % E(shot['title']))
    p.append(u'<p class="where">%s ／ %s</p>' % (E(shot['part']), E(shot['where'])))
    p.append(u'<p class="state">%s</p>'
             % (u'アップロード済み' if up else u'まだアップロードされていません'))
    p.append(u'</header>')
    if up:
        uri = thumb_data_uri(shot['url'])
        if uri:
            p.append(u'<div class="preview"><img src="%s" alt="%s" loading="lazy"></div>'
                     % (uri, E(shot['alt'])))
    p.append(u'<div class="fields">')
    for key, label, where, mono in FIELDS:
        pid = u'f%d%s' % (shot['n'], key)
        p.append(u'<div class="f">')
        p.append(u'<p class="label">%s<span>%s</span></p>' % (E(label), E(where)))
        p.append(u'<pre id="%s"%s>%s</pre>'
                 % (pid, u'' if mono else u' class="ja"', E(shot[key])))
        p.append(u'<button type="button" data-src="%s">コピー</button>' % pid)
        p.append(u'</div>')
    if shot['note']:
        p.append(u'<p class="note">%s</p>' % shot['note'])
    p.append(u'</div></div>')
    return u'\n'.join(p)


done = sum(1 for s in SHOTS if s['url'])

PAGE = u'''<title>量子記事の挿絵 SEO設定</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Zen+Antique&family=Zen+Kaku+Gothic+New:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{
  --ground:#EDF0F1; --paper:#FAFBFB; --ink:#14181C; --ink-soft:#4B545B;
  --rule:#CBD2D5; --copper:#A8642A; --keep:#2C6257; --drop:#8A3F32;
  --warn-bg:#F7EEE6; --ok-bg:#E9F0ED; --code-bg:#F1F3F4; --shadow:rgba(20,24,28,.10);
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --ground:#121618; --paper:#191E21; --ink:#E6EBED; --ink-soft:#9CA7AD;
    --rule:#2F373B; --copper:#D9945A; --keep:#72B9A5; --drop:#D08A76;
    --warn-bg:#251E19; --ok-bg:#16211D; --code-bg:#111618; --shadow:rgba(0,0,0,.45);
  }
}
:root[data-theme="dark"]{
  --ground:#121618; --paper:#191E21; --ink:#E6EBED; --ink-soft:#9CA7AD;
  --rule:#2F373B; --copper:#D9945A; --keep:#72B9A5; --drop:#D08A76;
  --warn-bg:#251E19; --ok-bg:#16211D; --code-bg:#111618; --shadow:rgba(0,0,0,.45);
}
*{box-sizing:border-box}
body{background:var(--ground);color:var(--ink);
  font-family:"Zen Kaku Gothic New","Hiragino Sans","Noto Sans JP",sans-serif;
  font-size:16px;line-height:1.85;margin:0;padding-inline:18px;padding-block:0}
.wrap{max-width:43rem;margin-inline:auto;padding-block:44px 72px}
.eyebrow{font-family:"IBM Plex Mono",monospace;font-size:.72rem;letter-spacing:.16em;
  text-transform:uppercase;color:var(--copper);margin:0 0 12px}
h1{font-family:"Zen Antique",serif;font-weight:400;font-size:clamp(1.65rem,6vw,2.2rem);
  line-height:1.42;text-wrap:balance;margin:0 0 14px}
.sub{color:var(--ink-soft);margin:0;font-size:.97rem}
section{margin-top:50px;display:flex;flex-direction:column;gap:16px}
h2{font-weight:700;font-size:1.18rem;line-height:1.5;text-wrap:balance;margin:0;
  padding-bottom:9px;border-bottom:2px solid var(--ink)}
.done{background:var(--ok-bg);border-left:4px solid var(--keep);padding:15px 18px}
.done p{margin:0}.done ul{margin:10px 0 0;padding-left:1.2em}.done li{margin-top:5px}
.done strong{color:var(--keep)}
.caveat{background:var(--warn-bg);border-left:4px solid var(--drop);padding:15px 18px}
.caveat p{margin:0}.caveat p + p{margin-top:9px}.caveat strong{color:var(--drop)}

.shot{background:var(--paper);border:1px solid var(--rule);box-shadow:0 1px 3px var(--shadow)}
.shot.pending{opacity:.72;border-style:dashed}
.shot > header{display:grid;grid-template-columns:2.4rem 1fr;gap:0 12px;
  padding:15px 18px 12px;border-bottom:1px solid var(--rule)}
.shot .num{font-family:"IBM Plex Mono",monospace;font-size:1.25rem;font-weight:500;
  color:var(--copper);font-variant-numeric:tabular-nums;line-height:1.35}
.shot h3{margin:0;font-size:1.02rem;font-weight:700;line-height:1.5}
.shot .where{grid-column:2;margin:4px 0 0;font-family:"IBM Plex Mono",monospace;
  font-size:.71rem;letter-spacing:.05em;color:var(--ink-soft)}
.shot .state{grid-column:2;margin:6px 0 0;font-size:.78rem;font-weight:700;color:var(--keep)}
.shot.pending .state{color:var(--ink-soft);font-weight:400}
.preview{padding:14px 18px 0}
.preview img{width:100%;height:auto;display:block;border:1px solid var(--rule)}
.fields{padding:14px 18px 17px;display:flex;flex-direction:column;gap:14px}
.f{display:flex;flex-direction:column;gap:7px}
.label{margin:0;font-weight:700;font-size:.9rem;display:flex;flex-wrap:wrap;
  align-items:baseline;gap:8px}
.label span{font-family:"IBM Plex Mono",monospace;font-size:.68rem;letter-spacing:.05em;
  color:var(--ink-soft);font-weight:400}
pre{font-family:"IBM Plex Mono",monospace;font-size:.8rem;line-height:1.75;
  background:var(--code-bg);border:1px solid var(--rule);padding:11px;margin:0;
  white-space:pre-wrap;word-break:break-word}
pre.ja{font-family:inherit;font-size:.93rem;line-height:1.8}
.note{margin:0;font-size:.87rem;color:var(--ink-soft);padding-top:2px;
  border-top:1px solid var(--rule)}
button{font-family:inherit;font-size:.85rem;font-weight:500;background:var(--copper);
  color:#fff;border:0;padding:8px 14px;cursor:pointer;align-self:flex-start}
button:focus-visible{outline:3px solid var(--keep);outline-offset:2px}
button[data-done="1"]{background:var(--keep)}
ol.steps{margin:0;padding-left:1.4em;display:flex;flex-direction:column;gap:11px}
ol.steps strong{color:var(--copper)}
.tblwrap{overflow-x:auto;border:1px solid var(--rule)}
table{border-collapse:collapse;width:100%;background:var(--paper);font-size:.9rem}
th,td{text-align:left;padding:10px 12px;border-bottom:1px solid var(--rule);vertical-align:top}
th{font-family:"IBM Plex Mono",monospace;font-size:.71rem;letter-spacing:.08em;
  color:var(--ink-soft);font-weight:500;background:var(--ground);white-space:nowrap}
tr:last-child td{border-bottom:0}
td.y{color:var(--keep);font-weight:700;white-space:nowrap}
footer{margin-top:56px;padding-top:20px;border-top:1px solid var(--rule);
  font-size:.85rem;color:var(--ink-soft)}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
</style>

<div class="wrap">

<p class="eyebrow">量子コンピュータ 前編・後編</p>
<h1>挿絵につける<br>名前と説明</h1>
<p class="sub">8枚ぶん。__DONE__枚がアップロード済みです。</p>

<section>
<h2>サイト側は、もう整っています</h2>
<div class="done">
<p><strong>調べたところ、技術面はすでに手当てされていました。</strong>ここは何もしなくて結構です。</p>
<ul>
<li><strong>WebPの自動生成</strong>（EWWW Image Optimizer）</li>
<li><strong>画面幅に応じた出し分け</strong>（300／768／1024／2048px を自動生成）</li>
<li><strong>遅延読み込み</strong>と、先頭画像の優先読み込み</li>
<li><strong>サイトマップに画像を登録</strong>（All in One SEO。すでに1,336枚）</li>
<li><strong>検索結果に画像を大きく出せる設定</strong>（max-image-preview:large）</li>
</ul>
<p style="margin-top:10px">やることは<strong>1枚ずつに名前と説明を付けることだけ</strong>です。</p>
</div>
</section>

<section>
<h2>ファイル名は、記事に貼る前に</h2>
<div class="caveat">
<p>いまのファイル名は <span style="font-family:'IBM Plex Mono',monospace;font-size:.85em">Gemini_Generated_Image_...</span> で、中身が何も分かりません。<strong>このURLはサイトマップに載って検索エンジンに送られます。</strong></p>
<p>WordPressは<strong>アップロード後にファイル名を変えられません。</strong>記事で使い始めてから変えると、画像が表示されなくなります。<strong>貼る前が、いちばん安いところです。</strong></p>
<p>キャプションなどを入力済みの分は、入れ直すと消えます。<strong>「ファイル名はこのままでよい」とお考えなら、代替テキストだけ入れてください。</strong>それで効き目の大半は取れます。</p>
</div>
</section>

<section>
<h2>1枚ずつの中身</h2>
__CARDS__
</section>

<section>
<h2>手順</h2>
<ol class="steps">
<li><strong>ファイル名を変えて、入れ直す。</strong>（据え置く場合はここを飛ばす）</li>
<li><strong>代替テキスト・タイトル・キャプション・説明</strong>の4欄を埋める。</li>
<li>アイキャッチに使う1番と5番は、記事の<strong>アイキャッチ画像に設定する。</strong>検索結果のサムネイルと、SNSで共有されたときの画像になります。</li>
<li>残りは、上の「入れる場所」に沿って本文に置く。<strong>6番と7番は必ず上下に並べてください。</strong>工場と根粒を見比べてもらうための2枚です。</li>
</ol>
</section>

<section>
<h2>やらなくてよいこと</h2>
<div class="tblwrap">
<table>
<thead><tr><th>よく言われること</th><th>このサイトでは</th></tr></thead>
<tbody>
<tr><td>WebPに変換する</td><td class="y">不要</td></tr>
<tr><td>画像を圧縮する</td><td class="y">不要</td></tr>
<tr><td>スマホ用に小さい画像を用意する</td><td class="y">不要</td></tr>
<tr><td>遅延読み込みを入れる</td><td class="y">不要</td></tr>
<tr><td>サイトマップに画像を追加する</td><td class="y">不要</td></tr>
<tr><td>2560pxを縮める</td><td>気にしなくて結構です。実際に読者へ送られるのは、画面幅に合った小さいほうです</td></tr>
</tbody>
</table>
</div>
<p class="note" style="border:0;padding:0">すべて自動で行われています。<strong>ここに手を出すと、かえって壊す危険があります。</strong></p>
</section>

<section>
<h2>ついでに、もっと効くこと</h2>
<p style="margin:0;font-size:.95rem">画像のSEOは、正直なところ<strong>効き目は小さいほう</strong>です。同じ手間をかけるなら、こちらのほうが効きます。</p>
<div class="tblwrap">
<table>
<thead><tr><th>項目</th><th>案</th></tr></thead>
<tbody>
<tr><td>記事のURL</td><td><span style="font-family:'IBM Plex Mono',monospace;font-size:.85em">quantum-01-kihon</span> ／ <span style="font-family:'IBM Plex Mono',monospace;font-size:.85em">quantum-02-doko</span></td></tr>
<tr><td>記事の見出し</td><td>量子コンピュータとは何か【前編】仕組みと原理を、嘘をつかずに</td></tr>
<tr><td>前編と後編を<br>互いにリンク</td><td>すでに原稿に「このシリーズの記事」として入れてあります</td></tr>
<tr><td>公開日</td><td>NECの報道が2026年9月上旬です。<strong>早いほうが読まれます</strong></td></tr>
</tbody>
</table>
</div>
</section>

<footer>
<p style="margin:0">アップロードされた画像には、作成元の情報がひとつも残っていませんでした（EXIFもIPTCも、アップロード時に削られています）。<strong>機械が読める印がない以上、人が読む文で書くしかありません。</strong>キャプションの「イメージ図（生成AIで作成）」を消さないでください。実在の装置の写真だと思われると、事実と違う印象を与えたことになります。</p>
</footer>

</div>

<script>
(function(){
  function attach(btn){
    var pre = document.getElementById(btn.getAttribute('data-src'));
    if(!pre) return;
    var label = btn.textContent;
    btn.addEventListener('click', function(){
      var text = pre.textContent;
      function done(){
        btn.textContent = 'コピーしました';
        btn.setAttribute('data-done','1');
        setTimeout(function(){ btn.textContent = label; btn.removeAttribute('data-done'); }, 2000);
      }
      function fallback(){
        var ta = document.createElement('textarea');
        ta.value = text; ta.setAttribute('readonly','');
        ta.style.position='fixed'; ta.style.top='-1000px';
        document.body.appendChild(ta); ta.select();
        try { document.execCommand('copy'); done(); }
        catch(e){ btn.textContent = 'コピーできませんでした'; }
        document.body.removeChild(ta);
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, fallback);
      } else { fallback(); }
    });
  }
  var b = document.querySelectorAll('button[data-src]');
  for (var i=0;i<b.length;i++) attach(b[i]);
})();
</script>
'''

page = (PAGE.replace(u'__DONE__', unicode(done) if str is bytes else str(done))
            .replace(u'__CARDS__', u'\n'.join(card(s) for s in SHOTS)))
io.open(OUT, 'w', encoding='utf-8').write(page)
print('wrote %s (%d bytes, uploaded=%d/%d)'
      % (OUT, len(page.encode('utf-8')), done, len(SHOTS)))
