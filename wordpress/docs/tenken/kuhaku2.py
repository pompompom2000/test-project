# -*- coding: utf-8 -*-
u"""
空白の直しの、取りこぼし4件。1件ずつ手で決めた。

  なぜ機械の規則にしないか
    全角スペース（　）には、意図して置かれたものがある。
      コンクリート用砕石及び砕砂　JIS　A5005   ← 区切り。残す
      盛岡市　永年除雪受注者感謝状　受贈        ← 区切り。残す
    機械で詰めると「砕砂JISA5005」になってしまう。
    だから、語を挟む仕掛けだと分かる4件だけを名指しで直す。

  ・鍵は環境変数 IZK_AUTH からしか読まない。標準出力にも出さない。
  ・--apply と --yes の両方がなければ、何も書き込まない。
  ・いまの値が、想定どおりであることを確かめてから書き込む。
  ・綴り（URL）と公開状態は変えない。書き込んだあと読み返す。
"""
import os, sys, json, base64
import urllib.request as ur

NAOSU = [
    # (綴り, どこ, いまの値, 直した値)
    ('post-1080', 'seo_title',
     u'【基礎知識】　黒土　(黒ぼく土·火山灰土壌)の特徴と農業での上手な使い方',
     u'【基礎知識】黒土（黒ぼく土・火山灰土壌）の特徴と農業での上手な使い方'),
    ('post-4342', 'post_title',
     u'ICT施工の時代だからこそ、「基本」を伝えたい― 技術承継への私たちの想い',
     u'ICT施工の時代だからこそ、「基本」を伝えたい―技術承継への私たちの想い'),
    ('post-284', 'seo_desc_sub',
     u'基盤整備工事の　VR動画　（第1弾）',
     u'基盤整備工事のVR動画（第1弾）'),
    ('post-803', 'seo_desc_sub',
     u'において、　汚水管建設工事　（下水工事）',
     u'において、汚水管建設工事（下水工事）'),
]

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

    ima = {d['slug']: d for d in json.load(open('/tmp/claude-0/site/seo-ima.json'))}

    for slug, doko, furui, atara in NAOSU:
        r = ima[slug]
        c = yobu('/aioseo/v1/post?postId=%d' % r['id'])['data']['currentPost']
        w = yobu('/wp/v2/%s/%d?context=edit' % (r['type'], r['id']))
        seo_t = c.get('title') or ''
        seo_d = c.get('description') or ''
        post_t = w['title']['raw']

        print(u'\n■ %s' % slug)
        if doko == 'seo_title':
            assert seo_t == furui, u'いまの値が想定と違う: %r' % seo_t
            atarashii_t, atarashii_d, atarashii_p = atara, seo_d, post_t
        elif doko == 'post_title':
            assert post_t == furui, u'いまの値が想定と違う: %r' % post_t
            atarashii_t, atarashii_d, atarashii_p = seo_t, seo_d, atara
        else:                                   # 説明文の一部だけ入れ替える
            assert seo_d.count(furui) == 1, u'目印が1つではない'
            atarashii_t, atarashii_d, atarashii_p = seo_t, seo_d.replace(furui, atara), post_t
        print(u'  前 %s' % (furui[:58]))
        print(u'  後 %s' % (atara[:58]))

        if not yaru:
            continue

        if atarashii_p != post_t:
            n = yobu('/wp/v2/%s/%d' % (r['type'], r['id']), {'title': atarashii_p})
            assert n['slug'] == r['slug'] and n['status'] == 'publish'
        if atarashii_t != seo_t or atarashii_d != seo_d:
            okuri = {'id': r['id'], 'title': atarashii_t, 'description': atarashii_d}
            if c.get('keyphrases'):
                okuri['keyphrases'] = c['keyphrases']
            yobu('/aioseo/v1/post', okuri)

        c2 = yobu('/aioseo/v1/post?postId=%d' % r['id'])['data']['currentPost']
        w2 = yobu('/wp/v2/%s/%d?context=edit' % (r['type'], r['id']))
        assert (c2.get('title') or '') == atarashii_t
        assert (c2.get('description') or '') == atarashii_d
        assert w2['title']['raw'] == atarashii_p
        assert w2['slug'] == r['slug'] and w2['status'] == 'publish'
        print(u'  入れました（読み返し一致）')

    if not yaru:
        print(u'\n--apply --yes が無いので、ここで終わります。')


if __name__ == '__main__':
    main()
