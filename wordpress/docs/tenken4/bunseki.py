# -*- coding: utf-8 -*-
u"""保存したHTML 172枚を読んで、検索向け・読みやすさ・前回の積み残し・重さを数える。"""
import re, json, io, sys, html, collections
D = sys.argv[1]
P = json.load(io.open(D + '/pages.json', encoding='utf-8'))
def meta(t, name, attr='name'):
    m = re.search(r'<meta %s="%s" content="([^"]*)"' % (attr, re.escape(name)), t); return html.unescape(m.group(1)) if m else None
rows = []
for d in P:
    t = io.open(D + '/html/' + d['file'], encoding='utf-8').read()
    body = t.split('<section id="main">')[-1].split('<!-- 本文スペース　ここまで -->')[0] if '<section id="main">' in t else t
    title = re.search(r'<title>(.*?)</title>', t, re.S); title = html.unescape(title.group(1).strip()) if title else ''
    imgs = re.findall(r'<img\b[^>]*>', body)
    noalt = [i for i in imgs if not re.search(r'\balt="[^"]+"', i)]
    lds = re.findall(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', t, re.S)
    types, authors = [], []
    for l in lds:
        try: j = json.loads(l)
        except Exception: continue
        g = j.get('@graph', [j]) if isinstance(j, dict) else j
        for n in g:
            if isinstance(n, dict):
                types.append(n.get('@type')); a = n.get('author')
                if isinstance(a, dict) and a.get('name'): authors.append(a['name'])
    h1 = len(re.findall(r'<h1\b', t)); 
    rows.append({'url': d['url'], 'map': d['map'], 'bytes': d['bytes'], 'title': title, 'tlen': len(title),
        'desc': meta(t, 'description'), 'dlen': len(meta(t, 'description') or ''), 'canonical': (re.search(r'<link rel="canonical" href="([^"]+)"', t) or [None, None])[1],
        'robots': meta(t, 'robots'), 'og_image': meta(t, 'og:image', 'property'), 'tw_card': meta(t, 'twitter:card'),
        'h1': h1, 'h2': len(re.findall(r'<h2\b', body)), 'imgs': len(imgs), 'noalt': len(noalt), 'noalt_src': [re.search(r'(?:data-src|src)="([^"]+)"', i).group(1)[-50:] for i in noalt if re.search(r'(?:data-src|src)="([^"]+)"', i)][:3],
        'ld_types': types, 'authors': authors, 'scripts_ext': len(re.findall(r'<script[^>]+src=', t)), 'css_ext': len(re.findall(r'<link[^>]+rel=.stylesheet', t)),
        'inline_style_blocks': len(re.findall(r'<style\b', t)), 'iframes': len(re.findall(r'<iframe\b', body)), 'videos': len(re.findall(r'<video\b', body)),
        'internal_links': len(set(re.findall(r'href="(https://www\.ishinazaka\.co\.jp/[^"#]*)"', body))), 'ext_links': len(set(re.findall(r'href="(https?://(?!www\.ishinazaka\.co\.jp)[^"]+)"', body))),
        'text_len': len(re.sub(r'\s', '', html.unescape(re.sub(r'<[^>]+>', '', re.sub(r'<(script|style)[^>]*>.*?</\1>', '', body, flags=re.S))))),
        'modified': meta(t, 'article:modified_time', 'property') or meta(t, 'og:updated_time', 'property'),
        'published': meta(t, 'article:published_time', 'property'),
        'lazy': body.count('class="lazyload') + body.count('lazyload"'), 'xmlns_https': 'xmlns="https://www.w3.org/1999/xhtml"' in t,
        'footer_alt_old': 'alt="株式会社石名坂"' in t, 'gc_name': (re.search(r'"@type":"GeneralContractor"[^}]*?"name":"([^"]+)"', t) or [None, None])[1],
        'hsts': bool((d.get('headers') or {}).get('Strict-Transport-Security')), 'cache': (d.get('headers') or {}).get('Cache-Control'), 'xcto': (d.get('headers') or {}).get('X-Content-Type-Options')})
json.dump(rows, io.open(D + '/bunseki.json', 'w', encoding='utf-8'), ensure_ascii=False)
n = len(rows); posts = [r for r in rows if r['map'].startswith('post-')]
print(u'ページ', n, u'／記事', len(posts))
print(u'題名 なし', sum(1 for r in rows if not r['title']), u'／ 35字超', sum(1 for r in rows if r['tlen'] > 35), u'／重複', sum(c - 1 for c in collections.Counter(r['title'] for r in rows).values() if c > 1))
print(u'説明文 なし', sum(1 for r in rows if not r['desc']), u'／ 120字超', sum(1 for r in rows if r['dlen'] > 120), u'／ 60字未満', sum(1 for r in rows if 0 < r['dlen'] < 60), u'／重複', sum(c - 1 for c in collections.Counter(r['desc'] for r in rows if r['desc']).values() if c > 1))
print(u'canonical なし', sum(1 for r in rows if not r['canonical']), u'／ 自分と違う', [r['url'] for r in rows if r['canonical'] and r['canonical'].rstrip('/') != r['url'].rstrip('/')][:5])
print(u'noindex', [r['url'] for r in rows if r['robots'] and 'noindex' in r['robots']])
print(u'h1 が1でない', collections.Counter(r['h1'] for r in rows))
print(u'og:image なし', [r['url'] for r in rows if not r['og_image']])
print(u'twitter:card あり', sum(1 for r in rows if r['tw_card']))
print(u'alt なし画像', sum(r['noalt'] for r in rows), u'枚 /', sum(1 for r in rows if r['noalt']), u'ページ')
au = collections.Counter(a for r in rows for a in set(r['authors'])); print(u'構造化データの著者', dict(au))
print(u'xmlns https', sum(1 for r in rows if r['xmlns_https']), u'／ フッターalt旧', sum(1 for r in rows if r['footer_alt_old']), u'／ GeneralContractor', collections.Counter(r['gc_name'] for r in rows))
print(u'HSTS', sum(1 for r in rows if r['hsts']), u'／ X-Content-Type-Options', sum(1 for r in rows if r['xcto']), u'／ Cache-Control', collections.Counter(r['cache'] for r in rows).most_common(3))
import statistics as st
print(u'HTML 重さ 中央値 %dKB 最大 %dKB %s' % (st.median(r['bytes'] for r in rows)//1024, max(r['bytes'] for r in rows)//1024, max(rows, key=lambda r: r['bytes'])['url']))
print(u'外部スクリプト数 中央値', st.median(r['scripts_ext'] for r in rows), u'／ CSS', st.median(r['css_ext'] for r in rows), u'／ style ブロック', st.median(r['inline_style_blocks'] for r in rows))
print(u'本文の字数 記事の中央値', st.median(r['text_len'] for r in posts), u'／ 500字未満の記事', sum(1 for r in posts if r['text_len'] < 500))
print(u'内部リンク 記事の中央値', st.median(r['internal_links'] for r in posts), u'／ 3本未満', sum(1 for r in posts if r['internal_links'] < 3))
print(u'iframe あり', sum(1 for r in rows if r['iframes']), u'／ video', sum(1 for r in rows if r['videos']))
yrs = collections.Counter((r['published'] or '')[:7] for r in posts); print(u'記事の公開月', sorted(yrs.items())[-8:])
print(u'説明文60字未満の例', [(r['url'][-40:], r['dlen']) for r in rows if 0 < r['dlen'] < 60][:8])
print(u'題名35字超の例', [(r['title'][:50], r['tlen']) for r in rows if r['tlen'] > 35][:8])
