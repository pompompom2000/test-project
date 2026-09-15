# -*- coding: utf-8 -*-
"""量子コンピュータ記事の挿絵を、Gemini API で作る。

使い方：
    export GEMINI_API_KEY='...'          # 鍵はここだけ。ファイルには書かない
    python3 gen_images.py --list         # 使えるモデルを一覧（鍵の疎通確認にもなる）
    python3 gen_images.py --dry-run      # 送る中身だけ確認。API は呼ばない
    python3 gen_images.py                # 8枚まとめて作る
    python3 gen_images.py --only 3 7     # 3番と7番だけ作り直す
    python3 gen_images.py --model gemini-3-pro-image

決めごと：
  ・絵に文字を入れさせない。全プロンプトの末尾に禁止文が入っている。
    日本語のキャプションは WordPress 側で付ける。
  ・鍵は環境変数からしか読まない。標準出力にも出さない。
  ・出力は quantum/NN-slug.png。あわせて manifest.md に
    どこに入れるか・キャプション・代替テキストを書き出す。
"""
from __future__ import print_function

import argparse
import base64
import io
import json
import os
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, 'quantum')
API = 'https://generativelanguage.googleapis.com/v1beta'
DEFAULT_MODEL = 'gemini-3.1-flash-image'

# 8枚すべてに付ける画風。ばらばらの絵柄だと記事が散らかるため。
STYLE = (
    u'Editorial illustration for a print magazine. Calm and precise, not flashy. '
    u'Muted palette: slate grey, deep indigo, warm copper, off-white paper ground. '
    u'Soft even light, subtle paper grain, flat shapes with light shading, '
    u'generous empty space. Absolutely no text, no letters, no numbers, no logos, '
    u'no watermarks, no signatures. Aspect ratio 16:9.'
)

