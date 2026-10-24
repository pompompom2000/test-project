#!/usr/bin/env python3
"""長距離戦（芝2500m以上）を集め、ロベルト系×馬場の検証データを作る。

設計は data/analysis/roberto-prereg.md に、データを見る前に固定してある。

3段階:
  find   日別一覧から 芝2500m以上 のレースIDを集める（長距離戦が組まれる月のみ走査）
  fetch  各レースの結果（馬場・着順・人気）と shutuba_past（父・母父）を取る
  sire   父・母父の父系をたどり、Roberto に行き着くかを判定する
"""
import datetime, html, json, os, re, sys, time, urllib.request

UA = {'User-Agent': 'Mozilla/5.0'}
LIST = 'https://db.netkeiba.com/race/list/{d}/'
RESULT = 'https://db.netkeiba.com/race/{rid}/'
PAST = 'https://race.netkeiba.com/race/shutuba_past.html?race_id={rid}'
PED = 'https://db.netkeiba.com/horse/ped/{hid}/'
RACES = 'data/analysis/longmud-races.json'
DATA = 'data/analysis/longmud-data.json'
SIRES = 'data/analysis/longmud-sires.json'
MONTHS = (1, 2, 3, 4, 5, 10, 12)
MIN_DIST = 2500


def get(url, enc='euc-jp'):
    last = None
    for i in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
                b = r.read()
            if enc == 'auto':
                for e in ('utf-8', 'euc_jp'):
                    try:
                        return b.decode(e)
                    except Exception:
                        pass
                return b.decode('utf-8', 'replace')
            return b.decode(enc, 'replace')
        except Exception as e:
            last = e
            time.sleep(3.0 * (i + 1))
    raise last


def find(years, sleep=2.2):
    st = json.load(open(RACES)) if os.path.exists(RACES) else {'dates': [], 'races': {}}
    seen = set(st['dates'])
    dates = []
    for y in years:
        d = datetime.date(y, 1, 1)
        while d.year == y:
            if d.weekday() >= 5 and d.month in MONTHS:
                dates.append(d.strftime('%Y%m%d'))
            d += datetime.timedelta(days=1)
    todo = [x for x in dates if x not in seen]
    print(f'{len(todo)}日分を走査', flush=True)
    for i, ds in enumerate(todo, 1):
        try:
            s = get(LIST.format(d=ds))
        except Exception as e:
            print(f'  {ds} ERR {e}', flush=True)
            continue
        for m in re.finditer(
                r'href="https://db\.netkeiba\.com/race/(\d{12})/"[^>]*title="([^"]*)"[^>]*>.*?'
                r'</a><br\s*/?>\s*<div>\s*([^<]*)', s, re.S):
            rid, title, info = m.group(1), html.unescape(m.group(2)), ' '.join(m.group(3).split())
            dm = re.match(r'芝(\d{4})', info)
            if not dm or int(dm.group(1)) < MIN_DIST:
                continue
            if rid[4:6] not in tuple(f'{k:02d}' for k in range(1, 11)):
                continue
            st['races'][rid] = {'date': ds, 'title': title, 'info': info,
                                'dist': int(dm.group(1))}
        st['dates'].append(ds)
        if i % 20 == 0:
            json.dump(st, open(RACES, 'w'), ensure_ascii=False)
            print(f'  {i}/{len(todo)} レース{len(st["races"])}', flush=True)
        time.sleep(sleep)
    json.dump(st, open(RACES, 'w'), ensure_ascii=False)
    print(f'{RACES}: {len(st["races"])}レース')


