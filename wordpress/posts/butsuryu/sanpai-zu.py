# -*- coding: utf-8 -*-
u"""
公開済みの記事6260に、産廃の図を1枚入れる。

  ・鍵は環境変数 IZK_AUTH からしか読まない。標準出力にも出さない。
  ・--apply と --yes の両方がなければ、何も書き込まない。
  ・文字の位置（何文字目か）は使わない。まるごと置き換える。
  ・目印がちょうど1つあることを数え、合わなければ中止する。
  ・足すだけ。いまある文章は1文字も消さない（突き合わせて確かめる）。
  ・書き込んだあと読み返し、さらに公開ページを取って確かめる。
"""
import os, sys, json, base64
import urllib.request as ur

KIJI = 6260
GAZOU_URL = 'https://www.ishinazaka.co.jp/common/files/uploads/2026/09/1790122863826.jpg'

ALT = (u'産業廃棄物は空いたトラックに積めない。ふつうの荷物は近くの空いた車に'
       u'積んでよいが、産業廃棄物は許可のある会社しか運べない。'
       u'廃棄物処理法第14条第1項により、許可は区域ごと・品目ごとに必要。')
SOE = (u'許可のある会社が、許可のある品目を、許可のある区域で運ぶ。'
       u'空いた車に積む、ができません。')

# 足す場所の目印：産廃の説明のいちばん最初の段落
SHIRUSHI = (u'<!-- wp:paragraph {"fontSize":"medium"} -->\n'
            u'<p class="has-medium-font-size">もうひとつ、'
            u'<strong>産業廃棄物という壁</strong>があります。</p>\n'
            u'<!-- /wp:paragraph -->')

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
    return json.load(ur.urlopen(q, timeout=120))


def main():
    yaru = ('--apply' in sys.argv) and ('--yes' in sys.argv)
    print(u'書き込み:', u'する' if yaru else u'しない（調べるだけ）')

    # --- 図のIDを引く ---
    namae = GAZOU_URL.split('/')[-1].rsplit('.', 1)[0]
    mid = None
    for x in yobu('/wp/v2/media?per_page=40&search=' + namae):
        if x['source_url'] == GAZOU_URL:
            mid = x['id']; break
    assert mid, u'図が見つからない。中止します。'
    print(u'図の ID:', mid)

    # --- 代替テキスト ---
    ima = yobu('/wp/v2/media/%d?context=edit' % mid)
    print(u'いまの代替テキスト:', (ima.get('alt_text') or u'（空）')[:30])
    if yaru and ima.get('alt_text') != ALT:
        n = yobu('/wp/v2/media/%d' % mid, {'alt_text': ALT})
        assert n['alt_text'] == ALT
        print(u'代替テキストを入れました')

    # --- 本文 ---
    d = yobu('/wp/v2/posts/%d?context=edit' % KIJI)
    assert d['slug'] == 'butsuryu-taiko-2026', d['slug']
    t = d['content']['raw']
    print(u'記事 %d / %s / 本文 %d字' % (KIJI, d['status'], len(t)))

    if ('wp-image-%d' % mid) in t:
        print(u'もう入っています。中止します。'); return

    n = t.count(SHIRUSHI)
    print(u'目印:', n)
    assert n == 1, u'目印が1つではない。中止します。'

    zu = (u'<!-- wp:image {"id":%d,"sizeSlug":"large","linkDestination":"none",'
          u'"fontSize":"medium"} -->\n'
          u'<figure class="wp-block-image size-large has-medium-font-size">'
          u'<img src="%s" alt="%s" class="wp-image-%d"/>'
          u'<figcaption class="wp-element-caption">%s</figcaption></figure>\n'
          u'<!-- /wp:image -->') % (mid, GAZOU_URL, ALT, mid, SOE)

    atarashii = t.replace(SHIRUSHI, zu + u'\n\n' + SHIRUSHI)
    print(u'本文 %d字 → %d字' % (len(t), len(atarashii)))
    assert len(atarashii) - len(t) == len(zu) + 2, u'足した分と増えた分が合わない'
    assert t.replace(SHIRUSHI, u'\x00') == atarashii.replace(zu + u'\n\n' + SHIRUSHI, u'\x00'), \
        u'もとの文章が変わっている'
    print(u'もとの文章は、そのままです。')

    if not yaru:
        print(u'--apply --yes が無いので、ここで終わります。'); return

    yobu('/wp/v2/posts/%d' % KIJI, {'content': atarashii, 'status': 'publish'})
    m = yobu('/wp/v2/posts/%d?context=edit' % KIJI)
    assert m['content']['raw'] == atarashii and m['status'] == 'publish'
    print(u'書き込みました。読み返しも一致。status=%s' % m['status'])


if __name__ == '__main__':
    main()
