# -*- coding: utf-8 -*-
u"""出典確認Aの直し（事実のずれ）を、公開済みの記事に反映する。

  安全のための約束
  ・鍵は環境変数 IZK_AUTH からしか読まない。標準出力にも絶対に出さない。
  ・--apply と --yes の両方がなければ、何も書き込まない。
  ・触るのは下の SHIRO に並べた6本の記事だけ。
  ・置き換えは「その文字列がちょうど何回あるか」を数え、合わないときは中止する。
  ・書き込んだあと、必ず読み返して確かめる。

  使い方
    python3 naoshi_a.py                 下見（何も書き込まない）
    python3 naoshi_a.py --apply --yes   反映する
"""
import os, sys, json, base64, io
import urllib.request

API = u'https://www.ishinazaka.co.jp/wp-json/wp/v2/posts/%d?context=edit'

# 記事番号 -> (投稿ID, 手元のファイル)
SHIRO = {
    1: (6188, 'part-1.html'),
    2: (6209, 'part-2.html'),
    3: (6210, 'part-3.html'),
    4: (6189, 'part-4.html'),
    5: (6212, 'part-5.html'),
    6: (6213, 'part-6.html'),
}

# (記事番号, 見出し, 前, 後, いくつあるはず)
NAOSHI = [
 # ---- 第1回：Nature の「表紙」は裏づけが取れなかった ----
 (1, u'A-1 表紙（本文）',
  u'論文は『Nature』の1999年4月29日号に載り、表紙を飾っています。',
  u'論文は『Nature』の1999年4月29日号に載りました。', 1),
 (1, u'A-1 表紙（図版）',
  u'「クーパー対箱」。Nature の表紙に',
  u'「クーパー対箱」。Nature 1999年4月29日号', 1),

 # ---- 第2回：50量子ビットに要したメモリは約2ペタバイト（2,048TiB） ----
 (2, u'A-2 メモリ（本文）',
  u'そのとき必要だったメモリは、<strong>1ペタバイト（100万ギガバイト）を超えています。</strong>',
  u'そのとき必要だったメモリは、<strong>約2ペタバイト（200万ギガバイト）です。</strong>', 1),
 (2, u'A-2 メモリ（1個増えると倍）',
  u'<strong>51量子ビットなら、約4ペタバイト。</strong>たった1個増えるだけで、必要なメモリが跳ね上がります。',
  u'<strong>51量子ビットなら、約4ペタバイト。</strong>たった1個増えるだけで、必要なメモリが倍になります。', 1),
 (2, u'A-2 メモリ（図版の説明文）',
  u'1ペタバイトを超えるメモリを要するが',
  u'約2ペタバイトのメモリを要するが', 1),
 (2, u'A-2 メモリ（図版）',
  u'>メモリ 1ペタバイト超<',
  u'>メモリ 約2ペタバイト<', 1),
 (2, u'A-2 メモリ（まとめ）',
  u'50量子ビットの再現に1ペタバイト超、51個で約4ペタバイト。',
  u'50量子ビットの再現に約2ペタバイト、51個で約4ペタバイト。', 1),

 # ---- 第4回：IBMの反論は「直後」ではなく、ほぼ同時 ----
 (4, u'A-4 IBMの反論の時期',
  u'ところが直後にIBMが「工夫すれば2日半でできる」と反論。',
  u'ところが、その発表とほぼ同時にIBMが「工夫すれば2日半でできる」と反論。', 1),
 # ---- 第4回：Nature編集部の言葉は「査読の記録」に書かれていた ----
 (4, u'A-5 Nature編集部（本文）',
  u'ところが、同じ時期に科学誌『Nature』に載った論文に、<strong>編集部が異例の注記をつけました。</strong>',
  u'ところが、同じ時期に科学誌『Nature』に載った論文とあわせて公開された査読の記録に、'
  u'<strong>編集部がこう書き残しています。</strong>', 1),
 (4, u'A-5 Nature編集部（まとめ）',
  u'Nature編集部が「証拠にはなっていない」と注記した例があります。',
  u'Nature編集部が「証拠にはなっていない」と書き残した例があります。', 1),
 # ---- 第4回：Googleの誤り訂正は2024年12月。Microsoftは2025年2月 ----
 (4, u'A-6 「同じ」が合っていない',
  u'なお同じ2024年12月、Googleが発表した誤り訂正の成果は',
  u'なお、その少し前の2024年12月に、Googleが発表した誤り訂正の成果は', 1),
 # ---- 第4回：フアン氏の実際の発言 ----
 (4, u'A-8 フアン氏の発言',
  u'2025年1月に「本当に役に立つ量子コンピュータは15年から30年先」と述べました。',
  u'2025年1月に「本当に役に立つ量子コンピュータは、15年では早すぎ、30年では遅すぎる。'
  u'20年なら多くの人が納得する」と述べました。', 1),

 # ---- 第5回：ハーバー・ボッシュ法の条件はJSTの記載どおりに。エネルギー割合は出典なし ----
 (5, u'A-9 ハーバー・ボッシュ法（本文）',
  u'400〜500度、数百気圧。人類が使う全エネルギーの数パーセントを、この工程が使っているとされます。',
  u'400〜600度、100〜200気圧。大量のエネルギーを使う工程です。', 1),
 (5, u'A-9 ハーバー・ボッシュ法（図版の説明文）',
  u'工場では400から500度・数百気圧を要し人類の全エネルギーの数パーセントを使う一方',
  u'工場では400から600度・100から200気圧を要し大量のエネルギーを使う一方', 1),
 (5, u'A-9 ハーバー・ボッシュ法（図版・温度）',
  u'>400〜500度</text>', u'>400〜600度</text>', 1),
 (5, u'A-9 ハーバー・ボッシュ法（図版・気圧）',
  u'>数百気圧</text>', u'>100〜200気圧</text>', 1),
 (5, u'A-10 エネルギー割合（図版）',
  u'>人類が使う全エネルギーの数パーセント</text>',
  u'>エネルギーを大量に使う工程</text>', 1),

 # ---- 最終回：出典は「15と21」ではなく「35以下」 ----
 (6, u'A-11 35以下（本文）',
  u'実際の量子コンピュータでこの手順を使って因数分解できた最大の数は、<strong>15と21</strong>'
  u'だと2024年の学術的な調査は報告しています。',
  u'実際の量子コンピュータでこの手順を使って因数分解できたのは、<strong>35以下のごく小さな数</strong>'
  u'だけだと2024年の学術的な調査は報告しています。', 1),
 (6, u'A-11 35以下（結び）',
  u'実機で因数分解できた最大の数は15と21。方式すら決まっていない。',
  u'実機で因数分解できたのは35以下のごく小さな数。方式すら決まっていない。', 1),
 (6, u'A-11 35以下（まとめ）',
  u'ただし実機で因数分解できた最大の数は15と21です。',
  u'ただし実機で因数分解できたのは、35以下のごく小さな数だけです。', 1),
]


