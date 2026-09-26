# -*- coding: utf-8 -*-
u"""カテゴリーの説明文にある「株式会社石名坂」を「株式会社 石名坂」にする。
鍵は環境変数 IZK_AUTH からだけ読む。--apply と --yes の両方がなければ書き込まない。
直す前の値は kategori-mae.json に控える。"""
import os, sys, re, json, io, base64, urllib.request as ur
A = {'Authorization': 'Basic ' + base64.b64encode(os.environ['IZK_AUTH'].encode()).decode(),
     'User-Agent': 'Mozilla/5.0'}
SEI = u'株式会社 石名坂'
ZURE = re.compile(u'株式会社(?:　)?石名坂')
ZENBU = re.compile(u'株式会社[ 　]?石名坂')
B = 'https://www.ishinazaka.co.jp/wp-json/wp/v2/categories'
def yobu(u, obj=None):
    q = ur.Request(u, headers=A, data=json.dumps(obj).encode() if obj else None, method='POST' if obj else 'GET')
    if obj: q.add_header('Content-Type', 'application/json; charset=utf-8')
    return json.load(ur.urlopen(q, timeout=60))
kaku = '--apply' in sys.argv and '--yes' in sys.argv
cs = [c for c in yobu(B + '?per_page=100&context=edit') if ZURE.search(c['description'])]
print(u'書き込み: ' + (u'する' if kaku else u'しない（調べるだけ）'))
print(u'直すカテゴリー: %d' % len(cs))
if not kaku: sys.exit()
io.open('kategori-mae.json', 'w', encoding='utf-8').write(json.dumps(
    [{'id': c['id'], 'slug': c['slug'], 'description': c['description']} for c in cs], ensure_ascii=False, indent=1))
for c in cs:
    atara = ZURE.sub(SEI, c['description'])
    assert ZENBU.sub('\0', atara) == ZENBU.sub('\0', c['description'])   # 社名の外は同じ
    yobu(B + '/%d' % c['id'], {'description': atara})
    m = yobu(B + '/%d?context=edit' % c['id'])
    assert m['description'] == atara and m['slug'] == c['slug'], c['slug']
    print(u'  %s: 直しました（%d か所）' % (c['slug'], len(ZURE.findall(c['description']))))
