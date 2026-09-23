# -*- coding: utf-8 -*-
u"""
消えていた出典リンクを差し替える（確かめの取れた4件）。

  ・鍵は環境変数 IZK_AUTH からしか読まない。標準出力にも出さない。
  ・--apply と --yes の両方がなければ、何も書き込まない。
  ・文字の位置（何文字目か）は使わない。まるごと置き換える。
  ・置き換える文字列がちょうど1回であることを数え、合わなければ中止する。
  ・その文字列の外が1文字も変わっていないことを確かめてから書き込む。
  ・綴り（URL）と公開状態は変えない。書き込んだあと読み返す。

  差し替え先は、すべて自分で取得して200と中身を確かめてある。
"""
import os, sys, json, base64
import urllib.request as ur

NAOSU = [
 # 奥州市のサイト改装で移動。新しい場所を確認済み（絵物語 (8)陸軍検疫所）
 ('goto-shinpei-02-taiwan',
  u'<a href="http://www.city.oshu.iwate.jp/shinpei/story/10.html" target="_blank" '
  u'rel="noopener">後藤新平記念館「後藤新平 絵物語 陸軍検疫所」</a>',
  u'<a href="https://www.city.oshu.iwate.jp/shinpei/shogai/1/939.html" target="_blank" '
  u'rel="noopener">奥州市「後藤新平 絵物語（8）陸軍検疫所」</a>'),

 # 岩手県のサイト改装で /nyuusatsu/sekkei/ の区画ごと消えた。
 # 記事が裏づけているのは「復興係数」。その記述のあるページへ。
 ('higashinihon-daishinsai-03-infra',
  u'<a href="https://www.pref.iwate.jp/kendozukuri/kensetsu/nyuusatsu/sekkei/1017258/index.html" '
  u'target="_blank" rel="noopener">岩手県「東日本大震災特例等」</a>',
  u'<a href="https://www.pref.iwate.jp/kendozukuri/kensetsu/1095164/1010932.html" '
  u'target="_blank" rel="noopener">岩手県「東日本大震災の復旧・復興事業等における'
  u'間接工事費の補正」（復興係数）</a>'),

 # インターリスク総研タイのブログが消えた。
 # 記事が裏づけているのは「浸水した工業団地と日系企業の数」。内閣府の図へ。
 ('kikouhendou-2050-keizai',
  u'<a href="https://www.interriskthai.co.th/ja/blog/2011年タイ大洪水を振り返ってその1/" '
  u'target="_blank" rel="noopener">2011年タイ大洪水を振り返って（MS＆ADインターリスク総研タイ）</a>',
  u'<a href="https://www5.cao.go.jp/j-j/cr/cr12/img/chr12010108z.html" target="_blank" '
  u'rel="noopener">内閣府「地域の経済2012」第1-1-8図 タイ洪水により浸水した'
  u'工業団地及び日系企業数、主要企業</a>'),

 # 催しのページが消えた。催し自体が終わっているため、ダム管理事務所へ。
 ('post-4202',
  u'<a href="https://www.pref.iwate.jp/morioka/tsunatori/1099596.html" title="">コチラ</a>',
  u'<a href="https://www.pref.iwate.jp/morioka/tsunatori/index.html" target="_blank" '
  u'rel="noopener">綱取ダム管理事務所のページ</a>'),
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
    return json.load(ur.urlopen(q, timeout=120))


def main():
    yaru = ('--apply' in sys.argv) and ('--yes' in sys.argv)
    print(u'書き込み:', u'する' if yaru else u'しない（調べるだけ）')

    for slug, furui, atara in NAOSU:
        d = yobu('/wp/v2/posts?slug=%s&context=edit' % slug)[0]
        t = d['content']['raw']
        n = t.count(furui)
        print(u'\n■ %s（ID %d）／ 目印 %d 回' % (slug, d['id'], n))
        if n == 0 and atara in t:
            print(u'  もう直っています。'); continue
        assert n == 1, u'目印が1つではない。中止します。'

        atarashii = t.replace(furui, atara)
        assert t.replace(furui, u'\x00') == atarashii.replace(atara, u'\x00'), u'外が変わっている'
        print(u'  前 %s' % furui[:120])
        print(u'  後 %s' % atara[:120])
        print(u'  本文 %d字 → %d字（この1か所だけ）' % (len(t), len(atarashii)))

        if not yaru:
            continue

        yobu('/wp/v2/posts/%d' % d['id'], {'content': atarashii, 'status': 'publish'})
        m = yobu('/wp/v2/posts/%d?context=edit' % d['id'])
        assert m['content']['raw'] == atarashii, u'書き込んだものと違う'
        assert m['slug'] == slug and m['status'] == 'publish'
        print(u'  入れました（読み返し一致）')

    if not yaru:
        print(u'\n--apply --yes が無いので、ここで終わります。')


if __name__ == '__main__':
    main()