def kagi():
    v = os.environ.get('IZK_AUTH')
    if not v:
        raise SystemExit(u'環境変数 IZK_AUTH が空です。鍵を渡してから実行してください。')
    return u'Basic ' + base64.b64encode(v.encode('utf-8')).decode('ascii')


def yomu(pid, auth):
    q = urllib.request.Request(API % pid, headers={'Authorization': auth})
    with urllib.request.urlopen(q, timeout=60) as r:
        return json.loads(r.read().decode('utf-8'))


def kaku(pid, honbun, auth):
    body = json.dumps({'content': honbun}).encode('utf-8')
    q = urllib.request.Request(API % pid, data=body, headers={
        'Authorization': auth, 'Content-Type': 'application/json'})
    with urllib.request.urlopen(q, timeout=90) as r:
        return json.loads(r.read().decode('utf-8'))


def ateru(honbun, n, kuchi):
    u"""n番の記事の本文に、直しを当てる。合わないときは例外。"""
    kazu = 0
    for (bn, midashi, mae, ato, hazu) in NAOSHI:
        if bn != n:
            continue
        aru = honbun.count(mae)
        if aru != hazu:
            raise SystemExit(u'【中止】%s：%d個あるはずが %d個でした。何も書き込んでいません。'
                             % (midashi, hazu, aru))
        if honbun.count(ato) and ato in honbun:
            pass  # 後の文字列が既にあっても、前の文字列が正しい数あるなら進める
        honbun = honbun.replace(mae, ato)
        kuchi.append(u'  ○ %s' % midashi)
        kazu += 1
    return honbun, kazu


def main():
    yaru = '--apply' in sys.argv and '--yes' in sys.argv
    here = os.path.dirname(os.path.abspath(__file__))

    print(u'■ まず手元のファイルで、直しがぴたりと当たるかを確かめます')
    tesaki = {}
    for n, (pid, f) in sorted(SHIRO.items()):
        if not any(x[0] == n for x in NAOSHI):
            continue
        s = io.open(os.path.join(here, f), encoding='utf-8').read()
        kuchi = []
        s2, kazu = ateru(s, n, kuchi)
        print(u'第%d回（%s）：%d件' % (n, f, kazu))
        for line in kuchi:
            print(line)
        tesaki[n] = (f, s2)

    if not yaru:
        print(u'\n下見はここまでです。書き込むときは --apply --yes をつけてください。')
        return

    auth = kagi()
    print(u'\n■ 公開中の記事に反映します')
    for n, (pid, f) in sorted(SHIRO.items()):
        if n not in tesaki:
            continue
        ima = yomu(pid, auth)
        honbun = ima['content']['raw']
        atarashii, kazu = ateru(honbun, n, [])
        if atarashii == honbun:
            print(u'第%d回（ID%d）：変わりません' % (n, pid))
            continue
        kaku(pid, atarashii, auth)
        nochi = yomu(pid, auth)['content']['raw']
        # 読み返して確かめる
        nokori = [m for (bn, md, m, a, h) in NAOSHI if bn == n and m in nochi]
        if nokori:
            print(u'第%d回（ID%d）：【要注意】直したはずの文字列が残っています' % (n, pid))
        else:
            print(u'第%d回（ID%d）：%d件を反映し、読み返して確かめました（%s）'
                  % (n, pid, kazu, ima['slug']))

    print(u'\n■ 手元のファイルも揃えます')
    for n, (f, s2) in sorted(tesaki.items()):
        io.open(os.path.join(here, f), 'w', encoding='utf-8').write(s2)
        print(u'  ○ %s' % f)


if __name__ == '__main__':
    main()
