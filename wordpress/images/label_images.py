# -*- coding: utf-8 -*-
"""生成した挿絵に、日本語の見出しを焼き込む。

生成AIに文字を描かせると日本語が崩れる。だから絵は文字なしで作らせ、
文字は**あとからこちらで正確に入れる**。

使い方：
    python3 label_images.py            # URLが登録済みのものを全部
    python3 label_images.py 1 2        # 番号を指定
    python3 label_images.py 1 --no-callouts

出来上がりは labeled/NN-slug.jpg。これをWordPressにアップロードする。

入れるもの：
  ・下の帯に「見出し」と「ひとこと」
  ・右上に「イメージ図」の札（実物の写真と誤認させないため）
  ・必要なら、絵の中の部位を指す引き出し線
"""
from __future__ import print_function

import argparse
import io
import os
import sys
import urllib.request

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, 'labeled')
CACHE = os.path.join(HERE, '.src-cache')
FONT = '/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf'

INK = (28, 33, 36)
PAPER = (250, 251, 251)
COPPER = (193, 128, 58)
GREY = (168, 178, 183)

# 番号 → 焼き込む文字。座標は元画像（2560x1429）を基準にした割合で指定する。
# callouts: (指す点x, 指す点y, 文字の位置x, 文字の位置y, 文字, 右寄せか)
LABELS = {
    1: dict(
        head=u'量子コンピュータを冷やす装置',
        sub=u'超電導方式の希釈冷凍機。すべての方式がこうなっているわけではありません',
        callouts=[
            (0.400, 0.392, 0.075, 0.150, u'銅の円盤', False),
            (0.462, 0.770, 0.075, 0.880, u'同軸ケーブル', False),
            (0.677, 0.489, 0.780, 0.220, u'真空の容器', False),
        ],
    ),
    2: dict(
        head=u'量子ビットを載せたチップ',
        sub=u'十字の形がひとつの量子ビット。1999年にNECが作った回路の子孫にあたります',
        callouts=[
            (0.313, 0.450, 0.235, 0.240, u'量子ビットの電極', True),
            (0.204, 0.634, 0.140, 0.800, u'金の細線', True),
        ],
    ),
    3: dict(
        head=u'分子の中の電子も「矢印」を持つ',
        sub=u'だから量子の機械と相性がよい。普通のコンピュータでは追えなくなります',
        callouts=[
            (0.382, 0.651, 0.055, 0.800, u'向きがばらばら', False),
            (0.636, 0.358, 0.945, 0.200, u'向きが揃っている', True),
        ],
    ),
    4: dict(
        head=u'50量子ビットを普通のコンピュータで',
        sub=u'再現するのに1ペタバイトを超えるメモリが要りました',
        callouts=[
            # 頼んでいない矢印が天井に出てきた。記事では矢印は
            # 「量子ビットの矢印」を指す言葉なので、放っておくと誤解を招く。
            # 記事の趣旨どおりの意味を与えて回収する。
            (0.470, 0.150, 0.045, 0.105, u'矢印を数で覚える', False),
        ],
        trim=True,  # 生成りの枠が付いて出てきたので切る
    ),
    5: dict(
        head=u'作り方は、まだ決まっていない',
        # 記事は六方式を挙げているが、絵に描かれているのは四つ。
        # 「六つが並んでいます」と書くと絵と合わないので、そう書かない。
        sub=u'六つあるうちの四つ。三十年以上研究されて、まだ本命が決まっていません',
        callouts=[
            (0.132, 0.537, 0.032, 0.920, u'超電導', False),
            (0.355, 0.430, 0.255, 0.075, u'原子・イオン', False),
            (0.620, 0.430, 0.575, 0.095, u'光', False),
            (0.855, 0.500, 0.800, 0.150, u'シリコン', False),
        ],
    ),
    6: dict(
        head=u'工場は 400〜500度・数百気圧',
        sub=u'アンモニアを作るのに、人類が使う全エネルギーの数パーセントを使います',
        # 塔のどれが反応器かは絵から判じられないので、指さない。
        # 見出しの数字と、7番との対比が伝えるべきことを伝えている。
        callouts=[],
        trim=True,  # 生成りの枠が付いて出てきたので切る
    ),
    7: dict(
        head=u'根粒は 常温・常圧',
        sub=u'同じことを土の中でやっています。そのしくみは、まだ解明されていません',
        # 根粒を見たことのない人が多い。名前と、切った中身の色を指す。
        callouts=[
            (0.365, 0.303, 0.055, 0.270, u'根粒', False),
            (0.636, 0.296, 0.955, 0.420, u'切ると中は赤い', True),
        ],
    ),
    8: dict(
        head=u'量子コンピュータは暗号を「壊す側」',
        sub=u'国は2035年を目処に、錠前の付け替えを進めています',
        callouts=[],
    ),
}


