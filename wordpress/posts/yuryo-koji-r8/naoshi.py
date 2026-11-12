# -*- coding: utf-8 -*-
u"""article-mae.html（直す前）と article.html（直した後）を見比べ、変わったブロックだけを
下書き（ID 6499）に反映する。配置済みの画像には触れない。
・鍵は環境変数 IZK_AUTH からしか読まない。標準出力にも出さない
・--apply と --yes の両方がなければ、何も書き込まない
・下書き（draft）でなければ中止する。公開はしない
・直す前のブロックが本文にちょうど1回あることを確かめてから置き換え、読み返す"""
import os, sys, io, json, base64, difflib, urllib.request as ur
SITE = 'https://www.ishinazaka.co.jp/wp-json'; PID = 6499
def yobu(p, obj=None):
    q = ur.Request(SITE + p, data=json.dumps(obj).encode('utf-8') if obj is not None else None, method='POST' if obj is not None else 'GET')
    q.add_header('Authorization', 'Basic ' + base64.b64encode(os.environ['IZK_AUTH'].encode()).decode()); q.add_header('User-Agent', 'Mozilla/5.0')
    if obj is not None: q.add_header('Content-Type', 'application/json; charset=utf-8')
    return json.load(ur.urlopen(q, timeout=120))
here = os.path.dirname(os.path.abspath(__file__))
mae = io.open(os.path.join(here, 'article-mae.html'), encoding='utf-8').read().split(u'\n\n')
ato = io.open(os.path.join(here, 'article.html'), encoding='utf-8').read().split(u'\n\n')
kaku = '--apply' in sys.argv and '--yes' in sys.argv
x = yobu('/wp/v2/posts/%d?context=edit' % PID)
if x['status'] != 'draft': print(u'下書きではありません。中止します。'); sys.exit(1)
body = x['content']['raw']; new = body
print(u'書き込み: ' + (u'する' if kaku else u'しない（確かめるだけ）'))
for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, mae, ato, autojunk=False).get_opcodes():
    if tag == 'equal': continue
    old = u'\n\n'.join(mae[i1:i2]); nu = u'\n\n'.join(ato[j1:j2])
    if tag == 'insert':
        anchor = mae[i1]; assert new.count(anchor) == 1, u'差し込み先が1つでない'
        new = new.replace(anchor, nu + u'\n\n' + anchor); print(u'差し込み:', nu[:40].replace('\n', ' ')); continue
    n = new.count(old)
    if n != 1: print(u'直す前のブロックが %d 回あります（1回のはず）。中止します。' % n); print(old[:120]); sys.exit(1)
    new = new.replace(old, nu); print(u'%s: %s…' % (tag, old[:40].replace('\n', ' ')))
print(u'本文 %d字 → %d字' % (len(body), len(new)))
if not kaku: sys.exit()
yobu('/wp/v2/posts/%d' % PID, {'content': new})
y = yobu('/wp/v2/posts/%d?context=edit' % PID)
assert y['content']['raw'] == new and y['status'] == 'draft'
print(u'反映しました。状態は %s のまま。' % y['status'])
