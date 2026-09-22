# -*- coding: utf-8 -*-
u"""
第6回（量子コンピュータ・最終回）に、「次の記事へ」を足す。
行き先は、総合物流施策大綱の記事。

  ★ この記事が「公開」になってから動かすこと。
    下書きのまま足すと、読者が404にぶつかる。
    そのため、行き先が draft のときは、自分から中止する。

  ・鍵は環境変数 IZK_AUTH からしか読まない。標準出力にも出さない。
  ・--apply と --yes の両方がなければ、何も書き込まない。
  ・空の段がちょうど2つあることを数え、合わなければ中止する。
  ・第6回の本文は、この1か所しか変えない。
  ・書き込んだあと、読み返して確かめる。
"""
import os, sys, json, base64
import urllib.request as ur

MOTO  = 'https://www.ishinazaka.co.jp/wp-json'
SAIGO = 6213            # 量子コンピュータ 第6回
IKISAKI = 6260          # 総合物流施策大綱
URL = 'https://www.ishinazaka.co.jp/butsuryu-taiko-2026/'

# 第5回で使われているものと、そっくり同じ形にする
TSUGI = (u'<!-- wp:column -->\n'
         u'<div class="wp-block-column"><!-- wp:image {"lightbox":{"enabled":false},'
         u'"id":1731,"width":"100px","sizeSlug":"full","linkDestination":"custom"} -->\n'
         u'<figure class="wp-block-image size-full is-resized">'
         u'<a href="%s"><img src="https://www.ishinazaka.co.jp/common/files/uploads/2026/04/'
         u'%%E6%%AC%%A1%%E3%%81%%AE%%E8%%A8%%98%%E4%%BA%%8B%%E3%%81%%B8%%E3%%83%%9C%%E3%%82%%BF%%E3%%83%%B3'
         u'-e1776822959719.png" alt="次の記事へ" class="wp-image-1731" '
         u'style="width:100px;height:auto"/></a></figure>\n'
         u'<!-- /wp:image --></div>\n'
         u'<!-- /wp:column --></div>\n'
         u'<!-- /wp:columns -->') % URL

KARA = (u'<!-- wp:column -->\n'
        u'<div class="wp-block-column"></div>\n'
        u'<!-- /wp:column --></div>\n'
        u'<!-- /wp:columns -->')

kagi = os.environ.get('IZK_AUTH')
if not kagi:
    print(u'環境変数 IZK_AUTH がありません。'); sys.exit(1)
ATAMA = {'Authorization': 'Basic ' + base64.b64encode(kagi.encode()).decode()}


def yobu(p, obj=None):
    q = ur.Request(MOTO + p,
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

    iki = yobu('/wp/v2/posts/%d?context=edit' % IKISAKI)
    print(u'行き先: %d / %s / %s' % (iki['id'], iki['slug'], iki['status']))
    if iki['status'] != 'publish':
        print(u'★ 行き先がまだ公開されていません。中止します。')
        print(u'  下書きのまま繋ぐと、読者が404にぶつかります。')
        return

    d = yobu('/wp/v2/posts/%d?context=edit' % SAIGO)
    assert d['slug'] == 'quantum-computer-06-cryptography', d['slug']
    assert d['status'] == 'publish', d['status']
    t = d['content']['raw']
    print(u'第6回: %s / %s / 本文 %d字' % (d['slug'], d['status'], len(t)))

    if u'次の記事へ' in t:
        print(u'もう「次の記事へ」が入っています。中止します。'); return

    n = t.count(KARA)
    print(u'いちばん後ろの空の段:', n)
    assert n == 1, u'空の段が1つではない。中止します。'

    atarashii = t.replace(KARA, TSUGI)
    print(u'本文 %d字 → %d字' % (len(t), len(atarashii)))
    assert atarashii.count(u'次の記事へ') == 1
    assert atarashii.count(u'前の記事へ') == t.count(u'前の記事へ')

    if not yaru:
        print(u'--apply --yes が無いので、ここで終わります。'); return

    nochi = yobu('/wp/v2/posts/%d' % SAIGO, {'content': atarashii, 'status': 'publish'})
    assert nochi['status'] == 'publish'
    m = yobu('/wp/v2/posts/%d?context=edit' % SAIGO)
    assert u'次の記事へ' in m['content']['raw'], u'入っていない'
    assert URL in m['content']['raw'], u'行き先が入っていない'
    print(u'入れました。読み返しも確かめました。')


if __name__ == '__main__':
    main()
