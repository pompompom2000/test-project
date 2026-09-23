# -*- coding: utf-8 -*-
u"""
VR動画3本の説明文（meta description）の取り違えを直す。

  第2弾・第3弾の説明文が、第1弾のまま複製されていた。
  検索結果に3本とも「第1弾」と表示されていた。

  それぞれの中身は、記事の見出しとYouTube側の動画題名で確かめた。
    第1弾 1BL北西側から4BL南西へ南向き／向中野22号線を西から東へ
    第2弾 屋敷田線を北から南へ／屋敷田2号線を西から東へ
    第3弾 西仙北津志田線を北から南へ

  ・鍵は環境変数 IZK_AUTH からしか読まない。標準出力にも出さない。
  ・--apply と --yes の両方がなければ、何も書き込まない。
  ・いまの値が想定どおりであることを確かめてから書き込む。
  ・AIOSEOの窓口は送らなかった項目を消すので、題名も一緒に送る。
  ・記事の本文・綴り・公開状態には触らない。書き込んだあと読み返す。
"""
import os, sys, json, base64
import urllib.request as ur

ATO = {
 'post-286': u'盛岡市の株式会社石名坂が手掛ける、道明地区新産業等用地（第二事業区）'
             u'基盤整備工事のVR動画（第2弾）です。屋敷田線を北から南へ、'
             u'屋敷田2号線を西から東へ移動する現場の様子を、VRでリアルに体感いただけます。',
 'post-289': u'盛岡市の株式会社石名坂が手掛ける、道明地区新産業等用地（第二事業区）'
             u'基盤整備工事のVR動画（第3弾）です。西仙北津志田線を北から南へ'
             u'移動する現場の様子を、VRでリアルに体感いただけます。',
}

kagi = os.environ.get('IZK_AUTH')
if not kagi:
    print(u'環境変数 IZK_AUTH がありません。'); sys.exit(1)
ATAMA = {'Authorization': 'Basic ' + base64.b64encode(kagi.encode()).decode()}


def yobu(p, obj=None):
    q = ur.Request('https://www.ishinazaka.co.jp/wp-json' + p,
                   data=json.dumps(obj).encode('utf-8') if obj else None,
                   method='POST' if obj else 'GET')
    for k, v in ATAMA.items():
        q.add_header(k, v)
    if obj:
        q.add_header('Content-Type', 'application/json; charset=utf-8')
    return json.load(ur.urlopen(q, timeout=90))


def main():
    yaru = ('--apply' in sys.argv) and ('--yes' in sys.argv)
    print(u'書き込み:', u'する' if yaru else u'しない（調べるだけ）')

    for slug, atara in sorted(ATO.items()):
        d = yobu('/wp/v2/posts?slug=%s&context=edit' % slug)[0]
        c = yobu('/aioseo/v1/post?postId=%d' % d['id'])['data']['currentPost']
        ima_t = c.get('title') or ''
        ima_d = c.get('description') or ''
        honbun = d['content']['raw']

        print(u'\n■ %s（ID %d）' % (slug, d['id']))
        if ima_d == atara:
            print(u'  もう直っています。'); continue
        assert u'（第1弾）' in ima_d, u'「第1弾」が入っていない。中止します。'
        print(u'  前 %s' % ima_d)
        print(u'  後 %s' % atara)
        print(u'  %d字 → %d字' % (len(ima_d), len(atara)))

        if not yaru:
            continue

        okuri = {'id': d['id'], 'title': ima_t, 'description': atara}
        if c.get('keyphrases'):
            okuri['keyphrases'] = c['keyphrases']
        yobu('/aioseo/v1/post', okuri)

        c2 = yobu('/aioseo/v1/post?postId=%d' % d['id'])['data']['currentPost']
        d2 = yobu('/wp/v2/posts/%d?context=edit' % d['id'])
        assert (c2.get('description') or '') == atara, u'説明文が入っていない'
        assert (c2.get('title') or '') == ima_t, u'題名が変わった'
        assert d2['content']['raw'] == honbun, u'本文が変わった'
        assert d2['slug'] == slug and d2['status'] == 'publish'
        print(u'  入れました（読み返し一致。本文は変わっていません）')

    if not yaru:
        print(u'\n--apply --yes が無いので、ここで終わります。')


if __name__ == '__main__':
    main()
