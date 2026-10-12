#!/usr/bin/env python3
"""検証セットの各レースについて外厩先（調整先の育成牧場）を収集する。

出典: かよちんの外厩情報-競馬wiki https://keiba-wiki.com/<YYMMDD><venue>/
ページは開催日単位で全レースの「馬名|騎手|外厩先」表を持つ。
ページが存在するのは2023年以降。

外厩はレース前に判明する情報なので先読みバイアスは入らない。
私的利用の範囲。リクエスト間隔を空ける。
"""
import glob, html, json, os, re, time, urllib.request

INTERVAL = 1.0
OUT = 'data/validation-g1-gaikyu.json'
VENUE = {'01': 'sapporo', '02': 'hakodate', '03': 'fukushima', '04': 'niigata',
         '05': 'tokyo', '06': 'nakayama', '07': 'chukyo', '08': 'kyouto',
         '09': 'hanshin', '10': 'kokura'}


def to_text(h):
    h = re.sub(r'(?is)<(script|style|noscript)[^>]*>.*?</\1>', ' ', h)
    h = re.sub(r'(?is)<br\s*/?>', '\n', h)
    h = re.sub(r'(?is)</(p|div|tr|li|h[1-6]|table)>', '\n', h)
    h = re.sub(r'(?is)</t[dh]>', ' | ', h)
    t = html.unescape(re.sub(r'(?s)<[^>]+>', ' ', h))
    return re.sub(r'[ \t　]+', ' ', t)


def parse_race(text, raceno):
    """指定レース番号の 馬番->外厩先 を返す。"""
    m = re.search(r'外厩情報【[^】]*?' + str(raceno) + r'R】', text)
    if not m:
        return None
    nxt = re.search(r'外厩情報【', text[m.end():])
    seg = text[m.end(): m.end() + (nxt.start() if nxt else 4000)]
    toks = [re.sub(r'\s+', ' ', x).strip() for x in seg.split('|')]
    try:
        k = next(i for i, x in enumerate(toks) if '外厩先' in x)
    except StopIteration:
        return None
    cells = [c for c in toks[k + 1:] if c]
    out, i = {}, 0
    while i + 3 < len(cells) + 1 and i + 3 <= len(cells):
        if not re.fullmatch(r'\d{1,2}', cells[i]):
            break
        out[int(cells[i])] = {'name': cells[i + 1], 'jockey': cells[i + 2],
                              'gaikyu': cells[i + 3]}
        i += 4
    return out or None


def main():
    targets = {}
    for p in sorted(glob.glob('data/validation-g1/*.json')):
        m = re.match(r'(\d{4})-(\d{2})-(\d{2})-(\d{12})\.json$', os.path.basename(p))
        y, mo, d, rid = m.groups()
        if int(y) < 2023:          # ページが存在しない
            continue
        slug = f"{y[2:]}{mo}{d}{VENUE.get(rid[4:6], '')}"
        targets.setdefault(slug, []).append(rid)

    out = json.load(open(OUT)) if os.path.exists(OUT) else {}
    todo = [(s, rs) for s, rs in sorted(targets.items())
            if any(r not in out for r in rs)]
    print(f'{len(targets)}開催日 / 未取得 {len(todo)}日', flush=True)

    for i, (slug, rids) in enumerate(todo, 1):
        url = f'https://keiba-wiki.com/{slug}/'
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=30) as r:
                text = to_text(r.read().decode('utf-8', 'replace'))
            for rid in rids:
                got = parse_race(text, int(rid[-2:]))
                out[rid] = got
                print(f"  [{i}/{len(todo)}] {slug} {rid[-2:]}R "
                      f"{'%d頭' % len(got) if got else '取得不可'}", flush=True)
        except Exception as e:
            print(f'  [{i}/{len(todo)}] {slug} ERROR {e}', flush=True)
        json.dump(out, open(OUT, 'w'), ensure_ascii=False)
        time.sleep(INTERVAL)

    ok = sum(1 for v in out.values() if v)
    print(f'完了: {ok}/{len(out)}レースで外厩情報を取得')


if __name__ == '__main__':
    main()
