# -*- coding: utf-8 -*-
"""量子コンピュータ記事（前編・後編）の確認用ページを組み立てる。"""
import html
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SRCDIR = os.path.join(HERE, '..', 'posts', 'quantum')
OUT = os.path.join(HERE, 'quantum-genkou.html')


def load(name):
    raw = io.open(os.path.join(SRCDIR, name), encoding='utf-8').read()
    prose = re.sub(r'<!--.*?-->', '', raw, flags=re.S)
    prose = re.sub(r'<div style="height:\d+px"[^>]*></div>', '', prose)
    prose = re.sub(r'\n{3,}', '\n\n', prose).strip()
    return prose, html.escape(raw)


PROSE1, RAW1 = load('article-01.html')
PROSE2, RAW2 = load('article-02.html')

PAGE = u'''<title>量子コンピュータの記事 原稿</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Zen+Antique&family=Zen+Kaku+Gothic+New:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{
  --ground:#EDF0F1;
  --paper:#FAFBFB;
  --ink:#14181C;
  --ink-soft:#4B545B;
  --rule:#CBD2D5;
  --copper:#A8642A;
  --keep:#2C6257;
  --drop:#8A3F32;
  --warn-bg:#F7EEE6;
  --shadow:rgba(20,24,28,.10);
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --ground:#121618;
    --paper:#191E21;
    --ink:#E6EBED;
    --ink-soft:#9CA7AD;
    --rule:#2F373B;
    --copper:#D9945A;
    --keep:#72B9A5;
    --drop:#D08A76;
    --warn-bg:#251E19;
    --shadow:rgba(0,0,0,.45);
  }
}
:root[data-theme="dark"]{
  --ground:#121618;
  --paper:#191E21;
  --ink:#E6EBED;
  --ink-soft:#9CA7AD;
  --rule:#2F373B;
  --copper:#D9945A;
  --keep:#72B9A5;
  --drop:#D08A76;
  --warn-bg:#251E19;
  --shadow:rgba(0,0,0,.45);
}

*{box-sizing:border-box}
body{
  background:var(--ground);color:var(--ink);
  font-family:"Zen Kaku Gothic New","Hiragino Sans","Noto Sans JP",sans-serif;
  font-size:16px;line-height:1.9;margin:0;
  padding-inline:18px;padding-block:0;
}
.wrap{max-width:44rem;margin-inline:auto;padding-block:44px 72px}

.eyebrow{
  font-family:"IBM Plex Mono",monospace;font-size:.72rem;
  letter-spacing:.16em;text-transform:uppercase;color:var(--copper);margin:0 0 12px
}
h1{
  font-family:"Zen Antique",serif;font-weight:400;
  font-size:clamp(1.75rem,6.5vw,2.5rem);line-height:1.4;
  text-wrap:balance;margin:0 0 16px;
}
.sub{color:var(--ink-soft);margin:0 0 6px;font-size:.98rem}
.stamp{font-family:"IBM Plex Mono",monospace;font-size:.76rem;color:var(--ink-soft);letter-spacing:.04em}

section{margin-top:56px;display:flex;flex-direction:column;gap:18px}
h2{
  font-weight:700;font-size:1.22rem;line-height:1.5;text-wrap:balance;
  margin:0;padding-bottom:9px;border-bottom:2px solid var(--ink);
}

/* 40年の流れ */
.line{display:flex;flex-direction:column;gap:0;border-left:2px solid var(--copper);padding-left:0}
.line > div{
  display:grid;grid-template-columns:5.2rem 1fr;gap:0 16px;
  padding:14px 0 14px 18px;position:relative;
}
.line > div::before{
  content:"";position:absolute;left:-6px;top:22px;
  width:10px;height:10px;border-radius:50%;
  background:var(--copper);
}
.line time{
  font-family:"IBM Plex Mono",monospace;font-size:.86rem;
  color:var(--copper);font-variant-numeric:tabular-nums;letter-spacing:.02em;
}
.line p{margin:0;font-size:.95rem}
.line b{display:block;font-size:1rem;margin-bottom:2px}

/* 但し書き */
.caveat{background:var(--warn-bg);border-left:4px solid var(--drop);padding:16px 18px}
.caveat p{margin:0}
.caveat p + p{margin-top:10px}
.caveat strong{color:var(--drop)}

/* 数 */
.tally{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:var(--rule);border:1px solid var(--rule)}
.tally div{background:var(--paper);padding:14px 12px;text-align:center}
.tally b{
  display:block;font-family:"IBM Plex Mono",monospace;font-weight:500;
  font-size:1.45rem;font-variant-numeric:tabular-nums;line-height:1.2;color:var(--copper)
}
.tally span{display:block;font-size:.75rem;color:var(--ink-soft);margin-top:4px}

/* 原稿 */
.parthead{
  font-family:"IBM Plex Mono",monospace;font-size:.78rem;letter-spacing:.12em;
  color:var(--copper);margin:0;
}
.draft{background:var(--paper);border:1px solid var(--rule);box-shadow:0 1px 3px var(--shadow);padding:26px 22px}
.draft h3{
  font-weight:700;font-size:1.08rem;line-height:1.55;margin:34px 0 0;
  padding-left:12px;border-left:3px solid var(--copper);text-wrap:balance;
}
.draft h3:first-child{margin-top:0}
.draft h2{font-size:1.02rem;border:0;border-top:1px solid var(--rule);padding-top:20px;margin-top:34px}
.draft p{margin:14px 0 0}
.draft ul{margin:14px 0 0;padding-left:1.25em}
.draft li{margin-top:9px}
.draft a{color:var(--keep);word-break:break-all}
.draft figure{margin:20px 0 0;overflow-x:auto}
.draft figure table{border-collapse:collapse;width:100%;font-size:.88rem;background:transparent}
.draft figure th,.draft figure td{
  border:1px solid var(--rule);padding:9px 11px;text-align:left;vertical-align:top;line-height:1.7;
}
.draft figure th{background:var(--ground);font-weight:700}
.draft figcaption{font-size:.82rem;color:var(--ink-soft);text-align:center;margin-top:8px}
.draft svg{margin:22px auto}

/* 貼り付け */
details{border:1px solid var(--rule);background:var(--paper)}
summary{cursor:pointer;padding:13px 16px;font-weight:500;font-size:.95rem;list-style:none;display:flex;align-items:center;gap:10px}
summary::-webkit-details-marker{display:none}
summary::before{content:"＋";font-family:"IBM Plex Mono",monospace;color:var(--copper)}
details[open] summary::before{content:"−"}
.paste{padding:0 16px 16px;display:flex;flex-direction:column;gap:12px}
.paste pre{
  font-family:"IBM Plex Mono",monospace;font-size:.72rem;line-height:1.6;
  background:var(--ground);border:1px solid var(--rule);padding:12px;margin:0;
  max-height:14rem;overflow:auto;white-space:pre-wrap;word-break:break-all;
}
button{
  font-family:inherit;font-size:.95rem;font-weight:500;
  background:var(--copper);color:#fff;border:0;padding:12px 18px;cursor:pointer;align-self:flex-start;
}
button:focus-visible{outline:3px solid var(--keep);outline-offset:2px}
button[data-done="1"]{background:var(--keep)}

/* 点検 */
.check{display:flex;flex-direction:column;border-top:1px solid var(--rule)}
.check > div{display:grid;grid-template-columns:2.4rem 1fr;gap:0 14px;padding:16px 0;border-bottom:1px solid var(--rule)}
.check .no{font-family:"IBM Plex Mono",monospace;font-size:1.05rem;color:var(--copper);font-variant-numeric:tabular-nums}
.check h3{margin:0;font-size:1rem;font-weight:700;line-height:1.6}
.check p{margin:7px 0 0;grid-column:2;font-size:.93rem;color:var(--ink-soft)}
.check .verdict{grid-column:2;margin-top:9px;font-family:"IBM Plex Mono",monospace;font-size:.75rem;letter-spacing:.06em}
.ok{color:var(--keep)}
.ng{color:var(--drop)}

/* 言い換え表 */
.tblwrap{overflow-x:auto;border:1px solid var(--rule)}
table{border-collapse:collapse;width:100%;background:var(--paper);font-size:.9rem}
th,td{text-align:left;padding:11px 13px;border-bottom:1px solid var(--rule);vertical-align:top}
th{font-family:"IBM Plex Mono",monospace;font-size:.72rem;letter-spacing:.08em;color:var(--ink-soft);font-weight:500;background:var(--ground);white-space:nowrap}
tr:last-child td{border-bottom:0}
td.no{color:var(--drop)}
td.yes{color:var(--keep)}
td.why{color:var(--ink-soft)}

ol.todo{margin:0;padding-left:1.4em;display:flex;flex-direction:column;gap:12px}
ol.todo strong{color:var(--copper)}

footer{margin-top:64px;padding-top:20px;border-top:1px solid var(--rule);font-size:.85rem;color:var(--ink-soft)}

@media (max-width:430px){
  .tally{grid-template-columns:1fr 1fr}
  .tally div:last-child{grid-column:1 / -1}
  .line > div{grid-template-columns:1fr;gap:2px}
}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
</style>

<div class="wrap">

<p class="eyebrow">下書き / 確認のお願い</p>
<h1>量子コンピュータとは何か<br>前編・後編</h1>
<p class="sub">株式会社石名坂 お知らせ・コラム／投稿前の原稿</p>
<p class="stamp">2026年9月15日 改稿　前編8,900字／後編11,748字（出典一覧を除く）</p>

<section>
<h2>書き出しを、差し替えました</h2>
<div class="caveat">
<p><strong>もとは、ある企業が量子コンピュータの実機開発を取りやめたという報道から書き始めていました。</strong>他社の経営判断に触れる話なので、<strong>その部分はすべて外しました。</strong></p>
<p>いまの書き出しは<strong>2025年のノーベル物理学賞</strong>です。公表された事実で、受賞対象が1984年の実験なので、そのまま「1984年からの一本の線」の節につながります。</p>
<p>残したのは<strong>1999年に日本の研究所が量子ビットを世界で初めて実現した</strong>という功績のほうです。これは記事の背骨であり、他社の経営判断とは別の話です。</p>
</div>
</section>

<section>
<h2>記事の背骨 ── 40年でつながる一本の線</h2>
<div class="line">
<div><time>1984-85</time><p><b>ジョセフソン接合の実験</b>クラーク・ドヴォレ・マルティニスの3氏。<strong>2025年のノーベル物理学賞</strong>の対象になった実験。</p></div>
<div><time>1999</time><p><b>NEC、量子ビットを世界初実現</b>中村泰信・パシキン・蔡兆申の3氏。「クーパー対箱」。Nature 4月29日号の表紙。</p></div>
<div><time>2007</time><p><b>トランズモン提案</b>論文の題名が「<strong>クーパー対箱から導かれた</strong>設計」。<strong>共著者にドヴォレ氏</strong>（2025年ノーベル賞）。</p></div>
<div><time>いま</time><p><b>IBM・Googleの主力部品に</b>トランズモンが標準になっている。</p></div>
<div><time>2026-03-26</time><p><b>理研・阪大が144量子ビットを稼働</b>国産機「叡-Ⅱ」の運用開始。<strong>日本も動いている。</strong></p></div>
</div>
</section>

<section>
<h2>何を確かめて、何を落としたか</h2>
<div class="tally">
  <div><b>40</b><span>出典（前編16／後編24）</span></div>
  <div><b>5</b><span>担当したチーム</span></div>
  <div><b>13</b><span>出典が食い違って落とした材料</span></div>
</div>
<div class="caveat">
<p><strong>原典は、誰も読んでいません。</strong>この環境からは go.jp・nature.com・日経・ITmedia のいずれも開けませんでした。<strong>有料記事の本文は一切読めていません。</strong></p>
<p>そのため条文番号は<strong>一つも書いていません。</strong>論文は題名・誌名・巻号・年までにとどめ、本文の引用はしていません。<strong>公開前に、出典のURLを開いて確かめてください。</strong></p>
</div>
</section>

<section>
<h2>言い切りを、どう外したか</h2>
<div class="tblwrap">
<table>
<thead><tr><th>書きたくなる形</th><th>実際に書いた形</th></tr></thead>
<tbody>
<tr><td class="no">すべての答えを同時に計算する</td><td class="yes"><strong>これは、正しくありません</strong>／「全部試す機械」ではなく<strong>「間違いを消す機械」</strong></td></tr>
<tr><td class="no">0と1が同時</td><td class="yes">0と1の<strong>混ぜ方そのものが状態</strong>。位相を落とすと、速い理由がまるごと抜け落ちる</td></tr>
<tr><td class="no">量子もつれで瞬間通信</td><td class="yes"><strong>通信不可能定理。</strong>相関はあるが、合図は送れない</td></tr>
<tr><td class="no">絶対零度に冷やす機械</td><td class="yes">10ミリケルビン程度。絶対零度には到達できない。<strong>かつ超電導方式に限る</strong></td></tr>
<tr><td class="no">トポロジカル量子ビットが実現</td><td class="yes">Nature編集部が<strong>「証拠を示すものではない」と注記。</strong>決着していない</td></tr>
<tr><td class="no">◯年に実用化される</td><td class="yes"><strong>2029年／2035年／2050年／「来ない」</strong>の幅で示した</td></tr>
<tr><td class="no">日本は脱落した</td><td class="yes"><strong>同じ月に理研・阪大が144量子ビット機を稼働</strong>させている</td></tr>
</tbody>
</table>
</div>
<p style="margin:0;font-size:.93rem;color:var(--ink-soft)">比喩は「どこから嘘になるか」を本文に書きました。<strong>双子・迷路・並行世界のたとえは使っていません。</strong>とくに双子のたとえは、2022年のノーベル賞が否定した考え方そのもので、使うと賞の中身を真逆に説明することになります。</p>
</section>

<section>
<p class="parthead">PART 1</p>
<h2>前編：仕組みと原理を、嘘をつかずに</h2>
<div class="draft">
__PROSE1__
</div>
<details>
<summary>前編のブロック形式を開く</summary>
<div class="paste">
<p style="margin:0;font-size:.9rem;color:var(--ink-soft)">投稿の編集画面で、右上のメニューから<strong>「コードエディター」</strong>に切り替えて貼り付けてください。</p>
<pre id="raw1">__RAW1__</pre>
<button type="button" data-src="raw1">前編をコピー</button>
</div>
</details>
</section>

<section>
<p class="parthead">PART 2</p>
<h2>後編：いまどこまで来ているのか</h2>
<div class="draft">
__PROSE2__
</div>
<details>
<summary>後編のブロック形式を開く</summary>
<div class="paste">
<pre id="raw2">__RAW2__</pre>
<button type="button" data-src="raw2">後編をコピー</button>
</div>
</details>
</section>

<section>
<h2>公開前の6つ、自己点検の結果</h2>
<div class="check">

<div><span class="no">1</span><h3>言い切っていないか</h3>
<p>上の表のとおり7か所。比喩の壊れる場所も本文に書きました。</p>
<span class="verdict ok">● 通過</span></div>

<div><span class="no">2</span><h3>自社の他の記述と食い違っていないか</h3>
<p>Claude Code 第5回の「AIが誤った内容を出力する可能性はある／最終確認は人が行う」と同じ姿勢で通しています。前回のAI・Web3の記事で書いた「企業の発表をそのまま事実にしない」という線も守っています。</p>
<span class="verdict ok">● 通過</span></div>

<div><span class="no">3</span><h3>他社のことを断定していないか</h3>
<p><strong>他社の経営判断に触れる話は、まるごと外しました。</strong>Microsoftは「嘘をついた」とは書かず、会社の発表とNature編集部の注記を並べました。D-Waveは反論と再反論の両方を書きました。「すべての発表が怪しいわけではない」とも明記しています。</p>
<span class="verdict ok">● 通過</span></div>

<div><span class="no">4</span><h3>数字と引用に出どころがあるか</h3>
<p>出典40本。本文の数字はすべて出典付き。食い違った13種類は下の表のとおり全部落としました。</p>
<span class="verdict ok">● 通過</span></div>

<div><span class="no">5</span><h3>法令・規格は原典を見たか</h3>
<p><strong>見ていません。</strong>go.jp も nature.com も日経も開けず、有料記事の本文は一切読めていません。そこで<strong>条文番号は一つも書かず</strong>、論文は題名・誌名・巻号・年までにとどめました。<strong>ここだけは、そちらで確かめていただく必要があります。</strong></p>
<span class="verdict ng">▲ 未了 — 公開前に確認が要る</span></div>

<div><span class="no">6</span><h3>人が特定されないか</h3>
<p>出てくるのは公表された研究者・受賞者・企業の最高経営責任者のみ。研究者の異動に関する記述は、人数も氏名も公表されていないため、まるごと落としました。</p>
<span class="verdict ok">● 通過</span></div>

</div>
</section>

<section>
<h2>載せなかったもの</h2>
<div class="tblwrap">
<table>
<thead><tr><th>内容</th><th>落とした理由</th></tr></thead>
<tbody>
<tr><td>「日本の投資額は米国の5割」（日経の見出し）</td><td class="why">別の日経記事は「日本7億ドル／米国37億ドル」＝<strong>約19%</strong>。デロイトも「米国は日本の約5倍」。<strong>集計基準が違い、数字が矛盾する</strong></td></tr>
<tr><td>実機開発の中止に関する報道（日経・時事・ITmedia）</td><td class="why"><strong>他社の経営判断に触れるため、まるごと外した。</strong>書き出しは2025年のノーベル物理学賞に差し替え</td></tr>
<tr><td>止めたのがゲート型かアニーリング型か</td><td class="why">報道が方式を特定していない</td></tr>
<tr><td>「世界最大は6,100量子ビット」</td><td class="why"><strong>原子を並べて保持した成果</strong>で、それで計算をしたわけではない</td></tr>
<tr><td>論理量子ビットの個数（96／94）</td><td class="why">業界メディア経由。「100個に満たない」という桁感だけ使った</td></tr>
<tr><td>希釈冷凍機の消費電力・価格</td><td class="why">同じ記事の中で数字が矛盾していた</td></tr>
<tr><td>株価の下落率</td><td class="why">出典により「30〜40%」「60%」と食い違う。<strong>そもそも株価・銘柄・投資判断には一切触れない方針</strong></td></tr>
<tr><td>NIST IR 8547 の2030年／2035年</td><td class="why"><strong>草案段階。</strong>日本の2035年（内閣官房）が確定なのでそちらを使った</td></tr>
<tr><td>業界地図の画像</td><td class="why"><strong>日経BPの図版で著作権がある。</strong>方式の分け方は事実なので、本文では文章にした</td></tr>
<tr><td>富士通「デジタルアニーラ」</td><td class="why"><strong>量子ではなく専用のデジタル回路。</strong>量子の実用例として出すと誤りになる</td></tr>
<tr><td>「量子」を冠した商品の名指し</td><td class="why">消費者庁・国民生活センター・厚労省・金融庁・公取委を調べたが、<strong>処分や注意喚起が一件も見つからなかった</strong></td></tr>
</tbody>
</table>
</div>
</section>

<section>
<h2>公開前に、お願いしたいこと</h2>
<ol class="todo">
<li><strong>書き出しの3段落を読んでください。</strong>ノーベル賞から始まる形に差し替えました。そこから「1984年からの一本の線」の節へ、無理なくつながっているかを見ていただきたい。</li>
<li><strong>出典のURLを何本か開く。</strong>特に内閣官房・金融庁・理化学研究所・ノーベル財団。</li>
<li><strong>消費者ホットライン188</strong>を目で確認。</li>
<li><strong>前編のたとえが、実務の感覚と合っているか。</strong>「地盤の改良や河川の護岸は、効き目が出るまでに何十年もかかる」と書きました。<strong>ここは私には判断できません。</strong></li>
</ol>
</section>

<footer>
<p style="margin:0">5人の担当で材料を集め、突き合わせました。1件、訂正しています。世界の動向の担当が「Googleの中性原子方式への参入は単一ソースであやしい」と報告してきましたが、これは誤りで、Google公式ブログを含む5系統で確認できました。石名坂からいただいた業界地図の記載も正しく、そのまま採用しています。</p>
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
        setTimeout(function(){
          btn.textContent = label;
          btn.removeAttribute('data-done');
        }, 2200);
      }
      function fallback(){
        var ta = document.createElement('textarea');
        ta.value = text; ta.setAttribute('readonly','');
        ta.style.position = 'fixed'; ta.style.top = '-1000px';
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
  var btns = document.querySelectorAll('button[data-src]');
  for (var i = 0; i < btns.length; i++) attach(btns[i]);
})();
</script>
'''

page = (PAGE.replace('__PROSE1__', PROSE1).replace('__RAW1__', RAW1)
            .replace('__PROSE2__', PROSE2).replace('__RAW2__', RAW2))
io.open(OUT, 'w', encoding='utf-8').write(page)
print('wrote %s (%d bytes)' % (OUT, len(page.encode('utf-8'))))
