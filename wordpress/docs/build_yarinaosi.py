# -*- coding: utf-8 -*-
"""挿絵を1番から作り直すための、手順書ページを作る。

中身は既存のファイルから読む。ここには何も書かない（二重管理を避けるため）。
  ・Geminiに貼る文 → images/gen_images.py の SHOTS と STYLE
  ・ファイル名・代替テキスト等 → docs/build_gazou_seo.py の SHOTS
  ・焼き込む文字 → images/label_images.py の LABELS

    python3 build_yarinaosi.py
"""
from __future__ import print_function

import html
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'sasie-yarinaosi.html')
E = html.escape


def pick(path, start, end):
    src = io.open(path, encoding='utf-8').read()
    ns = {}
    exec(compile(src[src.index(start):src.index(end)], path, 'exec'), ns)
    return ns


def load():
    img = os.path.join(HERE, '..', 'images')
    # prompt_of まで取り込んで、そのまま呼ぶ。ここで組み立て直すと
    # 矢印禁止のような後からの決めごとが手順書に反映されない。
    g = pick(os.path.join(img, 'gen_images.py'), 'STYLE = (', 'def get_key')
    s = pick(os.path.join(HERE, 'build_gazou_seo.py'), 'SHOTS = [', 'FIELDS = [')
    l = pick(os.path.join(img, 'label_images.py'), 'LABELS = {', 'def load_shots')
    prompts = {x['n']: g['prompt_of'](x) for x in g['SHOTS']}
    return [dict(seo, prompt=prompts[seo['n']], label=l['LABELS'].get(seo['n'], {}))
            for seo in s['SHOTS']]


SHOTS = load()
assert len(SHOTS) == 8, len(SHOTS)

SLOTS = [
    ('prompt', u'Gemini に貼る文',  u'英語のまま貼ってください', True),
    ('fname',  u'ファイル名',        u'保存するときの名前',       True),
    ('alt',    u'代替テキスト',      u'いちばん効く欄',           False),
    ('mtitle', u'タイトル',          u'メディアライブラリ',       False),
    ('caption', u'キャプション',     u'画像の下に出る文',         False),
    ('desc',   u'説明',              u'メディアライブラリ',       False),
]


def card(s):
    p = [u'<section class="shot" id="n%d">' % s['n']]
    p.append(u'<header class="head">')
    p.append(u'<span class="num">%d</span>' % s['n'])
    p.append(u'<div><h2>%s</h2>'
             u'<p class="where"><b>%s</b>／%s</p></div>'
             % (E(s['title']), E(s['part']), E(s['where'])))
    if s['url']:
        p.append(u'<span class="chip redo">いまの絵を差し替え</span>')
    else:
        p.append(u'<span class="chip new">これから作る</span>')
    p.append(u'</header>')

    p.append(u'<ol class="slots">')
    for i, (key, label, hint, mono) in enumerate(SLOTS, 1):
        pid = u'f%d%s' % (s['n'], key)
        p.append(u'<li>')
        p.append(u'<p class="lab"><span class="step">%d</span>%s'
                 u'<em>%s</em></p>' % (i, E(label), E(hint)))
        p.append(u'<div class="val">')
        p.append(u'<pre id="%s" class="%s">%s</pre>'
                 % (pid, u'mono' if mono else u'ja', E(s[key])))
        p.append(u'<button type="button" data-src="%s">コピー</button>' % pid)
        p.append(u'</div></li>')
    p.append(u'</ol>')

    lb = s['label']
    if lb:
        p.append(u'<div class="burn"><p class="bl">このあと、こちらで焼き込む文字</p>')
        p.append(u'<p class="bh">%s</p>' % E(lb['head']))
        p.append(u'<p class="bs">%s</p>' % E(lb['sub']))
        co = lb.get('callouts') or []
        if co:
            p.append(u'<p class="bc">引き出し線：%s</p>'
                     % E(u'／'.join(c[4] for c in co)))
        p.append(u'</div>')
    p.append(u'</section>')
    return u'\n'.join(p)


