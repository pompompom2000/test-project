# -*- coding: utf-8 -*-
"""全6回のSEO設定（All in One SEO）を書き込む。

公開済みの記事は、狙う言葉を必ず1つ決め、説明文を手書きしている。
下書きは初期値のままなので、plan.py の keyword と desc を入れる。

    python3 seo_series.py --show / --apply

決めごと：鍵は環境変数からしか読まない。下書き以外には触れない。
書き込む前にいまの値を出し、書き込んだあと読み直して確かめる。
"""
from __future__ import print_function

import argparse, base64, json, os, sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import plan

AIO = plan.SITE + '/wp-json/aioseo/v1'
WP = plan.SITE + '/wp-json/wp/v2'


def head():
    a = os.environ.get('IZK_AUTH')
    if not a:
        sys.exit(u'× 環境変数 IZK_AUTH がありません')
    return {'Authorization': 'Basic ' + base64.b64encode(a.encode('utf-8')).decode('ascii'),
            'User-Agent': 'izk-seo'}


def call(url, h, data=None):
    hh = dict(h)
    if data is not None:
        hh['Content-Type'] = 'application/json'
    req = Request(url, headers=hh, data=json.dumps(data).encode('utf-8') if data else None)
    try:
        return json.loads(urlopen(req, timeout=90).read().decode('utf-8'))
    except HTTPError as e:
        sys.exit(u'× %s %s' % (e.code, e.read().decode('utf-8', 'replace')[:300]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--show', action='store_true')
    ap.add_argument('--apply', action='store_true')
    a = ap.parse_args()
    if not (a.show or a.apply):
        ap.error(u'--show か --apply を指定してください')
    h = head()

    for spec in plan.PARTS:
        got = call('%s/posts?slug=%s&status=draft,publish&context=edit' % (WP, spec['slug']), h)
        if not got:
            sys.exit(u'× 第%d回の記事がありません' % spec['n'])
        p = got[0]
        print(u'\n=== 第%d回 ID%d（%s）===' % (spec['n'], p['id'], p['status']))
        if p['status'] != 'draft':
            print(u'  ! 下書きではありません。触りません。')
            continue
        cur = call('%s/post?postId=%d' % (AIO, p['id']), h)['data']['currentPost']
        print(u'  いま: 説明文「%s」／狙う言葉「%s」'
              % ((cur.get('description') or u'未設定')[:36], cur.get('focus_keyword') or u'未設定'))
        if not a.apply:
            print(u'  入れる: %s ／ %d字' % (spec['keyword'], len(spec['desc'])))
            continue
        body = dict(cur)
        body['postId'] = p['id']
        body['description'] = spec['desc']
        body['focus_keyword'] = spec['keyword']
        body['keyphrases'] = {'focus': {'keyphrase': spec['keyword'], 'score': 0, 'analysis': []},
                              'additional': cur.get('keyphrases', {}).get('additional', [])}
        call(AIO + '/post', h, body)
        back = call('%s/post?postId=%d' % (AIO, p['id']), h)['data']['currentPost']
        ok = (back.get('description') == spec['desc']
              and back.get('focus_keyword') == spec['keyword'])
        print(u'  %s 入りました：%s／%d字' % (u'○' if ok else u'×',
                                        back.get('focus_keyword'),
                                        len(back.get('description') or u'')))


if __name__ == '__main__':
    main()