SHOTS = [
    dict(
        n=1, slug='reibouki', part=u'前編',
        where=u'冒頭／アイキャッチ',
        scene=u'A tall chandelier-like dilution refrigerator for a superconducting quantum '
              u'computer, seen from a slightly low angle in a quiet empty laboratory. Several '
              u'large circular copper-gold plates stacked horizontally at different heights, '
              u'connected by vertical rods, with dense bundles of thin coaxial cables running '
              u'down between the plates. The lowest stage is smallest. A cylindrical vacuum '
              u'shell is lifted away and visible at the side. No people.',
        caption=u'超電導方式の量子コンピュータを冷やす装置。すべての方式がこうなっているわけでは'
                u'ありません。イメージ図（生成AIで作成）',
    ),
    dict(
        n=2, slug='chip', part=u'前編',
        where=u'「1984年から、一本の線がつながっています」',
        scene=u'Extreme close-up of a small square superconducting quantum processor chip resting '
              u'on a polished copper mount. On the chip surface, a regular grid of symmetric '
              u'cross-shaped metal patterns connected by fine meandering traces. Very thin bond '
              u'wires arc from the chip edge to a surrounding circuit board. Shallow depth of '
              u'field, the far corner slightly soft. No people.',
        caption=u'超電導方式の量子ビットを載せたチップ。1999年にNECが作った回路の子孫にあたります。'
                u'イメージ図（生成AIで作成）',
    ),
    dict(
        n=3, slug='bunshi', part=u'前編', arrows=True,
        where=u'「もうひとつ、圧倒的に得意なことがあります」',
        scene=u'A single small molecule floating in empty space: five or six simple spheres joined '
              u'by short straight rods, arranged in three dimensions. Around and between the '
              u'spheres, soft translucent grey clouds suggest where electrons might be. Scattered '
              u'through those clouds, many small copper-colored directional arrows point in many '
              u'different directions, like iron filings. Some arrows in one region line up '
              u'together and point the same way. Clean off-white background. No people.',
        caption=u'分子の中の電子も「矢印」を持っています。だから量子の機械と相性がよいのです。'
                u'イメージ図（生成AIで作成）',
    ),
    dict(
        n=4, slug='supercomputer', part=u'前編',
        where=u'「なぜ、普通のコンピュータでは追いつけないのか」',
        scene=u'A long aisle inside a supercomputer hall, seen straight down the middle in '
              u'one-point perspective. Identical tall equipment cabinets line both sides, '
              u'receding far into the distance and fading out. Thick cable trays overhead. '
              u'Cool blue-grey light. The aisle is empty, no people. The scale feels endless.',
        caption=u'50量子ビットを普通のコンピュータで再現するには、1ペタバイトを超えるメモリが'
                u'要りました。イメージ図（生成AIで作成）',
    ),
    dict(
        n=5, slug='housiki', part=u'後編',
        where=u'冒頭／アイキャッチ',
        scene=u'One long laboratory bench photographed straight on, with four completely different '
              u'pieces of apparatus standing side by side in a row, evenly spaced. From left to '
              u'right: a small hanging gold-copper cryostat tower; a sealed vacuum chamber crossed '
              u'by thin straight laser beams; an optical table with mirrors and beam splitters and '
              u'folded light paths; a bare silicon chip under a fine probe needle. They look '
              u'unrelated to each other. Plain wall behind. No people.',
        caption=u'作り方は六通りあり、まだ本命が決まっていません。主な方式のイメージ図'
                u'（生成AIで作成）',
    ),
    dict(
        n=6, slug='koujou', part=u'後編',
        where=u'「本命は、分子と材料のシミュレーションです」（7番と対で）',
        scene=u'A large industrial ammonia synthesis plant at dusk. Tall steel reactor columns and '
              u'pressure vessels, thick insulated pipework, valves and flanges, steam rising and '
              u'drifting sideways, a faint shimmer of heat. Cold blue evening sky behind, warm '
              u'lights low on the structure. Seen from middle distance. No people.',
        caption=u'肥料のもとになるアンモニアは、400〜500度・数百気圧で作られています。'
                u'イメージ図（生成AIで作成）',
    ),
    dict(
        n=7, slug='konryu', part=u'後編',
        where=u'6番のすぐ下。対にして使う',
        scene=u'The root system of a soybean plant just lifted from the ground, held up against '
              u'plain soft daylight. Fine pale roots spread out, and along them cluster many small '
              u'round nodules, some cut open to show a pink-red interior. Dark crumbs of soil '
              u'still cling to the roots and a few fall away. A couple of green leaves at the top '
              u'edge of the frame. Quiet, ordinary, close up. No people, no hands.',
        caption=u'マメ科の根につく根粒。ここでは常温・常圧で、同じことが行われています。しくみは'
                u'まだ解明されていません。イメージ図（生成AIで作成）',
    ),
    dict(
        n=8, slug='joumae', part=u'後編',
        where=u'「セキュリティのための機械ではありません」',
        scene=u'Two padlocks lying side by side on a worn wooden workbench, seen from directly '
              u'above. On the left, an old brass padlock, its shackle sprung open, slightly '
              u'tarnished. On the right, a new steel padlock, still closed and clean. Between '
              u'them, a single key and a small screwdriver. Plain bench, soft daylight from one '
              u'side. No people.',
        caption=u'量子コンピュータは暗号を「壊す側」です。国は2035年を目処に、錠前の付け替えを'
                u'進めています。イメージ図（生成AIで作成）',
    ),
    dict(
        n=9, slug='genba', part=u'後編',
        where=u'「私たちの業界は、どうか」',
        scene=u'A crushed-stone quarry and civil engineering yard in soft early morning '
              u'light, seen from middle distance. On the left, stepped rock benches cut '
              u'into a hillside. In the centre, three separate conical stockpiles of '
              u'graded aggregate, coarse to fine. A wheel loader stands beside them, '
              u'engine off. A small four-rotor survey drone hovers in the air above the '
              u'yard, seen small against the sky. Two slender survey poles stand planted '
              u'in the ground. Long quiet shadows. No people.',
        caption=u'いま現場で効いているのは、量子ではなくドローンによる測量や3次元の設計データです。'
                u'イメージ図（生成AIで作成）',
    ),
]


NO_ARROWS = (
    u' Do not draw any arrows, arrowheads, chevrons, flow lines or diagram '
    u'symbols anywhere in the picture, including on ceilings, trays and walls.'
)


def prompt_of(shot):
    """矢印は3番だけのもの。ほかの絵では禁じる。

    記事のなかで矢印は「量子ビットの矢印」を指す言葉なので、
    関係のない絵に出ると読み手が混乱する。
    """
    p = shot['scene'] + u'\n\n' + STYLE
    if not shot.get('arrows'):
        p += NO_ARROWS
    return p


def get_key():
    key = os.environ.get('GEMINI_API_KEY', '').strip()
    if not key:
        sys.stderr.write(
            u'鍵がありません。\n'
            u'  export GEMINI_API_KEY=\'...\'\n'
            u'として、もう一度実行してください。鍵はファイルに書かないでください。\n'
        )
        sys.exit(2)
    return key


