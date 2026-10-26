# -*- coding: utf-8 -*-
u"""article.html を WordPress に「下書き」として登録する。
・鍵は環境変数 IZK_AUTH からしか読まない。標準出力にも出さない
・--apply と --yes の両方がなければ、何も書き込まない
・status は draft 固定。このスクリプトから公開することはできない
・同じスラッグの投稿が既にあれば、新しく作らずに中止する"""
import os, sys, io, json, base64, urllib.request as ur

SITE = 'https://www.ishinazaka.co.jp/wp-json'
SLUG = 'iwate-eco-jigyosho-mitsuboshi'
TITLE = u'【お知らせ】「いわて地球環境にやさしい事業所」三つ星に認定されました'
SEO_TITLE = u'いわて地球環境にやさしい事業所とは？三つ星認定の基準と石名坂'
SEO_DESC = (u'令和8年10月16日、株式会社 石名坂は岩手県の「いわて地球環境にやさしい事業所」三つ星に認定されました。'
            u'星4段階の基準、エコスタッフの要件、県内の認定311事業所のうち三つ星13という状況を、県の要領と一覧から整理します。')
KEY = u'いわて地球環境にやさしい事業所'
CATS, TAGS = [1, 7], []   # 7 = 防災・環境（公開ページの category/information/environment）

def yobu(p, obj=None):
    q = ur.Request(SITE + p, data=json.dumps(obj).encode('utf-8') if obj is not None else None,
                   method='POST' if obj is not None else 'GET')
    q.add_header('Authorization', 'Basic ' + base64.b64encode(os.environ['IZK_AUTH'].encode()).decode())
    q.add_header('User-Agent', 'Mozilla/5.0')
    if obj is not None:
        q.add_header('Content-Type', 'application/json; charset=utf-8')
    return json.load(ur.urlopen(q, timeout=120))

def main():
    kaku = '--apply' in sys.argv and '--yes' in sys.argv
    here = os.path.dirname(os.path.abspath(__file__))
    body = io.open(os.path.join(here, 'article.html'), encoding='utf-8').read()
    print(u'書き込み: ' + (u'する（下書き）' if kaku else u'しない（確かめるだけ）'))
    print(u'題名: %s（%d字）' % (TITLE, len(TITLE)))
    print(u'検索向けの題名: %d字 ／ 説明文: %d字' % (len(SEO_TITLE), len(SEO_DESC)))
    aru = yobu('/wp/v2/posts?slug=%s&status=publish,draft,pending,future,private&_fields=id,status' % SLUG)
    if aru:
        print(u'同じスラッグの投稿が既にあります（ID %s）。中止します。' % aru[0]['id']); sys.exit(1)
    if not kaku:
        return
    x = yobu('/wp/v2/posts', {'title': TITLE, 'content': body, 'slug': SLUG, 'status': 'draft',
                              'categories': CATS, 'tags': TAGS})
    pid = x['id']
    yobu('/aioseo/v1/post', {'id': pid, 'title': SEO_TITLE, 'description': SEO_DESC,
                             'keyphrases': {'focus': {'keyphrase': KEY}, 'additional': []}})
    y = yobu('/wp/v2/posts/%d?context=edit' % pid)
    c = yobu('/aioseo/v1/post?postId=%d' % pid)['data']['currentPost']
    assert y['status'] == 'draft', y['status']
    assert y['content']['raw'] == body
    assert c['title'] == SEO_TITLE and c['description'] == SEO_DESC, (c['title'], c['description'])
    print(u'下書きを作りました。ID %d ／ 状態 %s' % (pid, y['status']))
    print(u'プレビュー: https://www.ishinazaka.co.jp/?p=%d&preview=true' % pid)

main()
