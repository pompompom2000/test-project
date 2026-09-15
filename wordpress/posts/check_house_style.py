# -*- coding: utf-8 -*-
"""下書きが、石名坂のいつもの型に合っているか点検する。

    python3 check_house_style.py quantum/article-01.html
    python3 check_house_style.py --corpus          # 公開済みの記事から測り直す

判断の根拠は wordpress/docs/ishinazaka-no-kuse.md にまとめてある。
そこの数字は、このスクリプトの --corpus が出したもの。

決めごと：
  ・このスクリプトは読むだけ。記事を書き換えることは絶対にしない。
  ・鍵は環境変数 IZK_AUTH からしか読まない。
  ・「型に合っていない」は、間違いという意味ではない。
    外す理由があるなら外してよい。黙って外れているのを防ぐためのもの。
"""
from __future__ import print_function

import argparse
import base64
import collections
import io
import json
import os
import re
import sys

try:
    from urllib.request import Request, urlopen
except ImportError:                                   # Python 2
    from urllib2 import Request, urlopen

SITE = 'https://www.ishinazaka.co.jp'
API = SITE + '/wp-json/wp/v2'
TEL = '019-638-7521'

# 話題ごとに使い分けているCTAの見出し（公開済み146本での件数）
CTA_HEADINGS = [
    (u'地域の守り手として', 35), (u'運搬・工事のご相談', 26),
    (u'工事のご相談・ご依頼', 22), (u'株式会社石名坂について', 20),
    (u'現場の仕事を、もっと知る', 15), (u'砕石・砂利のご注文・ご相談', 13),
    (u'除雪・排雪のご相談', 6), (u'建設・運搬のご相談', 6),
]

# ほぼ使わない言い回し（公開済みでの出現率 1%）
AVOID = [u'いかがでしょうか']

# 技術・コラム系の連載は、CTAの見出しに「株式会社石名坂について」を使っている
# （Claude Code 連載 5本すべて、AX の記事、AI の考察記事）。
# 全体では 14% の少数派だが、この手の記事ではこれが前例。
TECH_WORDS = (u'量子', u'Claude', u'AI', u'Web3', u'コンピュータ', u'生成')


def strip_tags(t):
    return re.sub(r'<[^>]+>', '', re.sub(r'<!--.*?-->', '', t, flags=re.S))


