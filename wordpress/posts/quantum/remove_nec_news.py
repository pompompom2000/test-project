# -*- coding: utf-8 -*-
"""NECの開発中止の報道に触れている部分を、記事から外す。

外すのは「2026年の開発中止の報道」だけ。
「1999年に量子ビットを世界初で実現した」という功績と、
1984年からの一本の線は残す。そこは記事の背骨であり、
他社の経営判断に触れる話ではないため。

書き出しは、中止の報道の代わりに2025年のノーベル物理学賞から始める。
賞は公表された事実で、1984年の実験が受賞対象なので、
そのまま「一本の線」の節につながる。

    python3 remove_nec_news.py

二度流しても重ならない。外す先が1件でなければ止める。
"""
from __future__ import print_function

import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

P = u'<!-- wp:paragraph {"fontSize":"medium"} -->\n<p class="has-medium-font-size">%s</p>\n<!-- /wp:paragraph -->'

# ── 前編の書き出しを差し替える ───────────────────────────────
OPENING_OLD = u'\n\n'.join([
    P % (u'2026年9月、ひとつのニュースが流れました。NECが量子コンピュータの実機の開発を'
         u'取りやめた、と報じられたのです。'),
    P % (u'NECは、いまIBMやGoogleが使っている量子コンピュータの、いちばん基礎になる部品を'
         u'世界で初めて作った会社です。その会社が、機械そのものを作ることから降りた。'),
    P % (u'このニュースをきっかけに、「そもそも量子コンピュータとは何なのか」を'
         u'調べてみました。前編では<strong>どういう仕組みで動き、なぜ普通のコンピュータより'
         u'速いのか</strong>を、後編では<strong>いまどこまで来ているのか</strong>を'
         u'ご紹介します。'),
])

OPENING_NEW = u'\n\n'.join([
    P % (u'2025年のノーベル物理学賞は、1984年から85年にかけて行われた、'
         u'ある電気回路の実験に贈られました。'),
    P % (u'その実験から40年。<strong>いまIBMやGoogleが動かしている量子コンピュータの、'
         u'いちばん基礎になる部品は、そこから一本の線でつながっています。</strong>'),
    P % (u'これを機に、「そもそも量子コンピュータとは何なのか」を調べてみました。'
         u'前編では<strong>どういう仕組みで動き、なぜ普通のコンピュータより速いのか'
         u'</strong>を、後編では<strong>いまどこまで来ているのか</strong>を'
         u'ご紹介します。'),
])


def find_block(t, start_key, end_key):
    """start_key を含むブロックの頭から、end_key を含むブロックの尻尾までを返す。"""
    i = t.index(start_key)
    s = t.rfind('<!-- wp:', 0, i)
    j = t.index(end_key)
    e = t.index('-->', t.index('<!-- /wp:', j)) + 3
    return s, e


def drop_list_items(t, marks):
    """出典の箇条書きを、目印で消す。"""
    out, n = t, 0
    for mark in marks:
        pat = re.compile(r'<!-- wp:list-item -->\s*<li>(?:(?!</li>).)*?'
                         + re.escape(mark) + r'.*?</li>\s*<!-- /wp:list-item -->\s*', re.S)
        out, k = pat.subn('', out)
        n += k
    return out, n


