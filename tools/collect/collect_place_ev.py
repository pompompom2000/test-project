"""複勝の最低払戻（下限）が効いている馬を、過去データで調べるための収集。

複勝には最低払戻100円（1.0倍）の下限がある。人気が集中しすぎた馬は
本来の確率に見合わない安さで止まる一方、下駄を履いた分だけ割安に
なることがある。それが実際に起きているかを確かめる。

各レースの結果ページから、全出走馬の「単勝オッズ・人気・着順」と、
3着以内馬の「複勝払戻」を取り出して1行にまとめる。
複勝オッズは事前には遡れないので、単勝オッズを人気集中の代理指標にする。
"""
import re, json, os, sys, time, html, csv
import subprocess
from concurrent.futures import ThreadPoolExecutor

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/125 Safari/537.36"
WORKERS = int(os.environ.get('FETCH_WORKERS', '3'))
REQUEST_INTERVAL = float(os.environ.get('FETCH_INTERVAL', '0.7'))
DAYLIST = os.environ.get('DAYLIST', 'daylist.json')
OUT = os.environ.get('PLACE_EV_OUT', 'place_ev.csv')


def get(url):
    time.sleep(REQUEST_INTERVAL)
    for _ in range(2):
        r = subprocess.run(['curl', '-sS', '-L', '--compressed', '-m', '25', '-A', UA, url],
                           capture_output=True)
        if r.returncode == 0 and r.stdout:
            return r.stdout.decode('utf-8', 'replace')
        time.sleep(1)
    return ''


def parse(rid):
    s = get(f"https://race.netkeiba.com/race/result.html?race_id={rid}")
    head = re.search(r'(?is)<div class="RaceList_NameBox">(.*?)</div>\s*</div>', s)
    if not head:
        return []
    h = re.sub(r'\s+', ' ', html.unescape(re.sub(r'(?is)<[^>]+>', ' ', head.group(1))))
    surf = re.search(r'(芝|ダ)(\d+)m', h)
    cond = re.search(r'馬場:(良|稍重|重|不良|稍|不)', h)
    if not surf or not cond:
        return []

    # 3着以内馬の複勝払戻を取り出す
    fuku = {}
    m = re.search(r'(?is)<tr class="Fukusho">(.*?)</tr>', s)
    if m:
        nums = re.findall(r'<div><span>(\d+)</span></div>', m.group(1))
        yens = re.findall(r'([\d,]+)円', m.group(1))
        for n, y in zip(nums, yens):
            fuku[int(n)] = int(y.replace(',', ''))
    if not fuku:
        return []

    rows = []
    field = 0
    for r in re.findall(r'(?is)<tr[^>]*class="[^"]*HorseList[^"]*"[^>]*>(.*?)</tr>', s):
        c = [re.sub(r'\s+', ' ', html.unescape(re.sub(r'(?is)<[^>]+>', ' ', t))).strip()
             for t in re.findall(r'(?is)<td[^>]*>(.*?)</td>', r)]
        c = [x for x in c if x]
        if len(c) < 10:
            continue
        try:
            place, no = int(c[0]), int(c[2])
        except ValueError:
            continue
        pop = od = None
        for x in c[7:]:
            if re.fullmatch(r'\d{1,2}', x) and pop is None and int(x) <= 18:
                pop = int(x)
            elif re.fullmatch(r'\d+\.\d', x) and od is None and float(x) >= 1:
                od = float(x)
        if pop is None or od is None:
            continue
        field += 1
        rows.append(dict(race_id=rid, no=no, place=place, win_odds=od, popularity=pop,
                         surface=surf.group(1), distance=int(surf.group(2)),
                         going=cond.group(1),
                         placed=1 if place <= 3 else 0,
                         place_payout=fuku.get(no, 0)))
    # 複勝は7頭立て以下だと2着まで。対象外にする
    if field < 8:
        return []
    for r in rows:
        r['field'] = field
    return rows


def main():
    days = json.load(open(DAYLIST))
    ids = sorted({rid for v in days.values() for rid in v})
    done = set()
    if os.path.exists(OUT):
        with open(OUT) as f:
            done = {row['race_id'] for row in csv.DictReader(f)}
    todo = [r for r in ids if r not in done]
    print(f'races: {len(ids)} / todo: {len(todo)}', file=sys.stderr, flush=True)

    fields = ['race_id', 'no', 'place', 'win_odds', 'popularity', 'surface',
              'distance', 'going', 'placed', 'place_payout', 'field']
    new = not os.path.exists(OUT)
    with open(OUT, 'a', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        if new:
            w.writeheader()
        with ThreadPoolExecutor(max_workers=WORKERS) as ex:
            for i, rows in enumerate(ex.map(parse, todo)):
                for r in rows:
                    w.writerow(r)
                if i % 100 == 0:
                    f.flush()
                    print(f'{i}/{len(todo)}', file=sys.stderr, flush=True)
    print('done', file=sys.stderr, flush=True)


if __name__ == '__main__':
    main()