def load_shots():
    import importlib.util  # noqa: F401
    path = os.path.join(HERE, '..', 'docs', 'build_gazou_seo.py')
    src = io.open(path, encoding='utf-8').read()
    ns = {}
    exec(compile(src[src.index('SHOTS = ['):src.index('FIELDS = [')], path, 'exec'), ns)
    return {s['n']: s for s in ns['SHOTS']}


def fetch(url):
    if not os.path.isdir(CACHE):
        os.makedirs(CACHE)
    key = os.path.join(CACHE, url.rsplit('/', 1)[-1])
    if not os.path.exists(key):
        with urllib.request.urlopen(url, timeout=90) as r:
            open(key, 'wb').write(r.read())
    return Image.open(key).convert('RGB')


def trim_border(im):
    """絵のまわりの生成りの枠を切り落とす。

    自動判定はしない。背景そのものが生成りの絵（3番など）を
    壊してしまうため、LABELS に trim=True と書いたものだけに使う。
    """
    w, h = im.size
    px = im.convert('RGB').load()

    def paper(x, y):
        r, g, b = px[x, y]
        return (r + g + b) / 3.0 > 235 and (max(r, g, b) - min(r, g, b)) < 22

    def ratio_row(y):
        xs = range(0, w, 8)
        return sum(1 for x in xs if paper(x, y)) / float(len(xs))

    def ratio_col(x):
        ys = range(0, h, 8)
        return sum(1 for y in ys if paper(x, y)) / float(len(ys))

    def first(rng, f):
        for i in rng:
            if f(i) < 0.5:
                return i
        return None

    top = first(range(h), ratio_row)
    bot = first(range(h - 1, -1, -1), ratio_row)
    left = first(range(w), ratio_col)
    right = first(range(w - 1, -1, -1), ratio_col)
    if None in (top, bot, left, right):
        raise SystemExit(u'枠を切ろうとしましたが、絵の範囲が分かりませんでした。')
    if (left, top, right, bot) == (0, 0, w - 1, h - 1):
        print(u'  枠はありませんでした（切らずに進みます）')
        return im
    im = im.crop((left, top, right + 1, bot + 1))
    print(u'  枠を切りました 上%d 下%d 左%d 右%d → %dx%d'
          % (top, h - 1 - bot, left, w - 1 - right, im.size[0], im.size[1]))

    # 枠の幅は上下左右で揃っていないので、切っただけでは 16:9 からずれる。
    # ほかの絵と形が違うと、記事に並べたとき背の高さがまちまちになる。
    iw, ih = im.size
    tw, th = (int(round(ih * 16 / 9.0)), ih) if iw / float(ih) > 16 / 9.0 \
        else (iw, int(round(iw * 9 / 16.0)))
    if (tw, th) != (iw, ih):
        x, y = (iw - tw) // 2, (ih - th) // 2
        im = im.crop((x, y, x + tw, y + th))
        print(u'  16:9 に切り揃えました → %dx%d' % im.size)

    # ほかの絵と大きさを揃える
    if im.size[0] != w:
        im = im.resize((w, int(round(w * im.size[1] / float(im.size[0])))), Image.LANCZOS)
        print(u'  ほかの絵に合わせて %dx%d に拡大' % im.size)
    return im


def bold(draw, xy, text, font, fill, weight=1):
    """そのまま描く。

    以前は少しずらして重ね描きして太く見せていたが、「量」のように
    横線の多い字は隙間が埋まって潰れる。太らせず、字を大きくして読ませる。
    """
    draw.text(xy, text, font=font, fill=fill)


