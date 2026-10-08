# -*- coding: utf-8 -*-
u"""盛岡の現場の一文を、石名坂自身が白ナンバーに頼んでいるように読めない形にする（藤原さんの指示）。
・鍵は IZK_AUTH からだけ読む。--apply と --yes の両方がなければ書き込まない
・下書きでなければ中止。置き換える文字列がちょうど1回あることを確かめる"""
import os, sys, json, base64, urllib.request as ur
SITE = 'https://www.ishinazaka.co.jp/wp-json'
PID = 6469
MAE = u'盛岡の現場では、工事の山場ほどダンプが足りなくなります。そんなとき「白ナンバーでも空いている車があるから頼もう」という話は、いまでも出てくることがあると思います。'
ATO = u'盛岡でも、工事の山場にはダンプが足りなくなります。そんな時期に「白ナンバーでも空いている車があれば」と考える会社がある、という話は、業界でいまも耳にします。'
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
print(u'置き換え後: ' + ATO)
if kaku:
    yobu('/wp/v2/posts/%d' % PID, {'content': new})
    y = yobu('/wp/v2/posts/%d?context=edit' % PID)
    assert y['content']['raw'] == new and y['status'] == 'draft'
    print(u'直しました。状態は %s のまま。' % y['status'])
