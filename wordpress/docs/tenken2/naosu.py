# -*- coding: utf-8 -*-
u"""
2回目の点検で見つかったものを直す。

  1) ai-agent の表示名を「株式会社石名坂」に（その7本の著者名が直る）
     ほかの2アカウント（管理用石名坂・echnaadmin）は、この鍵では編集できない（403）。
     回り道はしない。管理画面で直していただく。
  2) 取りこぼし2件（全角スペース1つずつ）
  3) 「農業肥料エネルギー」を、もとの「 農業 肥料 エネルギー 」に戻す
     （お預けの6件と同じ扱いにする、とのご判断）

  ・鍵は環境変数 IZK_AUTH からしか読まない。標準出力にも出さない。
  ・--apply と --yes の両方がなければ、何も書き込まない。
  ・位置は使わない。目印がちょうど1回であることを数えてから置き換える。
  ・AIOSEOの窓口は送らなかった項目を消すので、題名・説明文・焦点語をまとめて送る。
  ・綴り・公開状態・本文は変えない。書き込んだあと読み返す。
"""
import os, sys, json, base64
import urllib.request as ur

NAOSU = [
 # (綴り, どこ, 目印, 置き換え後)
 ('nougyou-energy-hiryou', 'post_title', u'「農業肥料エネルギー」', u'「 農業 肥料 エネルギー 」'),
 ('nougyou-energy-hiryou', 'seo_desc',   u'「農業肥料エネルギー」', u'「 農業 肥料 エネルギー 」'),
 ('post-1080',             'seo_desc',   u'黒土　＝火山灰土壌',  u'黒土＝火山灰土壌'),
 ('post-4342',             'seo_title',  u'技術承継　「基本」',  u'技術承継「基本」'),
]
HYOUJI = u'株式会社石名坂'

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

    # --- 1) 表示名 ---
    me = yobu('/wp/v2/users/me?context=edit')
    print(u'\n■ 自分の表示名: %s → %s' % (me['name'], HYOUJI))
    if yaru and me['name'] != HYOUJI:
        n = yobu('/wp/v2/users/me', {'name': HYOUJI, 'nickname': HYOUJI})
        m = yobu('/wp/v2/users/me?context=edit')
        assert m['name'] == HYOUJI, u'表示名が変わっていない'
        print(u'  変えました（読み返し一致）')

    # --- 2) 3) 題名・説明文 ---
    kiji = {}
    for slug, doko, mae, ato in NAOSU:
        if slug not in kiji:
            d = yobu('/wp/v2/posts?slug=%s&context=edit' % slug)[0]
            c = yobu('/aioseo/v1/post?postId=%d' % d['id'])['data']['currentPost']
            kiji[slug] = {'id': d['id'], 'honbun': d['content']['raw'],
                          'post_title': d['title']['raw'],
                          'seo_title': c.get('title') or '', 'seo_desc': c.get('description') or '',
                          'keyphrases': c.get('keyphrases'), 'kawatta': set()}
        k = kiji[slug]
        n = k[doko].count(mae)
        print(u'\n■ %s ／ %s ／ 目印 %d 回' % (slug, doko, n))
        assert n == 1, u'目印が1回ではない。中止します。'
        k[doko] = k[doko].replace(mae, ato)
        k['kawatta'].add(doko)
        print(u'  %r → %r' % (mae, ato))

    if not yaru:
        print(u'\n--apply --yes が無いので、ここで終わります。'); return

    for slug, k in kiji.items():
        if 'post_title' in k['kawatta']:
            n = yobu('/wp/v2/posts/%d' % k['id'], {'title': k['post_title']})
            assert n['slug'] == slug and n['status'] == 'publish'
        if k['kawatta'] & {'seo_title', 'seo_desc'}:
            okuri = {'id': k['id'], 'title': k['seo_title'], 'description': k['seo_desc']}
            if k['keyphrases']:
                okuri['keyphrases'] = k['keyphrases']
            yobu('/aioseo/v1/post', okuri)
        d2 = yobu('/wp/v2/posts/%d?context=edit' % k['id'])
        c2 = yobu('/aioseo/v1/post?postId=%d' % k['id'])['data']['currentPost']
        assert d2['title']['raw'] == k['post_title']
        assert (c2.get('title') or '') == k['seo_title']
        assert (c2.get('description') or '') == k['seo_desc']
        assert d2['content']['raw'] == k['honbun'], u'本文が変わった'
        assert d2['slug'] == slug and d2['status'] == 'publish'
        print(u'  %s 入れました（読み返し一致。本文は変わっていません）' % slug)


if __name__ == '__main__':
    main()
