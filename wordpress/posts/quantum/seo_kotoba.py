# -*- coding: utf-8 -*-
"""狙う言葉が抜けている場所に、言葉を入れる。

All in One SEO が見ている場所のうち、照合して抜けていたところだけを直す。
語を詰め込むのではなく、もともと書いてある内容を言い直すだけにする。

  前編（量子コンピュータ 仕組み）
    ・見出しに「仕組み」が1本もない → まとめの見出しに入れる
  後編（量子コンピュータ 実用化）
    ・題名に「実用化」がない     → post_drafts.py の題名を直す
    ・書き出しに「実用化」がない  → 三段目の言い方を変える
    ・見出しに全語そろったものがない → まとめの見出しに入れる

画像のaltは触らない。いまのaltは絵の中身を正確に説明しており、
そこへ狙う言葉を入れると説明が不正確になるため。

    python3 seo_kotoba.py

二度流しても重ならない。直す先が1件でなければ止める。
"""
from __future__ import print_function

import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

EDITS = [
    # ── 前編：まとめの見出しに「仕組み」を入れる ───────────────
    ('article-01.html',
     u'<h3 class="wp-block-heading has-medium-font-size">まとめ（前編）</h3>',
     u'<h3 class="wp-block-heading has-medium-font-size">'
     u'量子コンピュータの仕組み、まとめ（前編）</h3>'),

    # ── 後編：書き出しに「実用化」を入れる ─────────────────
    ('article-02.html',
     u'後編では、<strong>いまどこまで来ているのか</strong>を見ていきます。',
     u'後編では、<strong>実用化がいまどこまで来ているのか</strong>を見ていきます。'),

    # ── 後編：まとめの見出しに全語を入れる ─────────────────
    ('article-02.html',
     u'<h3 class="wp-block-heading has-medium-font-size">まとめ（後編）</h3>',
     u'<h3 class="wp-block-heading has-medium-font-size">'
     u'量子コンピュータの実用化、まとめ（後編）</h3>'),

    # ── 後編：題名に「実用化」を入れる ───────────────────
    ('post_drafts.py',
     u"title=u'量子コンピュータとは何か【後編】いまどこまで来ているのか',",
     u"title=u'量子コンピュータとは何か【後編】実用化はいつか、いまどこまで来ているのか',"),
]


def main():
    n = 0
    for fname, old, new in EDITS:
        path = os.path.join(HERE, fname)
        t = io.open(path, encoding='utf-8').read()
        if old not in t and new in t:
            print(u'－ %s：すでに入っています（%s…）' % (fname, new[:22]))
            continue
        if t.count(old) != 1:
            sys.stderr.write(u'× %s：直す先が %d 件\n  %s\n' % (fname, t.count(old), old[:50]))
            sys.exit(1)
        io.open(path, 'w', encoding='utf-8').write(t.replace(old, new))
        print(u'○ %s：%s' % (fname, new[:40]))
        n += 1
    print(u'\n%d か所 直しました。' % n)


if __name__ == '__main__':
    main()
