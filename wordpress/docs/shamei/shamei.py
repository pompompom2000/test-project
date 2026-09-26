# -*- coding: utf-8 -*-
u"""
会社名の表記を、正式な「株式会社 石名坂」（半角空白1つ）に揃える。

  直す形   株式会社石名坂（空白なし）／株式会社　石名坂（全角空白）
  直す場所 記事と固定ページの、題名・本文、All in One SEO の題名・説明文
           （公開中のものだけ。非公開の「基本パーツサンプル」には触らない）

  ・鍵は環境変数 IZK_AUTH からしか読まない。標準出力にも出さない。
  ・--apply と --yes の両方がなければ、何も書き込まない。
  ・書き込む前に、いまの値を shamei-mae.json に全部控える（元に戻せる）。
  ・会社名以外が1文字も変わっていないことを、会社名を同じ印に置き換えた
    文字列どうしの一致で確かめてから書き込む。
  ・綴り（URL）と公開状態は変えない。1ページごとに読み返して確かめる。
  ・AIOSEOの窓口は送らなかった項目を消すので、題名・説明文・焦点語をまとめて送る。
"""
import os, sys, io, json, re, time, base64
import urllib.request as ur

SEI = u'株式会社 石名坂'
ZURE = re.compile(u'株式会社(?:　)?石名坂')          # 空白なし・全角空白（正式形は含まない）
ZENBU = re.compile(u'株式会社[ 　]?石名坂')         # 突き合わせ用（正式形も含む）

kagi = os.environ.get('IZK_AUTH')
if not kagi:
    print(u'環境変数 IZK_AUTH がありません。'); sys.exit(1)
ATAMA = {'Authorization': 'Basic ' + base64.b64encode(kagi.encode()).decode()}


def yobu(p, obj=None):
    u"""サーバーが混んでいる（429/502/503/504）ときは、間を空けて最大5回まで取り直す。"""
    import urllib.error as ue
    for kai in range(6):
        q = ur.Request('https://www.ishinazaka.co.jp/wp-json' + p,
                       data=json.dumps(obj).encode('utf-8') if obj else None,
                       method='POST' if obj else 'GET')
        for k, v in ATAMA.items():
            q.add_header(k, v)
        if obj:
            q.add_header('Content-Type', 'application/json; charset=utf-8')
        try:
            time.sleep(0.3)                      # サーバーに負担をかけない
            return json.load(ur.urlopen(q, timeout=120))
        except ue.HTTPError as e:
            if e.code in (429, 502, 503, 504) and kai < 5:
                matsu = 5 * (2 ** kai)
                print(u'    （サーバーが混んでいる %d。%d秒待ちます）' % (e.code, matsu))
                time.sleep(matsu)
                continue
            raise


def naosu(s):
    return ZURE.sub(SEI, s) if s else s


def onaji_igai(a, b):
    u"""会社名以外が同じか"""
    return ZENBU.sub(u'\x00', a or '') == ZENBU.sub(u'\x00', b or '')


def main():
    yaru = ('--apply' in sys.argv) and ('--yes' in sys.argv)
    print(u'書き込み:', u'する' if yaru else u'しない（調べるだけ）')

    # --- いまの値を集めて控える ---
    ichiran = []
    for shurui in ('posts', 'pages'):
        pg = 1
        while True:
            d = yobu('/wp/v2/%s?per_page=50&page=%d&status=publish&context=edit' % (shurui, pg))
            for x in d:
                time.sleep(0.05)
                c = yobu('/aioseo/v1/post?postId=%d' % x['id'])['data']['currentPost']
                ichiran.append({'type': shurui, 'id': x['id'], 'slug': x['slug'],
                                'post_title': x['title']['raw'], 'content': x['content']['raw'],
                                'seo_title': c.get('title') or '', 'seo_desc': c.get('description') or '',
                                'keyphrases': c.get('keyphrases')})
            if len(d) < 50: break
            pg += 1
    if yaru:
        io.open('shamei-mae.json', 'w', encoding='utf-8').write(
            json.dumps(ichiran, ensure_ascii=False))
        print(u'直す前の値を控えました: %d ページ（shamei-mae.json）' % len(ichiran))

    shigoto = []
    for r in ichiran:
        a = {k: naosu(r[k]) for k in ('post_title', 'content', 'seo_title', 'seo_desc')}
        kawaru = [k for k in a if a[k] != r[k]]
        if kawaru:
            shigoto.append((r, a, kawaru))
    kazu = {k: sum(len(ZURE.findall(r[k])) for r, a, kw in shigoto) for k in
            ('post_title', 'content', 'seo_title', 'seo_desc')}
    print(u'対象ページ: %d（全 %d 中）' % (len(shigoto), len(ichiran)))
    for k, na in (('post_title', u'記事の題名'), ('seo_title', u'検索向けの題名'),
                  ('seo_desc', u'検索向けの説明文'), ('content', u'本文')):
        print(u'  %-10s %d か所' % (na, kazu[k]))

    if not yaru:
        print(u'--apply --yes が無いので、ここで終わります。'); return

    ok = ng = 0
    for i, (r, a, kawaru) in enumerate(shigoto, 1):
        time.sleep(0.12)
        try:
            for k in kawaru:
                assert onaji_igai(r[k], a[k]), u'会社名以外が変わっている: ' + k
            okuri = {}
            if 'post_title' in kawaru: okuri['title'] = a['post_title']
            if 'content' in kawaru: okuri['content'] = a['content']
            if okuri:
                n = yobu('/wp/v2/%s/%d' % (r['type'], r['id']), okuri)
                assert n['slug'] == r['slug'] and n['status'] == 'publish'
            if 'seo_title' in kawaru or 'seo_desc' in kawaru:
                o = {'id': r['id'], 'title': a['seo_title'], 'description': a['seo_desc']}
                if r['keyphrases']: o['keyphrases'] = r['keyphrases']
                yobu('/aioseo/v1/post', o)
            # 読み返し
            w = yobu('/wp/v2/%s/%d?context=edit' % (r['type'], r['id']))
            c = yobu('/aioseo/v1/post?postId=%d' % r['id'])['data']['currentPost']
            assert w['title']['raw'] == a['post_title'], u'記事の題名が違う'
            assert w['content']['raw'] == a['content'], u'本文が違う'
            assert (c.get('title') or '') == a['seo_title'], u'検索向けの題名が違う'
            assert (c.get('description') or '') == a['seo_desc'], u'検索向けの説明文が違う'
            assert w['slug'] == r['slug'] and w['status'] == 'publish'
            ok += 1
        except Exception as e:
            ng += 1
            print(u'  × %s -> %s %s' % (r['slug'], type(e).__name__, str(e)[:100]))
        if i % 20 == 0:
            print(u'  %d / %d（成功 %d 失敗 %d）' % (i, len(shigoto), ok, ng))
    print(u'\n終わりました。成功 %d ／ 失敗 %d' % (ok, ng))


if __name__ == '__main__':
    main()
