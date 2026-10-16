#!/usr/bin/env python3
"""秋華賞 過去20年の全出走馬の着順・馬体重を収集する。

db.netkeiba の結果テーブルから取得。列構成は年によって変わるので
ヘッダ行から列位置を引く。

私的利用の範囲。リクエスト間隔を空ける。
出力: data/analysis/shuka-sho-weights.json
"""
import html, json, os, re, sys, time, urllib.request

UA = {'User-Agent': 'Mozilla/5.0'}
OUT = 'data/analysis/shuka-sho-weights.json'


def cells(row):
    return [' '.join(html.unescape(re.sub(r'<[^>]+>', ' ', x)).split())
            for x in re.findall(r'(?is)<t[dh][^>]*>(.*?)</t[dh]>', row)]


def fetch(rid):
    u = f'https://db.netkeiba.com/race/{rid}/'
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40) as r:
        s = r.read().decode('euc-jp', 'replace')
    m = re.search(r'(?is)<table[^>]*class="[^"]*race_table_01[^"]*"[^>]*>(.*?)</table>', s)
    if not m:
        return None
    rows = re.findall(r'(?is)<tr[^>]*>(.*?)</tr>', m.group(1))
    if len(rows) < 2:
        return None
    # 各行の馬IDは馬名セルのリンクから取る
    ids = [re.search(r'/horse/(\d+)/', r) for r in rows[1:]]
    head = [h.replace(' ', '') for h in cells(rows[0])]

    def col(*names):
        for n in names:
            if n in head:
                return head.index(n)
        return None
    iw, ino, inm, ipop, iodds = (col('馬体重'), col('馬番'), col('馬名'),
                                 col('人気'), col('単勝'))
    iwk = col('枠番', '枠')
    title = re.search(r'<title>([^<|]*)', s)
    out = []
    for ri, row in enumerate(rows[1:]):
        c = cells(row)
        if len(c) <= max(x for x in (iw, ino, inm) if x is not None):
            continue
        pm = re.match(r'^(\d+)', c[0])
        if not pm:
            continue                      # 除外・中止・取消など
        demoted = '降' in c[0]            # 降着（例: "3(降)"）は馬券の対象
        wm = re.match(r'^(\d+)\(([-+]?\d+)\)$', c[iw]) if iw is not None else None
        out.append({
            'place': int(pm.group(1)), 'demoted': demoted,
            'no': int(c[ino]),
            'horseId': ids[ri].group(1) if ids[ri] else None,
            'waku': int(c[iwk]) if iwk is not None and c[iwk].isdigit() else None,
            'name': c[inm],
            'weight': int(wm.group(1)) if wm else None,
            'delta': int(wm.group(2)) if wm else None,
            'popularity': int(c[ipop]) if ipop is not None and c[ipop].isdigit() else None,
            'odds': float(c[iodds]) if iodds is not None and
                    re.fullmatch(r'[\d.]+', c[iodds] or '') else None})
    return {'title': title.group(1).strip() if title else '', 'horses': out}


def main():
    ids = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'shuka_ids.json'))
    out = json.load(open(OUT)) if os.path.exists(OUT) else {}
    for y in sorted(ids):
        if y in out:
            continue
        info = ids[y]
        try:
            r = fetch(info['raceId'])
        except Exception as e:
            print(f'{y} ERROR {e}', flush=True)
            time.sleep(1.0)
            continue
        if not r:
            print(f'{y} 取得不可', flush=True)
        else:
            out[y] = {**info, **r}
            nw = sum(1 for h in r['horses'] if h['weight'] is None)
            print(f"{y} {info['date']} {len(r['horses'])}頭"
                  + (f' (馬体重欠損{nw})' if nw else ''), flush=True)
        time.sleep(1.0)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, 'w'), ensure_ascii=False, indent=1)
    print(f'\n{len(out)}年分を {OUT} に保存')


if __name__ == '__main__':
    main()
