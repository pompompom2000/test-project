#!/usr/bin/env python3
"""秋華賞に出走した各馬の、秋華賞までのキャリア（出走数）を収集する。

db.netkeiba.com/horse/result/<id>/ の戦績テーブルから、
**秋華賞の施行日より前**の出走のみを数える（先読みバイアス防止）。

出力: data/analysis/shuka-sho-career.json
"""
import html, json, os, re, sys, time, urllib.request

UA = {'User-Agent': 'Mozilla/5.0'}
SRC = 'data/analysis/shuka-sho-weights.json'
OUT = 'data/analysis/shuka-sho-career.json'
URL = 'https://db.netkeiba.com/horse/result/{hid}/'


def career(hid, before):
    with urllib.request.urlopen(urllib.request.Request(URL.format(hid=hid), headers=UA),
                                timeout=40) as r:
        s = r.read().decode('euc-jp', 'replace')
    m = re.search(r'(?is)<table[^>]*class="[^"]*db_h_race_results[^"]*"[^>]*>(.*?)</table>', s)
    if not m:
        return None
    runs = []
    for row in re.findall(r'(?is)<tr[^>]*>(.*?)</tr>', m.group(1))[1:]:
        c = [' '.join(html.unescape(re.sub(r'<[^>]+>', ' ', x)).split())
             for x in re.findall(r'(?is)<t[dh][^>]*>(.*?)</t[dh]>', row)]
        if not c or not re.fullmatch(r'\d{4}/\d{2}/\d{2}', c[0]):
            continue
        dt = c[0].replace('/', '-')
        if dt >= before:                 # 秋華賞当日以降は数えない
            continue
        venue = c[1] if len(c) > 1 else ''
        jra = bool(re.match(r'^\d[^\d]', venue))   # "3京都7" 形式はJRA
        runs.append({'date': dt, 'venue': venue, 'jra': jra})
    return {'starts': len(runs),
            'jraStarts': sum(1 for r in runs if r['jra']),
            'firstRun': min((r['date'] for r in runs), default=None),
            'lastRun': max((r['date'] for r in runs), default=None)}


def main():
    src = json.load(open(SRC))
    out = json.load(open(OUT)) if os.path.exists(OUT) else {}
    todo = [(y, h) for y in sorted(src) for h in src[y]['horses']
            if h.get('horseId') and h['horseId'] not in out]
    print(f'未取得 {len(todo)}頭', flush=True)
    for i, (y, h) in enumerate(todo, 1):
        try:
            c = career(h['horseId'], src[y]['date'])
        except Exception as e:
            print(f"  {h['name']} ERROR {e}", flush=True)
            time.sleep(1.2)
            continue
        if c:
            out[h['horseId']] = {**c, 'year': int(y), 'name': h['name']}
        if i % 50 == 0:
            json.dump(out, open(OUT, 'w'), ensure_ascii=False)
            print(f'  [{i}/{len(todo)}] 保存', flush=True)
        time.sleep(0.9)
    json.dump(out, open(OUT, 'w'), ensure_ascii=False, indent=1)
    print(f'完了: {len(out)}頭')


if __name__ == '__main__':
    main()
