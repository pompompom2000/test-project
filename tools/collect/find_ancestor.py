#!/usr/bin/env python3
"""ある馬の血統をさかのぼって、指定した祖先がどこに入っているかを調べる。

5代血統表は1頭につき1フェッチで62セル取れる。目的の祖先が5代より前にいる
場合は、5代目の馬の5代血統表をさらに引いて継ぎ足す。同じ祖先は何頭もの
血統に現れるので、取得結果はキャッシュして二度引かない。

5代目セルには rowspan 属性が無い（省略＝1）ので、属性の有無で世代を決めると
32セルを丸ごと落とす。行×列のグリッドに復元する。

    python3 tools/collect/find_ancestor.py <対象馬ID> <祖先ID> [最大世代]
"""
import html, json, os, re, sys, time, urllib.request

UA = {'User-Agent': 'Mozilla/5.0'}
PED = 'https://db.netkeiba.com/horse/ped/{hid}/'
CACHE = 'data/analysis/ped-cache.json'
PAUSE = 2.2
_cache = None
_fetched = 0


def _load():
    global _cache
    if _cache is None:
        _cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    return _cache


def save():
    if _cache is not None:
        json.dump(_cache, open(CACHE, 'w'), ensure_ascii=False)


def get(url):
    last = None
    for i in range(6):
        try:
            b = urllib.request.urlopen(urllib.request.Request(url, headers=UA),
                                       timeout=40).read()
            for enc in ('euc_jp', 'utf-8'):
                try:
                    return b.decode(enc)
                except Exception:
                    pass
            return b.decode('utf-8', 'replace')
        except Exception as e:
            last = e
            time.sleep(5 * (i + 1))
    raise last


def ped5(hid):
    """馬ID -> {"g,i": [名前, ID]}。gは1..5、iは0..2^g-1（ビット0=父,1=母、上位が手前）。"""
    global _fetched
    c = _load()
    if hid in c:
        return c[hid]
    s = get(PED.format(hid=hid))
    _fetched += 1
    time.sleep(PAUSE)
    tb = re.search(r'(?is)<table[^>]*class="[^"]*blood_table[^"]*"[^>]*>(.*?)</table>', s)
    out = {}
    if tb:
        occ = {}
        for r, row in enumerate(re.findall(r'(?is)<tr[^>]*>(.*?)</tr>', tb.group(1))):
            for attr, cell in re.findall(r'(?is)<td([^>]*)>(.*?)</td>', row):
                col = 0
                while occ.get((r, col)):
                    col += 1
                sp = re.search(r'rowspan="(\d+)"', attr)
                span = int(sp.group(1)) if sp else 1
                for k in range(span):
                    occ[(r + k, col)] = True
                nm = html.unescape(re.sub(r'<[^>]+>', '', cell)).replace('\xa0', ' ').strip()
                nm = nm.split('\n')[0].strip()
                mid = re.search(r'/horse/(?:ped/)?([0-9a-z]{10})', cell)
                g = col + 1
                if g <= 5:
                    out[f'{g},{r // (32 >> g)}'] = [nm, mid.group(1) if mid else None]
    c[hid] = out
    return out


def path_str(g, i):
    """(世代, 通し番号) -> 父母のたどり方。"""
    return ''.join('母' if (i >> (g - 1 - k)) & 1 else '父' for k in range(g))


def find(start_id, target_id, max_gen=9, dam_only=True):
    """start_id から target_id に至る経路をすべて返す。世代は start_id から数える。"""
    hits, frontier = [], [(start_id, 0, '')]
    seen = set()
    while frontier:
        nxt = []
        for hid, base, pre in frontier:
            if hid is None or (hid, base) in seen:
                continue
            seen.add((hid, base))
            grid = ped5(hid)
            for key, (nm, mid) in grid.items():
                g, i = (int(x) for x in key.split(','))
                gen = base + g
                if gen > max_gen:
                    continue
                p = pre + path_str(g, i)
                if dam_only and not p.startswith('母'):
                    continue
                if mid == target_id:
                    hits.append((gen, p, nm))
                elif g == 5 and gen < max_gen and mid:
                    nxt.append((mid, gen, p))
        if hits:          # 最短世代で見つかったらそこで打ち切る
            break
        frontier = nxt
    return sorted(set(hits))


def main():
    start, target = sys.argv[1], sys.argv[2]
    mg = int(sys.argv[3]) if len(sys.argv) > 3 else 9
    try:
        for gen, p, nm in find(start, target, mg):
            print(f'  {gen}代前  {p}  {nm}')
    finally:
        save()
        print(f'  （新規取得 {_fetched} 件）')


if __name__ == '__main__':
    main()
