#!/usr/bin/env python3
"""追い切りタイムを馬番1-3について集める。

netkeibaは全頭の調教タイムを有料にしているが、各レースの**馬番1〜3**だけは
無料で、タイム・区間ラップ・併せ馬・脚色・日付まで全部出る（2015年まで遡れる）。
type=3は全頭だが評価文字のみでタイムが無い。type=0,1,2,4-8は3頭まで。

馬番は枠順抽選で決まり、調教の出来とは独立なので、
**馬番1-3は馬の無作為標本**になる。「調教タイムは市場を超える情報を持つか」
という問いは1頭単位の問いなので、無作為標本があれば答えられる。
（今日のレースの全頭に使う＝運用には足りない。検証専用。）

出力: data/analysis/oikiri-times-<tag>.json
使い方: python3 tools/collect/collect_oikiri_times.py <tag> <race_idを並べたファイル>
"""
import html, json, os, re, sys, time, urllib.request

UA = {'User-Agent': 'Mozilla/5.0'}
URL = 'https://race.netkeiba.com/race/oikiri.html?race_id={rid}&type=1'
NUM = re.compile(r'\d{1,3}\.\d')


def parse(rid):
    req = urllib.request.Request(URL.format(rid=rid), headers=UA)
    with urllib.request.urlopen(req, timeout=40) as r:
        s = r.read().decode('utf-8', 'replace')
    t = re.sub(r'(?is)<script.*?</script>', '', s)
    tb = re.search(r'(?is)<table[^>]*OikiriTable.*?</table>', t)
    if not tb:
        return {}
    out, cur = {}, None
    for row in re.findall(r'(?is)<tr[^>]*>(.*?)</tr>', tb.group(0)):
        cells = [html.unescape(re.sub(r'<[^>]+>', '', x)).replace('\n', ' ').strip()
                 for x in re.findall(r'(?is)<td[^>]*>(.*?)</td>', row)]
        cells = [c for c in cells if c]
        if len(cells) >= 4 and cells[0].isdigit() and cells[1].isdigit():
            cur = int(cells[1])
            out[cur] = {'waku': int(cells[0]), 'name': cells[3].split()[0], 'works': []}
        elif cur and cells and re.match(r'^\d{4}/\d{2}/\d{2}', cells[0]):
            joined = ' '.join(cells)
            laps = NUM.findall(re.sub(r'[^(]*?(\([\d.]+\))', r'\1 ', joined)) \
                if '(' in joined else []
            out[cur]['works'].append({
                'date': cells[0][:10],
                'course': cells[1],
                # 坂路行は '-' が入って列がずれるので、馬場は値で拾う
                'baba': next((x for x in cells if x in ('良', '稍', '重', '不')), ''),
                # 累計タイム（括弧外）と区間ラップ（括弧内）を分けて持つ
                'cum': NUM.findall(re.sub(r'\([^)]*\)', ' ', joined)),
                'lap': re.findall(r'\((\d{1,3}\.\d)\)', joined),
                'drive': next((x for x in cells if x in ('一杯', '強め', '馬也', 'Ｇ前', 'Ｇ強')), ''),
                'best': '一番時計' in joined,
                'raw': cells,
            })
    return out


def main():
    tag, listfile = sys.argv[1], sys.argv[2]
    rids = [l.strip() for l in open(listfile) if l.strip()]
    path = f'data/analysis/oikiri-times-{tag}.json'
    done = json.load(open(path)) if os.path.exists(path) else {}
    for i, rid in enumerate(rids, 1):
        if rid in done:
            continue
        try:
            done[rid] = parse(rid)
        except Exception as e:
            print(f'  {rid} ERR {e}')
            continue
        if i % 20 == 0 or i == len(rids):
            json.dump(done, open(path, 'w'), ensure_ascii=False)
            print(f'{i}/{len(rids)} 保存  {sum(len(v) for v in done.values())}頭')
        time.sleep(0.9)      # 私的利用。ToS第16条12号（サーバ負荷）に配慮
    json.dump(done, open(path, 'w'), ensure_ascii=False)
    print(f'{path}: {len(done)}レース {sum(len(v) for v in done.values())}頭')


if __name__ == '__main__':
    main()
