# -*- coding: utf-8 -*-
u"""
下書き 6260 に、図を6枚入れて、公開の手前までそろえる。

  ・鍵は環境変数 IZK_AUTH からしか読まない。標準出力にも出さない。
  ・--apply と --yes の両方がなければ、何も書き込まない。
  ・status は draft のまま。このスクリプトから公開することはできない。
  ・置き換える文字列が「ちょうど何回あるか」を数え、合わないときは中止する。
  ・書き込んだあと、必ず読み返して確かめる。

  引数なしで動かすと、調べるだけで終わる。
"""
import os, sys, io, json, base64, mimetypes
import urllib.request as ur
import urllib.error as ue

MOTO   = 'https://www.ishinazaka.co.jp/wp-json'
KIJI   = 6260                      # 総合物流施策大綱の下書き
SAIGO  = 6213                      # 量子コンピュータ 第6回（最終回）
KIJI_URL = 'https://www.ishinazaka.co.jp/butsuryu-taiko-2026/'

SEO_TITLE = u'総合物流施策大綱とは？国が決めた物流の5年計画を、やさしく解説'
SEO_SETSU = (u'2026年3月31日に閣議決定された「総合物流施策大綱（2026年度〜2030年度）」を、'
             u'高校生にも分かるように解説します。2030年度に約34%不足するはずだった輸送力、'
             u'そのうち14%を克服した現在地、賃金と労働時間を全産業平均まで引き上げる目標まで。')

kagi = os.environ.get('IZK_AUTH')
if not kagi:
    print(u'環境変数 IZK_AUTH がありません。'); sys.exit(1)
ATAMA = {'Authorization': 'Basic ' + base64.b64encode(kagi.encode()).decode()}


def yobu(path, data=None, method=None, nakami=None, namae=None):
    req = ur.Request(MOTO + path, data=data, method=method)
    for k, v in ATAMA.items():
        req.add_header(k, v)
    if nakami is not None:
        req.add_header('Content-Type', 'application/json; charset=utf-8')
    if namae is not None:
        req.add_header('Content-Disposition', 'attachment; filename="%s"' % namae)
        req.add_header('Content-Type', mimetypes.guess_type(namae)[0] or 'application/octet-stream')
    try:
        with ur.urlopen(req, timeout=120) as r:
            return json.load(r)
    except ue.HTTPError as e:
        print(u'  失敗 %s %s -> %s' % (method or 'GET', path, e.code))
        print(u'  ' + e.read().decode('utf-8', 'replace')[:400])
        raise


def okuru(path, obj, method='POST'):
    return yobu(path, data=json.dumps(obj).encode('utf-8'), method=method, nakami=True)


def media_sagasu(url):
    u"""公開URLから、メディアのIDを引く。見つからなければ None。"""
    namae = url.split('/')[-1].rsplit('.', 1)[0]
    m = yobu('/wp/v2/media?per_page=40&search=' + namae)
    for x in m:
        if x['source_url'] == url:
            return x['id']
    return None


def zukai_block(mid, url, alt, soe):
    return (u'<!-- wp:image {"id":%d,"sizeSlug":"large","linkDestination":"none"} -->\n'
            u'<figure class="wp-block-image size-large">'
            u'<img src="%s" alt="%s" class="wp-image-%d"/>'
            u'<figcaption class="wp-element-caption">%s</figcaption></figure>\n'
            u'<!-- /wp:image -->') % (mid, url, alt, mid, soe)


