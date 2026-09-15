# -*- coding: utf-8 -*-
"""下書きのSEO設定（All in One SEO）を書き込む。

このサイトは All in One SEO を使っている。公開済みの記事は、
・focus_keyword（狙う言葉）を必ず1つ決めている（12/12本）
・description（検索結果に出る説明文）を手書きしている（中央値91字）
下書きはどちらも未設定で、説明文が「#post_excerpt」のままだった。

    export IZK_AUTH='ai-agent:xxxx ...'
    python3 set_seo.py --show     # いまの値を見るだけ
    python3 set_seo.py --apply    # 書き込む

決めごと：
  ・鍵は環境変数からしか読まない。標準出力にも出さない。
  ・下書き以外には触れない。公開済みの記事は書き換えない。
  ・書き込む前に、いまの値を必ず表示する。
  ・書き込んだあと読み直して、狙った項目だけが変わったか確かめる。
"""
from __future__ import print_function

import argparse
import base64
import json
import os
import sys

from urllib.request import Request, urlopen
from urllib.error import HTTPError

SITE = 'https://www.ishinazaka.co.jp'
AIO = SITE + '/wp-json/aioseo/v1'
WP = SITE + '/wp-json/wp/v2'

# 狙う言葉は、全国で競り合う「量子コンピュータ」の一語ではなく、
# 記事の中身とそろう二語にする。公開済みも「駐車場 砕石」「Claude Code インストール」
# のように二語で取っている。
SEO = {
    6188: dict(
        keyword=u'量子コンピュータ 仕組み',
        desc=u'量子コンピュータの仕組みを、わかりやすさのために事実を曲げずに解説します。'
             u'量子ビットが持つ「矢印」とは何か、なぜ普通のコンピュータでは追いつけないのか。'
             u'2025年のノーベル物理学賞から説き起こす、全2回の前編です。',
    ),
    6189: dict(
        keyword=u'量子コンピュータ 実用化',
        desc=u'量子コンピュータの実用化はいつか。作り方は六通りあり、まだ本命が決まっていません。'
             u'何の分野で使えるのか、暗号が2035年に切り替わる話まで、'
             u'確かめられたこととまだのことを分けて解説する、全2回の後編です。',
    ),
}


def auth_header():
    a = os.environ.get('IZK_AUTH')
    if not a:
        sys.exit(u'× 環境変数 IZK_AUTH がありません（ai-agent:アプリケーションパスワード）')
    return {'Authorization': 'Basic ' + base64.b64encode(a.encode('utf-8')).decode('ascii'),
            'User-Agent': 'izk-seo'}


def call(url, head, data=None):
    h = dict(head)
    if data is not None:
        h['Content-Type'] = 'application/json'
    req = Request(url, headers=h, data=json.dumps(data).encode('utf-8') if data else None)
    try:
        return json.loads(urlopen(req, timeout=90).read().decode('utf-8'))
    except HTTPError as e:
        sys.exit(u'× %s\n  %s' % (e.code, e.read().decode('utf-8', 'replace')[:400]))


def current(pid, head):
    return call('%s/post?postId=%d' % (AIO, pid), head)['data']['currentPost']


def show(pid, c, label):
    print(u'  %s' % label)
    print(u'    説明文（%d字）: %s' % (len(c.get('description') or u''),
                                  c.get('description') or u'（未設定）'))
    print(u'    狙う言葉      : %s' % (c.get('focus_keyword') or u'（未設定）'))
    print(u'    SEOの点       : %s' % c.get('seo_score'))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--show', action='store_true')
    ap.add_argument('--apply', action='store_true')
    a = ap.parse_args()
    if not (a.show or a.apply):
        ap.error(u'--show か --apply を指定してください')
    head = auth_header()

    for pid, want in sorted(SEO.items()):
        post = call('%s/posts/%d?context=edit' % (WP, pid), head)
        print(u'\n=== ID%d %s ===' % (pid, post['title']['raw']))
        if post['status'] != 'draft':
            print(u'  ! 下書きではありません（%s）。触りません。' % post['status'])
            continue

        before = current(pid, head)
        show(pid, before, u'いまの値')
        if not a.apply:
            print(u'  → 入れる説明文（%d字）: %s' % (len(want['desc']), want['desc']))
            print(u'  → 入れる狙う言葉      : %s' % want['keyword'])
            continue

        # いまの値をそのまま土台にして、狙った欄だけ差し替える。
        # 部分的に送ると他の欄が消えることがあるため。
        body = dict(before)
        body['postId'] = pid
        body['description'] = want['desc']
        body['focus_keyword'] = want['keyword']
        body['keyphrases'] = {
            'focus': {'keyphrase': want['keyword'], 'score': 0, 'analysis': []},
            'additional': before.get('keyphrases', {}).get('additional', []),
        }
        call(AIO + '/post', head, body)

        after = current(pid, head)
        show(pid, after, u'書き込んだあと')

        # 狙った欄だけが変わったか確かめる
        watch = ['title', 'canonicalUrl', 'noindex', 'nofollow', 'og_title',
                 'og_description', 'og_image_type', 'permalink', 'postStatus']
        moved = [k for k in watch if before.get(k) != after.get(k)]
        print(u'    ほかの欄の変化: %s'
              % (u'、'.join(moved) if moved else u'なし（狙った欄だけ変わりました）'))
        ok = (after.get('description') == want['desc']
              and after.get('focus_keyword') == want['keyword'])
        print(u'    %s' % (u'○ 入りました' if ok else u'× 入っていません'))


if __name__ == '__main__':
    main()
