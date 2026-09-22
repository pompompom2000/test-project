# -*- coding: utf-8 -*-
u"""
公開済みの記事6260に、産廃は許可制という段落と、出典を1行足す。

  ・鍵は環境変数 IZK_AUTH からしか読まない。標準出力にも出さない。
  ・--apply と --yes の両方がなければ、何も書き込まない。
  ・文字の位置（何文字目か）は使わない。まるごと置き換える。
  ・目印がちょうど1つあることを数え、合わなければ中止する。
  ・足すだけ。いまある文章は1文字も消さない（目印を同じ印に置き換えて
    突き合わせ、一致することを確かめてから書き込む）。
  ・書き込んだあと読み返し、さらに公開ページを取って確かめる。
"""
import os, sys, io, json, base64
import urllib.request as ur

KIJI = 6260

# 足す場所の目印：帰り空荷の説明のいちばん最後の段落
SHIRUSHI = (u'<p class="has-medium-font-size">工程がそうなっている以上、'
            u'<strong>帰りの空荷は避けられません。</strong>'
            u'「積載効率41.3%」という数字の裏には、こういう事情があります。'
            u'運ぶ側が気合を入れれば上がる、という種類の数字ではありません。'
            u'人が足りないことも、若い人が入ってこないことも、業種を問わず同じです。</p>\n'
            u'<!-- /wp:paragraph -->')

# 出典の最後の項目のうしろ
SHUTTEN_SHIRUSHI = (u'<li>国土交通省 報道発表「トラックドライバーの１運行当たりの平均拘束時間に関する'
                    u'調査結果の公表」令和8年7月10日<br>'
                    u'<a href="https://www.mlit.go.jp/report/press/tokatsu02_hh_000084.html">'
                    u'https://www.mlit.go.jp/report/press/tokatsu02_hh_000084.html</a></li>\n'
                    u'<!-- /wp:list-item -->')

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

    dan  = io.open('sanpai.html', encoding='utf-8').read().strip()
    shut = io.open('sanpai-shutten.html', encoding='utf-8').read().strip()

    d = yobu('/wp/v2/posts/%d?context=edit' % KIJI)
    assert d['slug'] == 'butsuryu-taiko-2026', d['slug']
    t = d['content']['raw']
    print(u'記事 %d / %s / 本文 %d字' % (KIJI, d['status'], len(t)))

    if u'第14条第1項' in t:
        print(u'もう入っています。中止します。'); return

    n1, n2 = t.count(SHIRUSHI), t.count(SHUTTEN_SHIRUSHI)
    print(u'目印（本文）:', n1, u'／ 目印（出典）:', n2)
    assert n1 == 1 and n2 == 1, u'目印が1つではない。中止します。'

    atarashii = t.replace(SHIRUSHI, SHIRUSHI + u'\n\n' + dan)
    atarashii = atarashii.replace(SHUTTEN_SHIRUSHI, SHUTTEN_SHIRUSHI + u'\n' + shut)

    fueta = len(atarashii) - len(t)
    print(u'本文 %d字 → %d字（増えた分 %d）' % (len(t), len(atarashii), fueta))
    assert fueta == len(dan) + len(shut) + 3, u'足した分と増えた分が合わない'
    assert t.replace(SHIRUSHI, u'\x00').replace(SHUTTEN_SHIRUSHI, u'\x01') == \
           atarashii.replace(SHIRUSHI + u'\n\n' + dan, u'\x00').replace(
               SHUTTEN_SHIRUSHI + u'\n' + shut, u'\x01'), u'もとの文章が変わっている'
    print(u'もとの文章は、そのままです。')

    if not yaru:
        print(u'--apply --yes が無いので、ここで終わります。'); return

    yobu('/wp/v2/posts/%d' % KIJI, {'content': atarashii, 'status': 'publish'})
    m = yobu('/wp/v2/posts/%d?context=edit' % KIJI)
    assert m['content']['raw'] == atarashii, u'書き込んだものと違う'
    assert m['status'] == 'publish'
    print(u'書き込みました。読み返しも一致。status=%s' % m['status'])


if __name__ == '__main__':
    main()
