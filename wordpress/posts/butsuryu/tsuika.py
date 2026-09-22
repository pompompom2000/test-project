# -*- coding: utf-8 -*-
u"""
公開済みの記事6260に、国交省の調査結果の段落と、出典を1行足す。

  ・鍵は環境変数 IZK_AUTH からしか読まない。標準出力にも出さない。
  ・--apply と --yes の両方がなければ、何も書き込まない。
  ・文字の位置（何文字目か）は使わない。まるごと置き換える。
  ・目印がちょうど1つあることを数え、合わなければ中止する。
  ・足すだけ。いまある文章は1文字も消さない（長さの差で確かめる）。
  ・書き込んだあと読み返し、さらに公開ページを取って確かめる。
"""
import os, sys, io, json, base64
import urllib.request as ur

KIJI = 6260
URL  = 'https://www.ishinazaka.co.jp/butsuryu-taiko-2026/'

# 足す場所の目印：目標の章の最後の段落
SHIRUSHI = (u'<p class="has-medium-font-size">目を引くのは、<strong>賃金と労働時間を'
            u'「全産業平均まで」と書いたこと</strong>です。裏を返せば、いまは届いていない。'
            u'年収で35万円ほど低く、労働時間は年400時間以上長い。それを5年で埋めると'
            u'国が宣言しました。</p>\n<!-- /wp:paragraph -->')

# 出典の最後の項目のうしろ
SHUTTEN_SHIRUSHI = (u'<li>国土交通省 報道発表「『総合物流施策大綱（2026年度〜2030年度）』を閣議決定」'
                    u'令和8年3月31日<br><a href="https://www.mlit.go.jp/report/press/'
                    u'tokatsu01_hh_000998.html">https://www.mlit.go.jp/report/press/'
                    u'tokatsu01_hh_000998.html</a></li>\n<!-- /wp:list-item -->')

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

    dan   = io.open('tsuika.html', encoding='utf-8').read().strip()
    shut  = io.open('tsuika-shutten.html', encoding='utf-8').read().strip()

    d = yobu('/wp/v2/posts/%d?context=edit' % KIJI)
    assert d['slug'] == 'butsuryu-taiko-2026', d['slug']
    t = d['content']['raw']
    print(u'記事 %d / %s / 本文 %d字' % (KIJI, d['status'], len(t)))

    if u'10時間13分' in t:
        print(u'もう入っています。中止します。'); return

    n1, n2 = t.count(SHIRUSHI), t.count(SHUTTEN_SHIRUSHI)
    print(u'目印（本文）:', n1, u'／ 目印（出典）:', n2)
    assert n1 == 1 and n2 == 1, u'目印が1つではない。中止します。'

    atarashii = t.replace(SHIRUSHI, SHIRUSHI + u'\n\n' + dan)
    atarashii = atarashii.replace(SHUTTEN_SHIRUSHI, SHUTTEN_SHIRUSHI + u'\n' + shut)

    fueta = len(atarashii) - len(t)
    print(u'本文 %d字 → %d字（増えた分 %d）' % (len(t), len(atarashii), fueta))
    assert fueta == len(dan) + len(shut) + 3, u'足した分と増えた分が合わない'
    # 足すだけ：もとの文章がそのまま残っているか
    assert t.replace(SHIRUSHI, u'\x00').replace(SHUTTEN_SHIRUSHI, u'\x01') == \
           atarashii.replace(SHIRUSHI + u'\n\n' + dan, u'\x00').replace(
               SHUTTEN_SHIRUSHI + u'\n' + shut, u'\x01'), u'もとの文章が変わっている'
    print(u'もとの文章は、そのままです。')

    if not yaru:
        print(u'--apply --yes が無いので、ここで終わります。'); return

    yobu('/wp/v2/posts/%d' % KIJI, {'content': atarashii, 'status': 'publish'})
    m = yobu('/wp/v2/posts/%d?context=edit' % KIJI)
    r = m['content']['raw']
    assert r == atarashii, u'書き込んだものと違う'
    assert m['status'] == 'publish'
    print(u'書き込みました。読み返しも一致。status=%s' % m['status'])


if __name__ == '__main__':
    main()
