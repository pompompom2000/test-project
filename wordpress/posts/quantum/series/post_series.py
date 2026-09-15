# -*- coding: utf-8 -*-
"""全6回を、WordPress に下書きとして投稿する。

    export IZK_AUTH='ai-agent:xxxx ...'
    python3 post_series.py --dry-run
    python3 post_series.py

決めごと：
  ・status は draft 固定。このスクリプトから公開することはできない。
  ・公開済みの記事には触れない（前編・後編はそのまま）。
  ・写真の差し込み先が1件でなければ止める。
  ・投稿したあと読み直して、狙ったとおりか確かめる。
"""
from __future__ import print_function

import argparse
import io
import os
import re
import sys

import plan

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(SRC, '..', '..', 'images'))

SITE = plan.SITE
CATEGORIES = [1, 10]
# 第1回の「前の記事へ」。
# 前編・後編は引退させる方針になったので、その一つ手前の記事を指す。
FIRST_PREV = '/kensetsugyo-unso-kyoka-koushin/'

UP = SITE + '/common/files/uploads/2026/04'
PREV_IMG = UP + '/%E5%89%8D%E3%81%AE%E8%A8%98%E4%BA%8B%E3%81%B8-e1776822939829.png'
NEXT_IMG = UP + '/%E6%AC%A1%E3%81%AE%E8%A8%98%E4%BA%8B%E3%81%B8%E3%83%9C%E3%82%BF%E3%83%B3-e1776822959719.png'
LIST_IMG = UP + '/%E6%88%BB%E3%82%8B%E3%83%9C%E3%82%BF%E3%83%B32-e1776823039293.png'

SPACER = (u'<!-- wp:spacer {"height":"40px"} -->\n'
          u'<div style="height:40px" aria-hidden="true" class="wp-block-spacer"></div>\n'
          u'<!-- /wp:spacer -->')
BTN = (u'<!-- wp:image {"lightbox":{"enabled":false},"id":__ID__,"width":"100px",'
       u'"sizeSlug":"full","linkDestination":"custom"} -->\n'
       u'<figure class="wp-block-image size-full is-resized">'
       u'<a href="__HREF__"><img src="__SRC__" alt="__ALT__" '
       u'class="wp-image-__ID__" style="width:100px;height:auto"/></a></figure>\n'
       u'<!-- /wp:image -->')
H3 = (u'<!-- wp:heading {"level":3} -->\n'
      u'<h3 class="wp-block-heading">%s</h3>\n<!-- /wp:heading -->')
LI = u'<!-- wp:list-item -->\n<li>%s</li>\n<!-- /wp:list-item -->'
UL = u'<!-- wp:list -->\n<ul class="wp-block-list">\n%s\n</ul>\n<!-- /wp:list -->'


def button(mid, href, src, alt):
    return (BTN.replace('__ID__', str(mid)).replace('__HREF__', href)
            .replace('__SRC__', src).replace('__ALT__', alt))


def column(inner=u'', last=False):
    tail = u'</div>\n<!-- /wp:column -->'
    if last:
        tail += u'</div>\n<!-- /wp:columns -->'
    return u'<!-- wp:column -->\n<div class="wp-block-column">%s%s' % (inner, tail)


def nav(prev_url, next_url):
    left = button(1730, SITE + prev_url, PREV_IMG, u'前の記事へ')
    right = button(1731, SITE + next_url, NEXT_IMG, u'次の記事へ') if next_url else u''
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
        u'<!-- /wp:image -->'])


def series_list(me):
    rows = []
    for s in plan.PARTS:
        label = u'第%d回　%s' % (s['n'], re.sub(r'【.*?】', '', s['title']))
        if s['n'] == me:
            rows.append(u'<li>%s（この記事）</li>' % label)
        else:
            rows.append(u'<li><a href="%s/%s/">%s</a></li>' % (SITE, s['slug'], label))
    return (H3 % u'このシリーズの記事') + u'\n\n' + \
           (u'<!-- wp:list {"fontSize":"medium"} -->\n'
            u'<ul class="wp-block-list has-medium-font-size">%s</ul>\n'
            u'<!-- /wp:list -->' % u''.join(rows))


AWASETE = (H3 % u'あわせて読みたい') + u'\n\n' + (UL % u'\n'.join(LI % x for x in [
    u'<a href="%s/claude-code-01-overview/">Claude Code とは？'
    u'できることを初心者にもわかりやすく解説【第1回】</a>' % SITE,
    u'<a href="%s/claude-code-05-safety/">Claude Code 注意点【最終回】'
    u'安全に使うためのポイント</a>' % SITE,
]))


