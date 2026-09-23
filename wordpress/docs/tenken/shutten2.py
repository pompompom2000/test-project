# -*- coding: utf-8 -*-
u"""
消えた岩手日報の出典2件を直す（kikouhendou-2050-iwate-nougyou）。

  一等米比率 … 数字の元の出どころである農林水産省のページへ差し替える。
  アワビ    … 同じ数字を載せた官公庁の資料が見つからなかった。
              リンクだけ外し、日付を足して残す（紙の新聞を引くのと同じ形）。
              あわせて、資源の状況を裏づける岩手県のページを1本足す。

  ・鍵は環境変数 IZK_AUTH からしか読まない。標準出力にも出さない。
  ・--apply と --yes の両方がなければ、何も書き込まない。
  ・文字の位置（何文字目か）は使わない。まるごと置き換える。
  ・置き換える塊がちょうど1回であることを数え、合わなければ中止する。
  ・その塊の外が1文字も変わっていないことを確かめてから書き込む。
  ・綴り（URL）と公開状態は変えない。書き込んだあと読み返す。
"""
import os, sys, json, base64
import urllib.request as ur

SLUG = 'kikouhendou-2050-iwate-nougyou'

AWABI_MAE = (u'<!-- wp:list-item -->\n'
             u'<li><a href="https://www.iwate-np.co.jp/article/2021/1/22/90948" '
             u'target="_blank" rel="noopener">アワビ水揚げ減少に関する報道'
             u'（岩手日報、2021年1月）</a></li>\n'
             u'<!-- /wp:list-item -->')
AWABI_ATO = (u'<!-- wp:list-item -->\n'
             u'<li>アワビ水揚げ減少に関する報道（岩手日報、2021年1月22日）'
             u'※記事の公開は終了しています</li>\n'
             u'<!-- /wp:list-item -->\n\n'
             u'<!-- wp:list-item -->\n'
             u'<li><a href="https://www.pref.iwate.jp/kensei/profile/1000655/1016282.html" '
             u'target="_blank" rel="noopener">アワビ（いわてお国自慢）（岩手県）</a></li>\n'
             u'<!-- /wp:list-item -->')

KOME_MAE = (u'<!-- wp:list-item -->\n'
            u'<li><a href="https://www.iwate-np.co.jp/article/2023/11/1/152924" '
            u'target="_blank" rel="noopener">2023年産米の一等米比率に関する報道'
            u'（岩手日報、2023年11月）</a></li>\n'
            u'<!-- /wp:list-item -->')
KOME_ATO = (u'<!-- wp:list-item -->\n'
            u'<li><a href="https://www.maff.go.jp/j/seisan/syoryu/kensa/kome/" '
            u'target="_blank" rel="noopener">米穀の農産物検査結果'
            u'（農林水産省。令和5年産＝2023年産の一等米比率）</a></li>\n'
            u'<!-- /wp:list-item -->')

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
    return json.load(ur.urlopen(q, timeout=120))


def main():
    yaru = ('--apply' in sys.argv) and ('--yes' in sys.argv)
    print(u'書き込み:', u'する' if yaru else u'しない（調べるだけ）')

    d = yobu('/wp/v2/posts?slug=%s&context=edit' % SLUG)[0]
    t = d['content']['raw']
    print(u'記事 %d / %s / 本文 %d字' % (d['id'], d['status'], len(t)))

    if 'iwate-np.co.jp' not in t:
        print(u'もう直っています。中止します。'); return

    for na, mae in ((u'アワビ', AWABI_MAE), (u'一等米', KOME_MAE)):
        n = t.count(mae)
        print(u'  %s の塊: %d 回' % (na, n))
        assert n == 1, u'1回ではない。中止します。'

    atarashii = t.replace(AWABI_MAE, AWABI_ATO).replace(KOME_MAE, KOME_ATO)
    assert t.replace(AWABI_MAE, u'\x00').replace(KOME_MAE, u'\x01') == \
           atarashii.replace(AWABI_ATO, u'\x00').replace(KOME_ATO, u'\x01'), u'外が変わっている'
    print(u'  この2か所の外は、1文字も変わっていません。')
    print(u'  本文 %d字 → %d字' % (len(t), len(atarashii)))
    print(u'  岩手日報へのリンク:', atarashii.count('iwate-np.co.jp'), u'本（0になるはず）')

    if not yaru:
        print(u'\n--apply --yes が無いので、ここで終わります。'); return

    yobu('/wp/v2/posts/%d' % d['id'], {'content': atarashii, 'status': 'publish'})
    m = yobu('/wp/v2/posts/%d?context=edit' % d['id'])
    assert m['content']['raw'] == atarashii, u'書き込んだものと違う'
    assert m['slug'] == SLUG and m['status'] == 'publish'
    assert 'iwate-np.co.jp' not in m['content']['raw']
    print(u'  入れました（読み返し一致）')


if __name__ == '__main__':
    main()
