# -*- coding: utf-8 -*-
# 画像の重さと、サイト内リンクの生死を調べる（読むだけ）
import json, io, re, time, collections, urllib.parse as up
import urllib.request as ur, urllib.error as ue
from concurrent.futures import ThreadPoolExecutor
A = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/125.0 Safari/537.36','Accept-Language':'ja'}
R = json.load(io.open('/tmp/claude-0/site2/bunseki.json', encoding='utf-8'))
ok = [r for r in R if r.get('code') == 200]

def kanzen(u):
    p = up.urlsplit(u)
    path = p.path if re.search(r'%[0-9A-Fa-f]{2}', p.path) else up.quote(p.path)
    return up.urlunsplit((p.scheme, p.netloc, path, p.query, ''))

# 画像（サイト内のもの）
img_moto = collections.defaultdict(set)
for r in ok:
    for im in r['imgs']:
        s = im['src']
        if s.startswith('/'): s = 'https://www.ishinazaka.co.jp' + s
        if 'ishinazaka.co.jp' in s: img_moto[s].add(r['url'])
def omosa(u):
    time.sleep(0.05)
    try:
        r = ur.urlopen(ur.Request(kanzen(u), method='HEAD', headers=A), timeout=40)
        return u, r.getcode(), int(r.headers.get('Content-Length') or 0), r.headers.get('Content-Type')
    except ue.HTTPError as e:
        try:
            r = ur.urlopen(ur.Request(kanzen(u), headers=A), timeout=40)
            b = r.read(); return u, r.getcode(), len(b), r.headers.get('Content-Type')
        except ue.HTTPError as e2: return u, e2.code, 0, None
        except Exception as e2: return u, type(e2).__name__, 0, None
    except Exception as e:
        return u, type(e).__name__, 0, None
res = {}
with ThreadPoolExecutor(max_workers=6) as ex:
    for u, c, n, ty in ex.map(omosa, sorted(img_moto)):
        res[u] = {'code': c, 'bytes': n, 'type': ty, 'pages': sorted(img_moto[u])}
json.dump(res, io.open('/tmp/claude-0/site2/img.json', 'w', encoding='utf-8'), ensure_ascii=False)
print(u'画像（サイト内）:', len(res))

# サイト内リンク
shitte = set(r['url'].rstrip('/') for r in R)
uchi_moto = collections.defaultdict(set)
for r in ok:
    for l in r['uchi']:
        l2 = l.split('?')[0].rstrip('/')
        if re.search(r'\.(png|jpe?g|gif|webp|svg|pdf|css|js|xml|ico|mp4)$', l2, re.I): continue
        if '/wp-json' in l2 or '/common/sys/' in l2 or '/feed' in l2: continue
        if l2 not in shitte: uchi_moto[l2].add(r['url'])
def iki(u):
    time.sleep(0.08)
    try:
        r = ur.urlopen(ur.Request(kanzen(u + '/'), headers=A), timeout=40)
        return u, r.getcode(), r.geturl()
    except ue.HTTPError as e: return u, e.code, None
    except Exception as e: return u, type(e).__name__, None
res2 = {}
with ThreadPoolExecutor(max_workers=5) as ex:
    for u, c, saigo in ex.map(iki, sorted(uchi_moto)):
        res2[u] = {'code': c, 'saigo': saigo, 'pages': sorted(uchi_moto[u])}
json.dump(res2, io.open('/tmp/claude-0/site2/uchi.json', 'w', encoding='utf-8'), ensure_ascii=False)
print(u'サイトマップに無いサイト内リンク先:', len(res2))
