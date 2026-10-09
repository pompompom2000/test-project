# -*- coding: utf-8 -*-
u"""8月の記事（ID 4563、意見募集の段階の内容）の冒頭に、正式に決まった記事への案内を1段落足す。
・鍵は IZK_AUTH からだけ読む。--apply と --yes の両方がなければ書き込まない
・行き先（6469）が公開済みでなければ中止。目印がちょうど1回あることを確かめ、
  足した段落の外側が一字も変わっていないことを確かめてから書き込む"""
import os, sys, json, base64, urllib.request as ur
SITE = 'https://www.ishinazaka.co.jp/wp-json'
MOTO, IKI = 4563, 6469
MARK = u'<!-- wp:paragraph {"fontSize":"medium"} -->\n<p class="has-medium-font-size">国土交通省は令和8年7月30日'
URL = u'https://www.ishinazaka.co.jp/shiro-tora-shobun-kijun-kakutei/'
TSUIKI = (u'<!-- wp:paragraph {"fontSize":"medium"} -->\n<p class="has-medium-font-size"><strong>【2026年10月9日 追記】</strong>'
          u'この記事は、7月30日に始まった意見募集の段階の内容です。改正は9月29日に正式に決まり、10月1日以降の違反から適用されています。'
          u'決まった日数と、新たに加わった決まりは「<a href="%s">白トラの行政処分、10月1日から重く｜決まった日数と新たに加わった決まり</a>」にまとめました。</p>\n'
          u'<!-- /wp:paragraph -->\n\n') % URL
def yobu(p, obj=None):
    q = ur.Request(SITE + p, data=json.dumps(obj).encode('utf-8') if obj is not None else None,
                   method='POST' if obj is not None else 'GET')
    q.add_header('Authorization', 'Basic ' + base64.b64encode(os.environ['IZK_AUTH'].encode()).decode())
    q.add_header('User-Agent', 'Mozilla/5.0')
    if obj is not None: q.add_header('Content-Type', 'application/json; charset=utf-8')
    return json.load(ur.urlopen(q, timeout=120))
kaku = '--apply' in sys.argv and '--yes' in sys.argv
print(u'書き込み: ' + (u'する' if kaku else u'しない'))
assert yobu('/wp/v2/posts/%d?_fields=status' % IKI)['status'] == 'publish', u'行き先が未公開'
x = yobu('/wp/v2/posts/%d?context=edit' % MOTO)
assert x['slug'] == 'shiro-tora-gyousei-shobun-hikiage' and x['status'] == 'publish'
body = x['content']['raw']
if URL in body:
    print(u'もう案内が入っています。中止します。'); sys.exit()
n = body.count(MARK); print(u'目印:', n)
assert n == 1
new = body.replace(MARK, TSUIKI + MARK)
assert new.replace(TSUIKI + MARK, u'\x00') == body.replace(MARK, u'\x00')
if not kaku: sys.exit()
yobu('/wp/v2/posts/%d' % MOTO, {'content': new})
y = yobu('/wp/v2/posts/%d?context=edit' % MOTO)
assert y['content']['raw'] == new and y['status'] == 'publish'
print(u'足しました。状態は %s のまま。' % y['status'])
