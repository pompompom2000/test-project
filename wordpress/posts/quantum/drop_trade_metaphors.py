# -*- coding: utf-8 -*-
"""建設の専門用語を使ったたとえを外す。

高校生が読んで詰まらないようにするため。
外すのは「粒度・締固め・転圧」といった、その業界の人しか
使わない言葉が入っているものだけ。

「橋の設計が六通りあって」は残す。橋は誰でも知っており、
専門用語も入っていないため。

    python3 drop_trade_metaphors.py
"""
from __future__ import print_function

import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

P = u'<!-- wp:paragraph {"fontSize":"medium"} -->\n<p class="has-medium-font-size">%s</p>\n<!-- /wp:paragraph -->'

# (ファイル, 消すもの, 代わりに置くもの。空なら段落ごと消す)
EDITS = [
    ('article-01.html',
     u'砕石で言えば、粒の数を数えても品質はわかりません。'
     u'粒度や締固めの具合を見なければ意味がない。それと似た話です。',
     u''),

    ('article-02.html',
     u'建設の機械にたとえるなら、振動ローラーのようなものだと思います。'
     u'転圧では代わりのきかない働きをしますが、それで柱は立てられません。'
     u'<strong>置き換えではなく、持ち場が違う。</strong>',
     u'<strong>置き換えではなく、持ち場が違う。</strong>'
     u'そう考えるのが、いちばん近いと思います。'),
]


def main():
    n = 0
    for fname, old, new in EDITS:
        path = os.path.join(HERE, fname)
        t = io.open(path, encoding='utf-8').read()
        block_old = P % old
        if block_old not in t:
            print(u'－ %s：すでに外れています' % fname)
            continue
        if t.count(block_old) != 1:
            sys.stderr.write(u'× %s：%d 件\n' % (fname, t.count(block_old)))
            sys.exit(1)
        t = t.replace(block_old, (P % new) if new else u'')
        t = re.sub(r'\n{3,}', '\n\n', t)
        io.open(path, 'w', encoding='utf-8').write(t)
        print(u'○ %s：%s' % (fname, u'段落ごと削除' if not new else u'専門用語を抜いて書き換え'))
        n += 1

    print()
    for f in ('article-01.html', 'article-02.html'):
        s = re.sub(r'<[^>]+>', '', io.open(os.path.join(HERE, f), encoding='utf-8').read())
        left = [w for w in [u'粒度', u'締固め', u'転圧', u'振動ローラー', u'砕石で言えば']
                if w in s]
        print(u'%s に残る建設の専門用語：%s' % (f, u'、'.join(left) if left else u'なし'))
    print(u'\n%d か所 外しました。' % n)


if __name__ == '__main__':
    main()
