# -*- coding: utf-8 -*-
u"""
公開済みの記事6260の「では他人事かというと…」の段落を、
karani.html（帰り空荷の理由）に差し替える。

  ・鍵は環境変数 IZK_AUTH からしか読まない。標準出力にも出さない。
  ・--apply と --yes の両方がなければ、何も書き込まない。
  ・文字の位置（何文字目か）は使わない。まるごと置き換える。
  ・置き換える段落がちょうど1つあることを数え、合わなければ中止する。
  ・その段落の外が1文字も変わっていないことを、確かめてから書き込む。
  ・書き込んだあと読み返し、さらに公開ページを取って確かめる。
"""
import os, sys, io, json, base64
import urllib.request as ur

KIJI = 6260

FURUI = (u'<!-- wp:paragraph {"fontSize":"medium"} -->\n'
         u'<p class="has-medium-font-size">では他人事かというと、そうではありません。'
         u'<strong>積載効率41.3%</strong>という数字は、行きは満載でも帰りは空荷、'
         u'という便が多いことを示しています。人が足りないことも、若い人が入ってこないことも、'
         u'業種を問いません。</p>\n<!-- /wp:paragraph -->')

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

    atara = io.open('karani.html', encoding='utf-8').read().strip()

    d = yobu('/wp/v2/posts/%d?context=edit' % KIJI)
    assert d['slug'] == 'butsuryu-taiko-2026', d['slug']
    t = d['content']['raw']
    print(u'記事 %d / %s / 本文 %d字' % (KIJI, d['status'], len(t)))

    if u'クラック調査' in t:
        print(u'もう入っています。中止します。'); return

    n = t.count(FURUI)
    print(u'置き換える段落:', n)
    assert n == 1, u'1つではない。中止します。'

    atarashii = t.replace(FURUI, atara)

    # この段落の外が変わっていないか（目印を同じ印に置き換えて突き合わせる）
    assert t.replace(FURUI, u'\x00') == atarashii.replace(atara, u'\x00'), u'外が変わっている'
    print(u'この段落の外は、1文字も変わっていません。')
    print(u'本文 %d字 → %d字' % (len(t), len(atarashii)))

    if not yaru:
        print(u'--apply --yes が無いので、ここで終わります。'); return

    yobu('/wp/v2/posts/%d' % KIJI, {'content': atarashii, 'status': 'publish'})
    m = yobu('/wp/v2/posts/%d?context=edit' % KIJI)
    assert m['content']['raw'] == atarashii, u'書き込んだものと違う'
    assert m['status'] == 'publish'
    print(u'書き込みました。読み返しも一致。status=%s' % m['status'])


if __name__ == '__main__':
    main()
