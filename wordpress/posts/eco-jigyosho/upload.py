# -*- coding: utf-8 -*-
u"""認定書の画像（PDFから取り出したJPEG）をメディアに登録する。
鍵は IZK_AUTH からだけ読む。--apply と --yes の両方がなければ書き込まない。"""
import os, sys, json, base64, urllib.request as ur
SITE = 'https://www.ishinazaka.co.jp/wp-json'
SRC = sys.argv[1]
NAME = 'iwate-eco-jigyosho-ninteisho-2026-tate.jpg'
ALT = u'「いわて地球環境にやさしい事業所」認定書。認定番号8-3-1、認定区分は三つ星、事業所名は株式会社 石名坂、認定期間は令和8年10月16日から令和11年10月31日まで。岩手県知事名。'
kaku = '--apply' in sys.argv and '--yes' in sys.argv
data = open(SRC, 'rb').read()
print(u'書き込み: ' + (u'する' if kaku else u'しない'), u'／ 画像 %d KB' % (len(data) // 1024))
if not kaku: sys.exit()
q = ur.Request(SITE + '/wp/v2/media', data=data, method='POST')
q.add_header('Authorization', 'Basic ' + base64.b64encode(os.environ['IZK_AUTH'].encode()).decode())
q.add_header('User-Agent', 'Mozilla/5.0'); q.add_header('Content-Type', 'image/jpeg')
q.add_header('Content-Disposition', 'attachment; filename="%s"' % NAME)
m = json.load(ur.urlopen(q, timeout=180))
q2 = ur.Request(SITE + '/wp/v2/media/%d' % m['id'], data=json.dumps({'alt_text': ALT, 'title': u'いわて地球環境にやさしい事業所 認定書（三つ星）'}).encode('utf-8'), method='POST')
for k, v in (('Authorization', 'Basic ' + base64.b64encode(os.environ['IZK_AUTH'].encode()).decode()), ('User-Agent', 'Mozilla/5.0'), ('Content-Type', 'application/json; charset=utf-8')): q2.add_header(k, v)
m2 = json.load(ur.urlopen(q2, timeout=60))
print(u'登録しました。メディアID %d ／ %s ／ %sx%s' % (m2['id'], m2['source_url'], m2['media_details'].get('width'), m2['media_details'].get('height')))
