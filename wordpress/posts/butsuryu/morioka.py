# -*- coding: utf-8 -*-
u"""
公開済みの記事6260の「盛岡で、ダンプを持つ側から見ると」の中身を、
morioka.html に差し替える。

  ・鍵は環境変数 IZK_AUTH からしか読まない。標準出力にも出さない。
  ・--apply と --yes の両方がなければ、何も書き込まない。
  ・章の切れ目（見出しから次の見出しまで）で取り出し、ちょうど1つで
    なければ中止する。
  ・消す部分に、いま直したい文が入っていることを確かめてから消す。
  ・この章の外が1文字も変わっていないことを、確かめてから書き込む。
  ・書き込んだあと読み返し、さらに公開ページを取って確かめる。
"""
import os, sys, io, json, base64
import urllib.request as ur

KIJI = 6260
MIDASHI = (u'<!-- wp:heading {"level":3,"fontSize":"medium"} -->\n'
           u'<h3 class="wp-block-heading has-medium-font-size">'
           u'盛岡で、ダンプを持つ側から見ると</h3>\n<!-- /wp:heading -->')
TSUGI = u'<!-- wp:heading {"level":3,"fontSize":"medium"} -->\n' \
        u'<h3 class="wp-block-heading has-medium-font-size">まとめ</h3>'

# 消える側に、必ず入っているはずの文（間違った記述）
KESU_SHOUKO = [u'大綱の数字は、どれも現場の風景そのものです。',
               u'1日にすると3時間ほどです。現場に着いて、順番を待って、荷を降ろす。']

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

    atarashii_dan = io.open('morioka.html', encoding='utf-8').read().strip()

    d = yobu('/wp/v2/posts/%d?context=edit' % KIJI)
    assert d['slug'] == 'butsuryu-taiko-2026', d['slug']
    t = d['content']['raw']
    print(u'記事 %d / %s / 本文 %d字' % (KIJI, d['status'], len(t)))

    assert t.count(MIDASHI) == 1, u'章の見出しが1つではない'
    assert t.count(TSUGI) == 1, u'「まとめ」の見出しが1つではない'
    i = t.index(MIDASHI) + len(MIDASHI)
    j = t.index(TSUGI)
    assert j > i, u'章の順番がおかしい'
    furui_dan = t[i:j]
    print(u'いまの中身 %d字' % len(furui_dan))

    for s in KESU_SHOUKO:
        assert s in furui_dan, u'消すはずの文が見つからない: ' + s[:20]
    print(u'直したい文が、消える側にあることを確かめました。')

    mae, ato = t[:i], t[j:]
    atarashii = mae + u'\n\n' + atarashii_dan + u'\n\n' + ato

    # 章の外が変わっていないか
    assert atarashii.startswith(mae) and atarashii.endswith(ato), u'章の外が動いている'
    print(u'本文 %d字 → %d字' % (len(t), len(atarashii)))
    print(u'章の外: 前 %d字 / 後 %d字（どちらもそのまま）' % (len(mae), len(ato)))

    if not yaru:
        io.open('morioka-sashikae-zumi.html', 'w', encoding='utf-8').write(atarashii)
        print(u'組み上げたものを morioka-sashikae-zumi.html に書きました')
        print(u'--apply --yes が無いので、ここで終わります。'); return

    yobu('/wp/v2/posts/%d' % KIJI, {'content': atarashii, 'status': 'publish'})
    m = yobu('/wp/v2/posts/%d?context=edit' % KIJI)
    assert m['content']['raw'] == atarashii, u'書き込んだものと違う'
    assert m['status'] == 'publish'
    print(u'書き込みました。読み返しも一致。status=%s' % m['status'])


if __name__ == '__main__':
    main()
