# -*- coding: utf-8 -*-
# 2回目の点検：全ページを取り直して、HTMLをそのまま保存する（鍵は使わない）
import re, json, io, time, hashlib
import urllib.request as ur, urllib.error as ue
from concurrent.futures import ThreadPoolExecutor

A = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/125.0 Safari/537.36',
     'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
     'Accept-Language':'ja,en-US;q=0.9'}

def toru(u):
    r = ur.urlopen(ur.Request(u, headers=A), timeout=60)
    return r.getcode(), r.read().decode('utf-8', 'replace'), r.geturl()

def locs(s):
    return re.findall(r'<loc>\s*(?:<!\[CDATA\[)?\s*(https?://[^\]<\s]+?)\s*(?:\]\]>)?\s*</loc>', s)

c, s, _ = toru('https://www.ishinazaka.co.jp/sitemap.xml')
url = []
for k in locs(s):
    _, ss, _ = toru(k)
    for u in locs(ss):
        url.append({'map': k.split('/')[-1], 'url': u})
print(u'サイトマップ:', len(url))

def hozon(rec):
    time.sleep(0.15)
    u = rec['url']
    try:
        c, t, saigo = toru(u)
    except ue.HTTPError as e:
        rec['code'] = e.code; return rec
    except Exception as e:
        rec['code'] = type(e).__name__; return rec
    rec['code'] = c
    rec['saigo'] = saigo
    rec['bytes'] = len(t.encode('utf-8'))
    na = hashlib.md5(u.encode()).hexdigest()[:12] + '.html'
    io.open('/tmp/claude-0/site2/html/' + na, 'w', encoding='utf-8').write(t)
    rec['file'] = na
    return rec

out = []
with ThreadPoolExecutor(max_workers=4) as ex:
    for i, r in enumerate(ex.map(hozon, url), 1):
        out.append(r)
json.dump(out, io.open('/tmp/claude-0/site2/pages.json', 'w', encoding='utf-8'), ensure_ascii=False)
print(u'取得:', len(out), u'／ 200以外:', [(d['url'], d['code']) for d in out if d['code'] != 200])
