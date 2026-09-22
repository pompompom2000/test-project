# -*- coding: utf-8 -*-
u"""
下書き6260の、図の説明文をMサイズにする。

  ・鍵は環境変数 IZK_AUTH からしか読まない。標準出力にも出さない。
  ・--apply と --yes の両方がなければ、何も書き込まない。
  ・status は draft のまま。このスクリプトから公開することはできない。
  ・こちらで入れた6枚の図だけを変える。呼びかけ欄（CTA）の画像には触らない。
  ・文字の位置（何文字目か）は使わない。まるごと一度に置き換える。
    位置を使って切り貼りすると、置き換えで長さが変わったときにずれる。
    実際にそれで本文を壊し、控え6279から戻した。
  ・書き込んだあと、読み返して確かめる。
"""
import os, sys, json, base64, re
import urllib.request as ur

KIJI  = 6260
ZUKAI = [6277, 6267, 6273, 6274, 6270, 6276]   # 00 01 02 03 04 05

kagi = os.environ.get('IZK_AUTH')
if not kagi:
    print(u'環境変数 IZK_AUTH がありません。'); sys.exit(1)
ATAMA = {'Authorization': 'Basic ' + base64.b64encode(kagi.encode()).decode()}


def yobu(p, obj=None):
    q = ur.Request('https://www.ishinazaka.co.jp/wp-json' + p,
                   data=json.dumps(obj).encode('utf-8') if obj else None,
                   method='POST' if obj else 'GET')
    for k, v in ATAMA.items():
        q.add_header(k, v)
    if obj:
        q.add_header('Content-Type', 'application/json; charset=utf-8')
    return json.load(ur.urlopen(q, timeout=90))


def main():
    yaru = ('--apply' in sys.argv) and ('--yes' in sys.argv)
    print(u'書き込み:', u'する' if yaru else u'しない（調べるだけ）')

    d = yobu('/wp/v2/posts/%d?context=edit' % KIJI)
    assert d['slug'] == 'butsuryu-taiko-2026' and d['status'] == 'draft'
    t = d['content']['raw']
    print(u'いまの本文 %d字 / 図 %d枚' % (len(t), t.count(u'<figure class="wp-block-image size-large">')))

    atarashii = t
    naoshita = 0
    for mid in ZUKAI:
        furui = (u'<!-- wp:image {"id":%d,"sizeSlug":"large","linkDestination":"none"} -->\n'
                 u'<figure class="wp-block-image size-large">') % mid
        atara = (u'<!-- wp:image {"id":%d,"sizeSlug":"large","linkDestination":"none",'
                 u'"fontSize":"medium"} -->\n'
                 u'<figure class="wp-block-image size-large has-medium-font-size">') % mid
        n = atarashii.count(furui)
        if n != 1:
            print(u'  ID %d が %d 個。中止します。' % (mid, n)); sys.exit(1)
        atarashii = atarashii.replace(furui, atara)
        naoshita += 1

    print(u'直した図:', naoshita)
    assert naoshita == 6
    assert atarashii.count(u'has-medium-font-size') == t.count(u'has-medium-font-size') + 6
    assert atarashii.count(u'<figure') == t.count(u'<figure'), u'図の数が変わっている'
    assert atarashii.count(u'<img ')  == t.count(u'<img '),  u'画像の数が変わっている'
    print(u'本文 %d字 → %d字（増えた分 %d）' % (len(t), len(atarashii), len(atarashii) - len(t)))

    if not yaru:
        print(u'--apply --yes が無いので、ここで終わります。'); return

    yobu('/wp/v2/posts/%d' % KIJI, {'content': atarashii, 'status': 'draft'})
    m = yobu('/wp/v2/posts/%d?context=edit' % KIJI)
    r = m['content']['raw']
    print(u'読み返し: %d字 / 図 %d枚 / Mの図 %d枚 / status=%s'
          % (len(r),
             r.count(u'<figure class="wp-block-image size-large'),
             r.count(u'<figure class="wp-block-image size-large has-medium-font-size">'),
             m['status']))
    assert m['status'] == 'draft'
    assert r.count(u'<figure class="wp-block-image size-large has-medium-font-size">') == 6
    assert r.count(u'<img ') == t.count(u'<img ')
    print(u'確かめました。')


if __name__ == '__main__':
    main()
