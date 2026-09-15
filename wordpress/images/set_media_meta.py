# -*- coding: utf-8 -*-
"""アップロード済みの画像に、代替テキスト等を入れる。

使い方：
    export IZK_AUTH='ai-agent:xxxx xxxx xxxx xxxx xxxx xxxx'

    # いまの状態を見る（何も変えない）
    python3 set_media_meta.py --show 1 2

    # 4欄を入れる（ファイル名はそのまま）
    python3 set_media_meta.py --apply 1 2

    # ファイル名も変える（入れ直し。古いほうは残る）
    python3 set_media_meta.py --reupload 1

    # 入れ直したうえで、古いほうを消す（要 --yes）
    python3 set_media_meta.py --reupload 1 --delete-old --yes

できること／できないこと：
  ・代替テキスト・タイトル・キャプション・説明 → APIで書き換えられる
  ・ファイル名そのもの → 書き換えられない。入れ直すしかない

入れ直すときは、labeled/NN-ファイル名 があればそれを上げる。
つまり先に label_images.py を走らせておくこと。

安全のための決めごと：
  ・削除は --delete-old と --yes の両方がないと絶対に行わない
  ・変える前に、いまの値を必ず表示する
  ・鍵は環境変数からしか読まない
"""
from __future__ import print_function

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'docs'))

SITE = 'https://www.ishinazaka.co.jp'
API = SITE + '/wp-json/wp/v2'


def load_shots():
    """docs/build_gazou_seo.py の SHOTS をそのまま使う（二重管理を避ける）。"""
    import importlib.util
    path = os.path.join(HERE, '..', 'docs', 'build_gazou_seo.py')
    src = open(path, encoding='utf-8').read()
    # ページ生成まで走らせたくないので、SHOTS の定義部分だけ取り出す
    start = src.index('SHOTS = [')
    end = src.index('FIELDS = [')
    ns = {}
    exec(compile(src[start:end], path, 'exec'), ns)
    return ns['SHOTS']


def auth_header():
    a = os.environ.get('IZK_AUTH', '').strip()
    if not a or ':' not in a:
        sys.stderr.write(
            u"鍵がありません。\n"
            u"  export IZK_AUTH='ai-agent:xxxx xxxx xxxx xxxx xxxx xxxx'\n"
            u"として、もう一度実行してください。\n")
        sys.exit(2)
    return 'Basic ' + base64.b64encode(a.encode('utf-8')).decode('ascii')


def call(path, auth, data=None, method=None, raw=None, headers=None, timeout=90):
    hdr = {'Authorization': auth, 'User-Agent': 'izk-media/1.0'}
    if headers:
        hdr.update(headers)
    body = None
    if data is not None:
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        hdr['Content-Type'] = 'application/json; charset=utf-8'
    elif raw is not None:
        body = raw
    req = urllib.request.Request(
        path if path.startswith('http') else API + path,
        data=body, headers=hdr,
        method=method or ('POST' if body is not None else 'GET'))
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            txt = r.read().decode('utf-8')
            return json.loads(txt) if txt.strip() else {}
    except urllib.error.HTTPError as e:
        raise SystemExit(u'APIがエラーを返しました（HTTP %s）\n%s'
                         % (e.code, e.read().decode('utf-8', 'replace')[:700]))


def find_by_url(url, auth):
    """URLからメディアIDを探す。ファイル名で検索する。"""
    fname = url.rsplit('/', 1)[-1].rsplit('.', 1)[0]
    q = '/media?search=%s&per_page=20&context=edit' % urllib.parse.quote(fname)
    for m in call(q, auth):
        if m.get('source_url') == url:
            return m
    return None


def show(m):
    def plain(v):
        if isinstance(v, dict):
            return v.get('raw', v.get('rendered', ''))
        return v or ''
    print(u'  ID        : %s' % m.get('id'))
    print(u'  ファイル  : %s' % m.get('source_url', '').rsplit('/', 1)[-1])
    print(u'  代替text  : %s' % (plain(m.get('alt_text')) or u'（空）'))
    print(u'  タイトル  : %s' % (plain(m.get('title')) or u'（空）'))
    print(u'  キャプション: %s' % (plain(m.get('caption')) or u'（空）'))
    print(u'  説明      : %s' % (plain(m.get('description')) or u'（空）'))


def fields_of(shot):
    return {
        'alt_text': shot['alt'],
        'title': shot['mtitle'],
        'caption': shot['caption'],
        'description': shot['desc'],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--show', nargs='*', type=int)
    ap.add_argument('--apply', nargs='*', type=int)
    ap.add_argument('--reupload', nargs='*', type=int)
    ap.add_argument('--delete-old', action='store_true')
    ap.add_argument('--yes', action='store_true')
    args = ap.parse_args()

    shots = {s['n']: s for s in load_shots()}
    nums = args.show or args.apply or args.reupload
    if not nums:
        ap.print_help()
        return
    auth = auth_header()

    for n in nums:
        s = shots.get(n)
        if not s:
            print(u'%d番は一覧にありません' % n)
            continue
        if not s['url']:
            print(u'%d番（%s）はURLが未登録です' % (n, s['title']))
            continue

        print(u'\n=== %d. %s ===' % (n, s['title']))
        m = find_by_url(s['url'], auth)
        if not m:
            print(u'  × このURLのメディアが見つかりません')
            continue
        print(u'-- いまの状態 --')
        show(m)

        if args.show:
            continue

        if args.apply:
            print(u'-- 入れる --')
            saved = call('/media/%d' % m['id'], auth, data=fields_of(s))
            show(saved)
            print(u'  ○ 入れました（ファイル名はそのままです）')
            continue

        if args.reupload:
            print(u'-- 入れ直す --')
            # 文字を焼き込んだものがあれば、そちらを上げる。
            # 焼き込む前のものを上げてしまうと、見出しのない絵が site に載る。
            lab = os.path.join(HERE, 'labeled', '%02d-%s' % (n, s['fname']))
            if os.path.exists(lab):
                blob = open(lab, 'rb').read()
                print(u'  文字入り: %s' % os.path.basename(lab))
            else:
                with urllib.request.urlopen(s['url'], timeout=90) as r:
                    blob = r.read()
                print(u'  ! 文字入りが見つからないので、元の絵をそのまま上げます')
                print(u'    （先に python3 label_images.py %d を実行してください）' % n)
            print(u'  大きさ: %.2f MB' % (len(blob) / 1048576.0))
            new = call('/media', auth, raw=blob, headers={
                'Content-Type': 'image/jpeg',
                'Content-Disposition': 'attachment; filename="%s"' % s['fname'],
            })
            print(u'  新しいID: %s' % new.get('id'))
            print(u'  新しいURL: %s' % new.get('source_url'))
            saved = call('/media/%d' % new['id'], auth, data=fields_of(s))
            show(saved)

            if args.delete_old:
                if not args.yes:
                    print(u'  ! 古いほう（ID %s）は消していません。'
                          u'消すなら --yes を付けてください' % m['id'])
                else:
                    call('/media/%d?force=true' % m['id'], auth, method='DELETE')
                    print(u'  ○ 古いほう（ID %s）を削除しました' % m['id'])
            else:
                print(u'  古いほう（ID %s）はそのまま残しています' % m['id'])


if __name__ == '__main__':
    main()