def main():
    changed = 0

    # ═══ 前編 ═══
    p1 = os.path.join(HERE, 'article-01.html')
    t = io.open(p1, encoding='utf-8').read()

    if OPENING_NEW in t:
        print(u'－ 前編：すでに書き出しが差し替わっています')
    else:
        if t.count(OPENING_OLD) != 1:
            sys.stderr.write(u'× 前編：書き出しが %d 件\n' % t.count(OPENING_OLD))
            sys.exit(1)
        t = t.replace(OPENING_OLD, OPENING_NEW)
        print(u'○ 前編：書き出しをノーベル賞から始まる形に差し替え')
        changed += 1

    # 「まず、ニュースを正確に」の節をまるごと外す
    if u'まず、ニュースを正確に' in t:
        s, e = find_block(t, u'まず、ニュースを正確に</h3>',
                          u'ですのでこの記事では、「NECが撤退した」とは書きません')
        t = t[:s] + t[e:]
        t = re.sub(r'\n{3,}', '\n\n', t)
        print(u'○ 前編：「まず、ニュースを正確に」の節を削除（見出し＋3箇条＋締めの段落）')
        changed += 1
    else:
        print(u'－ 前編：「まず、ニュースを正確に」はすでにありません')

    # 年表の図を外す（build_figures.py で作り直す）
    m = re.search(r'<!-- wp:html -->\s*<figure[^>]*>\s*<svg[^>]*aria-label="1984年から'
                  r'85年のジョセフソン.*?<!-- /wp:html -->', t, re.S)
    if m:
        t = t[:m.start()] + t[m.end():]
        t = re.sub(r'\n{3,}', '\n\n', t)
        print(u'○ 前編：年表の図をいったん外した（2026年の行を抜いて作り直す）')
        changed += 1
    else:
        print(u'－ 前編：年表の図は外れています')

    # 中止を報じた出典3本
    t, n = drop_list_items(t, [u'DGXZQOUC051KF0V00C26A9000000',
                               u'k=2026090700732',
                               u'2609/08/2000001250'])
    if n:
        print(u'○ 前編：中止を報じた出典を %d 本 削除' % n)
        changed += 1

    io.open(p1, 'w', encoding='utf-8').write(t)

    # ═══ 後編 ═══
    p2 = os.path.join(HERE, 'article-02.html')
    t = io.open(p2, encoding='utf-8').read()

    PAIRS = [
        # 「冒頭のNECの話に戻ると」の段落
        (u'冒頭のNECの話に戻ると、報じられている中止の理由のひとつが、まさに'
         u'<strong>「有力な方式が定まらない」</strong>ことでした。橋の設計が六通りあって、'
         u'どれが正解かまだわからないまま、十年以上お金を出し続ける。'
         u'そう考えると、判断の重さが少し想像できます。',
         u'方式が決まらないというのは、お金を出す側にとっては重い話です。'
         u'橋の設計が六通りあって、どれが正解かまだわからないまま、'
         u'十年以上お金を出し続ける。<strong>そう考えると、この分野に取り組む難しさが'
         u'少し想像できます。</strong>'),

        # 見出し
        (u'<h3 class="wp-block-heading has-medium-font-size">'
         u'日本は、降りたわけではありません</h3>',
         u'<h3 class="wp-block-heading has-medium-font-size">'
         u'日本は、どこまで来ているのか</h3>'),

        (u'冒頭のニュースから、「日本は量子から脱落したのか」と受け取る方が'
         u'いるかもしれません。事実は、そうではありません。',
         u'海外の大企業の話ばかりが目につきますが、'
         u'日本の状況もご紹介しておきます。'),

        (u'NECが実機の開発を取りやめたと報じられたのは2026年3月末のことですが、'
         u'<strong>同じ2026年3月26日、理化学研究所と大阪大学は144量子ビットの'
         u'国産機「叡-Ⅱ（えいツー）」の運用を始めています。</strong>'
         u'2023年に公開された64量子ビットの初号機「叡」の後継機です。',
         u'<strong>2026年3月26日、理化学研究所と大阪大学は144量子ビットの'
         u'国産機「叡-Ⅱ（えいツー）」の運用を始めました。</strong>'
         u'2023年に公開された64量子ビットの初号機「叡」の後継機です。'),

        (u'超電導（富士通）、イオントラップ、光（NTTほか）、シリコン（日立製作所）。'
         u'一社が実機づくりから降りたことと、国として降りたことは、別の話です。',
         u'超電導（富士通）、イオントラップ、光（NTTほか）、シリコン（日立製作所）。'),

        # まとめの箇条
        (u'<li>NECが実機開発をやめたと報じられた同じ月に、'
         u'<strong>理研と大阪大学は144量子ビットの国産機を動かし始めています。</strong></li>',
         u'<li>日本も動いています。<strong>2026年3月、理研と大阪大学は144量子ビットの'
         u'国産機を動かし始めました。</strong>六つの方式のうち四つに、'
         u'日本の組織の名前が出てきます。</li>'),
    ]
    for old, new in PAIRS:
        # 「直したあとの文」が「直す前の文」の一部になっていることがある
        # （末尾の一文だけ落とす場合など）。new が見えるだけでは済んだ証拠に
        # ならないので、old が消えていることまで確かめる。
        if old not in t and new in t:
            print(u'－ 後編：すでに直っています（%s…）' % old[:20])
            continue
        if t.count(old) != 1:
            sys.stderr.write(u'× 後編：直す先が %d 件\n  %s\n' % (t.count(old), old[:44]))
            sys.exit(1)
        t = t.replace(old, new)
        print(u'○ 後編：%s…' % old[:26])
        changed += 1

    io.open(p2, 'w', encoding='utf-8').write(t)

    # 残っていないか
    print()
    for f in ('article-01.html', 'article-02.html'):
        s = io.open(os.path.join(HERE, f), encoding='utf-8').read()
        hits = [x for x in re.findall(r'[^。\n]*NEC[^。\n]*。?', re.sub(r'<[^>]+>', '', s)) if x.strip()]
        print(u'%s に残る NEC の記述 %d件' % (f, len(hits)))
        for h in hits:
            print(u'   %s' % h.strip()[:76])
    print(u'\n%d か所 手を入れました。' % changed)


if __name__ == '__main__':
    main()
