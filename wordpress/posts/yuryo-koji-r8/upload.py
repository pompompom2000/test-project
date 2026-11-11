# -*- coding: utf-8 -*-
u"""表彰状などのスキャン画像をメディアに登録する。
鍵は IZK_AUTH からだけ読む。--apply と --yes の両方がなければ書き込まない。
使い方: IZK_AUTH=... python3 -I upload.py <jpg> <番号 01|02> --apply --yes"""
import os, sys, json, base64, urllib.request as ur
SITE = 'https://www.ishinazaka.co.jp/wp-json'
ZU = {
 '01': ('morioka-yuryo-koji-r8-hyoshojo.jpg',
        u'令和8年度 盛岡市優良建設工事表彰の表彰状。道明地区新産業等用地（第二事業区）基盤整備工事、石名坂・三陸土建特定共同企業体。令和8年11月11日、盛岡市長名。',
        u'令和8年度 盛岡市優良建設工事 表彰状'),
 '02': ('morioka-yuryo-koji-r8-shikijidai.jpg',
        u'令和8年度 盛岡市優良建設工事表彰式の式次第の表紙。令和8年11月11日午後2時、プラザおでって おでってホール、盛岡市。',
        u'令和8年度 盛岡市優良建設工事表彰式 式次第'),
}
SRC, BAN = sys.argv[1], sys.argv[2]
NAME, ALT, TITLE = ZU[BAN]
kaku = '--apply' in sys.argv and '--yes' in sys.argv
data = open(SRC, 'rb').read()
print(u'書き込み: ' + (u'する' if kaku else u'しない'), u'／ %s ／ 画像 %d KB' % (NAME, len(data) // 1024))
if not kaku: sys.exit()
q = ur.Request(SITE + '/wp/v2/media', data=data, method='POST')
q.add_header('Authorization', 'Basic ' + base64.b64encode(os.environ['IZK_AUTH'].encode()).decode())
q.add_header('User-Agent', 'Mozilla/5.0'); q.add_header('Content-Type', 'image/jpeg')
q.add_header('Content-Disposition', 'attachment; filename="%s"' % NAME)
m = json.load(ur.urlopen(q, timeout=180))
q2 = ur.Request(SITE + '/wp/v2/media/%d' % m['id'], data=json.dumps({'alt_text': ALT, 'title': TITLE}).encode('utf-8'), method='POST')
for k, v in (('Authorization', 'Basic ' + base64.b64encode(os.environ['IZK_AUTH'].encode()).decode()), ('User-Agent', 'Mozilla/5.0'), ('Content-Type', 'application/json; charset=utf-8')): q2.add_header(k, v)
m2 = json.load(ur.urlopen(q2, timeout=60))
print(u'登録しました。メディアID %d ／ %s ／ %sx%s' % (m2['id'], m2['source_url'], m2['media_details'].get('width'), m2['media_details'].get('height')))
