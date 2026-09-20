"""秋（9〜12月）のG1レースを年ごとに収集する。

race_list からグレードアイコンでG1を判定し、結果ページから着順・オッズ・
馬体重などを取り出す。道悪に限定せず、良馬場も含めて集める。
"""
import re, json, subprocess, sys, os, time, html, datetime
from concurrent.futures import ThreadPoolExecutor

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/125 Safari/537.36"
JYO = {'01': '札幌', '02': '函館', '03': '福島', '04': '新潟', '05': '東京',
       '06': '中山', '07': '中京', '08': '京都', '09': '阪神', '10': '小倉'}
YEARS = [int(y) for y in os.environ.get('G1_YEARS', '2015,2016,2017,2018,2019,2020,2021,2022,2023,2024,2025').split(',')]


def get(url):
    for _ in range(3):
        r = subprocess.run(['curl', '-sS', '-L', '--compressed', '-m', '25', '-A', UA, url],
                           capture_output=True)
        if r.returncode == 0 and r.stdout:
            return r.stdout.decode('utf-8', 'replace')
        time.sleep(1)
    return ''


def autumn_dates(year):
    """9月1日から12月31日までの土日（祝日開催も拾うため月曜も含める）。"""
    d = datetime.date(year, 9, 1)
    end = datetime.date(year, 12, 31)
    out = []
    while d <= end:
        if d.weekday() in (0, 5, 6):
            out.append(d.strftime('%Y%m%d'))
        d += datetime.timedelta(days=1)
    return out


def g1_ids_for_date(ds):
    """その日のG1レースの race_id と名前を返す。

    各レースの <li> に終了タグが無いため、開始タグで分割して
    1レースぶんの断片を切り出す。グレードは Icon_GradeType1 で判定するが、
    GradeType10 などに部分一致しないよう単語境界で確認する。
    """
    s = get(f"https://race.netkeiba.com/top/race_list_sub.html?kaisai_date={ds}")
    chunks = re.split(r'<li class="RaceList_DataItem', s)[1:]
    out = []
    for item in chunks:
        if not re.search(r'Icon_GradeType1(?![0-9])', item):
            continue
        rid = re.search(r'race_id=(\d{12})', item)
        nm = re.search(r'(?is)<span class="ItemTitle">(.*?)</span>', item)
        if rid:
            out.append((rid.group(1), html.unescape(re.sub(r'<[^>]+>', '', nm.group(1))).strip() if nm else ''))
    return out


def parse_result(rid):
    s = get(f"https://race.netkeiba.com/race/result.html?race_id={rid}")
    m = re.search(r'(?is)<div class="RaceList_NameBox">(.*?)</div>\s*</div>', s)
    if not m:
        return None
    head = re.sub(r'\s+', ' ', html.unescape(re.sub(r'(?is)<[^>]+>', ' ', m.group(1))))
    surf = re.search(r'(芝|ダ)(\d+)m', head)
    cond = re.search(r'馬場:(良|稍重|重|不良|稍|不)', head)
    name = re.search(r'\d+R\s+(\S+)', head)
    if not surf or not cond:
        return None
    horses = []
    for r in re.findall(r'(?is)<tr[^>]*class="[^"]*HorseList[^"]*"[^>]*>(.*?)</tr>', s):
        hid = re.search(r'/horse/(\d{10})', r)
        c = [re.sub(r'\s+', ' ', html.unescape(re.sub(r'(?is)<[^>]+>', ' ', t))).strip()
             for t in re.findall(r'(?is)<td[^>]*>(.*?)</td>', r)]
        c = [x for x in c if x]
        if len(c) < 10 or not hid:
            continue
        try:
            place, waku, no = int(c[0]), int(c[1]), int(c[2])
        except ValueError:
            continue
        pop = od = None
        for x in c[7:]:
            if re.fullmatch(r'\d{1,2}', x) and pop is None and int(x) <= 18:
                pop = int(x)
            elif re.fullmatch(r'\d+\.\d', x) and od is None and float(x) >= 1:
                od = float(x)
        mw = re.search(r'(\d{3})\s*\([-+]?\d+\)', ' '.join(c))
        horses.append(dict(place=place, waku=waku, no=no, name=c[3], id=hid.group(1),
                           sexage=c[4], jockey=c[6], popularity=pop, odds=od,
                           weight=int(mw.group(1)) if mw else None))
    if len(horses) < 8:
        return None
    return dict(race_id=rid, track=JYO.get(rid[4:6], rid[4:6]),
                surface='turf' if surf.group(1) == '芝' else 'dirt',
                distance=int(surf.group(2)),
                cond={'良': 'firm', '稍重': 'good', '稍': 'good',
                      '重': 'yielding', '不良': 'soft', '不': 'soft'}[cond.group(1)],
                name=name.group(1) if name else '', head=head, horses=horses)


def main():
    out_file = os.environ.get('G1_RACES', 'g1_races.json')
    races = json.load(open(out_file)) if os.path.exists(out_file) else {}

    dates = [d for y in YEARS for d in autumn_dates(y)]
    print(f'dates to scan: {len(dates)}', file=sys.stderr, flush=True)

    found = []
    with ThreadPoolExecutor(max_workers=10) as ex:
        for ds, ids in zip(dates, ex.map(g1_ids_for_date, dates)):
            for rid, nm in ids:
                found.append((ds, rid, nm))
    print(f'G1 races found: {len(found)}', file=sys.stderr, flush=True)

    todo = [(ds, rid, nm) for ds, rid, nm in found if rid not in races]
    with ThreadPoolExecutor(max_workers=8) as ex:
        for (ds, rid, nm), r in zip(todo, ex.map(lambda t: parse_result(t[1]), todo)):
            if not r:
                continue
            r['date'] = f"{ds[:4]}-{ds[4:6]}-{ds[6:]}"
            races[rid] = r
            print(f"keep {rid} {r['date']} {r['track']} {r['distance']} {r['cond']} {r['name']} {len(r['horses'])}",
                  file=sys.stderr, flush=True)
    json.dump(races, open(out_file, 'w'), ensure_ascii=False)
    print(f'total G1 races: {len(races)}', file=sys.stderr, flush=True)


if __name__ == '__main__':
    main()
