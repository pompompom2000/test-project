# -*- coding: utf-8 -*-
u"""記事（ID 6490）の認定書画像を、横向きの 6491 から縦向きの 6493 に差し替え、アイキャッチも変える。
古い 6491 は自分で登録したものなので、差し替えが確かめられたら消す。
鍵は IZK_AUTH からだけ読む。--apply と --yes の両方がなければ書き込まない。下書きでなければ中止。"""
import os, sys, re, json, base64, urllib.request as ur
SITE = 'https://www.ishinazaka.co.jp/wp-json'; PID, OLD, NEW = 6490, 6491, 6493
def yobu(p, obj=None, method=None):
    q = ur.Request(SITE + p, data=json.dumps(obj).encode('utf-8') if obj is not None else None, method=method or ('POST' if obj is not None else 'GET'))
    q.add_header('Authorization', 'Basic ' + base64.b64encode(os.environ['IZK_AUTH'].encode()).decode()); q.add_header('User-Agent', 'Mozilla/5.0')
    if obj is not None: q.add_header('Content-Type', 'application/json; charset=utf-8')
    return json.load(ur.urlopen(q, timeout=120))
kaku = '--apply' in sys.argv and '--yes' in sys.argv
x = yobu('/wp/v2/posts/%d?context=edit' % PID); assert x['status'] == 'draft', x['status']
body = x['content']['raw']
m = yobu('/wp/v2/media/%d' % NEW); url = m['media_details']['sizes'].get('large', {}).get('source_url') or m['source_url']
blk = re.findall(r'<!-- wp:image \{"id":%d,.*?<!-- /wp:image -->\n\n' % OLD, body, flags=re.S)
print(u'書き込み: ' + (u'する' if kaku else u'しない'), u'／ 古い画像の塊: %d 個 ／ 新しい画像の大きさ: %sx%s' % (len(blk), m['media_details'].get('width'), m['media_details'].get('height')))
assert len(blk) == 1
old = blk[0]
new = re.sub(r'"id":%d,' % OLD, '"id":%d,' % NEW, old); new = re.sub(r'src="[^"]+"', 'src="%s"' % url, new); new = new.replace('wp-image-%d' % OLD, 'wp-image-%d' % NEW)
assert new.count(str(NEW)) >= 2 and str(OLD) not in new
atara = body.replace(old, new); assert atara.replace(new, '\x00') == body.replace(old, '\x00')
if not kaku: sys.exit()
yobu('/wp/v2/media/%d' % NEW, {'post': PID})
yobu('/wp/v2/posts/%d' % PID, {'content': atara, 'featured_media': NEW})
y = yobu('/wp/v2/posts/%d?context=edit' % PID)
assert y['content']['raw'] == atara and y['featured_media'] == NEW and y['status'] == 'draft'
print(u'差し替えました。アイキャッチ %d、状態 %s' % (y['featured_media'], y['status']))
r = yobu('/wp/v2/media/%d?force=true' % OLD, method='DELETE'); print(u'古い画像 %d を消しました: %s' % (OLD, r.get('deleted')))
