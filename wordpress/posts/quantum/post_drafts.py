# -*- coding: utf-8 -*-
"""量子コンピュータの記事を、WordPress に下書きとして投稿する。

    export IZK_AUTH='ai-agent:xxxx xxxx xxxx xxxx xxxx xxxx'
    python3 post_drafts.py --dry-run     # 送る中身を確かめる（APIは呼ばない）
    python3 post_drafts.py               # 下書きを作る／更新する

決めごと：
  ・status は draft 固定。このスクリプトから公開することはできない。
  ・同じスラッグの記事がすでにあれば作り直さず、中身を差し替える。
    ただし公開済みの記事には触れない（下書きのときだけ書き換える）。
  ・挿絵は差し込み先が1件でないと止める。取り違えを防ぐため。
  ・1番と5番はアイキャッチにするので、本文には入れない。二重になるため。
"""
from __future__ import print_function

import argparse
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'images'))

SITE = 'https://www.ishinazaka.co.jp'
CATEGORIES = [1, 10]            # お知らせ／コラム（Claude Code 連載と同じ）

POSTS = [
    dict(
        file='article-01.html',
        slug='quantum-computer-01-mechanism',
        title=u'量子コンピュータとは何か【前編】仕組みと原理を。',
        excerpt=u'2025年のノーベル物理学賞は、1984年の電気回路の実験に贈られました。'
                u'そこから40年。量子ビットが持つ「矢印」とは何か、'
                u'なぜ普通のコンピュータでは追いつけないのか。'
                u'わかりやすさのために事実を曲げずに、仕組みと原理をご説明します。',
        featured=1,
        images=[
            (u'<h3 class="wp-block-heading has-medium-font-size">'
             u'1984年から、一本の線がつながっています</h3>\n<!-- /wp:heading -->', 2),
            (u'<h3 class="wp-block-heading has-medium-font-size">'
             u'なぜ、普通のコンピュータでは追いつけないのか</h3>\n<!-- /wp:heading -->', 4),
            (u'<h3 class="wp-block-heading has-medium-font-size">'
             u'もうひとつ、圧倒的に得意なことがあります</h3>\n<!-- /wp:heading -->', 3),
        ],
        links=[(u'<li>量子コンピュータとは何か【後編】実用化はいつか、いまどこまで来ているのか（近日公開）</li>',
                u'<li><a href="%s/quantum-computer-02-status/">'
                u'量子コンピュータとは何か【後編】実用化はいつか、いまどこまで来ているのか</a></li>' % SITE)],
    ),
    dict(
        file='article-02.html',
        slug='quantum-computer-02-status',
        title=u'量子コンピュータとは何か【後編】実用化はいつか、いまどこまで来ているのか',
        excerpt=u'作り方は六通りあり、まだ本命が決まっていません。'
                u'何の分野で使えるのか、いつ実用化されるのか、'
                u'そして私たちの暮らしに関わる2035年の話まで。'
                u'確かめられたことと、まだのことを分けてご紹介します。',
        featured=5,
        images=[
            (u'<p class="has-medium-font-size">肥料の原料になるアンモニアは、'
             u'<strong>ハーバー・ボッシュ法</strong>という方法で作られています。'
             u'400〜500度、数百気圧。人類が使う全エネルギーの数パーセントを、'
             u'この工程が使っているとされます。</p>\n<!-- /wp:paragraph -->', 6),
            (u'<p class="has-medium-font-size">ところが、<strong>同じことを常温・常圧で'
             u'やっている生き物がいます。</strong>マメ科の植物の根につく根粒菌です。'
             u'「ニトロゲナーゼ」という酵素が、空気中の窒素からアンモニアを'
             u'作っています。畑をやっている方にはおなじみの話だと思います。</p>\n'
             u'<!-- /wp:paragraph -->', 7),
            (u'<h3 class="wp-block-heading has-medium-font-size">'
             u'「セキュリティのための機械」ではありません</h3>\n<!-- /wp:heading -->', 8),
        ],
        links=[(u'<li>量子コンピュータとは何か【前編】仕組みと原理を。</li>',
                u'<li><a href="%s/quantum-computer-01-mechanism/">'
                u'量子コンピュータとは何か【前編】仕組みと原理を。</a></li>' % SITE)],
    ),
]


def image_block(media, shot):
    """WordPress の画像ブロック。キャプションは一覧と同じ文を使う。"""
    return (
        u'<!-- wp:image {"id":%d,"sizeSlug":"large","linkDestination":"none"} -->\n'
        u'<figure class="wp-block-image size-large">'
        u'<img src="%s" alt="%s" class="wp-image-%d"/>'
        u'<figcaption class="wp-element-caption">%s</figcaption></figure>\n'
        u'<!-- /wp:image -->'
        % (media['id'], shot['url'], shot['alt'], media['id'], shot['caption'])
    )


def build(spec, shots, media_of):
    t = io.open(os.path.join(HERE, spec['file']), encoding='utf-8').read()

    for anchor, n in spec['images']:
        if t.count(anchor) != 1:
            sys.stderr.write(u'× %s：%d番の差し込み先が %d 件（1件でないと止めます）\n'
                             % (spec['file'], n, t.count(anchor)))
            sys.exit(1)
        t = t.replace(anchor, anchor + u'\n\n' + image_block(media_of[n], shots[n]))

    for old, new in spec['links']:
        if t.count(old) != 1:
            sys.stderr.write(u'× %s：差し替えるリンクが %d 件\n' % (spec['file'], t.count(old)))
            sys.exit(1)
        t = t.replace(old, new)
    return t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    import set_media_meta as smm
    auth = smm.auth_header()
    shots = {s['n']: s for s in smm.load_shots()}

    media_of = {}
    for n in range(1, 9):
        md = smm.find_by_url(shots[n]['url'], auth)
        if not md:
            sys.stderr.write(u'× %d番の画像がサイトに見つかりません\n' % n)
            sys.exit(1)
        media_of[n] = md

    for spec in POSTS:
        body = build(spec, shots, media_of)
        print(u'\n=== %s ===' % spec['title'])
        print(u'  スラッグ  : %s' % spec['slug'])
        print(u'  本文      : %d字（ブロック込み）' % len(body))
        print(u'  アイキャッチ: %d番 ID%s' % (spec['featured'], media_of[spec['featured']]['id']))
        print(u'  差し込んだ絵: %s' % u'、'.join(
            u'%d番(ID%s)' % (n, media_of[n]['id']) for _, n in spec['images']))

        if args.dry_run:
            continue

        found = smm.call('/posts?slug=%s&status=draft,publish,pending,private&context=edit'
                         % spec['slug'], auth)
        data = {
            'title': spec['title'],
            'slug': spec['slug'],
            'content': body,
            'excerpt': spec['excerpt'],
            'status': 'draft',
            'categories': CATEGORIES,
            'featured_media': media_of[spec['featured']]['id'],
        }
        if found:
            p = found[0]
            if p['status'] != 'draft':
                print(u'  ! すでに「%s」の記事があります。触りません（ID %s）'
                      % (p['status'], p['id']))
                continue
            del data['status']      # 下書きのまま
            r = smm.call('/posts/%d' % p['id'], auth, data=data)
            print(u'  ○ 下書きを更新しました（ID %s）' % r['id'])
        else:
            r = smm.call('/posts', auth, data=data)
            print(u'  ○ 下書きを作りました（ID %s）' % r['id'])
        print(u'  編集画面  : %s/wp-admin/post.php?post=%s&action=edit' % (SITE, r['id']))


if __name__ == '__main__':
    main()
