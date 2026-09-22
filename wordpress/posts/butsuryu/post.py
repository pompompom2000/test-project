# -*- coding: utf-8 -*-
u"""総合物流施策大綱の記事を、下書きとして投稿する。

    IZK_AUTH='ai-agent:xxxx ...' python3 post.py --dry-run
    IZK_AUTH='ai-agent:xxxx ...' python3 post.py

  決めごと（quantum連載の post_series.py と同じ）
  ・鍵は環境変数からしか読まない。標準出力にも出さない。
  ・status は draft 固定。このスクリプトから公開することはできない。
  ・公開済みの記事には触れない。
  ・CTAと前後ナビの骨組みは、公開済みの記事からそのまま借りる。
"""
from __future__ import print_function
import argparse, base64, io, json, os, re, sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
POSTS = os.path.dirname(HERE)
SITE = 'https://www.ishinazaka.co.jp'
API = SITE + '/wp-json/wp/v2'
CATEGORIES = [1, 10]

SLUG = 'butsuryu-taiko-2026'
TITLE = u' 総合物流施策大綱 とは？国が決めた物流の5年計画を、やさしく解説'
DESC = (u'2026年3月31日に閣議決定された「総合物流施策大綱（2026年度〜2030年度）」を、'
        u'はじめての方にもわかるようにご紹介します。輸送力不足34%と14%の意味、5つの柱、'
        u'2030年の目標を、盛岡でダンプを持つ側から見た話も交えて。')
PREV = '/quantum-computer-06-cryptography/'   # いま最新の記事
AWASETE = [
    'kensetsugyo-unso-kyoka-koushin',
    'kaisei-kamotsu',
    'industrial-waste-contract',
]

UP = SITE + '/common/files/uploads/2026/04'
PREV_IMG = UP + '/%E5%89%8D%E3%81%AE%E8%A8%98%E4%BA%8B%E3%81%B8-e1776822939829.png'
LIST_IMG = UP + '/%E6%88%BB%E3%82%8B%E3%83%9C%E3%82%BF%E3%83%B32-e1776823039293.png'

SPACER = (u'<!-- wp:spacer {"height":"40px"} -->\n'
          u'<div style="height:40px" aria-hidden="true" class="wp-block-spacer"></div>\n'
          u'<!-- /wp:spacer -->')
H3 = (u'<!-- wp:heading {"level":3} -->\n'
      u'<h3 class="wp-block-heading">%s</h3>\n<!-- /wp:heading -->')
LI = u'<!-- wp:list-item -->\n<li>%s</li>\n<!-- /wp:list-item -->'
UL = u'<!-- wp:list -->\n<ul class="wp-block-list">\n%s\n</ul>\n<!-- /wp:list -->'


def auth_header():
    v = os.environ.get('IZK_AUTH')
    if not v:
        raise SystemExit(u'環境変数 IZK_AUTH が空です。')
    return 'Basic ' + base64.b64encode(v.encode('utf-8')).decode('ascii')


def call(path, auth, data=None):
    body = json.dumps(data).encode('utf-8') if data is not None else None
    h = {'Authorization': auth}
    if body:
        h['Content-Type'] = 'application/json'
    q = urllib.request.Request(API + path, data=body, headers=h)
    with urllib.request.urlopen(q, timeout=90) as r:
        return json.loads(r.read().decode('utf-8'))


def column(inner=u'', last=False):
    tail = u'</div>\n<!-- /wp:column -->'
    if last:
        tail += u'</div>\n<!-- /wp:columns -->'
    return u'<!-- wp:column -->\n<div class="wp-block-column">%s%s' % (inner, tail)