PAGE = u'''<title>挿絵の作り直し手順</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Zen+Antique&family=Zen+Kaku+Gothic+New:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{
  --ground:#E9ECED; --paper:#FBFBFA; --sunk:#F1F2F1;
  --ink:#1C2124; --ink-soft:#585F63; --ink-faint:#868E92;
  --rule:#CDD2D3; --rule-soft:#E0E4E4;
  --copper:#A8642A; --copper-soft:#F3EBE2;
  --new:#2C6257; --new-soft:#E7EFEC;
  --shadow:rgba(28,33,36,.09);
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --ground:#111516; --paper:#191D1F; --sunk:#131819;
    --ink:#E8ECEC; --ink-soft:#A0A9AC; --ink-faint:#798286;
    --rule:#2C3336; --rule-soft:#232A2C;
    --copper:#D2925B; --copper-soft:#241C14;
    --new:#77BBA8; --new-soft:#14201D;
    --shadow:rgba(0,0,0,.5);
  }
}
:root[data-theme="dark"]{
  --ground:#111516; --paper:#191D1F; --sunk:#131819;
  --ink:#E8ECEC; --ink-soft:#A0A9AC; --ink-faint:#798286;
  --rule:#2C3336; --rule-soft:#232A2C;
  --copper:#D2925B; --copper-soft:#241C14;
  --new:#77BBA8; --new-soft:#14201D;
  --shadow:rgba(0,0,0,.5);
}
*{box-sizing:border-box}
body{
  margin:0; background:var(--ground); color:var(--ink);
  font-family:"Zen Kaku Gothic New","Hiragino Kaku Gothic ProN","Yu Gothic",sans-serif;
  font-size:16px; line-height:1.85;
  -webkit-text-size-adjust:100%;
}
.wrap{max-width:760px; margin:0 auto; padding:0 18px; padding-block:clamp(28px,6vw,56px)}
h1{
  font-family:"Zen Antique",serif; font-weight:400;
  font-size:clamp(28px,7vw,40px); line-height:1.35; letter-spacing:.02em;
  margin:0 0 .5em; text-wrap:balance;
}
.lede{color:var(--ink-soft); margin:0 0 6px; font-size:15px}
.stamp{
  display:inline-block; font-size:12px; letter-spacing:.14em;
  color:var(--copper); border:1px solid var(--copper);
  padding:3px 10px; border-radius:2px; margin-bottom:18px;
}

/* 進め方 */
.flow{
  background:var(--paper); border:1px solid var(--rule);
  border-radius:3px; padding:20px 20px 8px; margin:26px 0 40px;
  box-shadow:0 1px 2px var(--shadow);
}
.flow h2{font-size:15px; margin:0 0 14px; letter-spacing:.06em}
.flow ol{margin:0; padding:0; list-style:none; display:grid; gap:14px}
.flow li{display:grid; grid-template-columns:26px 1fr; gap:12px; align-items:start}
.flow b{
  font-family:"IBM Plex Mono",monospace; font-weight:500; font-size:13px;
  color:var(--copper); border:1px solid var(--rule); border-radius:50%;
  width:26px; height:26px; display:grid; place-items:center; margin-top:3px;
}
.flow p{margin:0; font-size:15px}
.flow p span{display:block; color:var(--ink-soft); font-size:13.5px; line-height:1.7}
.flow footer{
  border-top:1px solid var(--rule-soft); margin-top:16px; padding:12px 0 10px;
  font-size:13.5px; color:var(--ink-soft);
}

/* 1枚ぶん */
.shot{
  background:var(--paper); border:1px solid var(--rule);
  border-radius:3px; margin:0 0 30px; overflow:hidden;
  box-shadow:0 1px 2px var(--shadow);
}
.head{
  display:grid; grid-template-columns:auto 1fr; gap:14px; align-items:start;
  padding:20px; border-bottom:1px solid var(--rule-soft);
}
.num{
  font-family:"Zen Antique",serif; font-size:34px; line-height:1;
  color:var(--copper); width:40px; text-align:center;
}
.head h2{font-size:19px; margin:0; line-height:1.4; letter-spacing:.01em}
.where{margin:2px 0 0; font-size:13.5px; color:var(--ink-soft)}
.where b{color:var(--ink); font-weight:500}
.chip{
  grid-column:2; justify-self:start; font-size:12px; letter-spacing:.06em;
  padding:2px 9px; border-radius:2px; margin-top:8px;
}
.chip.redo{background:var(--copper-soft); color:var(--copper)}
.chip.new{background:var(--new-soft); color:var(--new)}

.slots{margin:0; padding:0; list-style:none}
.slots li{padding:16px 20px; border-bottom:1px solid var(--rule-soft)}
.lab{
  margin:0 0 8px; font-size:14px; font-weight:500;
  display:flex; align-items:center; gap:9px; flex-wrap:wrap;
}
.step{
  font-family:"IBM Plex Mono",monospace; font-size:11px; font-weight:500;
  color:var(--ink-faint); border:1px solid var(--rule);
  width:19px; height:19px; border-radius:2px; display:grid; place-items:center;
}
.lab em{font-style:normal; font-size:12.5px; color:var(--ink-faint); font-weight:400}
.val{display:flex; gap:10px; align-items:flex-start}
pre{
  flex:1; min-width:0; margin:0; padding:11px 13px;
  background:var(--sunk); border:1px solid var(--rule-soft); border-radius:2px;
  white-space:pre-wrap; word-break:break-word; overflow-wrap:anywhere;
}
pre.mono{font-family:"IBM Plex Mono",monospace; font-size:13px; line-height:1.75}
pre.ja{font-family:inherit; font-size:14px; line-height:1.8}
button{
  flex:none; font:inherit; font-size:13px; cursor:pointer;
  background:transparent; color:var(--copper);
  border:1px solid var(--copper); border-radius:2px; padding:7px 12px;
  min-width:64px;
}
button:hover{background:var(--copper-soft)}
button:focus-visible{outline:2px solid var(--copper); outline-offset:2px}
button.done{background:var(--copper); color:var(--paper)}

.burn{padding:16px 20px 18px; background:var(--sunk)}
.bl{
  margin:0 0 9px; font-size:11.5px; letter-spacing:.12em; color:var(--ink-faint);
}
.bh{margin:0; font-size:17px; font-weight:700; line-height:1.5}
.bs{margin:3px 0 0; font-size:13.5px; color:var(--ink-soft); line-height:1.75}
.bc{
  margin:9px 0 0; font-size:13px; color:var(--copper);
  border-top:1px solid var(--rule-soft); padding-top:9px;
}
footer.end{
  color:var(--ink-soft); font-size:13.5px; line-height:1.85;
  border-top:1px solid var(--rule); padding-top:18px; margin-top:8px;
}
@media (max-width:420px){
  .val{flex-direction:column}
  button{width:100%}
}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
</style>

<div class="wrap">
<p class="stamp">株式会社石名坂／量子コンピュータ記事</p>
<h1>挿絵の作り直し手順</h1>
<p class="lede">1番から8番まで、上から順に。1枚ずつ片づけてください。</p>

<div class="flow">
<h2>1枚あたりの進め方</h2>
<ol>
<li><b>1</b><p>Gemini アプリに「Gemini に貼る文」を貼る<span>英語のままで結構です。日本語に直すと絵が変わります。文字は入れさせません——あとでこちらが正確に焼き込みます。</span></p></li>
<li><b>2</b><p>出てきた絵を保存する<span>気に入らなければ、同じ文でもう一度。何度でも構いません。</span></p></li>
<li><b>3</b><p>WordPress に上げて、URL を送る<span>ファイル名はそのままで結構です。こちらで正しい名前に付け替えます。</span></p></li>
<li><b>4</b><p>あとはこちらで<span>日本語の見出しを焼き込み、正しいファイル名で入れ直し、代替テキスト・タイトル・キャプション・説明を入れて、古いほうを消します。</span></p></li>
</ol>
<footer>いま使っている Gemini 3.6 Flash は、絵そのものを描くモデルではありません。アプリが裏で Nano Banana 2 に渡しています。つまり絵の出来は Flash の番号では変わりません。</footer>
</div>

__CARDS__

<footer class="end">
1番と2番は、すでにサイトに上がっているものと差し替えになります。新しいほうが入り、そのあと古いほうを消します。消す前に必ずお伝えします。<br><br>
キャプションの「イメージ図（生成AIで作成）」は、8枚すべてに付けたままにしてください。実在の装置の写真ではないことを、読む人に伝えるためです。
</footer>
</div>

<script>
document.querySelectorAll('button[data-src]').forEach(function(b){
  b.addEventListener('click', function(){
    var t = document.getElementById(b.dataset.src);
    if(!t) return;
    var txt = t.textContent;
    var done = function(){
      var was = b.textContent;
      b.textContent = 'コピーしました';
      b.classList.add('done');
      setTimeout(function(){ b.textContent = was; b.classList.remove('done'); }, 1600);
    };
    if(navigator.clipboard && navigator.clipboard.writeText){
      navigator.clipboard.writeText(txt).then(done, function(){ fallback(txt, done); });
    } else { fallback(txt, done); }
  });
});
function fallback(txt, done){
  var a = document.createElement('textarea');
  a.value = txt; a.setAttribute('readonly','');
  a.style.position='fixed'; a.style.top='-1000px';
  document.body.appendChild(a); a.select();
  try{ document.execCommand('copy'); done(); }catch(e){}
  document.body.removeChild(a);
}
</script>
'''

page = PAGE.replace(u'__CARDS__', u'\n'.join(card(s) for s in SHOTS))
io.open(OUT, 'w', encoding='utf-8').write(page)
print(u'%s  %.1f KB  （%d枚）' % (OUT, os.path.getsize(OUT) / 1024.0, len(SHOTS)))
