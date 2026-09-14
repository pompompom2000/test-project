# -*- coding: utf-8 -*-
"""AI・Web3記事の確認用ページを組み立てる。

article.html（WordPressのブロック形式）から
 ・読む用の本文
 ・貼り付け用の生データ
の2つを作って、確認用のHTMLに埋め込む。
"""
import html
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', 'posts', 'ai-web3', 'article.html')
OUT = os.path.join(HERE, 'ai-web3-genkou.html')

raw = io.open(SRC, encoding='utf-8').read()

# 読む用：ブロックのコメントと空白ブロックを落とす
prose = re.sub(r'<!--.*?-->', '', raw, flags=re.S)
prose = re.sub(r'<div style="height:\d+px"[^>]*></div>', '', prose)
prose = re.sub(r'\n{3,}', '\n\n', prose).strip()

# 貼り付け用：そのまま。HTMLエスケープして <pre> に入れる
escaped = html.escape(raw)

PAGE = u'''<title>AI・Web3の記事 原稿</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@500;700&family=Zen+Kaku+Gothic+New:wght@400;500;700&family=Roboto+Mono:wght@400;500&display=swap">
<style>
:root{
  --stone:#EFF1F0;
  --paper:#FBFBFA;
  --ink:#1A1E1C;
  --ink-soft:#4E5654;
  --rule:#CDD3D1;
  --survey:#24425C;
  --keep:#2E6B4F;
  --drop:#8A4B22;
  --warn-bg:#F6EEE6;
  --keep-bg:#E8F0EB;
  --shadow:rgba(26,30,28,.09);
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --stone:#15191A;
    --paper:#1C2122;
    --ink:#E7EBEA;
    --ink-soft:#A3ADAB;
    --rule:#333B3C;
    --survey:#8FB4D4;
    --keep:#79BE9A;
    --drop:#D79A6B;
    --warn-bg:#2A2320;
    --keep-bg:#1E2A25;
    --shadow:rgba(0,0,0,.4);
  }
}
:root[data-theme="dark"]{
  --stone:#15191A;
  --paper:#1C2122;
  --ink:#E7EBEA;
  --ink-soft:#A3ADAB;
  --rule:#333B3C;
  --survey:#8FB4D4;
  --keep:#79BE9A;
  --drop:#D79A6B;
  --warn-bg:#2A2320;
  --keep-bg:#1E2A25;
  --shadow:rgba(0,0,0,.4);
}

*{box-sizing:border-box}
body{
  background:var(--stone);
  color:var(--ink);
  font-family:"Zen Kaku Gothic New","Hiragino Sans","Noto Sans JP",sans-serif;
  font-size:16px;
  line-height:1.9;
  margin:0;
  padding-inline:18px;
  padding-block:0;
}
.wrap{max-width:44rem;margin-inline:auto;padding-block:44px 72px}

/* ---- 見出し ---- */
.eyebrow{
  font-family:"Roboto Mono",monospace;
  font-size:.72rem;letter-spacing:.16em;text-transform:uppercase;
  color:var(--ink-soft);margin:0 0 10px
}
h1{
  font-family:"Shippori Mincho",serif;font-weight:700;
  font-size:clamp(1.7rem,6vw,2.4rem);line-height:1.42;
  text-wrap:balance;margin:0 0 14px;letter-spacing:.01em;
}
.sub{color:var(--ink-soft);margin:0 0 6px;font-size:.98rem}
.stamp{
  font-family:"Roboto Mono",monospace;font-size:.76rem;
  color:var(--ink-soft);letter-spacing:.04em
}

h2{
  font-family:"Shippori Mincho",serif;font-weight:700;
  font-size:1.3rem;line-height:1.5;text-wrap:balance;
  margin:0;padding-bottom:9px;border-bottom:2px solid var(--ink);
}
section{margin-top:56px;display:flex;flex-direction:column;gap:18px}

/* ---- 数の並び ---- */
.tally{
  display:grid;grid-template-columns:repeat(3,1fr);gap:1px;
  background:var(--rule);border:1px solid var(--rule);
}
.tally div{background:var(--paper);padding:14px 12px;text-align:center}
.tally b{
  display:block;font-family:"Roboto Mono",monospace;font-weight:500;
  font-size:1.5rem;font-variant-numeric:tabular-nums;line-height:1.2;
  color:var(--survey)
}
.tally span{display:block;font-size:.76rem;color:var(--ink-soft);margin-top:4px}

/* ---- 但し書き ---- */
.caveat{
  background:var(--warn-bg);
  border-left:4px solid var(--drop);
  padding:16px 18px;
}
.caveat p{margin:0}
.caveat p + p{margin-top:10px}
.caveat strong{color:var(--drop)}

/* ---- 原稿 ---- */
.draft{
  background:var(--paper);
  border:1px solid var(--rule);
  box-shadow:0 1px 3px var(--shadow);
  padding:26px 22px;
}
.draft h3{
  font-family:"Shippori Mincho",serif;font-weight:700;
  font-size:1.1rem;line-height:1.55;margin:34px 0 0;
  padding-left:12px;border-left:3px solid var(--survey);
  text-wrap:balance;
}
.draft h3:first-child{margin-top:0}
.draft h2{
  font-size:1.05rem;border:0;border-top:1px solid var(--rule);
  padding-top:20px;margin-top:34px;
}
.draft p{margin:14px 0 0}
.draft ul{margin:14px 0 0;padding-left:1.25em}
.draft li{margin-top:9px}
.draft a{color:var(--survey);word-break:break-all}
.draft strong{font-weight:700}

/* ---- 貼り付け ---- */
details{border:1px solid var(--rule);background:var(--paper)}
summary{
  cursor:pointer;padding:13px 16px;font-weight:500;font-size:.95rem;
  list-style:none;display:flex;align-items:center;gap:10px;
}
summary::-webkit-details-marker{display:none}
summary::before{content:"＋";font-family:"Roboto Mono",monospace;color:var(--survey)}
details[open] summary::before{content:"−"}
.paste{padding:0 16px 16px;display:flex;flex-direction:column;gap:12px}
pre#raw{
  font-family:"Roboto Mono",monospace;font-size:.72rem;line-height:1.6;
  background:var(--stone);border:1px solid var(--rule);
  padding:12px;margin:0;max-height:15rem;overflow:auto;white-space:pre-wrap;
  word-break:break-all;
}
button{
  font-family:inherit;font-size:.95rem;font-weight:500;
  background:var(--survey);color:var(--paper);
  border:0;padding:12px 18px;cursor:pointer;align-self:flex-start;
}
button:focus-visible{outline:3px solid var(--keep);outline-offset:2px}
button[data-done="1"]{background:var(--keep)}

/* ---- 点検 ---- */
.check{display:flex;flex-direction:column;gap:0;border-top:1px solid var(--rule)}
.check > div{
  display:grid;grid-template-columns:2.4rem 1fr;gap:0 14px;
  padding:16px 0;border-bottom:1px solid var(--rule);
}
.check .no{
  font-family:"Roboto Mono",monospace;font-size:1.05rem;
  color:var(--survey);font-variant-numeric:tabular-nums;
}
.check h3{margin:0;font-size:1rem;font-weight:700;line-height:1.6}
.check p{margin:7px 0 0;grid-column:2;font-size:.93rem;color:var(--ink-soft)}
.check .verdict{
  grid-column:2;margin-top:9px;font-family:"Roboto Mono",monospace;
  font-size:.75rem;letter-spacing:.06em;
}
.ok{color:var(--keep)}
.ng{color:var(--drop)}

/* ---- 表 ---- */
.tblwrap{overflow-x:auto;border:1px solid var(--rule)}
table{border-collapse:collapse;width:100%;background:var(--paper);font-size:.9rem}
th,td{text-align:left;padding:11px 13px;border-bottom:1px solid var(--rule);vertical-align:top}
th{
  font-family:"Roboto Mono",monospace;font-size:.72rem;letter-spacing:.08em;
  color:var(--ink-soft);font-weight:500;background:var(--stone);white-space:nowrap;
}
tr:last-child td{border-bottom:0}
td.why{color:var(--ink-soft)}

/* ---- お願い ---- */
ol.todo{margin:0;padding-left:1.4em;display:flex;flex-direction:column;gap:12px}
ol.todo li{padding-left:4px}
ol.todo strong{color:var(--survey)}

footer{
  margin-top:64px;padding-top:20px;border-top:1px solid var(--rule);
  font-size:.85rem;color:var(--ink-soft);
}
@media (max-width:430px){
  .tally{grid-template-columns:1fr 1fr}
  .tally div:last-child{grid-column:1 / -1}
}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
</style>

<div class="wrap">

<p class="eyebrow">下書き / 確認のお願い</p>
<h1>AIとWeb3で暮らしはどう変わる？<br>知っておきたい基礎知識</h1>
<p class="sub">株式会社石名坂 お知らせ・コラム／投稿前の原稿</p>
<p class="stamp">2026年9月14日 作成　本文6,300字</p>

<section>
<h2>何を確かめて、何を落としたか</h2>
<div class="tally">
  <div><b>25</b><span>出典</span></div>
  <div><b>17</b><span>本文の数字（全部出典つき）</span></div>
  <div><b>10</b><span>出典が食い違って落とした数字</span></div>
</div>

<div class="caveat">
<p><strong>先に、正直なところを。</strong>今回は外の検索はできましたが、<strong>官公庁のページを直接開くことは遮断されていました。</strong>金融庁・総務省・警察庁・国民生活センター・文科省・国交省・盛岡市、いずれも開けていません。</p>
<p>つまり、出典のURLは出せますが、<strong>そのページの中身を私は読んでいません。</strong>複数の検索結果が一致したものだけを採用しています。公開前に、いくつか実際に開いて確かめてください。</p>
</div>
</section>

<section>
<h2>原稿</h2>
<div class="draft">
__PROSE__
</div>
</section>

<section>
<h2>WordPressに貼る</h2>
<details>
<summary>ブロック形式の原稿を開く</summary>
<div class="paste">
<p style="margin:0;font-size:.9rem;color:var(--ink-soft)">投稿の編集画面で、右上のメニューから<strong>「コードエディター」</strong>に切り替えて貼り付けてください。</p>
<pre id="raw">__RAW__</pre>
<button id="copy" type="button">原稿をコピー</button>
</div>
</details>
</section>

<section>
<h2>公開前の6つ、自己点検の結果</h2>
<div class="check">

<div>
<span class="no">1</span>
<h3>言い切っていないか</h3>
<p>「ブロックチェーンは改ざんできない」「Web3で社会が変わる」「AI新法で規制がかかった」。書きたくなる形を6か所、意識して外しました。残した「必ず」は3か所で、うち2つは否定とお願いです。</p>
<span class="verdict ok">● 通過</span>
</div>

<div>
<span class="no">2</span>
<h3>自社の他の記述と食い違っていないか</h3>
<p>Claude Code 第5回の「出力結果は必ず人の目で確認する」「下ごしらえをAIに、最終確認は人が」と突き合わせ、3点すべて一致させました。サイトのAI案内係についても「お見積りやご注文は必ずお電話かフォームで」と書き、自社を例外扱いしていません。</p>
<span class="verdict ok">● 通過</span>
</div>

<div>
<span class="no">3</span>
<h3>他社のことを断定していないか</h3>
<p>暗号資産の流出事件は社名を書かず「国内の暗号資産交換業者」としました。無登録業者も名指しせず、金融庁の一覧で確認する方法を案内しています。施工管理アプリのシェアは各社の自社公表値だったので書きませんでした。</p>
<span class="verdict ok">● 通過</span>
</div>

<div>
<span class="no">4</span>
<h3>数字と引用に出どころがあるか</h3>
<p>本文の数字17個すべてに出典があります。複数の出典が一致しなかった数字10種類は、下の表のとおり全部落としました。</p>
<span class="verdict ok">● 通過</span>
</div>

<div>
<span class="no">5</span>
<h3>法令・規格は原典を見たか</h3>
<p><strong>見ていません。</strong>この環境から官公庁のページを開けないためです。そこで条文番号は民法85条だけにとどめ、資金決済法は条番号を書かず「資金決済法に定義があります」の粒度にしました。<strong>ここだけは、そちらで確かめていただく必要があります。</strong></p>
<span class="verdict ng">▲ 未了 — 公開前に確認が要る</span>
</div>

<div>
<span class="no">6</span>
<h3>人が特定されないか</h3>
<p>実在の個人は一人も出てきません。被害事例は国民生活センターが公表しているもので、年代も地域も書いていません。</p>
<span class="verdict ok">● 通過</span>
</div>

</div>
</section>

<section>
<h2>載せなかったもの</h2>
<p style="margin:0;color:var(--ink-soft);font-size:.93rem">調べはしたが、記事に入れなかったものです。入れなかった理由のほうが大事だと思うので残します。</p>
<div class="tblwrap">
<table>
<thead><tr><th>内容</th><th>落とした理由</th></tr></thead>
<tbody>
<tr><td>盛岡市消費生活センターの直通番号</td><td class="why">検索するたび <span style="font-family:'Roboto Mono',monospace">019-604-4111</span> と <span style="font-family:'Roboto Mono',monospace">019-624-4111</span> の二つが出た。市のページを開けず確定できないので、<strong>188だけ</strong>を載せた（188から同センターにつながる）</td></tr>
<tr><td>AI音声で家族の声をまねる詐欺</td><td class="why">国内の被害について、公的機関の注意喚起が見つからなかった。「急増しています」と書くと事実に反するおそれ</td></tr>
<tr><td>中小企業の生成AI導入率</td><td class="why">5% / 23.4% / 23.5% と三説あり、調査元が特定できない</td></tr>
<tr><td>スマートスピーカーの普及率</td><td class="why">民間2調査が 8% と 21.6% で2倍以上開く。官庁統計なし</td></tr>
<tr><td>暗号資産の登録業者数</td><td class="why">28社 / 29社 で食い違う。「金融庁の一覧で確認できます」と誘導に切り替えた</td></tr>
<tr><td>暗号資産の税率20%</td><td class="why">移行の議論はあるが、全出典が「見込み」「有力」と留保。開始時期を断定できない</td></tr>
<tr><td>インボイスの経過措置（2026年10月からの変更）</td><td class="why">公開月と重なり、間違えると実害が出る。税理士の確認が要るので、この記事では扱わない</td></tr>
<tr><td>岩手県の遠隔臨場要領・JCIP対応</td><td class="why">地元の話ほど裏が取れなかった</td></tr>
<tr><td>盛岡市の実証の「その後」</td><td class="why">続報がない。<strong>過去形・3課限定</strong>で書いた</td></tr>
<tr><td>手口の細かい説明</td><td class="why">実行できる粒度になる。「こういう連絡が来たら疑う」にとどめた</td></tr>
</tbody>
</table>
</div>
</section>

<section>
<h2>公開前に、お願いしたいこと</h2>
<ol class="todo">
<li><strong>出典のURLを何本か開いて、生きているか確かめる。</strong>特に金融庁・警察庁・国民生活センターの3つ。読者がいちばん頼る先です。</li>
<li><strong>相談先の 188 と #9110 を、目で見て確認する。</strong>ここを間違えると、困った人が助けを求められません。</li>
<li><strong>盛岡市の実証について書いた段落を読む。</strong>市に対して失礼がないか、地元の感覚で見てください。</li>
<li><strong>「当社でもAIを使っています」の段落</strong>が、いまのチャットボットの実態と合っているか。</li>
</ol>
</section>

<footer>
<p style="margin:0">この原稿は、5人の担当が集めた材料を突き合わせて作りました。うち1件、出典の取り違えが見つかっています。「Web3の明確な定義が定まっていない」という一文の出どころは情報通信白書ではなく、総務省の研究会資料でした。白書を出典にしていたら、リンクを開いた読者に食い違いを指摘されていたところです。</p>
</footer>

</div>

<script>
(function(){
  var btn = document.getElementById('copy');
  var pre = document.getElementById('raw');
  if(!btn || !pre) return;
  btn.addEventListener('click', function(){
    var text = pre.textContent;
    function done(){
      btn.textContent = 'コピーしました';
      btn.setAttribute('data-done','1');
      setTimeout(function(){
        btn.textContent = '原稿をコピー';
        btn.removeAttribute('data-done');
      }, 2200);
    }
    function fallback(){
      var ta = document.createElement('textarea');
      ta.value = text;
      ta.setAttribute('readonly','');
      ta.style.position = 'fixed';
      ta.style.top = '-1000px';
      document.body.appendChild(ta);
      ta.select();
      try { document.execCommand('copy'); done(); }
      catch(e){ btn.textContent = 'コピーできませんでした'; }
      document.body.removeChild(ta);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done, fallback);
    } else {
      fallback();
    }
  });
})();
</script>
'''

page = PAGE.replace('__PROSE__', prose).replace('__RAW__', escaped)
io.open(OUT, 'w', encoding='utf-8').write(page)
print('wrote %s (%d bytes)' % (OUT, len(page.encode('utf-8'))))
