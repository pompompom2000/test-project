# -*- coding: utf-8 -*-
u"""記事の抜粋（SNSで共有したときの説明に使われる）にある「株式会社石名坂」を直す。
鍵は IZK_AUTH からだけ読む。--apply と --yes の両方がなければ書き込まない。控えは bassui-mae.json。"""
import os, sys, re, io, json, base64, urllib.request as ur
A = {'Authorization': 'Basic ' + base64.b64encode(os.environ['IZK_AUTH'].encode()).decode(), 'User-Agent': 'Mozilla/5.0'}
SEI = u'株式会社 石名坂'
ZURE = re.compile(u'株式会社(?:　)?石名坂')
ZENBU = re.compile(u'株式会社[ 　]?石名坂')
def yobu(p, obj=None):
    q = ur.Request('https://www.ishinazaka.co.jp/wp-json' + p, headers=A,
                   data=json.dumps(obj).encode() if obj else None, method='POST' if obj else 'GET')
    if obj: q.add_header('Content-Type', 'application/json; charset=utf-8')
    return json.load(ur.urlopen(q, timeout=60))
kaku = '--apply' in sys.argv and '--yes' in sys.argv
ID = 4639
x = yobu('/wp/v2/posts/%d?context=edit' % ID)
mae = x['excerpt']['raw']
atara = ZURE.sub(SEI, mae)
print(u'書き込み: ' + (u'する' if kaku else u'しない'), u'／直す箇所: %d' % len(ZURE.findall(mae)))
if not kaku or atara == mae: sys.exit()
assert ZENBU.sub('\0', atara) == ZENBU.sub('\0', mae)
io.open('bassui-mae.json', 'w', encoding='utf-8').write(json.dumps({'id': ID, 'excerpt': mae}, ensure_ascii=False))
yobu('/wp/v2/posts/%d' % ID, {'excerpt': atara})
y = yobu('/wp/v2/posts/%d?context=edit' % ID)
assert y['excerpt']['raw'] == atara and y['content']['raw'] == x['content']['raw'] and y['status'] == x['status']
print(u'直しました。本文・公開状態は変わっていません。')
