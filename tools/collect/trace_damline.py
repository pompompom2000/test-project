#!/usr/bin/env python3
"""馬の牝系（母→母の母→…）を遡る。

netkeiba の5代血統表は、母側の先頭セルが行16/24/28/30/31に並ぶ。
最後（5代母）のIDから再帰して、さらに5代遡る。

使い方: python3 tools/collect/trace_damline.py <horse_id> [深さ]
"""
import html, json, os, re, sys, time, urllib.request

UA = {'User-Agent': 'Mozilla/5.0'}
URL = 'https://db.netkeiba.com/horse/ped/{hid}/'
CACHE = {}


def dam_line_5(hid):
    """この馬の母・母母・母母母・母母母母・母母母母母 を返す。"""
    if hid in CACHE:
        return CACHE[hid]
    with urllib.request.urlopen(urllib.request.Request(URL.format(hid=hid), headers=UA),
                                timeout=40) as r:
        s = r.read().decode('euc-jp', 'replace')
    m = re.search(r'(?is)<table[^>]*class="[^"]*blood_table[^"]*"[^>]*>(.*?)</table>', s)
    if not m:
        CACHE[hid] = []
        return []
    rows = re.findall(r'(?is)<tr[^>]*>(.*?)</tr>', m.group(1))
    out = []
    for ri in (16, 24, 28, 30, 31):           # 母側の先頭セルが並ぶ行
        if ri >= len(rows):
            break
        td = re.search(r'(?is)<td[^>]*>(.*?)</td>', rows[ri])
        if not td:
            break
        a = re.search(r'/horse/(?:ped/)?(\w+)/"[^>]*>([^<]+)<', td.group(1))
        if not a:
            break
        name = html.unescape(a.group(2)).replace('\xa0', ' ').strip()
        out.append({'id': a.group(1), 'name': name})
    CACHE[hid] = out
    return out


def trace(hid, max_gen=20, sleep=0.9):
    line, cur = [], hid
    while len(line) < max_gen:
        seg = dam_line_5(cur)
        time.sleep(sleep)
        if not seg:
            break
        for x in seg:
            if len(line) < max_gen:
                line.append(x)
        # 5代揃わなくても、取れた最後の先祖から続きを辿る
        # （血統表の一部にリンクが無い馬がいるため）
        nxt = seg[-1]['id']
        if nxt == cur:
            break
        cur = nxt
    return line


if __name__ == '__main__':
    hid = sys.argv[1]
    depth = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    for i, x in enumerate(trace(hid, depth), 1):
        print(f'{i:>2}代母  {x["name"]:<30}{x["id"]}')
