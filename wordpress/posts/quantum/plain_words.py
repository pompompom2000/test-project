# -*- coding: utf-8 -*-
"""説明なしで出てくる言葉に、短い言い換えを足す。

高校生が読んで詰まらないようにするため。本文の主張は変えない。
足すのは括弧の中か、一文だけ。二度流しても重ならない。

    python3 plain_words.py
"""
from __future__ import print_function

import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

EDITS = [
    # ── 前編 ───────────────────────────────────────────────
    ('article-01.html',
     u'長さは「その答えが出やすいかどうか」を、向きは「位相」と呼ばれるものを表します。',
     u'長さは「その答えが出やすいかどうか」を、向きは「位相」と呼ばれるものを表します。'
     u'位相という名前は、覚えなくて結構です。<strong>大事なのは「向きがある」ということ'
     u'だけ</strong>です。'),

    ('article-01.html',
     u'決められないものは、合図に使えません。相関があるとわかるのは、'
     u'あとで普通の通信で結果を突き合わせたときです。',
     u'決められないものは、合図に使えません。'
     u'<strong>二人の目が揃っていたとわかるのは、あとで電話やメールなど'
     u'普通の方法で結果を見せ合ったとき</strong>です。'),

    ('article-01.html',
     u'だから化学の計算は、いまでも近似に頼っています。',
     u'だから化学の計算は、いまでも近似——おおよその値で済ませるやり方——に'
     u'頼っています。'),

    ('article-01.html',
     u'後編で、この「分子と材料のシミュレーション」が、',
     u'後編で、この「分子と材料のシミュレーション」——計算で分子の'
     u'ふるまいを真似ること——が、'),

    # ── 後編 ───────────────────────────────────────────────
    ('article-02.html',
     u'作り直しが必要なのは、インターネットの通信などに使う「公開鍵暗号」のほうです。'
     u'もうひとつの「共通鍵暗号」は、鍵を長くすれば当面は大丈夫とされています。',
     u'作り直しが必要なのは、インターネットの通信などに使う'
     u'<strong>「公開鍵暗号」</strong>——鍵を二つに分け、片方を誰にでも見える形で'
     u'配る方式——のほうです。もうひとつの<strong>「共通鍵暗号」</strong>——'
     u'送る側と受け取る側が同じ鍵を使う方式——は、鍵を長くすれば当面は'
     u'大丈夫とされています。'),

    ('article-02.html',
     u'最初の用途は<strong>触媒の探索</strong>だろうと見られています。',
     u'最初の用途は<strong>触媒の探索</strong>——化学反応を助ける物質を'
     u'探すこと——だろうと見られています。'),
]


def main():
    done = 0
    for fname, old, new in EDITS:
        path = os.path.join(HERE, fname)
        t = io.open(path, encoding='utf-8').read()
        if new in t:
            print(u'－ %s：すでに直っています' % fname)
            continue
        if t.count(old) != 1:
            sys.stderr.write(u'× %s：直す先が %d 件（1件でないと止めます）\n  %s\n'
                             % (fname, t.count(old), old[:40]))
            sys.exit(1)
        io.open(path, 'w', encoding='utf-8').write(t.replace(old, new))
        print(u'○ %s：%s …' % (fname, old[:26]))
        done += 1
    print(u'\n%d か所 直しました。' % done)


if __name__ == '__main__':
    main()
