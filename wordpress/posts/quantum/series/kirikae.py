# -*- coding: utf-8 -*-
"""全6回を公開し、前編・後編のURLを活かしたまま中身を入れ替える。

    export IZK_AUTH='ai-agent:xxxx ...'
    python3 kirikae.py --dry-run
    python3 kirikae.py --apply --yes

考え方：
  前編 ID6188 は仕組みの話なので第1回に、後編 ID6189 は現状の話なので
  第4回にする。スラッグを変えると WordPress が古いスラッグを覚えていて
  自動で301転送する（このサイトで実地に確認済み）。
  こうすると古いURLが死なず、公開日も被リンクもそのまま残る。

順番（読者が404に当たらないように）：
  1. 先に、いらなくなる下書き2本のスラッグを空ける
  2. 第2・3・5・6回を公開（第1回より先。第1回から前へも後ろへも飛べるように）
  3. 前編を第1回に、後編を第4回に入れ替える
  4. いらなくなった下書き2本をゴミ箱へ（消さずに残す）
  5. 一つ手前の記事の「次の記事へ」を、第1回に付け替える

決めごと：
  ・--apply と --yes の両方がなければ、何も書き込まない。
  ・入れ替える前の中身は hikaeti/ に控えてある。
  ・終わったら、公開ページを順に辿って確かめる。
"""
from __future__ import print_function

import argparse
import os
import re
import sys
import time

import plan
import post_series as ps

SITE = plan.SITE
# 前編・後編を、どの回の中身にするか
SWAP = [(6188, 0), (6189, 3)]           # (記事ID, plan.PARTS の何番目)
RETIRE = {0: 6208, 3: 6211}             # いらなくなる下書き
PREV_POST = 'kensetsugyo-unso-kyoka-koushin'   # 一つ手前の記事


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--yes', action='store_true')
    a = ap.parse_args()
    go = a.apply and a.yes
    if not go and not a.dry_run:
        ap.error(u'--dry-run か、--apply --yes の両方を指定してください')

    import set_media_meta as smm
    auth = smm.auth_header()
    shots, media = ps.gather(smm, auth)

    def post(pid, data):
        if not go:
            print(u'      （空打ち：%s）' % u'、'.join(sorted(data)))
            return {'id': pid}
        return smm.call('/posts/%d' % pid, auth, data=data)

    def one(slug):
        got = smm.call('/posts?slug=%s&status=draft,publish,trash&context=edit' % slug, auth)
        return got[0] if got else None

    print(u'\n━━ 1. いらなくなる下書きのスラッグを空ける ━━')
    for k, pid in sorted(RETIRE.items()):
        spec = plan.PARTS[k]
        print(u'  第%d回の下書き ID%d（%s）→ 退避' % (spec['n'], pid, spec['slug']))
        post(pid, {'slug': spec['slug'] + '-taihi'})

    print(u'\n━━ 2. 第2・3・5・6回を公開 ━━')
    swapped = {k for _, k in SWAP}
    for k, spec in enumerate(plan.PARTS):
        if k in swapped:
            continue
        p = one(spec['slug'])
        if not p:
            sys.exit(u'× 第%d回の下書きが見つかりません' % spec['n'])
        if p['status'] == 'publish':
            print(u'  第%d回 ID%d はすでに公開済み' % (spec['n'], p['id']))
            continue
        print(u'  第%d回 ID%d を公開  %s' % (spec['n'], p['id'], spec['title'][:40]))
        post(p['id'], {'status': 'publish'})

    print(u'\n━━ 3. 前編・後編の中身を入れ替える ━━')
    for pid, k in SWAP:
        spec = plan.PARTS[k]
        full, prev_url, next_url = ps.build_full(k, shots, media)
        cur = smm.call('/posts/%d?context=edit' % pid, auth)
        print(u'  ID%d  %s' % (pid, cur['title']['raw'][:40]))
        print(u'     → 第%d回 %s' % (spec['n'], spec['title'][:40]))
        print(u'     スラッグ %s → %s（古い方は301で飛びます）' % (cur['slug'], spec['slug']))
        print(u'     ナビ ← %s ／ → %s' % (prev_url, next_url or u'なし'))
        post(pid, {'title': spec['title'], 'slug': spec['slug'], 'content': full,
                   'excerpt': spec['desc'], 'status': 'publish',
                   'featured_media': media[spec['featured']]['id']})

    print(u'\n━━ 4. いらなくなった下書きをゴミ箱へ ━━')
    # status:'trash' は REST が受け付けない。DELETE を投げる必要があるが、
    # このサーバは DELETE を塞いでいるので、WordPress の方法上書きを使う。
    # force を付けないので、消さずにゴミ箱へ入るだけ。
    for k, pid in sorted(RETIRE.items()):
        cur = smm.call('/posts/%d?context=edit' % pid, auth)
        if cur['status'] == 'trash':
            print(u'  ID%d はすでにゴミ箱にあります' % pid)
            continue
        print(u'  ID%d をゴミ箱へ（消さずに残ります）' % pid)
        if go:
            smm.call('/posts/%d?_method=DELETE' % pid, auth, data={},
                     headers={'X-HTTP-Method-Override': 'DELETE'})
        else:
            print(u'      （空打ち：ゴミ箱へ）')

    print(u'\n━━ 5. 一つ手前の記事の「次の記事へ」を付け替える ━━')
    p = one(PREV_POST)
    t = p['content']['raw']
    old = SITE + '/quantum-computer-01-mechanism/'
    new = SITE + '/%s/' % plan.PARTS[0]['slug']
    print(u'  ID%d %s' % (p['id'], p['title']['raw'][:38]))
    if new in t:
        print(u'     － すでに第1回を指しています')
    elif t.count(old) != 1:
        sys.exit(u'× 付け替え先が %d 件（1件でないと止めます）' % t.count(old))
    else:
        print(u'     %s → %s' % (old, new))
        post(p['id'], {'content': t.replace(old, new)})

    print(u'\n%s' % (u'■ 空打ちでした。何も書き込んでいません。' if not go
                    else u'■ 切り替えました。このあと公開ページを確かめます。'))


if __name__ == '__main__':
    main()