def main():
    yaru = ('--apply' in sys.argv) and ('--yes' in sys.argv)
    print(u'書き込み:', u'する' if yaru else u'しない（調べるだけ）')
    print()

    G = json.load(io.open('gazou.json', encoding='utf-8'))

    # --- 1. いまの下書きを読む -------------------------------------------
    kiji = yobu('/wp/v2/posts/%d?context=edit' % KIJI)
    assert kiji['slug'] == 'butsuryu-taiko-2026', kiji['slug']
    assert kiji['status'] == 'draft', kiji['status']
    honbun = kiji['content']['raw']
    print(u'下書き %d / %s / %s / 本文 %d字' % (KIJI, kiji['slug'], kiji['status'], len(honbun)))
    print(u'題名:', kiji['title']['raw'])
    print(u'いまのアイキャッチ:', kiji.get('featured_media'))
    print()

    # --- 2. 画像のIDを引く -----------------------------------------------
    print(u'== 画像 ==')
    for k in sorted(G):
        g = G[k]
        if g['url'] is None:
            print(u'%s  まだ上げていない（%s）' % (k, g['moto']))
            continue
        g['id'] = media_sagasu(g['url'])
        print(u'%s  ID=%s  %s' % (k, g['id'], g['url'].split('/')[-1]))
    print()

    # --- 3. 00 を上げる ---------------------------------------------------
    g00 = G['00']
    if g00['url'] is None:
        michi = os.path.join('..', '..', 'images', 'butsuryu', g00['moto'])
        okisa = os.path.getsize(michi)
        print(u'00 を上げます: %s（%d バイト）' % (g00['moto'], okisa))
        if yaru:
            with io.open(michi, 'rb') as f:
                tama = yobu('/wp/v2/media', data=f.read(), method='POST', namae=g00['moto'])
            g00['id'], g00['url'] = tama['id'], tama['source_url']
            print(u'  上げました ID=%d %s' % (g00['id'], g00['url']))
        else:
            print(u'  （書き込みはしません）')
    print()

    # --- 4. 代替テキストを入れる -----------------------------------------
    print(u'== 代替テキスト ==')
    for k in sorted(G):
        g = G[k]
        if not g.get('id'):
            print(u'%s  IDが無いので飛ばす' % k); continue
        ima = yobu('/wp/v2/media/%d?context=edit' % g['id'])
        print(u'%s  いま「%s」' % (k, (ima.get('alt_text') or u'（空）')[:40]))
        if ima.get('alt_text') == g['alt']:
            print(u'    もう同じです'); continue
        print(u'    入れる「%s…」' % g['alt'][:40])
        if yaru:
            nochi = okuru('/wp/v2/media/%d' % g['id'], {'alt_text': g['alt']})
            assert nochi['alt_text'] == g['alt'], u'代替テキストが入っていない'
            print(u'    入れました')
    print()

    # --- 5. 本文を組み替える ---------------------------------------------
    print(u'== 本文 ==')
    atarashii = honbun

    # 5-1. SVGの図3枚を、画像に差し替える
    import re
    svgs = list(re.finditer(r'<!-- wp:html -->\n<figure[^>]*>\n<svg.*?</figure>\n<!-- /wp:html -->',
                            atarashii, re.S))
    if not svgs:
        svgs = list(re.finditer(r'<!-- wp:html -->.*?<svg.*?<!-- /wp:html -->', atarashii, re.S))
    print(u'見つかったSVGの図:', len(svgs))
    assert len(svgs) == 3, u'SVGが3つではない。中止します。'

    for no, k in ((2, '03'), (1, '02'), (0, '01')):      # 後ろから差し替える
        g = G[k]
        if not g.get('id'):
            print(u'%s のIDが無いので、差し替えません' % k); continue
        m = svgs[no]
        atarashii = atarashii[:m.start()] + zukai_block(g['id'], g['url'], g['alt'], g['soe']) + atarashii[m.end():]
        svgs = list(re.finditer(r'<!-- wp:html -->.*?<svg.*?<!-- /wp:html -->', atarashii, re.S))
        print(u'%s に差し替えました' % k)

    # 5-2. 04 を、目標の表のすぐ下に入れる
    shirushi = u'<!-- /wp:table -->'
    assert atarashii.count(shirushi) == 1, u'表が1つではない'
    if G['04'].get('id'):
        g = G['04']
        atarashii = atarashii.replace(
            shirushi, shirushi + u'\n\n' + zukai_block(g['id'], g['url'], g['alt'], g['soe']))
        print(u'04 を表の下に入れました')

    # 5-3. 05 を、高校生の章の見出しのすぐ下に入れる
    midashi = (u'<h3 class="wp-block-heading has-medium-font-size">'
               u'高校生のあなたに、関係があること</h3>\n<!-- /wp:heading -->')
    assert atarashii.count(midashi) == 1, u'高校生の見出しが1つではない'
    if G['05'].get('id'):
        g = G['05']
        atarashii = atarashii.replace(
            midashi, midashi + u'\n\n' + zukai_block(g['id'], g['url'], g['alt'], g['soe']))
        print(u'05 を高校生の章に入れました')

    # 5-4. 00 を、いちばん上の導入のすぐ下に入れる
    if G['00'].get('id'):
        g = G['00']
        shirushi2 = u'<!-- wp:image'
        ichi = atarashii.index(shirushi2)                # 最初の図（01）の直前
        atarashii = atarashii[:ichi] + zukai_block(g['id'], g['url'], g['alt'], g['soe']) + u'\n\n' + atarashii[ichi:]
        print(u'00 を導入の下に入れました')

    print(u'本文 %d字 → %d字' % (len(honbun), len(atarashii)))
    print(u'画像ブロックの数:', atarashii.count(u'<!-- wp:image'))
    print(u'残ったSVG:', atarashii.count(u'<svg'))
    print()

    io.open('honbun-haichi-zumi.html', 'w', encoding='utf-8').write(atarashii)
    print(u'組み上げた本文を honbun-haichi-zumi.html に書きました')
    print()

    if not yaru:
        print(u'--apply --yes が無いので、ここで終わります。')
        return

    # --- 6. 書き込む ------------------------------------------------------
    okuri = {'content': atarashii, 'status': 'draft'}
    if G['01'].get('id'):
        okuri['featured_media'] = G['01']['id']          # 一覧で読めるのは01
    nochi = okuru('/wp/v2/posts/%d' % KIJI, okuri)
    assert nochi['status'] == 'draft', u'下書きのままではない'
    print(u'書き込みました。status=%s featured_media=%s' % (nochi['status'], nochi.get('featured_media')))

    # 読み返して確かめる
    tashikame = yobu('/wp/v2/posts/%d?context=edit' % KIJI)
    assert tashikame['content']['raw'].count(u'<!-- wp:image') == atarashii.count(u'<!-- wp:image')
    assert u'<svg' not in tashikame['content']['raw'], u'SVGが残っている'
    print(u'読み返し：画像%d枚、SVGなし、status=%s'
          % (tashikame['content']['raw'].count(u'<!-- wp:image'), tashikame['status']))

    # --- 7. SEO ------------------------------------------------------------
    try:
        seo = okuru('/aioseo/v1/post', {'id': KIJI, 'title': SEO_TITLE, 'description': SEO_SETSU})
        print(u'SEOを入れました')
    except Exception:
        print(u'SEOは入りませんでした。画面から入れてください。')


if __name__ == '__main__':
    main()
