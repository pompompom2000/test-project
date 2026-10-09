# -*- coding: utf-8 -*-
u"""白トラの記事（ID 6469）を公開する。藤原さんの「公開して」（2026年10月9日）を受けて作った。
・鍵は IZK_AUTH からだけ読む。--apply と --yes の両方がなければ書き込まない
・この記事以外は触らない。本文は変えず、状態だけを draft → publish にする
・公開後、公開ページが200で開き、題名と画像5枚が見えることを確かめる"""
import os, sys, json, base64, re, urllib.request as ur
SITE = 'https://www.ishinazaka.co.jp/wp-json'
PID = 6469
def yobu(p, obj=None):
    q = ur.Request(SITE + p, data=json.dumps(obj).encode('utf-8') if obj is not None else None,
                   method='POST' if obj is not None else 'GET')
    q.add_header('Authorization', 'Basic ' + base64.b64encode(os.environ['IZK_AUTH'].encode()).decode())
    q.add_header('User-Agent', 'Mozilla/5.0')
    if obj is not None: q.add_header('Content-Type', 'application/json; charset=utf-8')
    return json.load(ur.urlopen(q, timeout=120))
kaku = '--apply' in sys.argv and '--yes' in sys.argv
x = yobu('/wp/v2/posts/%d?context=edit' % PID)
print(u'書き込み: ' + (u'する（公開）' if kaku else u'しない'), u'／いまの状態:', x['status'], u'／スラッグ:', x['slug'])
assert x['slug'] == 'shiro-tora-shobun-kijun-kakutei'
if x['status'] != 'draft':
    print(u'下書きではありません。中止します。'); sys.exit(1)
mae = x['content']['raw']
if not kaku: sys.exit()
yobu('/wp/v2/posts/%d' % PID, {'status': 'publish'})
y = yobu('/wp/v2/posts/%d?context=edit' % PID)
assert y['status'] == 'publish' and y['content']['raw'] == mae
print(u'公開しました:', y['link'], y['date'])
h = ur.urlopen(ur.Request(y['link'] + '?nc=1', headers={'User-Agent': 'Mozilla/5.0'}), timeout=60).read().decode('utf-8')
print(u'公開ページ: 題名あり=%s ／ 画像=%d枚' % (u'白トラの行政処分、10月1日から重く' in h,
      len(set(re.findall(r'wp-image-(6472|6473|6476|6477|6478)', h)))))
