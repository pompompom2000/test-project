#!/usr/bin/env python3
"""京都芝2000mのレースを集め、父×コースを検証するためのデータを作る。

3段階:
  find   開催日のレース一覧(db.netkeiba.com/race/list/YYYYMMDD/)から
         京都・芝2000mのレースIDを集める
  fetch  各レースの結果(着順・人気・確定単勝オッズ)と
         出馬表(shutuba_past: 父が載っている)を取得
  （解析は別スクリプト）

京都は2020年4月〜2023年4月が改修で非開催。
"""
import datetime, html, json, os, re, sys, time, urllib.request

UA = {'User-Agent': 'Mozilla/5.0'}
LIST = 'https://db.netkeiba.com/race/list/{d}/'
RESULT = 'https://db.netkeiba.com/race/{rid}/'
SHUTUBA = 'https://race.netkeiba.com/race/shutuba_past.html?race_id={rid}'
RACES = 'data/analysis/kyoto2000-races.json'
DATA = 'data/analysis/kyoto2000-data.json'


def get(url, enc='euc-jp'):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
        return r.read().decode(enc, 'replace')


def find(years, sleep=0.8):
    out = json.load(open(RACES)) if os.path.exists(RACES) else {}
    seen = set(out.get('_dates', []))
    races = out.get('races', {})
    dates = []
    for y in years:
        d = datetime.date(y, 1, 1)
        while d.year == y:
            if d.weekday() >= 5:                 # 土日のみ（祝日開催は取りこぼす）
                dates.append(d.strftime('%Y%m%d'))
            d += datetime.timedelta(days=1)
    todo = [d for d in dates if d not in seen]
    print(f'{len(todo)}日分を確認', flush=True)
    for i, ds in enumerate(todo, 1):
        try:
            s = get(LIST.format(d=ds))
        except Exception as e:
            print(f'  {ds} ERROR {e}', flush=True)
            time.sleep(1.0)
            continue
        # 京都のレースで 芝2000 のものを拾う
        for m in re.finditer(
                r'href="https://db\.netkeiba\.com/race/(\d{12})/"[^>]*title="([^"]*)"[^>]*>.*?'
                r'</a><br\s*/?>\s*<div>\s*([^<]*)', s, re.S):
            rid, title, info = m.group(1), m.group(2), ' '.join(m.group(3).split())
            if rid[4:6] != '08':                 # 京都=08
                continue
            if not re.match(r'芝2000', info):
                continue
            races[rid] = {'date': f'{ds[:4]}-{ds[4:6]}-{ds[6:]}',
                          'title': html.unescape(title), 'info': info}
        seen.add(ds)
        if i % 50 == 0:
            json.dump({'_dates': sorted(seen), 'races': races},
                      open(RACES, 'w'), ensure_ascii=False)
            print(f'  [{i}/{len(todo)}] {ds} 累計{len(races)}レース', flush=True)
        time.sleep(sleep)
    json.dump({'_dates': sorted(seen), 'races': races}, open(RACES, 'w'), ensure_ascii=False)
    print(f'完了: 京都芝2000m {len(races)}レース')


def cells(row):
    return [' '.join(html.unescape(re.sub(r'<[^>]+>', ' ', x)).split())
            for x in re.findall(r'(?is)<t[dh][^>]*>(.*?)</t[dh]>', row)]


def fetch_one(rid):
    s = get(RESULT.format(rid=rid))
    m = re.search(r'(?is)<table[^>]*class="[^"]*race_table_01[^"]*"[^>]*>(.*?)</table>', s)
    if not m:
        return None
    rows = re.findall(r'(?is)<tr[^>]*>(.*?)</tr>', m.group(1))
    head = [h.replace(' ', '') for h in cells(rows[0])]

    def col(*names):
        for n in names:
            if n in head:
                return head.index(n)
    ino, ipop, iodds = col('馬番'), col('人気'), col('単勝')
    res = []
    for row in rows[1:]:
        c = cells(row)
        pm = re.match(r'^(\d+)', c[0]) if c else None
        if not pm or ino is None or len(c) <= ino:
            continue
        res.append({'place': int(pm.group(1)), 'no': int(c[ino]),
                    'popularity': int(c[ipop]) if ipop is not None and c[ipop].isdigit() else None,
                    'odds': float(c[iodds]) if iodds is not None and
                            re.fullmatch(r'[\d.]+', c[iodds] or '') else None})
    time.sleep(0.6)
    # 出馬表から父を取る
    t = get(SHUTUBA.format(rid=rid), 'utf-8')
    sires = {}
    for blk in re.findall(r'(?is)<td class="Horse_Info"[^>]*>(.*?)</td>', t):
        sm = re.search(r'(?is)<div class="Horse01[^"]*">([^<]*)</div>', blk)
        hm = re.search(r'(?is)<div class="Horse02">.*?/horse/(\d+)[^>]*>\s*([^<]+)</a>', blk)
        if sm and hm:
            sires[hm.group(2).strip()] = {'sire': sm.group(1).strip(), 'horseId': hm.group(1)}
    # 馬名は結果表から引く必要があるので、着順表の馬名も取る
    names = {}
    for row in rows[1:]:
        c = cells(row)
        pm = re.match(r'^(\d+)', c[0]) if c else None
        inm = col('馬名')
        if pm and inm is not None and len(c) > inm:
            names[int(c[ino])] = c[inm]
    for r in res:
        nm = names.get(r['no'], '')
        r['name'] = nm
        info = sires.get(nm)
        r['sire'] = info['sire'] if info else None
        r['horseId'] = info['horseId'] if info else None
    return res


def fetch(sleep=0.8):
    races = json.load(open(RACES))['races']
    out = json.load(open(DATA)) if os.path.exists(DATA) else {}
    todo = [r for r in sorted(races) if r not in out]
    print(f'{len(todo)}レースを取得', flush=True)
    for i, rid in enumerate(todo, 1):
        try:
            res = fetch_one(rid)
        except Exception as e:
            print(f'  {rid} ERROR {e}', flush=True)
            time.sleep(1.2)
            continue
        if res:
            out[rid] = {**races[rid], 'horses': res}
        if i % 25 == 0:
            json.dump(out, open(DATA, 'w'), ensure_ascii=False)
            ns = sum(1 for v in out.values() for h in v['horses'] if h['sire'])
            print(f'  [{i}/{len(todo)}] {len(out)}レース 父あり{ns}頭', flush=True)
        time.sleep(sleep)
    json.dump(out, open(DATA, 'w'), ensure_ascii=False)
    print(f'完了: {len(out)}レース')


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'find':
        find([int(x) for x in sys.argv[2].split(',')])
    elif cmd == 'fetch':
        fetch()
