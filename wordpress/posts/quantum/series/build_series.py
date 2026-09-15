# -*- coding: utf-8 -*-
"""公開中の二本を材料に、全6回の記事ファイルを組み立てる。

    python3 build_series.py

もとの article-01.html / article-02.html は読むだけで、書き換えない。
出来上がるのは part-1.html 〜 part-6.html。
写真は post_series.py が投稿時に差し込むので、ここでは目印だけ置く。
"""
from __future__ import print_function

import io
import os
import re
import sys

import plan

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)

H3 = (u'<!-- wp:heading {"level":3,"fontSize":"medium"} -->\n'
      u'<h3 class="wp-block-heading has-medium-font-size">%s</h3>\n'
      u'<!-- /wp:heading -->')
P = (u'<!-- wp:paragraph {"fontSize":"medium"} -->\n'
     u'<p class="has-medium-font-size">%s</p>\n<!-- /wp:paragraph -->')
LI = u'<!-- wp:list-item -->\n<li>%s</li>\n<!-- /wp:list-item -->'
UL = (u'<!-- wp:list {"fontSize":"medium"} -->\n'
      u'<ul class="wp-block-list has-medium-font-size">\n%s\n</ul>\n<!-- /wp:list -->')


def cut(path):
    """記事を、書き出し／節／末尾に分ける。"""
    t = io.open(path, encoding='utf-8').read()
    head = t[:t.index('<!-- ISNZ-REL -->')]
    pat = re.compile(r'(<!-- wp:heading[^>]*-->\s*<h3[^>]*>.*?</h3>\s*<!-- /wp:heading -->)', re.S)
    parts = pat.split(head)
    secs = []
    for k in range(1, len(parts), 2):
        secs.append({'head': parts[k],
                     'title': re.sub(r'<[^>]+>', '', parts[k]).strip(),
                     'body': (parts[k + 1] if k + 1 < len(parts) else u'').strip()})
    return secs, t


def main():
    A, rawA = cut(os.path.join(SRC, 'article-01.html'))
    B, rawB = cut(os.path.join(SRC, 'article-02.html'))
    POOL = {}
    for tag, lst in (('1', A), ('2', B)):
        for i, s in enumerate(lst):
            POOL['%s-%02d' % (tag, i)] = s

    # 出典の箇条書きを全部集める
    srcs = []
    for lst in (A, B):
        for s in lst:
            if u'参考・出典' in s['title']:
                srcs += re.findall(r'<!-- wp:list-item -->\s*(<li>.*?</li>)\s*<!-- /wp:list-item -->',
                                   s['body'], re.S)
    print(u'出典 全%d本' % len(srcs))

    # 第2回の図（打ち消し合い）を、最終回でもう一度使う
    refig = None
    m = re.search(r'<!-- wp:html -->\s*<figure[^>]*>\s*<svg[^>]*aria-label="[^"]*矢印[^"]*"'
                  r'.*?<!-- /wp:html -->', POOL['1-03']['body'], re.S)
    if m:
        refig = m.group(0)

    used_src, fixed = set(), []
    for spec in plan.PARTS:
        out = []

        # ── 書き出し ───────────────────────────────
        for p in spec['lead']:
            out.append(P % p)

        # ── 節 ─────────────────────────────────
        for a, _ in spec.get('body_img', []):
            if a not in spec['secs']:
                sys.exit(u'× 第%d回：写真の目印「%s」がこの回の節にありません'
                         % (spec['n'], a))
        for key in spec['secs']:
            if key not in POOL:
                sys.exit(u'× 節 %s が見つかりません' % key)
            s = POOL[key]
            out.append(s['head'])
            body = s['body']
            for a, z in plan.REWRITE:
                if a in body:
                    body = body.replace(a, z)
                    fixed.append((spec['n'], a[:26]))
            for anchor, num in spec.get('body_img', []):
                if anchor == key:
                    body = u'<!-- ISNZ-PHOTO-%d -->\n\n' % num + body
            out.append(body)

        # 最終回だけ、暗号の話の前に第2回の図をもう一度置く
        if spec.get('refig') and refig:
            out.insert(len(spec['lead']) + 1, refig)

        # ── まとめ ──────────────────────────────
        out.append(H3 % (u'量子コンピュータ%s、まとめ（第%d回）'
                         % ({1: u'とは', 2: u'はなぜ速いのか', 3: u'の誤解',
                             4: u'の現状', 5: u'の用途', 6: u'と暗号'}[spec['n']], spec['n'])))
        out.append(UL % u'\n'.join(LI % plan.BULLETS[b] for b in spec['matome']))
        out.append(P % spec['matome_end'])
        out.append(P % (u'本稿は執筆時点（2026年9月）の情報です。この分野は動きが速く、'
                        u'内容は変わっていきます。下記の出典元で最新の情報をご確認ください。'))

        # ── 参考・出典 ───────────────────────────
        picked = []
        for mark in spec['src']:
            hit = [x for x in srcs if mark in x]
            if not hit:
                sys.exit(u'× 第%d回：出典の目印「%s」に当たるものがありません' % (spec['n'], mark))
            for x in hit:
                if x not in picked:
                    picked.append(x)
                    used_src.add(x)
        out.append(H3 % u'参考・出典')
        out.append(UL % u'\n'.join(LI % re.sub(r'^<li>|</li>$', '', x) for x in picked))

        body = u'\n\n'.join(out) + u'\n'
        path = os.path.join(HERE, 'part-%d.html' % spec['n'])
        io.open(path, 'w', encoding='utf-8').write(body)

        txt = re.sub(r'\s+', '', re.sub(r'<[^>]+>', '',
                     re.sub(r'<svg.*?</svg>|<!--.*?-->', '', body, flags=re.S)))
        print(u'○ 第%d回 %-30s 本文%5d字 図%d 出典%2d本'
              % (spec['n'], spec['slug'], len(txt), body.count('<svg'), len(picked)))

    print(u'\n回をまたいだ言い回しの直し %d件' % len(fixed))
    for n, s in fixed:
        print(u'   第%d回  %s…' % (n, s))
    if len(fixed) != len(plan.REWRITE):
        sys.stderr.write(u'× 直しの表 %d件のうち %d件しか当たっていません\n'
                         % (len(plan.REWRITE), len(fixed)))
        sys.exit(1)

    left = [x for x in srcs if x not in used_src]
    print(u'\n使わなかった出典 %d本' % len(left))
    for x in left:
        print(u'   %s' % re.sub(r'\s+', ' ', re.sub('<[^>]+>', '', x))[:88])


if __name__ == '__main__':
    main()