# ────────────────────────────────── 点検
def check(path):
    t = io.open(path, encoding='utf-8').read()
    body = strip_tags(t)
    ok, warn = [], []

    def test(cond, good, bad):
        (ok if cond else warn).append(good if cond else bad)

    # 末尾の型
    test('<!-- ISNZ-REL -->' in t, u'ISNZ-REL の目印がある',
         u'ISNZ-REL の目印がない（公開済み 100%）')
    test('<!-- ISNZ-CTA -->' in t, u'ISNZ-CTA の目印がある',
         u'ISNZ-CTA の目印がない（公開済み 97%）')
    if '<!-- ISNZ-REL -->' in t and '<!-- ISNZ-CTA -->' in t:
        test(t.index('<!-- ISNZ-REL -->') < t.index('<!-- ISNZ-CTA -->'),
             u'REL → CTA の順になっている', u'REL と CTA の順が逆')
    test(TEL in t, u'電話番号がある', u'電話番号 %s がない（公開済み 100%%）' % TEL)
    test('/contact/' in t, u'お問い合わせフォームへのリンクがある',
         u'お問い合わせフォームへのリンクがない（公開済み 99%）')
    # いちばん新しい記事には「次の記事へ」がない（空のカラムにしてある）ので、
    # 「前の記事へ」があれば型どおりとみなす。
    test(u'前の記事へ' in t, u'前後の記事ナビがある（次の記事へ %s）'
         % (u'あり' if u'次の記事へ' in t else u'なし＝いちばん新しい記事の形'),
         u'前後の記事ナビ（前の記事へ）がない（公開済み 99%）')
    test(u'あわせて読みたい' in t or u'このシリーズの記事' in t,
         u'関連記事の案内がある',
         u'「あわせて読みたい」も「このシリーズの記事」もない（公開済み 77%／26%）')
    test(u'お知らせ一覧へ' in t, u'お知らせ一覧へ戻るボタンがある',
         u'お知らせ一覧へ戻るボタンがない（公開済み 89%）')

    # CTAの見出し
    heads = [strip_tags(h) for h in re.findall(r'isnz-cta-heading">(.*?)</h2>', t)]
    if not heads:
        warn.append(u'CTAの見出し（isnz-cta-heading）がない')
    else:
        for h in heads:
            if h == u'株式会社石名坂について':
                if any(w in body for w in TECH_WORDS):
                    ok.append(u'CTAの見出し「%s」。'
                              u'技術・コラム系ではこれが前例（Claude Code 連載と同じ）' % h)
                else:
                    warn.append(u'CTAの見出しが「%s」。'
                                u'工事や運搬の話なら、話題に合わせた見出しに変える' % h)
            elif any(h == k for k, _ in CTA_HEADINGS):
                ok.append(u'CTAの見出し「%s」はいつも使っている形' % h)
            else:
                warn.append(u'CTAの見出し「%s」は前例がない。'
                            u'新しく作るなら意図してのことか確かめる' % h)

    # 分量
    n = len(body)
    if n > 3000:
        warn.append(u'本文 %d字。公開済みの中央値は 1,677字で、3,000字超は上位16%%。'
                    u'連載に割ることを考える' % n)
    else:
        ok.append(u'本文 %d字（中央値 1,677字）' % n)

    ss = [len(s) for s in body.split(u'。') if 4 < len(s) < 400]
    if ss:
        ss.sort()
        med = ss[len(ss) // 2]
        over = 100 * sum(1 for x in ss if x > 60) // len(ss)
        test(med <= 60, u'一文の中央値 %d字（公開済み 53字）' % med,
             u'一文の中央値 %d字。公開済みは 53字' % med)
        if over > 55:
            warn.append(u'60字を超える文が %d%%。公開済みは 40%%' % over)

    # 組み立て
    # ナビのボタン（前の記事へ・次の記事へ・お知らせ一覧へ）は挿絵ではないので、
    # 数える前に切り落とす。
    core = t[:t.index(u'<!-- ISNZ-REL -->')] if u'<!-- ISNZ-REL -->' in t else t

    h2 = len(re.findall(r'<!-- wp:heading {"level":2|<h2', t))
    h3 = len(re.findall(r'<h3', t))
    img = len(re.findall(r'<!-- wp:image', core))
    svg = len(re.findall(r'<svg', core))
    ok.append(u'見出し h2 %d / h3 %d（公開済み 3.3 / 4.8）' % (h2, h3))
    test(img + svg >= 3, u'図と絵が %d点（画像 %d・図 %d／公開済み 4.3枚）' % (img + svg, img, svg),
         u'図と絵が %d点しかない。公開済みは1本あたり 4.3枚' % (img + svg))

    blocks = [b for b in re.findall(r'<!-- wp:([\w/]+)', core) if b != 'spacer']
    first = next((i for i, b in enumerate(blocks) if b in ('image', 'html')), None)
    if first is None:
        warn.append(u'本文に図も絵もない')
    elif first > 8:
        warn.append(u'最初の図が %d ブロック目。公開済みは5ブロック目あたり' % first)
    else:
        ok.append(u'最初の図が %d ブロック目（公開済み 5前後）' % first)

    fs = len(re.findall(r'wp:paragraph {"fontSize":"medium"}', t))
    par = len(re.findall(r'<!-- wp:paragraph', t))
    if par:
        r = 100 * fs // par
        test(r >= 50, u'段落の %d%% に fontSize:medium（公開済み 63%%）' % r,
             u'段落の %d%% にしか fontSize:medium がない（公開済み 63%%）' % r)

    # 書きぶり
    local = [w for w in (u'盛岡', u'岩手') if w in body]
    test(bool(local), u'地名が入っている（%s）' % u'・'.join(local),
         u'盛岡も岩手も出てこない（公開済み 84%／46%）')
    test(any(w in body for w in (u'石名坂', u'当社', u'弊社', u'自社', u'私たち')),
         u'自社に触れている', u'自社にまったく触れていない')
    for w in AVOID:
        if w in body:
            warn.append(u'「%s」を使っている。公開済みではほとんど使っていない' % w)
    test(u'まとめ' in body, u'「まとめ」がある', u'「まとめ」がない（公開済み 52%）')

    print(u'\n=== %s ===' % os.path.basename(path))
    for s in ok:
        print(u'  ○ %s' % s)
    for s in warn:
        print(u'  ・%s' % s)
    print(u'\n  合っている %d件／見直す %d件' % (len(ok), len(warn)))
    return len(warn)


# ────────────────────────────────── 測り直す
def fetch_all(what):
    auth = os.environ.get('IZK_AUTH')
    head = {'User-Agent': 'izk-style-check'}
    if auth:
        head['Authorization'] = 'Basic ' + base64.b64encode(
            auth.encode('utf-8')).decode('ascii')
    out, page = [], 1
    while True:
        url = '%s/%s?per_page=50&page=%d&status=publish' % (API, what, page)
        if auth:
            url += '&context=edit'
        try:
            r = urlopen(Request(url, headers=head), timeout=60)
        except Exception as e:
            if page > 1 and '400' in str(e):
                break
            raise
        got = json.loads(r.read().decode('utf-8'))
        if not got:
            break
        out += got
        page += 1
    return out


def corpus(cache):
    if cache and os.path.exists(cache):
        posts = json.loads(io.open(cache, encoding='utf-8').read())
        print(u'手元の写しを使います：%s' % cache)
    else:
        posts = fetch_all('posts')
        if cache:
            io.open(cache, 'w', encoding='utf-8').write(
                json.dumps(posts, ensure_ascii=False))
    print(u'公開済みの記事 %d本' % len(posts))

    def raw(p):
        c = p['content']
        return c.get('raw') or c['rendered']

    L = sorted(len(strip_tags(raw(p))) for p in posts)
    print(u'  本文の字数  中央値 %d／平均 %d' % (L[len(L) // 2], sum(L) // len(L)))
    T = sorted(len(p['title'].get('raw') or p['title']['rendered']) for p in posts)
    print(u'  題名の字数  中央値 %d' % T[len(T) // 2])
    for label, w in ((u'前後の記事ナビ', u'前の記事へ'), (u'ISNZ-CTA', '<!-- ISNZ-CTA -->'),
                     (u'電話番号', TEL), (u'あわせて読みたい', u'あわせて読みたい')):
        n = sum(1 for p in posts if w in raw(p))
        print(u'  %-12s %3d本 (%d%%)' % (label, n, 100 * n // len(posts)))
    C = collections.Counter()
    for p in posts:
        for h in re.findall(r'isnz-cta-heading">(.*?)</h2>', raw(p)):
            C[strip_tags(h)] += 1
    print(u'  CTAの見出し %d種類：%s' % (
        len(C), u'、'.join(u'%s %d' % kv for kv in C.most_common())))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('files', nargs='*')
    ap.add_argument('--corpus', action='store_true', help=u'公開済みの記事から測り直す')
    ap.add_argument('--cache', help=u'取ってきた記事の置き場（あれば読む）')
    a = ap.parse_args()

    if a.corpus:
        corpus(a.cache)
        return
    if not a.files:
        ap.error(u'点検するファイルを指定してください')
    bad = sum(check(f) for f in a.files)
    print(u'\n見直す点 合計 %d件（間違いという意味ではありません）' % bad)


if __name__ == '__main__':
    main()
