# -*- coding: utf-8 -*-
"""前後の記事の鎖をつなぐ。

新しい記事を公開すると、それまで最新だった記事の「次の記事へ」が
空のままになる。公開済み146本のうち99%にこのナビがあるので、
空いたままだと読者がたどれず、内部リンクも一本足りない。

    export IZK_AUTH='ai-agent:xxxx ...'
    python3 tsunagi.py --show                # いまの状態を見るだけ
    python3 tsunagi.py --apply

決めごと：
  ・鍵は環境変数からしか読まない。標準出力にも出さない。
  ・書き換える前に、いまの中身を必ず表示する。
  ・差し込み先が1件でなければ止める。取り違えを防ぐため。
  ・書いたあと読み直して、狙ったとおりかを確かめる。
  ・本文には触らない。足すのは画像リンク一つだけ。
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
W = SITE + '/wp-json/wp/v2'
NEXT_IMG = (SITE + '/common/files/uploads/2026/04/'
            '%E6%AC%A1%E3%81%AE%E8%A8%98%E4%BA%8B%E3%81%B8%E3%83%9C%E3%82%BF%E3%83%B3'
            '-e1776822959719.png')

# 最後の空カラム。これを「次の記事へ」の入ったカラムに差し替える。
EMPTY_LAST = (u'<!-- wp:column -->\n<div class="wp-block-column"></div>\n'
              u'<!-- /wp:column --></div>\n<!-- /wp:columns -->')

# 画像URLに % が入っているので、書式指定は使わず __HREF__ を置き換える。
FILLED_LAST = (
    u'<!-- wp:column -->\n'
    u'<div class="wp-block-column"><!-- wp:image {"lightbox":{"enabled":false},'
    u'"id":1731,"width":"100px","sizeSlug":"full","linkDestination":"custom"} -->\n'
    u'<figure class="wp-block-image size-full is-resized">'
    u'<a href="__HREF__"><img src="' + NEXT_IMG + u'" alt="次の記事へ" '
    u'class="wp-image-1731" style="width:100px;height:auto"/></a></figure>\n'
    u'<!-- /wp:image --></div>\n'
    u'<!-- /wp:column --></div>\n<!-- /wp:columns -->')


# (直す記事のスラッグ, その「次の記事へ」が指す先のスラッグ)
CHAIN = [('kensetsugyo-unso-kyoka-koushin', 'quantum-computer-01-mechanism')]

# 題名が変わった記事を指している文言をそろえる
# (直す記事のスラッグ, 前の文言, いまの文言)
RELABEL = [('quantum-computer-02-status',
            u'量子コンピュータとは何か【前編】仕組みと原理を、嘘をつかずに',
            u'量子コンピュータとは何か【前編】仕組みと原理を。')]


def head():
    a = os.environ.get('IZK_AUTH')
    if not a:
        sys.exit(u'× 環境変数 IZK_AUTH がありません')
    return {'Authorization': 'Basic ' + base64.b64encode(a.encode('utf-8')).decode('ascii'),
            'User-Agent': 'izk-tsunagi'}


def call(path, h, data=None):
    hh = dict(h)
    if data is not None:
        hh['Content-Type'] = 'application/json'
    req = Request(W + path, headers=hh,
                  data=json.dumps(data).encode('utf-8') if data else None)
    try:
        return json.loads(urlopen(req, timeout=90).read().decode('utf-8'))
    except HTTPError as e:
        sys.exit(u'× %s\n  %s' % (e.code, e.read().decode('utf-8', 'replace')[:300]))


def one(slug, h):
    got = call('/posts?slug=%s&status=publish,draft&context=edit' % slug, h)
    if len(got) != 1:
        sys.exit(u'× %s の記事が %d 件' % (slug, len(got)))
    return got[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--show', action='store_true')
    ap.add_argument('--apply', action='store_true')
    a = ap.parse_args()
    if not (a.show or a.apply):
        ap.error(u'--show か --apply を指定してください')
    h = head()

    # ── ① 鎖をつなぐ ──────────────────────────────────
    for slug, to_slug in CHAIN:
        p, q = one(slug, h), one(to_slug, h)
        t = p['content']['raw']
        print(u'\n=== ① %s（ID%d）に「次の記事へ」を足す ===' % (p['title']['raw'][:34], p['id']))
        print(u'   つなぐ先: %s' % q['title']['raw'])
        print(u'             %s/%s/' % (SITE, to_slug))
        if u'次の記事へ' in t:
            print(u'   － すでに入っています。何もしません。')
            continue
        if t.count(EMPTY_LAST) != 1:
            sys.exit(u'× 差し込み先の空カラムが %d 件（1件でないと止めます）' % t.count(EMPTY_LAST))
        print(u'   いまは最後のカラムが空です（差し込み先 1件 確認）')
        if not a.apply:
            continue
        filled = FILLED_LAST.replace(u'__HREF__', u'%s/%s/' % (SITE, to_slug))
        new = t.replace(EMPTY_LAST, filled)
        call('/posts/%d' % p['id'], h, {'content': new})
        back = one(slug, h)['content']['raw']
        print(u'   %s 読み直し：「次の記事へ」%s／リンク先 %s'
              % (u'○' if u'次の記事へ' in back else u'×',
                 u'あり' if u'次の記事へ' in back else u'なし',
                 u'正' if ('%s/%s/' % (SITE, to_slug)) in back else u'誤'))
        print(u'   本文の長さ %d字 → %d字（差 %+d）' % (len(t), len(back), len(back) - len(t)))

    # ── ② 題名の文言をそろえる ─────────────────────────
    for slug, old, new in RELABEL:
        p = one(slug, h)
        t = p['content']['raw']
        print(u'\n=== ② %s（ID%d）の文言をそろえる ===' % (p['title']['raw'][:34], p['id']))
        if old not in t and new in t:
            print(u'   － すでにそろっています。何もしません。')
            continue
        if t.count(old) != 1:
            sys.exit(u'× 直す先が %d 件' % t.count(old))
        print(u'   いま : %s' % old)
        print(u'   直後 : %s' % new)
        if not a.apply:
            continue
        call('/posts/%d' % p['id'], h, {'content': t.replace(old, new)})
        back = one(slug, h)['content']['raw']
        print(u'   %s 読み直し：新しい文言 %s／古い文言 %s'
              % (u'○' if (new in back and old not in back) else u'×',
                 u'あり' if new in back else u'なし',
                 u'残っている' if old in back else u'なし'))


if __name__ == '__main__':
    main()
