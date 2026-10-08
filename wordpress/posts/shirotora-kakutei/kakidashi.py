# -*- coding: utf-8 -*-
u"""書き出しの一文から、関連会社の名前を外す（藤原さんの指示）。
・鍵は IZK_AUTH からだけ読む。--apply と --yes の両方がなければ書き込まない
・下書きでなければ中止。置き換える文字列がちょうど1回あることを確かめる"""
import os, sys, json, base64, urllib.request as ur
SITE = 'https://www.ishinazaka.co.jp/wp-json'
PID = 6469
MAE = u'10月6日、関連会社の有限会社石名坂商事が加わっている岩手県トラック協会のダンプトラック部会から、会員向けのお知らせがFAXで届きました。'
ATO = u'10月6日、岩手県トラック協会のダンプトラック部会から、会員向けのお知らせがFAXで届きました。'
def yobu(p, obj=None):
    q = ur.Request(SITE + p, data=json.dumps(obj).encode('utf-8') if obj is not None else None,
                   method='POST' if obj is not None else 'GET')
    q.add_header('Authorization', 'Basic ' + base64.b64encode(os.environ['IZK_AUTH'].encode()).decode())
    q.add_header('User-Agent', 'Mozilla/5.0')
    if obj is not None: q.add_header('Content-Type', 'application/json; charset=utf-8')
    return json.load(ur.urlopen(q, timeout=120))
kaku = '--apply' in sys.argv and '--yes' in sys.argv
x = yobu('/wp/v2/posts/%d?context=edit' % PID)
assert x['status'] == 'draft', x['status']
body = x['content']['raw']
n = body.count(MAE)
print(u'書き込み: ' + (u'する' if kaku else u'しない'), u'／置き換える箇所: %d' % n)
if n != 1: sys.exit(1)
new = body.replace(MAE, ATO)
assert new.replace(ATO, u'\x00') == body.replace(MAE, u'\x00')
print(u'石名坂商事の残り（置き換え後）: %d' % new.count(u'石名坂商事'))
if kaku:
    yobu('/wp/v2/posts/%d' % PID, {'content': new})
    y = yobu('/wp/v2/posts/%d?context=edit' % PID)
    assert y['content']['raw'] == new and y['status'] == 'draft'
    print(u'直しました。状態は %s のまま。' % y['status'])