def draw_callout(d, im, c, f_small):
    w, h = im.size
    tx, ty = c[0] * w, c[1] * h
    lx, ly = c[2] * w, c[3] * h
    right = c[5]
    label = c[4]

    tw = d.textlength(label, font=f_small)
    pad = int(h * 0.011)
    bw, bh = tw + pad * 2, f_small.size + pad * 2
    bx = lx - bw if right else lx
    by = ly - bh / 2.0

    # 引き出し線：指す点に近いほうの辺から出す
    edge_x = bx if tx < bx + bw / 2.0 else bx + bw
    anchor = (edge_x, by + bh / 2.0)
    d.line([anchor, (tx, ty)], fill=COPPER, width=max(2, int(h * 0.0022)))
    r = max(4, int(h * 0.005))
    d.ellipse([tx - r, ty - r, tx + r, ty + r], fill=COPPER)

    # 札
    d.rectangle([bx, by, bx + bw, by + bh], fill=PAPER, outline=COPPER,
                width=max(2, int(h * 0.0016)))
    bold(d, (bx + pad, by + pad - f_small.size * 0.08), label, f_small, INK)


def label_one(shot, spec, no_callouts=False):
    im = fetch(shot['url'])
    # 帯を足した絵は 16:9 ではなくなる。それをもう一度食わせると
    # 帯が二重になり、引き出し線の座標も全部ずれる。ここで止める。
    # 枠を切る前に見ること。切ったあとの比は当てにならない。
    w, h = im.size
    if abs(w / float(h) - 16 / 9.0) > 0.03:
        raise SystemExit(
            u'%d番：もとの絵が 16:9 ではありません（%dx%d、比 %.3f）。\n'
            u'すでに文字を焼き込んだ絵を指していませんか。\n'
            u'SHOTS の url を、文字を入れる前の絵に戻してください。'
            % (shot['n'], w, h, w / float(h)))
    if spec.get('trim'):
        im = trim_border(im)
    w, h = im.size
    band_h = max(120, int(h * 0.125))
    out = Image.new('RGB', (w, h + band_h), INK)
    out.paste(im, (0, 0))
    d = ImageDraw.Draw(out)

    f_head = ImageFont.truetype(FONT, int(band_h * 0.37))
    f_sub = ImageFont.truetype(FONT, int(band_h * 0.215))
    f_tag = ImageFont.truetype(FONT, int(h * 0.024))
    f_call = ImageFont.truetype(FONT, int(h * 0.030))

    # 右上：イメージ図の札（実物の写真と誤認させない）
    tag = u'イメージ図'
    tw = d.textlength(tag, font=f_tag)
    pad = int(h * 0.012)
    m = int(h * 0.028)
    d.rectangle([w - m - tw - pad * 2, m, w - m, m + f_tag.size + pad * 2], fill=COPPER)
    bold(d, (w - m - tw - pad, m + pad - f_tag.size * 0.08), tag, f_tag, PAPER)

    # 引き出し線
    if not no_callouts:
        for c in spec.get('callouts', []):
            draw_callout(d, im, c, f_call)

    # 下の帯
    bar = int(w * 0.006)
    left = int(w * 0.030)
    d.rectangle([left, h + int(band_h * 0.20), left + bar, h + int(band_h * 0.80)],
                fill=COPPER)
    tx = left + bar + int(w * 0.026)
    bold(d, (tx, h + int(band_h * 0.17)), spec['head'], f_head, PAPER, weight=3)
    d.text((tx, h + int(band_h * 0.585)), spec['sub'], font=f_sub, fill=GREY)

    if not os.path.isdir(OUTDIR):
        os.makedirs(OUTDIR)
    path = os.path.join(OUTDIR, shot['fname'])
    out.save(path, 'JPEG', quality=88, optimize=True)
    return path, out.size, os.path.getsize(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('nums', nargs='*', type=int)
    ap.add_argument('--no-callouts', action='store_true')
    args = ap.parse_args()

    shots = load_shots()
    targets = args.nums or sorted(shots)
    made = 0
    for n in targets:
        s = shots.get(n)
        if not s or not s['url']:
            print(u'%d番：まだアップロードされていません' % n)
            continue
        spec = LABELS.get(n)
        if not spec:
            print(u'%d番：焼き込む文字が未設定です' % n)
            continue
        path, size, nbytes = label_one(s, spec, args.no_callouts)
        print(u'%d番 ○ %s  %dx%d  %.2f MB'
              % (n, os.path.basename(path), size[0], size[1], nbytes / 1048576.0))
        made += 1
    if made:
        print(u'\n%s に出力しました。' % OUTDIR)
        print(u'目で見て、文字の位置と引き出し線がおかしくないか確かめてください。')


if __name__ == '__main__':
    main()
