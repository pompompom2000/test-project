# -*- coding: utf-8 -*-
u"""Geminiで作った画像を、白トラの記事の下書き（ID 6469）に配置する。
・鍵は環境変数 IZK_AUTH からしか読まない。標準出力にも出さない
・--apply と --yes の両方がなければ、何も書き込まない
・下書き（draft）でなければ中止する。公開はしない
・目印の文字列がちょうど1回あることを確かめてから、その直前に差し込む
・差し込んだ部分の外側が一字も変わっていないことを確かめ、読み返す"""
import os, sys, json, base64, urllib.request as ur

SITE = 'https://www.ishinazaka.co.jp/wp-json'
PID = 6469
# 番号: (メディアID, 直前に差し込む目印, 代替テキスト, キャプション, アイキャッチにするか)
GAZOU = {
  '01': (6472, u'<!-- wp:heading {"level":3,"fontSize":"medium"} -->\n<h3 class="wp-block-heading has-medium-font-size">決まったこと',
         u'白トラの行政処分が令和8年10月1日から重くなり、車が使えない日数が延びることを示す図。白いトラックとカレンダーの絵。',
         u'10月1日以降の違反から、新しい基準で処分されます。', True),
  '02': (6473, u'<!-- wp:paragraph {"fontSize":"medium"} -->\n<p class="has-medium-font-size">白トラを商売として続けていれば',
         u'許可なく運送の商売をしたときの、車が使えない日数の変化を示す図。1回目は60日から120日に、2回目は120日から180日に延びる。',
         u'左が9月30日までの違反、右が10月1日以降の違反です。', False),
  '03': (6476, u'<!-- wp:paragraph {"fontSize":"medium"} -->\n<p class="has-medium-font-size">あわせて、8月の記事で',
         u'使用禁止になると、車検証を返し、ナンバーを預けることを示す図。その間、その車は道路を走れない。書類とナンバーの板の絵。',
         u'今回の改正で、通達に新しく書き加えられた決まりです。', False),
  '04': (6477, u'<!-- wp:heading {"level":3,"fontSize":"medium"} -->\n<h3 class="wp-block-heading has-medium-font-size">岩手でも',
         u'無許可の業者に運送を頼んだ場合、頼んだ側は4月から100万円以下の罰金、運んだ側は10月から車が使えない日数が延びたことを示す図。',
         u'4月は頼む側、10月は運ぶ側。半年で両方の決まりが強まりました。', False),
  '05': (6478, u'<!-- wp:heading {"level":3,"fontSize":"medium"} -->\n<h3 class="wp-block-heading has-medium-font-size">まとめ',
         u'運送を頼む前にナンバーの色を見ることを示す図。緑ナンバーは他社の荷物を運べる。白ナンバーで運べるのは基本、自社の荷物。',
         u'他社の荷物を運ぶトラックなら、ナンバーは緑です。', False),
}

def yobu(p, obj=None):
    q = ur.Request(SITE + p, data=json.dumps(obj).encode('utf-8') if obj is not None else None,
                   method='POST' if obj is not None else 'GET')
    q.add_header('Authorization', 'Basic ' + base64.b64encode(os.environ['IZK_AUTH'].encode()).decode())
    q.add_header('User-Agent', 'Mozilla/5.0')
    if obj is not None:
        q.add_header('Content-Type', 'application/json; charset=utf-8')
    return json.load(ur.urlopen(q, timeout=120))

def block(mid, url, alt, cap):
    return (u'<!-- wp:image {"id":%d,"sizeSlug":"large","linkDestination":"none","fontSize":"medium"} -->\n'
            u'<figure class="wp-block-image size-large has-medium-font-size"><img src="%s" alt="%s" class="wp-image-%d"/>'
            u'<figcaption class="wp-element-caption">%s</figcaption></figure>\n<!-- /wp:image -->\n\n' % (mid, url, alt, mid, cap))

def main():
    kaku = '--apply' in sys.argv and '--yes' in sys.argv
    bango = [a for a in sys.argv[1:] if a in GAZOU]
    if not bango:
        print(u'番号を指定してください（例: 01）'); sys.exit(1)
    x = yobu('/wp/v2/posts/%d?context=edit' % PID)
    if x['status'] != 'draft':
        print(u'下書きではありません（%s）。中止します。' % x['status']); sys.exit(1)
    body = x['content']['raw']
    print(u'書き込み: ' + (u'する' if kaku else u'しない（確かめるだけ）'))
    featured = None
    for b in bango:
        mid, mark, alt, cap, eye = GAZOU[b]
        if ('wp-image-%d' % mid) in body:
            print(u'%s: もう配置されています。飛ばします。' % b); continue
        n = body.count(mark)
        if n != 1:
            print(u'%s: 目印が %d 回あります（1回のはず）。中止します。' % (b, n)); sys.exit(1)
        m = yobu('/wp/v2/media/%d?context=edit' % mid)
        url = m['media_details']['sizes'].get('large', {}).get('source_url') or m['source_url']
        new = body.replace(mark, block(mid, url, alt, cap) + mark)
        SEN = u'\x00'
        assert new.replace(block(mid, url, alt, cap) + mark, SEN) == body.replace(mark, SEN)
        print(u'%s: メディア %d を「%s…」の直前に置きます' % (b, mid, mark.split('>')[-1][:12]))
        body = new
        if eye: featured = mid
        if kaku:
            yobu('/wp/v2/media/%d' % mid, {'alt_text': alt, 'post': PID})
    if not kaku:
        return
    data = {'content': body}
    if featured: data['featured_media'] = featured
    yobu('/wp/v2/posts/%d' % PID, data)
    y = yobu('/wp/v2/posts/%d?context=edit' % PID)
    assert y['content']['raw'] == body and y['status'] == 'draft'
    if featured: assert y['featured_media'] == featured
    print(u'配置しました。状態は %s のまま。アイキャッチ: %s' % (y['status'], y['featured_media']))

main()
