# -*- coding: utf-8 -*-
u"""連載6本の公開日時を、第1回から順に並ぶように振り直す。

  なぜ要るか
  第1回（ID6188）と第4回（ID6189）は、もとの「前編」「後編」の中身を
  入れ替えて使ったため、前編・後編を公開した9月15日夜の日時が残っている。
  そのせいでお知らせ一覧の並びが崩れている。

  安全のための約束
  ・鍵は環境変数 IZK_AUTH からしか読まない。標準出力にも出さない。
  ・--apply と --yes の両方がなければ、何も書き込まない。
  ・触るのは下に並べた6本だけ。slug が合わなければ中止する。
  ・本文には一切触らない。date と date_gmt だけを送る。
  ・書き込んだあと、必ず読み返して確かめる。
"""
import os, sys, json, base64
import urllib.request
from datetime import datetime, timedelta

API = u'https://www.ishinazaka.co.jp/wp-json/wp/v2/posts/%d?context=edit'

# (投稿ID, slug, 呼び名, 新しい公開日時。日本時間)
YOTEI = [
    (6188, 'quantum-computer-01-basics',       u'第1回',   '2026-09-16T08:41:00'),
    (6209, 'quantum-computer-02-why-fast',     u'第2回',   '2026-09-16T08:42:00'),
    (6210, 'quantum-computer-03-misconceptions', u'第3回', '2026-09-16T08:43:00'),
    (6189, 'quantum-computer-04-status-now',   u'第4回',   '2026-09-16T08:44:00'),
    (6212, 'quantum-computer-05-applications', u'第5回',   '2026-09-16T08:45:00'),
    (6213, 'quantum-computer-06-cryptography', u'最終回',  '2026-09-16T08:46:00'),
]
JST = timedelta(hours=9)


def kagi():
    v = os.environ.get('IZK_AUTH')
    if not v:
        raise SystemExit(u'環境変数 IZK_AUTH が空です。')
    return u'Basic ' + base64.b64encode(v.encode('utf-8')).decode('ascii')


def yomu(pid, auth):
    q = urllib.request.Request(API % pid, headers={'Authorization': auth})
    with urllib.request.urlopen(q, timeout=60) as r:
        return json.loads(r.read().decode('utf-8'))


def kaku(pid, dt, auth):
    gmt = (datetime.strptime(dt, '%Y-%m-%dT%H:%M:%S') - JST).strftime('%Y-%m-%dT%H:%M:%S')
    body = json.dumps({'date': dt, 'date_gmt': gmt}).encode('utf-8')
    q = urllib.request.Request(API % pid, data=body, headers={
        'Authorization': auth, 'Content-Type': 'application/json'})
    with urllib.request.urlopen(q, timeout=90) as r:
        return json.loads(r.read().decode('utf-8'))


def main():
    yaru = '--apply' in sys.argv and '--yes' in sys.argv
    auth = kagi()

    print(u'■ いまの公開日時')
    ima = {}
    for pid, slug, na, atarashii in YOTEI:
        p = yomu(pid, auth)
        if p['slug'] != slug:
            raise SystemExit(u'【中止】ID%d の slug が %s ではなく %s でした。'
                             % (pid, slug, p['slug']))
        if p['status'] != 'publish':
            raise SystemExit(u'【中止】ID%d が公開状態ではありません（%s）。' % (pid, p['status']))
        ima[pid] = p
        shirushi = u'  ' if p['date'].startswith(atarashii[:10]) else u'←'
        print(u'  %-4s %s  →  %s %s' % (na, p['date'], atarashii, shirushi))

    if not yaru:
        print(u'\n下見はここまでです。書き込むときは --apply --yes をつけてください。')
        return

    print(u'\n■ 振り直します（本文には触りません）')
    for pid, slug, na, atarashii in YOTEI:
        if ima[pid]['date'] == atarashii:
            print(u'  %-4s 変わりません' % na)
            continue
        mae_honbun = ima[pid]['content']['raw']
        kaku(pid, atarashii, auth)
        nochi = yomu(pid, auth)
        ok_hi = nochi['date'] == atarashii
        ok_hon = nochi['content']['raw'] == mae_honbun
        ok_st = nochi['status'] == 'publish'
        print(u'  %-4s %s／本文 %s／公開 %s'
              % (na, nochi['date'],
                 u'変わりなし' if ok_hon else u'【要注意】変わった',
                 u'のまま' if ok_st else u'【要注意】' + nochi['status']))
        if not (ok_hi and ok_hon and ok_st):
            raise SystemExit(u'【中止】%s で思わぬ変化がありました。' % na)


if __name__ == '__main__':
    main()
