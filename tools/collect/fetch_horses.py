"""検証用に、出走各馬の血統（父）と全戦績を取得してキャッシュする。

races_raw.json（collect_races.py の出力）に登場する馬をまとめて取得する。
netkeiba への負荷を抑えるため、同時実行数は控えめにしている。
"""
import re, json, subprocess, os, html, sys, time
from concurrent.futures import ThreadPoolExecutor

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/125 Safari/537.36"
CACHE = os.environ.get('HORSE_CACHE', 'horse_cache')
RACES = os.environ.get('RACES_RAW', 'races_raw.json')
os.makedirs(CACHE, exist_ok=True)


def get(url):
    for _ in range(3):
        r = subprocess.run(['curl', '-sS', '-L', '--compressed', '-m', '25', '-A', UA, url],
                           capture_output=True)
        if r.returncode == 0 and r.stdout:
            return r.stdout.decode('euc-jp', 'replace')
        time.sleep(1)
    return ''


def fetch(hid):
    path = os.path.join(CACHE, f'{hid}.json')
    if os.path.exists(path):
        return 0
    ped = get(f"https://db.netkeiba.com/horse/ped/{hid}/")
    cells = re.findall(r'(?is)<td[^>]*class="[^"]*b_ml[^"]*"[^>]*>(.*?)</td>', ped)
    sire = ''
    if cells:
        sire = re.sub(r'\s+', ' ', html.unescape(re.sub(r'(?is)<[^>]+>', '', cells[0]))).strip().split()[0]

    res = get(f"https://db.netkeiba.com/horse/result/{hid}/")
    rows = []
    tb = re.search(r'(?is)<table[^>]*db_h_race_results.*?>(.*?)</table>', res)
    if tb:
        for tr in re.findall(r'(?is)<tr>(.*?)</tr>', tb.group(1)):
            c = [re.sub(r'\s+', ' ', html.unescape(re.sub(r'(?is)<[^>]+>', '', t))).strip()
                 for t in re.findall(r'(?is)<td[^>]*>(.*?)</td>', tr)]
            if len(c) >= 26:
                rows.append(c)
    json.dump({'id': hid, 'sire': sire, 'rows': rows}, open(path, 'w'), ensure_ascii=False)
    return 1


def main():
    races = json.load(open(RACES))
    ids = sorted({h['id'] for v in races.values() for h in v['horses']})
    print(f'unique horses: {len(ids)}', file=sys.stderr, flush=True)
    done = 0
    with ThreadPoolExecutor(max_workers=10) as ex:
        for i, r in enumerate(ex.map(fetch, ids)):
            done += r
            if i % 25 == 0:
                print(f'{i}/{len(ids)} newly fetched={done}', file=sys.stderr, flush=True)
    print(f'cached files: {len(os.listdir(CACHE))}', file=sys.stderr, flush=True)


if __name__ == '__main__':
    main()