def cta():
    """CTAは、いま公開されている前編からそのまま借りる（形をそろえるため）。"""
    t = io.open(os.path.join(SRC, 'article-01.html'), encoding='utf-8').read()
    i = t.index('<!-- ISNZ-CTA -->')
    j = t.index('<!-- wp:spacer {"height":"40px"} -->', i)
    return t[i:j].rstrip()


def image_block(media, shot):
    return (u'<!-- wp:image {"id":%d,"sizeSlug":"large","linkDestination":"none"} -->\n'
            u'<figure class="wp-block-image size-large">'
            u'<img src="%s" alt="%s" class="wp-image-%d"/>'
            u'<figcaption class="wp-element-caption">%s</figcaption></figure>\n'
            u'<!-- /wp:image -->'
            % (media['id'], shot['url'], shot['alt'], media['id'], shot['caption']))


def gather(smm, auth):
    """写真の情報を集める。"""
    shots = {s['n']: s for s in smm.load_shots()}
    media = {}
    for n in range(1, 9):
        md = smm.find_by_url(shots[n]['url'], auth)
        if not md:
            sys.exit(u'× %d番の画像がサイトに見つかりません' % n)
        media[n] = md
    return shots, media


def build_full(k, shots, media):
    """第k+1回の本文を、末尾まで組み立てて返す。"""
    spec = plan.PARTS[k]
    body = io.open(os.path.join(HERE, 'part-%d.html' % spec['n']), encoding='utf-8').read()
    for mark in re.findall(r'<!-- ISNZ-PHOTO-(\d+) -->', body):
        n = int(mark)
        tag = u'<!-- ISNZ-PHOTO-%d -->' % n
        if body.count(tag) != 1:
            sys.exit(u'× 第%d回：%d番の差し込み先が %d件' % (spec['n'], n, body.count(tag)))
        body = body.replace(tag, image_block(media[n], shots[n]))
    prev_url = FIRST_PREV if k == 0 else '/%s/' % plan.PARTS[k-1]['slug']
    next_url = None if k == len(plan.PARTS)-1 else '/%s/' % plan.PARTS[k+1]['slug']
    full = u'\n\n'.join([body.rstrip(), u'<!-- ISNZ-REL -->',
                         series_list(spec['n']), AWASETE, cta(), nav(prev_url, next_url)])
    return full, prev_url, next_url


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    import set_media_meta as smm
    auth = smm.auth_header()
    shots, media = gather(smm, auth)

    for k, spec in enumerate(plan.PARTS):
        full, prev_url, next_url = build_full(k, shots, media)

        txt = re.sub(r'\s+', '', re.sub(r'<[^>]+>', '',
                     re.sub(r'<svg.*?</svg>|<!--.*?-->', '', full, flags=re.S)))
        print(u'\n=== 第%d回 %s ===' % (spec['n'], spec['title']))
        print(u'  スラッグ  : %s' % spec['slug'])
        print(u'  本文      : %d字（表示される文字）' % len(txt))
        print(u'  アイキャッチ: %d番 ID%s' % (spec['featured'], media[spec['featured']]['id']))
        print(u'  ナビ      : ← %s ／ → %s' % (prev_url, next_url or u'なし'))
        print(u'  狙う言葉  : %s' % spec['keyword'])
        if args.dry_run:
            continue

        found = smm.call('/posts?slug=%s&status=draft,publish,pending,private&context=edit'
                         % spec['slug'], auth)
        data = {'title': spec['title'], 'slug': spec['slug'], 'content': full,
                'excerpt': spec['desc'], 'status': 'draft', 'categories': CATEGORIES,
                'featured_media': media[spec['featured']]['id']}
        if found:
            p = found[0]
            if p['status'] != 'draft':
                print(u'  ! すでに「%s」の記事があります。触りません（ID %s）' % (p['status'], p['id']))
                continue
            del data['status']
            r = smm.call('/posts/%d' % p['id'], auth, data=data)
            print(u'  ○ 下書きを更新しました（ID %s）' % r['id'])
        else:
            r = smm.call('/posts', auth, data=data)
            print(u'  ○ 下書きを作りました（ID %s）' % r['id'])
        print(u'  編集画面  : %s/wp-admin/post.php?post=%s&action=edit' % (SITE, r['id']))


if __name__ == '__main__':
    main()
