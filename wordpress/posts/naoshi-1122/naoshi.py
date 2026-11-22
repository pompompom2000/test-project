# -*- coding: utf-8 -*-
u"""5回目の点検（11月19日）で見つけた私の誤り2つを直す。藤原さんの「直して」（11月22日）を受けて作った。
 1. 三つ星認定の記事（ID 6490）の分類：[1, 7]（お知らせ・除雪・排雪）→ [1, 82]（お知らせ・防災・環境）
 2. 表彰の記事（ID 6499）の説明文：138字 → 110字前後
・鍵は環境変数 IZK_AUTH からしか読まない。標準出力にも出さない
・--apply と --yes の両方がなければ、何も書き込まない
・本文・題名・状態（公開のまま）は変えない。変える前の値を控えに残す
・AIOSEO は題名・説明文・キーフレーズを一緒に送らないと消えるので、今の題名とキーフレーズを読んでそのまま送る"""
import os, sys, io, json, base64, urllib.request as ur
SITE = 'https://www.ishinazaka.co.jp/wp-json'
ECO, YURYO = 6490, 6499
NEW_DESC = (u'令和8年11月11日、石名坂・三陸土建特定共同企業体の道明地区新産業等用地（第二事業区）基盤整備工事が、'
            u'盛岡市優良建設工事として表彰されました。2年連続の受賞です。選ばれ方（成績80点以上、5年間の平均点）と工事の中身を整理します。')
def yobu(p, obj=None):
    q = ur.Request(SITE + p, data=json.dumps(obj).encode('utf-8') if obj is not None else None, method='POST' if obj is not None else 'GET')
    q.add_header('Authorization', 'Basic ' + base64.b64encode(os.environ['IZK_AUTH'].encode()).decode()); q.add_header('User-Agent', 'Mozilla/5.0')
    if obj is not None: q.add_header('Content-Type', 'application/json; charset=utf-8')
    return json.load(ur.urlopen(q, timeout=120))
kaku = '--apply' in sys.argv and '--yes' in sys.argv
here = os.path.dirname(os.path.abspath(__file__))
print(u'書き込み: ' + (u'する' if kaku else u'しない（確かめるだけ）'))
cats = {c['id']: c['name'] for c in yobu('/wp/v2/categories?per_page=50&_fields=id,name')}
assert cats[7] == u'除雪・排雪' and cats[82] == u'防災・環境' and cats[1] == u'お知らせ', cats
e = yobu('/wp/v2/posts/%d?context=edit' % ECO)
assert e['slug'] == 'iwate-eco-jigyosho-mitsuboshi' and e['status'] == 'publish'
y = yobu('/wp/v2/posts/%d?context=edit' % YURYO)
assert y['slug'] == 'morioka-yuryo-kensetsu-koji-r8' and y['status'] == 'publish'
a = yobu('/aioseo/v1/post?postId=%d' % YURYO)['data']['currentPost']
kp = a.get('keyphrases')
if isinstance(kp, str): kp = json.loads(kp)
print(u'1. 三つ星の分類: %s → [1, 82]（%s）' % (e['categories'], u'・'.join(cats[c] for c in e['categories'])))
print(u'2. 表彰の説明文: %d字 → %d字' % (len(a['description']), len(NEW_DESC)))
print(u'   新: ' + NEW_DESC)
io.open(os.path.join(here, 'mae.json'), 'w', encoding='utf-8').write(json.dumps(
    {'eco_categories': e['categories'], 'yuryo_seo_title': a['title'], 'yuryo_seo_desc': a['description'], 'yuryo_keyphrases': kp}, ensure_ascii=False, indent=1))
if not kaku: sys.exit()
mae_body_e = e['content']['raw']
yobu('/wp/v2/posts/%d' % ECO, {'categories': [1, 82]})
e2 = yobu('/wp/v2/posts/%d?context=edit' % ECO)
assert sorted(e2['categories']) == [1, 82] and e2['status'] == 'publish' and e2['content']['raw'] == mae_body_e
yobu('/aioseo/v1/post', {'id': YURYO, 'title': a['title'], 'description': NEW_DESC, 'keyphrases': kp})
a2 = yobu('/aioseo/v1/post?postId=%d' % YURYO)['data']['currentPost']
kp2 = a2.get('keyphrases'); kp2 = json.loads(kp2) if isinstance(kp2, str) else kp2
assert a2['description'] == NEW_DESC and a2['title'] == a['title'], (a2['title'], a2['description'])
assert (kp2 or {}).get('focus', {}).get('keyphrase') == (kp or {}).get('focus', {}).get('keyphrase')
print(u'直しました。読み返しも確かめました。')
