# -*- coding: utf-8 -*-
"""記事の末尾に「前の記事へ／次の記事へ」の画像ナビと「お知らせ一覧へ」を足す。

公開済み146本のうち 99% にこのナビがあり、89% に一覧へ戻るボタンがある。
下書きだけ落ちていたので、Claude Code 連載とまったく同じ形で足す。

つなぎ先：
  前編 ← いま公開されている最新の記事（2026-09-10）／→ 後編
  後編 ← 前編／次はまだないので、そこは空のカラムにする
         （公開済みでも、いちばん新しい記事は空にしてある）

    python3 add_nav.py

二度流しても重ならない。すでにナビがあれば何もしない。
"""
from __future__ import print_function

import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = 'https://www.ishinazaka.co.jp'
UP = SITE + '/common/files/uploads/2026/04'

PREV_IMG = UP + '/%E5%89%8D%E3%81%AE%E8%A8%98%E4%BA%8B%E3%81%B8-e1776822939829.png'
NEXT_IMG = UP + '/%E6%AC%A1%E3%81%AE%E8%A8%98%E4%BA%8B%E3%81%B8%E3%83%9C%E3%82%BF%E3%83%B3-e1776822959719.png'
LIST_IMG = UP + '/%E6%88%BB%E3%82%8B%E3%83%9C%E3%82%BF%E3%83%B32-e1776823039293.png'

SPACER = (u'<!-- wp:spacer {"height":"40px"} -->\n'
          u'<div style="height:40px" aria-hidden="true" class="wp-block-spacer"></div>\n'
          u'<!-- /wp:spacer -->')

BUTTON = (u'<!-- wp:image {"lightbox":{"enabled":false},"id":%(id)d,"width":"100px",'
          u'"sizeSlug":"full","linkDestination":"custom"} -->\n'
          u'<figure class="wp-block-image size-full is-resized">'
          u'<a href="%(href)s"><img src="%(src)s" alt="%(alt)s" '
          u'class="wp-image-%(id)d" style="width:100px;height:auto"/></a></figure>\n'
          u'<!-- /wp:image -->')


def column(inner=u'', last=False):
    """カラムひとつ。最後のカラムだけ、外側の div も一緒に閉じる（本家と同じ形）。"""
    tail = u'</div>\n<!-- /wp:column -->'
    if last:
        tail = u'</div>\n<!-- /wp:column --></div>\n<!-- /wp:columns -->'
    return u'<!-- wp:column -->\n<div class="wp-block-column">%s%s' % (inner, tail)


def nav(prev_url, next_url):
    left = BUTTON % dict(id=1730, href=SITE + prev_url, src=PREV_IMG, alt=u'前の記事へ')
    right = (BUTTON % dict(id=1731, href=SITE + next_url, src=NEXT_IMG, alt=u'次の記事へ')
             ) if next_url else u''
    return u'\n'.join([
        SPACER, u'',
        u'<!-- wp:columns {"isStackedOnMobile":false} -->',
        u'<div class="wp-block-columns is-not-stacked-on-mobile">' + column(left),
        u'', column(), u'', column(right, last=True),
        u'', SPACER, u'',
        u'<!-- wp:image {"lightbox":{"enabled":false},"id":1361,"sizeSlug":"full",'
        u'"linkDestination":"custom"} -->',
        u'<figure class="wp-block-image size-full">'
        u'<a href="%s/category/information/"><img src="%s" alt="お知らせ一覧へ" '
        u'class="wp-image-1361"/></a></figure>' % (SITE, LIST_IMG),
        u'<!-- /wp:image -->',
    ])


JOBS = [
    ('article-01.html', '/kensetsugyo-unso-kyoka-koushin/', '/quantum-computer-02-status/'),
    ('article-02.html', '/quantum-computer-01-mechanism/', None),
]


def main():
    n = 0
    for fname, prev_url, next_url in JOBS:
        path = os.path.join(HERE, fname)
        t = io.open(path, encoding='utf-8').read()
        if u'前の記事へ' in t:
            print(u'－ %s：ナビはすでにあります' % fname)
            continue
        if u'<!-- ISNZ-CTA -->' not in t:
            sys.stderr.write(u'× %s：ISNZ-CTA の目印がありません\n' % fname)
            sys.exit(1)
        t = t.rstrip() + u'\n\n' + nav(prev_url, next_url) + u'\n'
        io.open(path, 'w', encoding='utf-8').write(t)
        print(u'○ %s：前＝%s／次＝%s' % (fname, prev_url, next_url or u'なし（空カラム）'))
        n += 1
    print(u'\n%d本に足しました。' % n)


if __name__ == '__main__':
    main()