def parse_result(rid):
    s = get(RESULT.format(rid=rid))
    dm = re.search(r'(?is)<diary_snap_cut>(.*?)</diary_snap_cut>', s)
    info = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', dm.group(1)))) if dm else ''
    gm = re.search(r'芝\s*:\s*(良|稍重|重|不良)', info)
    tb = re.search(r'(?is)<table[^>]*class="[^"]*race_table_01[^"]*"[^>]*>(.*?)</table>', s)
    if not tb or not gm:
        return None
    rows = re.findall(r'(?is)<tr[^>]*>(.*?)</tr>', tb.group(1))
    cell = lambda r: [html.unescape(re.sub(r'<[^>]+>', '', x)).strip()
                      for x in re.findall(r'(?is)<t[dh][^>]*>(.*?)</t[dh]>', r)]
    hdr = [re.sub(r'\s+', ' ', h) for h in cell(rows[0])]
    try:
        i_fin = next(i for i, h in enumerate(hdr) if h.startswith('着順'))
        i_no = next(i for i, h in enumerate(hdr) if h.startswith('馬番'))
        i_pop = next(i for i, h in enumerate(hdr) if h.startswith('人気'))
    except StopIteration:
        return None
    horses = []
    for r in rows[1:]:
        c = cell(r)
        if len(c) <= max(i_fin, i_no, i_pop) or not c[i_no].isdigit():
            continue
        fm = re.match(r'^(\d+)', c[i_fin])
        horses.append({'no': int(c[i_no]),
                       'finish': int(fm.group(1)) if fm else None,
                       'pop': int(c[i_pop]) if c[i_pop].isdigit() else None})
    return {'ground': gm.group(1), 'horses': horses} if horses else None


def parse_past(rid):
    """shutuba_past から 馬番 -> (父, 母父)。行の並びは
    枠 / 馬番 / 印 / Horse_Info(父=Horse01, 馬名=Horse02, 母=Horse03, 母父=Horse04)。"""
    s = get(PAST.format(rid=rid), enc='auto')
    out = {}
    for row in re.findall(r'(?is)<tr[^>]*class="[^"]*HorseList[^"]*"[^>]*>(.*?)</tr>', s):
        tds = re.findall(r'(?is)<td[^>]*>(.*?)</td>', row)
        if len(tds) < 2:
            continue
        nums = [re.sub(r'<[^>]+>', '', t).strip() for t in tds[:2]]
        if not nums[1].isdigit():
            continue
        no = int(nums[1])
        blk = row
        sire = re.search(r'(?is)<div class="Horse01[^"]*">\s*([^<]+?)\s*</div>', blk)
        bms = re.search(r'(?is)<div class="Horse04[^"]*">\s*\(?\s*([^)<]+?)\s*\)?\s*</div>', blk)
        # 馬IDも取る。種牡馬名から馬IDを引けなかったときに、この馬の血統表から
        # 父・母父のIDを読む回り道ができる
        hid = re.search(r'(?is)<div class="Horse02">.*?/horse/([0-9a-z]{10})', blk)
        out[no] = {'sire': sire.group(1).strip() if sire else None,
                   'bms': bms.group(1).strip() if bms else None,
                   'id': hid.group(1) if hid else None}
    return out


def fetch(sleep=2.2):
    ids = json.load(open(RACES))['races']
    done = json.load(open(DATA)) if os.path.exists(DATA) else {}
    todo = [r for r in sorted(ids) if r not in done]
    print(f'{len(todo)}レース', flush=True)
    for i, rid in enumerate(todo, 1):
        try:
            res = parse_result(rid)
            time.sleep(sleep)
            past = parse_past(rid)
        except Exception as e:
            print(f'  {rid} ERR {e}', flush=True)
            time.sleep(sleep)
            continue
        if res:
            for h in res['horses']:
                p = past.get(h['no'], {})
                h['sire'], h['bms'] = p.get('sire'), p.get('bms')
            res.update(ids[rid])
            done[rid] = res
        if i % 20 == 0:
            json.dump(done, open(DATA, 'w'), ensure_ascii=False)
            print(f'  {i}/{len(todo)} 取得{len(done)}', flush=True)
        time.sleep(sleep)
    json.dump(done, open(DATA, 'w'), ensure_ascii=False)
    print(f'{DATA}: {len(done)}レース')


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'find':
        find(range(int(sys.argv[2]), int(sys.argv[3]) + 1))
    elif cmd == 'fetch':
        fetch()
