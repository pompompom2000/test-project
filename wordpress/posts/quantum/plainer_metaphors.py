# -*- coding: utf-8 -*-
"""たとえを、もっと身近なものに替える。

・音叉 → ブランコ
  理屈は同じ（合った調子だけ力が積み上がる）が、ブランコは
  誰でも体で知っている。音叉は見たことのない人が多い。
・橋の設計のたとえ → なくす

    python3 plainer_metaphors.py
"""
from __future__ import print_function

import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

EDITS = [
    # ── 音叉 → ブランコ ───────────────────────────────────
    ('article-01.html',
     u'音叉を思い浮かべてください。ある高さの音を出すと、'
     u'同じ高さに合わせた音叉だけが共鳴して鳴りだします。それ以外の音には'
     u'反応しません。同じ調子の振動が重なったときだけ、揺れが積み上がるからです。',
     u'ブランコを思い浮かべてください。<strong>ちょうどよい間隔で押してやると、'
     u'どんどん高くなります。</strong>ところが、でたらめな調子で押すと、'
     u'かえって止まってしまう。押した力どうしが、打ち消し合うからです。'),

    ('article-01.html',
     u'矢印の足し算も同じです。<strong>隠れた繰り返しの周期にぴったり合ったときだけ、'
     u'矢印が揃って合計が大きくなります。</strong>ずれていれば、矢印はばらけて消えます。'
     u'量子コンピュータは、この「共鳴する周期」を探し当てるのが、飛び抜けて得意なのです。',
     u'矢印の足し算も、これと同じです。<strong>隠れた繰り返しの周期——'
     u'くり返しの間隔のことです——にぴったり合ったときだけ、矢印が揃って'
     u'合計が大きくなります。</strong>ずれていれば、矢印はばらけて消えます。'
     u'量子コンピュータは、この「ぴったり合う間隔」を探し当てるのが、'
     u'飛び抜けて得意なのです。'),

    ('article-01.html',
     u'音叉の例えも、ここで壊れます。音叉は自分の高さの音にしか反応しませんが、'
     u'量子コンピュータは<strong>候補になる周期を一度にまとめて調べています。</strong>'
     u'そこは音叉より、はるかに贅沢な仕掛けです。',
     u'ブランコのたとえも、ここで壊れます。ブランコは一つの調子にしか合いませんが、'
     u'量子コンピュータは<strong>候補になる間隔を一度にまとめて調べています。</strong>'
     u'そこはブランコより、はるかに贅沢な仕掛けです。'),

    # ── 橋のたとえを外す ──────────────────────────────────
    ('article-02.html',
     u'方式が決まらないというのは、お金を出す側にとっては重い話です。'
     u'橋の設計が六通りあって、どれが正解かまだわからないまま、'
     u'十年以上お金を出し続ける。<strong>そう考えると、この分野に取り組む難しさが'
     u'少し想像できます。</strong>',
     u'方式が決まらないというのは、お金を出す側にとっては重い話です。'
     u'どれが正解かわからないまま、十年以上お金を出し続けることになります。'
     u'<strong>そう考えると、この分野に取り組む難しさが少し想像できます。</strong>'),
]


def main():
    n = 0
    for fname, old, new in EDITS:
        path = os.path.join(HERE, fname)
        t = io.open(path, encoding='utf-8').read()
        if old not in t and new in t:
            print(u'－ %s：すでに直っています（%s…）' % (fname, old[:18]))
            continue
        if t.count(old) != 1:
            sys.stderr.write(u'× %s：直す先が %d 件\n  %s\n' % (fname, t.count(old), old[:44]))
            sys.exit(1)
        io.open(path, 'w', encoding='utf-8').write(t.replace(old, new))
        print(u'○ %s：%s…' % (fname, old[:24]))
        n += 1

    print()
    for f in ('article-01.html', 'article-02.html'):
        s = io.open(os.path.join(HERE, f), encoding='utf-8').read()
        left = [w for w in [u'音叉', u'橋の設計', u'共鳴'] if w in s]
        print(u'%s に残る言葉：%s' % (f, u'、'.join(left) if left else u'なし'))
    print(u'\n%d か所 直しました。' % n)


if __name__ == '__main__':
    main()
