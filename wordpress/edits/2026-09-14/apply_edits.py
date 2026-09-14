"""石名坂：承認済みの10件を、WordPress REST API で適用する。

・記事ごとに、直前にもう一度読み直してから置き換える
・置き換え前の本文を backup-<id>-before.txt に保存する
・old が想定の件数見つからない箇所は、飛ばして報告する
・content 以外の項目は送らない（タイトル・公開状態などは触らない）
"""
import base64
import io
import json
import os
import sys
import time
import urllib.request

SITE = 'https://www.ishinazaka.co.jp'
AUTH = os.environ['IZK_AUTH']
HDR = {
    'Authorization': 'Basic ' + base64.b64encode(AUTH.encode()).decode(),
    'Content-Type': 'application/json; charset=utf-8',
    'User-Agent': 'izk-edit/1.0',
}


def api(path, data=None, method='GET'):
    body = json.dumps(data, ensure_ascii=False).encode('utf-8') if data is not None else None
    req = urllib.request.Request(SITE + path, data=body, headers=HDR, method=method)
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode('utf-8'))


def nth_replace(s, old, new, nth):
    """nth 番目に出てくる old だけを new に置き換える"""
    idx = -1
    for _ in range(nth):
        idx = s.find(old, idx + 1)
        if idx < 0:
            return None
    return s[:idx] + new + s[idx + len(old):]


edits = json.load(io.open(sys.argv[1], encoding='utf-8'))

by_post = {}
for e in edits:
    by_post.setdefault(e['pid'], []).append(e)

results = []
for pid, items in by_post.items():
    # 投稿か固定ページか。edits 側で kind を指定できる（既定は投稿）
    kind = items[0].get('kind', 'posts')

    current = api('/wp-json/wp/v2/%s/%d?context=edit' % (kind, pid))
    raw = current['content']['raw']
    io.open('backup-%d-before.txt' % pid, 'w', encoding='utf-8').write(raw)

    new_raw = raw
    applied = []
    for e in items:
        found = new_raw.count(e['old'])

        # nth が "all" のときは、見つかったものを全部置き換える
        if e['nth'] == 'all':
            if found == 0:
                results.append((pid, e['name'], '× 見つからない'))
                continue
            new_raw = new_raw.replace(e['old'], e['new'])
            applied.append('%s（%d件）' % (e['name'], found))
            continue

        if found < e['nth']:
            results.append((pid, e['name'], '× 見つからない（%d件）' % found))
            continue
        out = nth_replace(new_raw, e['old'], e['new'], e['nth'])
        if out is None:
            results.append((pid, e['name'], '× 置換できず'))
            continue
        new_raw = out
        applied.append(e['name'])

    if new_raw == raw:
        results.append((pid, '(全体)', '― 変更なし。送信しません'))
        continue

    saved = api('/wp-json/wp/v2/%s/%d' % (kind, pid), {'content': new_raw}, method='POST')
    io.open('backup-%d-after.txt' % pid, 'w', encoding='utf-8').write(saved['content']['raw'])

    for name in applied:
        results.append((pid, name, '○ 反映'))
    results.append((pid, '(保存)', '○ 更新 ' + str(saved.get('modified', ''))))
    time.sleep(0.6)

print('%5s  %-30s %s' % ('記事', '内容', '結果'))
print('-' * 68)
for pid, name, status in results:
    print('%5d  %-30s %s' % (pid, name, status))
