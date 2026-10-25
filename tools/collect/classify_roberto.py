#!/usr/bin/env python3
"""父・母父の名前から「父系をさかのぼってRobertoに行き着くか」を判定する。

事前登録（data/analysis/roberto-prereg.md）の定義:
  ロベルト系 = 父の父系、または母父の父系が Roberto に行き着く馬

種牡馬1頭につき2フェッチ（名前検索→5代血統表）で済むので、
出走馬ごとに血統を引く必要がない。判定結果はキャッシュする。

実装上の注意が2つある。
  - 5代血統表の5代目セルには rowspan 属性が無い（省略＝1）。属性の有無で
    世代を決めると32セルある5代目を丸ごと落とす。行×列のグリッドに復元する。
  - 検索語が1頭だけに一致すると、netkeiba は一覧ではなく馬ページへ
    リダイレクトする。最終URLを見ないとIDが取れない。
  - 外国産馬のIDは数字だけではない（例: ブライアンズタイム = 000a000082）。
"""
import html, json, os, re, sys, time, urllib.request, urllib.parse

UA = {'User-Agent': 'Mozilla/5.0'}
SEARCH = 'https://db.netkeiba.com/?pid=horse_list&word={q}&match=c'
PED = 'https://db.netkeiba.com/horse/ped/{hid}/'
CACHE = 'data/analysis/roberto-sires.json'


def get(url, want_url=False):
    last = None
    for i in range(6):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40)
            b, fin = r.read(), r.geturl()
            s = None
            for e in ('euc_jp', 'utf-8'):
                try:
                    s = b.decode(e)
                    break
                except Exception:
                    pass
            s = s if s is not None else b.decode('utf-8', 'replace')
            return (s, fin) if want_url else s
        except Exception as e:
            last = e
            time.sleep(5 * (i + 1))
    raise last


def find_id(name):
    s, fin = get(SEARCH.format(q=urllib.parse.quote(name.encode('euc-jp', 'replace'))),
                 want_url=True)
    m = re.search(r'/horse/([0-9a-z]{10})/?$', fin)
    if m:
        return m.group(1)
    for hid, nm in re.findall(r'/horse/([0-9a-z]{10})/?"[^>]*>\s*([^<]{1,40})', s):
        if html.unescape(nm).strip() == name:
            return hid
    return None


def grid(tb):
    """5代血統表を (世代, 通し番号) -> 名前 に復元する。"""
    occ, out = {}, {}
    for r, row in enumerate(re.findall(r'(?is)<tr[^>]*>(.*?)</tr>', tb)):
        for attr, cell in re.findall(r'(?is)<td([^>]*)>(.*?)</td>', row):
            c = 0
            while occ.get((r, c)):
                c += 1
            sp = re.search(r'rowspan="(\d+)"', attr)
            span = int(sp.group(1)) if sp else 1
            for k in range(span):
                occ[(r + k, c)] = True
            nm = html.unescape(re.sub(r'<[^>]+>', '', cell)).replace('\xa0', ' ').strip()
            out[(c + 1, r // (32 >> (c + 1)))] = nm.split('\n')[0].strip()
    return out


def classify(name):
    """その種牡馬の父系にRobertoがいるか。"""
    hid = find_id(name)
    time.sleep(2.0)
    if not hid:
        return {'id': None, 'roberto': None, 'gen': None, 'line': []}
    tb = re.search(r'(?is)<table[^>]*class="[^"]*blood_table[^"]*"[^>]*>(.*?)</table>',
                   get(PED.format(hid=hid)))
    if not tb:
        return {'id': hid, 'roberto': None, 'gen': None, 'line': []}
    g = grid(tb.group(1))
    line = [g.get((k, 0), '') for k in range(1, 6)]     # 父系＝通し番号0
    hit = next((k for k, v in enumerate(line, 1) if re.search(r'\bRoberto\b', v)), None)
    return {'id': hid, 'roberto': hit is not None, 'gen': hit, 'line': line}


def main():
    names = json.load(open(sys.argv[1]))
    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    todo = [n for n in names if n and n not in cache]
    print(f'{len(todo)}頭を判定（キャッシュ済み {len(cache)}）', flush=True)
    for i, n in enumerate(todo, 1):
        try:
            cache[n] = classify(n)
        except Exception as e:
            print(f'  {n} ERR {e}', flush=True)
            time.sleep(3.0)
            continue
        if i % 20 == 0:
            json.dump(cache, open(CACHE, 'w'), ensure_ascii=False)
            print(f'  {i}/{len(todo)} ロベルト系 {sum(1 for v in cache.values() if v.get("roberto"))}',
                  flush=True)
        time.sleep(2.0)
    json.dump(cache, open(CACHE, 'w'), ensure_ascii=False)
    print(f'{CACHE}: {len(cache)}頭、うちロベルト系 '
          f'{sum(1 for v in cache.values() if v.get("roberto"))}')


if __name__ == '__main__':
    main()
