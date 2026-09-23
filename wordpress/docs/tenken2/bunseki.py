# -*- coding: utf-8 -*-
# 2回目の点検：保存したHTMLを読んで、ページごとの情報を取り出す（読むだけ）
import re, json, io, html
P = json.load(io.open('/tmp/claude-0/site2/pages.json', encoding='utf-8'))
NIHON = re.compile(u'[぀-ゟ゠-ヿ一-鿿、-〿！-｠・]')

def fushizen(s):
    if not s: return 0
    s = re.sub(u' +', u' ', s); n = 0
    for i, ch in enumerate(s):
        if ch != u' ': continue
        m = s[i-1] if i > 0 else u''; a = s[i+1] if i+1 < len(s) else u''
        if (m and NIHON.match(m)) or (a and NIHON.match(a)): n += 1
    return n

def hiku(t, pat):
    m = re.search(pat, t, re.S | re.I)
    return html.unescape(m.group(1).strip()) if m else None

out = []
for d in P:
    if d.get('code') != 200: out.append(d); continue
    t = io.open('/tmp/claude-0/site2/html/' + d['file'], encoding='utf-8').read()
    i = t.find('</head>'); atama, hon = t[:i], t[i:]
    r = dict(d)
    r['title'] = hiku(atama, r'<title>(.*?)</title>')
    r['desc']  = hiku(atama, r'<meta name="description" content="(.*?)"')
    r['canon'] = hiku(atama, r'<link rel="canonical" href="(.*?)"')
    r['robots']= hiku(atama, r'<meta name="robots" content="(.*?)"')
    r['og_t']  = hiku(atama, r'property="og:title" content="(.*?)"')
    r['og_d']  = hiku(atama, r'property="og:description" content="(.*?)"')
    r['og_i']  = hiku(atama, r'property="og:image" content="(.*?)"')
    r['tw']    = hiku(atama, r'name="twitter:card" content="(.*?)"')
    r['lang']  = hiku(t[:400], r'<html[^>]*lang="([^"]+)"')
    r['vp']    = bool(re.search(r'name="viewport"', atama))
    # JSON-LD
    r['ld_types'], r['ld_author'], r['ld_pub'], r['ld_mod'] = [], [], None, None
    for m in re.finditer(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', t, re.S):
        try: j = json.loads(m.group(1))
        except Exception: r['ld_types'].append('READ_ERROR'); continue
        g = j.get('@graph', [j]) if isinstance(j, dict) else j
        for x in g:
            if not isinstance(x, dict): continue
            ty = x.get('@type'); ty = ty if isinstance(ty, str) else ','.join(ty or [])
            r['ld_types'].append(ty)
            if ty == 'Person': r['ld_author'].append(x.get('name'))
            if ty in ('BlogPosting', 'Article', 'NewsArticle'):
                r['ld_pub'] = x.get('datePublished'); r['ld_mod'] = x.get('dateModified')
    # 本文
    hon2 = re.sub(r'<script.*?</script>|<style.*?</style>|<noscript.*?</noscript>', '', hon, flags=re.S)
    r['h1'] = [html.unescape(re.sub(r'<[^>]+>', '', x)).strip() for x in re.findall(r'<h1[^>]*>(.*?)</h1>', hon2, re.S)]
    r['h2'] = len(re.findall(r'<h2[^>]*>', hon2)); r['h3'] = len(re.findall(r'<h3[^>]*>', hon2))
    r['moji'] = len(re.sub(r'\s+', '', html.unescape(re.sub(r'<[^>]+>', '', hon2))))
    # 画像
    img = {}
    for m in re.finditer(r'<img[^>]*>', hon2):
        s = m.group(0)
        src = hiku(s, r'data-src="([^"]+)"') or hiku(s, r'\ssrc="([^"]+)"') or ''
        if src.startswith('data:'): continue
        alt = hiku(s, r'alt="([^"]*)"')
        wh = bool(re.search(r'\swidth="\d', s)) and bool(re.search(r'\sheight="\d', s))
        if src not in img: img[src] = (alt, wh)
    r['imgs'] = [{'src': k, 'alt': v[0], 'wh': v[1]} for k, v in img.items()]
    # リンク
    r['uchi'] = sorted(set(html.unescape(x) for x in re.findall(r'href="(https?://www\.ishinazaka\.co\.jp/[^"#]*)"', hon2)))
    r['soto'] = sorted(set(html.unescape(x) for x in re.findall(r'href="(https?://(?!www\.ishinazaka\.co\.jp)[^"]+)"', hon2)))
    r['http_src'] = sorted(set(re.findall(r'(?:src|href)="(http://[^"]+\.(?:js|css|png|jpe?g|gif|webp|svg))"', t)))
    r['sp'] = fushizen(r['title']) + fushizen(r['desc']) + sum(fushizen(x) for x in r['h1'])
    r['n_script'] = len(re.findall(r'<script\b', t)); r['n_css'] = len(re.findall(r'rel=["\']stylesheet', t))
    out.append(r)
json.dump(out, io.open('/tmp/claude-0/site2/bunseki.json', 'w', encoding='utf-8'), ensure_ascii=False)
print(u'分析しました:', len(out))
