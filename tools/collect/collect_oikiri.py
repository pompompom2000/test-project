#!/usr/bin/env python3
"""調教評価（netkeibaの追い切り評価 S/A/B/C/D）を過去レースから集める。

発見の経緯:
  - db.netkeiba.com/horse/training.html?id=... は有料（プレミアム導線のみ返る）
  - race.netkeiba.com/race/oikiri.html?race_id=...&type=2 は先頭3頭しか出ない
  - type=3 なら全頭の「評価（文字）＋短評」が無料で、2015年まで遡れる

出力: data/analysis/oikiri-<set>.json
使い方: python3 tools/collect/collect_oikiri.py g1
"""
import glob, html, json, os, re, sys, time, urllib.request

UA = {'User-Agent': 'Mozilla/5.0'}
URL = 'https://race.netkeiba.com/race/oikiri.html?race_id={rid}&type=3'
SETS = {'g1': 'data/validation-g1/*.json', 'val': 'data/validation/*.json'}


def grades(rid):
    """馬番 -> {'verdict': 短評, 'grade': 評価文字} を返す。"""
    req = urllib.request.Request(URL.format(rid=rid), headers=UA)
    with urllib.request.urlopen(req, timeout=40) as r:
        s = r.read().decode('utf-8', 'replace')
    t = re.sub(r'(?is)<script.*?</script>', '', s)
    m = re.search(r'(?is)<table[^>]*OikiriTable.*?</table>', t)
    if not m:
        return {}
    out = {}
    for row in re.findall(r'(?is)<tr[^>]*>(.*?)</tr>', m.group(0)):
        c = [html.unescape(re.sub(r'<[^>]+>', '', x)).strip()
             for x in re.findall(r'(?is)<td[^>]*>(.*?)</td>', row)]
        c = [x for x in c if x]
        # 枠, 馬番, 印セル, 馬名, 短評, 評価
        if len(c) >= 6 and c[0].isdigit() and c[1].isdigit():
            out[int(c[1])] = {'name': c[3], 'verdict': c[-2], 'grade': c[-1]}
    return out


def main():
    key = sys.argv[1] if len(sys.argv) > 1 else 'g1'
    files = sorted(glob.glob(SETS[key]))
    outpath = f'data/analysis/oikiri-{key}.json'
    done = json.load(open(outpath)) if os.path.exists(outpath) else {}
    for i, f in enumerate(files, 1):
        d = json.load(open(f))
        rid = d['raceId']
        if rid in done:
            continue
        try:
            g = grades(rid)
        except Exception as e:
            print(f'  {rid} ERR {e}')
            continue
        done[rid] = {'title': d['title'], 'file': os.path.basename(f),
                     'grades': {str(k): v for k, v in g.items()}}
        print(f'{i:4d}/{len(files)} {rid} {len(g):3d}頭 {d["title"][:40]}')
        json.dump(done, open(outpath, 'w'), ensure_ascii=False)
        time.sleep(0.9)      # 私的利用。ToS第16条12号（サーバ負荷）に配慮
    print(f'{outpath}: {len(done)}レース')


if __name__ == '__main__':
    main()
