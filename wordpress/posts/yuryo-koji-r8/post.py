# -*- coding: utf-8 -*-
u"""article.html を WordPress に「下書き」として登録する。
・鍵は環境変数 IZK_AUTH からしか読まない。標準出力にも出さない
・--apply と --yes の両方がなければ、何も書き込まない
・status は draft 固定。このスクリプトから公開することはできない
・同じスラッグの投稿が既にあれば、新しく作らずに中止する"""
import os, sys, io, json, base64, urllib.request as ur

SITE = 'https://www.ishinazaka.co.jp/wp-json'
SLUG = 'morioka-yuryo-kensetsu-koji-r8'
TITLE = u'【お知らせ】道明地区の基盤整備工事が「令和8年度 盛岡市優良建設工事」に表彰されました'
SEO_TITLE = u'盛岡市優良建設工事表彰とは？道明地区の基盤整備工事で2年連続受賞'
SEO_DESC = (u'令和8年11月11日、石名坂・三陸土建特定共同企業体の「道明地区新産業等用地（第二事業区）基盤整備工事」が令和8年度 盛岡市優良建設工事に表彰されました。'
            u'表彰の目的と選ばれ方（成績80点以上、5年間の平均点）、工事の中身、道明地区の用地について、市の要綱と要領から整理します。')
KEY = u'盛岡市優良建設工事表彰'
CATS, TAGS = [1, 5], [48, 92]   # 5 = 施工実績（works）、48 = 盛岡、92 = 建設業

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