def nav():
    u"""前の記事へだけ。いちばん新しい記事なので「次の記事へ」は置かない。"""
    left = (u'<!-- wp:image {"lightbox":{"enabled":false},"id":1730,"width":"100px",'
            u'"sizeSlug":"full","linkDestination":"custom"} -->\n'
            u'<figure class="wp-block-image size-full is-resized">'
            u'<a href="%s%s"><img src="%s" alt="前の記事へ" '
            u'class="wp-image-1730" style="width:100px;height:auto"/></a></figure>\n'
            u'<!-- /wp:image -->' % (SITE, PREV, PREV_IMG))
    return u'\n'.join([
        SPACER, u'',
        u'<!-- wp:columns {"isStackedOnMobile":false} -->',
        u'<div class="wp-block-columns is-not-stacked-on-mobile">' + column(left),
        u'', column(), u'', column(u'', last=True),
        u'', SPACER, u'',
        u'<!-- wp:image {"lightbox":{"enabled":false},"id":1361,"sizeSlug":"full",'
        u'"linkDestination":"custom"} -->',
        u'<figure class="wp-block-image size-full">'
        u'<a href="%s/category/information/"><img src="%s" alt="お知らせ一覧へ" '
        u'class="wp-image-1361"/></a></figure>' % (SITE, LIST_IMG),
        u'<!-- /wp:image -->'])


def awasete(auth):
    u"""あわせて読みたい。題名はサイトから取ってくる（書き写し間違いを防ぐため）。"""
    rows = []
    for slug in AWASETE:
        found = call('/posts?slug=%s&status=publish&context=edit' % slug, auth)
        if not found:
            sys.exit(u'× あわせて読みたい：%s が見つかりません' % slug)
        t = re.sub(r'\s+', ' ', found[0]['title']['raw']).strip()
        rows.append(u'<a href="%s/%s/">%s</a>' % (SITE, slug, t))
    return (H3 % u'あわせて読みたい') + u'\n\n' + (UL % u'\n'.join(LI % x for x in rows))


CTA_MOTO = 'industrial-waste-contract'   # 運搬の話なので、産廃書面化の記事から借りる


def cta(auth):
    u"""CTAは公開中の記事からそのまま借りる（いま出ている形と確実にそろえるため）。"""
    found = call('/posts?slug=%s&status=publish&context=edit' % CTA_MOTO, auth)
    if not found:
        sys.exit(u'× CTAの借り元 %s が見つかりません' % CTA_MOTO)
    t = found[0]['content']['raw']
    i = t.index('<!-- ISNZ-CTA -->')
    j = t.index('<!-- wp:spacer {"height":"40px"} -->', i)
    return t[i:j].rstrip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    auth = auth_header()

    body = io.open(os.path.join(HERE, 'honbun.html'), encoding='utf-8').read().rstrip()
    full = u'\n\n'.join([body, u'<!-- ISNZ-REL -->', awasete(auth), cta(auth), nav()])

    mieru = re.sub(r'\s+', '', re.sub(r'<[^>]+>', '',
                   re.sub(r'<svg.*?</svg>|<!--.*?-->', '', full, flags=re.S)))
    print(u'題名      : %s（%d字）' % (TITLE, len(TITLE.strip())))
    print(u'スラッグ  : %s' % SLUG)
    print(u'本文      : %d字（末尾まで含めた、表示される文字）' % len(mieru))
    print(u'前の記事へ: %s' % PREV)
    for k in ('<!-- ISNZ-REL -->', '<!-- ISNZ-CTA -->', '019-638-7521',
              '/contact/', u'前の記事へ', u'お知らせ一覧へ'):
        print(u'  %-22s %s' % (k, u'あり' if k in full else u'【ありません】'))

    if args.dry_run:
        io.open(os.path.join(HERE, 'full-preview.html'), 'w', encoding='utf-8').write(full)
        print(u'\n下見はここまで。full-preview.html に書き出しました。')
        return

    found = call('/posts?slug=%s&status=draft,publish,pending,private&context=edit' % SLUG, auth)
    data = {'title': TITLE, 'slug': SLUG, 'content': full,
            'excerpt': DESC, 'categories': CATEGORIES}
    if found:
        p = found[0]
        if p['status'] != 'draft':
            raise SystemExit(u'× すでに「%s」の記事があります。触りません（ID %s）'
                             % (p['status'], p['id']))
        r = call('/posts/%d' % p['id'], auth, data=data)
        print(u'\n○ 下書きを更新しました（ID %s）' % r['id'])
    else:
        data['status'] = 'draft'
        r = call('/posts', auth, data=data)
        print(u'\n○ 下書きを作りました（ID %s）' % r['id'])
    print(u'  編集画面: %s/common/sys/wp-admin/post.php?post=%s&action=edit' % (SITE, r['id']))


if __name__ == '__main__':
    main()
