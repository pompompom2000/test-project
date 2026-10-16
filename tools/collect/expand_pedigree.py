#!/usr/bin/env python3
"""血統表を再帰展開して、指定した先祖が含まれるかを全経路で探す。

netkeiba の5代血統表(blood_table)は32行。各行の先頭セルから
世代を復元できる（rowspanが 16/8/4/2/1 → 1〜5代前）。
5代前の32頭それぞれの血統表を引けば、合計10代まで展開できる。

ancestors(hid, depth) は {馬ID: (最小世代, 馬名)} を返す。
先祖は共有されるのでプロセス内でキャッシュする。
"""
import html, json, os, re, sys, time, urllib.request

UA = {'User-Agent': 'Mozilla/5.0'}
URL = 'https://db.netkeiba.com/horse/ped/{hid}/'
CACHE_FILE = 'data/analysis/ped-cache.json'
_CACHE = json.load(open(CACHE_FILE)) if os.path.exists(CACHE_FILE) else {}
_FETCHED = [0]


def ped5(hid, sleep=0.8):
    """1〜5代前の先祖を [(世代, id, 名前)] で返す。"""
    if hid in _CACHE:
        return [tuple(x) for x in _CACHE[hid]]
    with urllib.request.urlopen(urllib.request.Request(URL.format(hid=hid), headers=UA),
                                timeout=40) as r:
        s = r.read().decode('euc-jp', 'replace')
    _FETCHED[0] += 1
    time.sleep(sleep)
    m = re.search(r'(?is)<table[^>]*class="[^"]*blood_table[^"]*"[^>]*>(.*?)</table>', s)
    out = []
    if m:
        # rowspan 16/8/4/2/1 が 1/2/3/4/5代前に対応する
        span2gen = {'16': 1, '8': 2, '4': 3, '2': 4, '1': 5}
        for row in re.findall(r'(?is)<tr[^>]*>(.*?)</tr>', m.group(1)):
            for attr, cell in re.findall(r'(?is)<td([^>]*)>(.*?)</td>', row):
                rs = re.search(r'rowspan="?(\d+)', attr)
                gen = span2gen.get(rs.group(1) if rs else '1')
                if not gen:
                    continue
                a = re.search(r'/horse/(?:ped/)?(\w+)/"[^>]*>([^<]+)<', cell)
                if a:
                    out.append((gen, a.group(1),
                                html.unescape(a.group(2)).replace('\xa0', ' ').strip()))
    _CACHE[hid] = out
    return out


def ancestors(hid, depth=10, sleep=0.8):
    """depth代前までの全先祖 {id: (最小世代, 名前)}。"""
    found, frontier = {}, [(hid, 0)]
    while frontier:
        nxt = []
        for base, off in frontier:
            if off >= depth:
                continue
            for gen, aid, name in ped5(base, sleep):
                g = off + gen
                if g > depth:
                    continue
                if aid not in found or found[aid][0] > g:
                    found[aid] = (g, name)
                if gen == 5 and g < depth:
                    nxt.append((aid, g))
        frontier = nxt
    return found


def save_cache():
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    json.dump(_CACHE, open(CACHE_FILE, 'w'), ensure_ascii=False)


if __name__ == '__main__':
    hid = sys.argv[1]
    depth = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    a = ancestors(hid, depth)
    save_cache()
    print(f'{len(a)}頭の先祖（{depth}代まで） 取得ページ数 {_FETCHED[0]}')
    for t in ("bunty's flight", 'miss disco', 'bold ruler', 'french deputy'):
        hit = [(g, n) for i, (g, n) in a.items()
               if t in re.sub(r"[’'`]", "'", n).lower()]
        print(f'  {t:<18}', hit if hit else '—')