def call(path, key, payload=None, timeout=180):
    """payload が None なら GET。鍵はヘッダで渡す（URLに載せるとログに残るため）。"""
    body = json.dumps(payload).encode('utf-8') if payload is not None else None
    req = urllib.request.Request(
        API + path,
        data=body,
        headers={
            'x-goog-api-key': key,
            'Content-Type': 'application/json',
            'User-Agent': 'izk-figures/1.0',
        },
        method='POST' if body is not None else 'GET',
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        detail = e.read().decode('utf-8', 'replace')[:800]
        raise SystemExit(u'API がエラーを返しました（HTTP %s）\n%s' % (e.code, detail))


def list_models(key):
    data = call('/models', key)
    rows = []
    for m in data.get('models', []):
        name = m.get('name', '').split('/')[-1]
        methods = m.get('supportedGenerationMethods', [])
        if 'image' in name.lower() or 'imagen' in name.lower():
            rows.append((name, ','.join(methods)))
    if not rows:
        print(u'画像系のモデルが見つかりませんでした。全モデル数: %d'
              % len(data.get('models', [])))
        return
    print(u'%-34s %s' % (u'モデル', u'使えるメソッド'))
    print(u'-' * 74)
    for name, methods in sorted(rows):
        print(u'%-34s %s' % (name, methods))


def extract_images(resp):
    out = []
    for cand in resp.get('candidates', []):
        for part in cand.get('content', {}).get('parts', []):
            inline = part.get('inlineData') or part.get('inline_data')
            if inline and inline.get('data'):
                out.append((inline.get('mimeType') or inline.get('mime_type') or 'image/png',
                            inline['data']))
    return out


def generate(shot, key, model):
    payload = {
        'contents': [{'role': 'user', 'parts': [{'text': prompt_of(shot)}]}],
        'generationConfig': {'responseModalities': ['IMAGE']},
    }
    resp = call('/models/%s:generateContent' % model, key, payload)
    imgs = extract_images(resp)
    if not imgs:
        fb = resp.get('promptFeedback') or {}
        finish = [c.get('finishReason') for c in resp.get('candidates', [])]
        raise SystemExit(u'%d番：画像が返りませんでした。finishReason=%s feedback=%s'
                         % (shot['n'], finish, json.dumps(fb, ensure_ascii=False)[:300]))
    mime, b64 = imgs[0]
    ext = 'png' if 'png' in mime else ('jpg' if 'jpeg' in mime else 'bin')
    path = os.path.join(OUTDIR, '%02d-%s.%s' % (shot['n'], shot['slug'], ext))
    with open(path, 'wb') as f:
        f.write(base64.b64decode(b64))
    return path, os.path.getsize(path)


def write_manifest(made):
    lines = [u'# 量子記事の挿絵 一覧', u'',
             u'`gen_images.py` で作ったもの。**すべてイメージ図であり、実物の写真ではありません。**',
             u'キャプションから「イメージ図（生成AIで作成）」を消さないでください。', u'']
    for shot in SHOTS:
        got = made.get(shot['n'])
        lines.append(u'## %d. %s（%s）' % (shot['n'], shot['slug'], shot['part']))
        lines.append(u'')
        lines.append(u'- **入れる場所**：%s' % shot['where'])
        lines.append(u'- **ファイル**：%s' % (os.path.basename(got) if got else u'（未生成）'))
        lines.append(u'- **キャプション／代替テキスト**：')
        lines.append(u'  > %s' % shot['caption'])
        lines.append(u'')
    io.open(os.path.join(HERE, 'manifest.md'), 'w', encoding='utf-8').write(u'\n'.join(lines))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--list', action='store_true', help=u'使えるモデルを一覧')
    ap.add_argument('--dry-run', action='store_true', help=u'送る中身だけ表示。APIは呼ばない')
    ap.add_argument('--only', nargs='*', type=int, default=None, help=u'番号を指定して作り直す')
    ap.add_argument('--model', default=os.environ.get('GEMINI_IMAGE_MODEL', DEFAULT_MODEL))
    args = ap.parse_args()

    targets = [s for s in SHOTS if args.only is None or s['n'] in args.only]

    if args.dry_run:
        print(u'モデル: %s' % args.model)
        print(u'枚数  : %d' % len(targets))
        for s in targets:
            print(u'\n--- %d. %s（%s／%s）---' % (s['n'], s['slug'], s['part'], s['where']))
            print(prompt_of(s))
        print(u'\n（--dry-run のため API は呼んでいません）')
        return

    key = get_key()
    if args.list:
        list_models(key)
        return

    if not os.path.isdir(OUTDIR):
        os.makedirs(OUTDIR)

    made = {}
    for s in targets:
        sys.stdout.write(u'%d. %s ... ' % (s['n'], s['slug']))
        sys.stdout.flush()
        path, size = generate(s, key, args.model)
        made[s['n']] = path
        print(u'○ %s（%.1f MB）' % (os.path.basename(path), size / 1048576.0))
        time.sleep(1.0)

    write_manifest(made)
    print(u'\n%d枚できました。%s' % (len(made), OUTDIR))
    print(u'必ず目で見て、絵の中に文字が入っていないか確かめてください。')


if __name__ == '__main__':
    main()
