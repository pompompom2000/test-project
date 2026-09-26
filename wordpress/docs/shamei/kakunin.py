# -*- coding: utf-8 -*-
u"""公開ページを開いて、「株式会社石名坂」「株式会社　石名坂」が残っていないか数える。
書き込みはしない。場所ごと（題名・説明文・本文・それ以外）に分けて数える。"""
import re, json, time, urllib.request as ur
from concurrent.futures import ThreadPoolExecutor
ZURE = re.compile(u'株式会社(?:　)?石名坂')
UA = {'User-Agent': 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/128 Mobile Safari/537.36'}
def toru(u):
    for i in range(4):
        try:
            return ur.urlopen(ur.Request(u, headers=UA), timeout=60).read().decode('utf-8', 'replace')
        except Exception:
            time.sleep(5 * (i + 1))
    return None
sm = toru('https://www.ishinazaka.co.jp/sitemap.xml') or ''
subs = re.findall(r'<loc>(?:<!\[CDATA\[)?([^<\]]+)', sm)
urls = []
for s in subs:
    if s.endswith('.xml'):
        urls += [u for u in re.findall(r'<loc>(?:<!\[CDATA\[)?([^<\]]+)', toru(s) or '') if not u.endswith('.xml')]
    else:
        urls.append(s)
urls = sorted(set(urls))
def mite(u):
    h = toru(u)
    if h is None:
        return u, None
    h2 = re.sub(r'\s*\?ver=[^"\']*', '', h)
    ks = {}
    t = re.search(r'<title>(.*?)</title>', h, re.S)
    ks['題名'] = len(ZURE.findall(t.group(1))) if t else 0
    ks['説明・OGP'] = sum(len(ZURE.findall(m)) for m in re.findall(r'<meta[^>]+content="([^"]*)"', h))
    ks['構造化データ'] = sum(len(ZURE.findall(m)) for m in re.findall(r'<script[^>]*ld\+json[^>]*>(.*?)</script>', h, re.S))
    b = re.search(r'<div class="entry-content[^"]*"[^>]*>(.*?)<footer|<div class="entry-content[^"]*"[^>]*>(.*)', h, re.S)
    ks['本文'] = len(ZURE.findall(b.group(0))) if b else 0
    ks['全体'] = len(ZURE.findall(h))
    return u, ks
with ThreadPoolExecutor(4) as ex:
    kekka = list(ex.map(mite, urls))
gokei = {}
nokori = []
for u, ks in kekka:
    if ks is None:
        nokori.append((u, u'取れず')); continue
    for k, v in ks.items(): gokei[k] = gokei.get(k, 0) + v
    if ks['全体']:
        nokori.append((u, ks))
print(u'公開ページ: %d' % len(urls))
print(u'合計: ' + json.dumps(gokei, ensure_ascii=False))
for u, ks in nokori[:15]:
    print(u, json.dumps(ks, ensure_ascii=False))
print(u'残りのあるページ: %d' % len(nokori))
