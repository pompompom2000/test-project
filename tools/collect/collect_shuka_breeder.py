#!/usr/bin/env python3
"""秋華賞出走馬の生産者を収集する。

db.netkeiba.com/horse/<id>/ のプロフィール表（db_prof_table）から
「生産者」「産地」を取る。生産者は馬の属性なので先読みの問題はない。

出力: data/analysis/shuka-sho-breeder.json
"""
import html, json, os, re, sys, time, urllib.request

UA = {'User-Agent': 'Mozilla/5.0'}
SRC = 'data/analysis/shuka-sho-weights.json'
OUT = 'data/analysis/shuka-sho-breeder.json'
URL = 'https://db.netkeiba.com/horse/{hid}/'


def profile(hid):
    with urllib.request.urlopen(urllib.request.Request(URL.format(hid=hid), headers=UA),
                                timeout=40) as r:
        s = r.read().decode('euc-jp', 'replace')
    m = re.search(r'(?is)<table[^>]*class="[^"]*db_prof_table[^"]*"[^>]*>(.*?)</table>', s)
    if not m:
        return None
    out = {}
    for row in re.findall(r'(?is)<tr[^>]*>(.*?)</tr>', m.group(1)):
        c = [' '.join(html.unescape(re.sub(r'<[^>]+>', ' ', x)).split())
             for x in re.findall(r'(?is)<t[dh][^>]*>(.*?)</t[dh]>', row)]
        if len(c) >= 2:
            out[c[0]] = c[1]
    return {'breeder': out.get('生産者'), 'origin': out.get('産地'),
            'owner': out.get('馬主')}


def main():
    src = json.load(open(SRC))
    out = json.load(open(OUT)) if os.path.exists(OUT) else {}
    todo = [(y, h) for y in sorted(src) for h in src[y]['horses']
            if h.get('horseId') and h['horseId'] not in out]
    print(f'未取得 {len(todo)}頭', flush=True)
    for i, (y, h) in enumerate(todo, 1):
        try:
            p = profile(h['horseId'])
        except Exception as e:
            print(f"  {h['name']} ERROR {e}", flush=True)
            time.sleep(1.2)
            continue
        if p:
            out[h['horseId']] = {**p, 'year': int(y), 'name': h['name']}
        if i % 50 == 0:
            json.dump(out, open(OUT, 'w'), ensure_ascii=False)
            print(f'  [{i}/{len(todo)}]', flush=True)
        time.sleep(0.9)
    json.dump(out, open(OUT, 'w'), ensure_ascii=False, indent=1)
    miss = sum(1 for v in out.values() if not v.get('breeder'))
    print(f'完了: {len(out)}頭（生産者欠損 {miss}）')


if __name__ == '__main__':
    main()
