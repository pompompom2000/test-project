#!/usr/bin/env python3
"""1頭軸と2頭軸の比較用に、着順3頭の人気順位と3連複払戻を集める。

各レースから必要なのは次の3つだけ:
  - 出走頭数
  - 馬券内3頭の「人気順位」
  - 3連複の確定払戻
払戻表の組（馬番）を結果表の人気に対応させるので、降着・同着も正しく扱える。

使い方:
  python3 tools/collect/collect_trio_payouts.py list 2025     # レースIDを集める
  python3 tools/collect/collect_trio_payouts.py fetch         # 結果と払戻を取る
"""
import datetime, html, json, os, re, sys, time, urllib.request

UA = {'User-Agent': 'Mozilla/5.0'}
LIST = 'https://db.netkeiba.com/race/list/{d}/'
RESULT = 'https://db.netkeiba.com/race/{rid}/'
IDS = 'data/analysis/trio-races.json'
OUT = 'data/analysis/trio-payouts.json'
SKIP = 'data/analysis/trio-skipped.json'


def get(url, enc='euc-jp'):
    """db.netkeiba はアクセスが詰まると400を返す。待って数回やり直す。"""
    last = None
    for i in range(5):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.read().decode(enc, 'replace')
        except Exception as e:
            last = e
            time.sleep(3.0 * (i + 1))
    raise last


def collect_ids(year, sleep=0.8):
    store = json.load(open(IDS)) if os.path.exists(IDS) else {'dates': [], 'races': {}}
    seen = set(store['dates'])
    d, dates = datetime.date(year, 1, 1), []
    while d.year == year:
        if d.weekday() >= 5:
            dates.append(d.strftime('%Y%m%d'))
        d += datetime.timedelta(days=1)
    todo = [x for x in dates if x not in seen]
    print(f'{len(todo)}日分', flush=True)
    for i, ds in enumerate(todo, 1):
        try:
            s = get(LIST.format(d=ds))
        except Exception as e:
            print(f'  {ds} ERR {e}', flush=True); time.sleep(1.0); continue
        for m in re.finditer(r'href="https://db\.netkeiba\.com/race/(\d{12})/"', s):
            store['races'].setdefault(m.group(1), {'date': ds})
        store['dates'].append(ds)
        if i % 20 == 0:
            json.dump(store, open(IDS, 'w'))
            print(f'  {i}/{len(todo)} レース{len(store["races"])}', flush=True)
        time.sleep(sleep)
    json.dump(store, open(IDS, 'w'))
    print(f'{IDS}: {len(store["races"])}レース')


def parse(rid):
    s = get(RESULT.format(rid=rid))
    tb = re.search(r'(?is)<table[^>]*class="[^"]*race_table_01[^"]*"[^>]*>(.*?)</table>', s)
    if not tb:
        return None
    rows = re.findall(r'(?is)<tr[^>]*>(.*?)</tr>', tb.group(1))
    if len(rows) < 4:
        return None
    cell = lambda row: [html.unescape(re.sub(r'<[^>]+>', '', x)).strip()
                        for x in re.findall(r'(?is)<t[dh][^>]*>(.*?)</t[dh]>', row)]
    hdr = [re.sub(r'\s+', ' ', h) for h in cell(rows[0])]
    # 列の並びはページによって違うので見出しで位置を引く
    try:
        i_no = next(i for i, h in enumerate(hdr) if h.startswith('馬番'))
        i_pop = next(i for i, h in enumerate(hdr) if h.startswith('人気'))
    except StopIteration:
        return None
    pop, runners = {}, 0
    for row in rows[1:]:
        c = cell(row)
        if len(c) <= max(i_no, i_pop) or not c[i_no].isdigit():
            continue
        runners += 1
        if c[i_pop].isdigit():
            pop[int(c[i_no])] = int(c[i_pop])
    if runners < 3:
        return None
    trio = []
    for pt in re.findall(r'(?is)<table[^>]*class="[^"]*pay_table_01[^"]*"[^>]*>(.*?)</table>', s):
        for row in re.findall(r'(?is)<tr[^>]*>(.*?)</tr>', pt):
            th = re.search(r'(?is)<th[^>]*>(.*?)</th>', row)
            if not th:
                continue
            lab = html.unescape(re.sub(r'<[^>]+>', '', th.group(1))).strip()
            if lab not in ('三連複', '3連複'):
                continue
            tds = re.findall(r'(?is)<td[^>]*>(.*?)</td>', row)
            if len(tds) < 2:
                continue
            combos = [x for x in re.split(r'(?i)<br\s*/?>', tds[0]) if x.strip()]
            pays = [x for x in re.split(r'(?i)<br\s*/?>', tds[1]) if x.strip()]
            for cb, py in zip(combos, pays):
                nos = [int(x) for x in re.findall(r'\d+', re.sub(r'<[^>]+>', '', cb))]
                yen = re.sub(r'[^\d]', '', re.sub(r'<[^>]+>', '', py))
                if len(nos) == 3 and yen:
                    trio.append({'nos': nos, 'pay': int(yen)})
    if not trio:
        return None
    out = []
    for t in trio:
        ps = [pop.get(n) for n in t['nos']]
        if any(p is None for p in ps):
            return None
        out.append({'pops': sorted(ps), 'pay': t['pay']})
    return {'runners': runners, 'trio': out}


def fetch(sleep=2.5):
    """取得できなかったレースは飛ばして続ける。400が続くときは間隔を伸ばす。"""
    ids = json.load(open(IDS))['races']
    done = json.load(open(OUT)) if os.path.exists(OUT) else {}
    skip = json.load(open(SKIP)) if os.path.exists(SKIP) else []
    bad = set(skip)
    todo = [r for r in sorted(ids) if r not in done and r not in bad]
    print(f'{len(todo)}レース（取得済み{len(done)}、失敗済み{len(bad)}）', flush=True)
    miss = 0
    for i, rid in enumerate(todo, 1):
        try:
            d = parse(rid)
            miss = 0
        except Exception as e:
            miss += 1
            bad.add(rid)
            if miss % 10 == 0:
                print(f'  {rid} 連続失敗{miss} 60秒待つ', flush=True)
                time.sleep(60)
            time.sleep(sleep)
            continue
        if d:
            d['date'] = ids[rid]['date']
            done[rid] = d
        if i % 100 == 0:
            json.dump(done, open(OUT, 'w'))
            json.dump(sorted(bad), open(SKIP, 'w'))
            print(f'  {i}/{len(todo)} 取得{len(done)} 失敗{len(bad)}', flush=True)
        time.sleep(sleep)
    json.dump(done, open(OUT, 'w'))
    json.dump(sorted(bad), open(SKIP, 'w'))
    print(f'{OUT}: {len(done)}レース（失敗 {len(bad)}）')


if __name__ == '__main__':
    if sys.argv[1] == 'list':
        collect_ids(int(sys.argv[2]))
    else:
        fetch()
