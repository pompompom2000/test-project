#!/usr/bin/env python3
"""VRS18のAI予測記事を発見し、予測表画像と市場オッズを集めて manifest を出す。

実行タイミング: 開催日の朝（第1レース発走前）。
開催がない日・記事が未投稿の日は何もせず終了する。

予測値は記事内のグラフ画像にしか無いため、数値の読み取りはモデルが行う。
OCR(tesseract)を321頭で検証したが一致率37%で、小数点の脱落など
後段で検出できない誤りが多かったため採用しなかった。

2026-10-25に、3会場36レース分の予測表が前日(10/24)の記事の画像と
バイト単位で同一だったことがある（投稿者が前日の書き出しを貼り直した）。
画像にしか数値が無い以上、中身だけ見ても気づけない。各画像のmd5を
manifestに残し、前回のmanifestと照合して流用を検出する。

出力: <outdir>/manifest.json と <outdir>/img/<venue>-<race>.png
使い方: python3 tools/collect/vrs18_prepare.py [YYYY-MM-DD]
"""
import glob, hashlib, html, json, os, re, sys, time, urllib.request
from datetime import datetime, timedelta, timezone

JST = timezone(timedelta(hours=9))
UA = {'User-Agent': 'Mozilla/5.0'}
LIST_API = 'https://note.com/api/v2/creators/vrs18/contents?kind=note&page=1'
ODDS_API = ('https://race.netkeiba.com/api/api_get_jra_odds.html'
            '?type=2&race_id={rid}&action=init')
VENUE = {'札幌': '01', '函館': '02', '福島': '03', '新潟': '04', '東京': '05',
         '中山': '06', '中京': '07', '京都': '08', '阪神': '09', '小倉': '10'}
TITLE_RE = re.compile(r'AI予測【(\d+)回(.+?)(\d+)日目】(\d{4})\.(\d{2})\.(\d{2})')


def get(url, binary=False):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
        b = r.read()
    return b if binary else b.decode('utf-8', 'replace')


def find_articles(date):
    """その日のAI予測記事を (会場, race_id接頭辞, URL) で返す。"""
    d = json.loads(get(LIST_API))
    out = []
    for n in d['data']['contents']:
        m = TITLE_RE.search(n['name'])
        if not m:
            continue
        kai, venue, day, y, mo, dd = m.groups()
        if f'{y}-{mo}-{dd}' != date or venue not in VENUE:
            continue
        out.append({'venue': venue, 'title': n['name'],
                    'url': f"https://note.com/vrs18/n/{n['key']}",
                    'publishedAt': n['publishAt'],
                    'prefix': f'{y}{VENUE[venue]}{int(kai):02d}{int(day):02d}'})
    return out


def race_images(article_html):
    """見出しのレース番号 -> 先頭画像(予測表)のURL。"""
    a = re.search(r'(?is)<article[^>]*>(.*?)</article>', article_html)
    body = a.group(1) if a else article_html
    items = re.findall(r'(?is)<h[1-6][^>]*>(.*?)</h[1-6]>|<img[^>]+src="([^"]+)"', body)
    cur, out = None, {}
    for h, img in items:
        if h:
            t = html.unescape(re.sub(r'<[^>]+>', '', h)).strip()
            m = re.search(r'(\d{1,2})Ｒ', t)
            cur = int(m.group(1)) if m else None
        elif img and '/img/' in img and cur and cur not in out:
            out[cur] = img.split('?')[0]
    return out


def fetch_odds(rid):
    d = json.loads(get(ODDS_API.format(rid=rid)))
    return {'status': d.get('status'),
            'at': (d.get('data') or {}).get('official_datetime'),
            'odds': (d.get('data') or {}).get('odds', {}).get('2')}


def prev_article(venue, date):
    """その会場の、dateより前で最も新しいAI予測記事。"""
    cand = []
    for page in (1, 2):
        d = json.loads(get(LIST_API.replace('page=1', f'page={page}')))
        for n in d['data']['contents']:
            m = TITLE_RE.search(n['name'])
            if not m:
                continue
            _, v, _, y, mo, dd = m.groups()
            if v == venue and f'{y}-{mo}-{dd}' < date:
                cand.append((f'{y}-{mo}-{dd}', n['key']))
    return max(cand) if cand else None


def flag_reused_images(man, date):
    """予測表が前の開催日の使い回しでないか。

    2026-10-25に、3会場36レースすべての予測表が前日(10/24)の記事の画像と
    バイト単位で同一だった。数値は画像にしか無いので、転記してからでは
    どの日のどの馬の数字なのか判別できない。

    照合先は2つ。前回のmanifest（取得済みのmd5、追加の通信なし）と、
    前の開催日の記事そのもの。後者が要るのは、使い回し元がこちらの
    収集していない日（上の例では10/24）でありうるため。
    記事側はまず1レース目と最終レースの2枚だけ引く。この2枚が一致したら
    記事ごと使い回されているので、そこで初めて全レースを照合する。
    """
    prev = sorted(f for f in glob.glob('data/tracking/work/*/manifest.json')
                  if f.split('/')[-2] < date)
    seen = {}
    if prev:
        old = json.load(open(prev[-1]))
        seen = {r['imageMd5']: f"{old['date']} {v['venue']}{r['race']}"
                for v in old['venues'] for r in v['races'] if r.get('imageMd5')}

    dup = 0
    for v in man['venues']:
        hit = [r for r in v['races'] if r.get('imageMd5') in seen]
        if not hit:
            pa = prev_article(v['venue'], date)
            if pa:
                pd, key = pa
                imgs = race_images(get(f'https://note.com/vrs18/n/{key}'))
                probe = {}
                for no in ({min(imgs), max(imgs)} if imgs else ()):
                    probe[hashlib.md5(get(imgs[no], binary=True)).hexdigest()] = \
                        f'{pd} {v["venue"]}{no}R'
                    time.sleep(0.4)
                if any(r.get('imageMd5') in probe for r in v['races']):
                    for no in sorted(imgs):
                        if no in (min(imgs), max(imgs)):
                            continue
                        probe[hashlib.md5(get(imgs[no], binary=True)).hexdigest()] = \
                            f'{pd} {v["venue"]}{no}R'
                        time.sleep(0.4)
                hit = [r for r in v['races'] if r.get('imageMd5') in probe]
                seen.update(probe)
        for r in hit:
            r['reusedFrom'] = seen[r['imageMd5']]
        if hit:
            v['imagesReused'] = len(hit)
            dup += len(hit)
            print(f"  警告: {v['venue']} の {len(hit)}レースの予測表が "
                  f"{seen[hit[0]['imageMd5']].split()[0]} の記事と同一", flush=True)
    if dup:
        man['imagesReused'] = dup
    return dup


def main():
    date = sys.argv[1] if len(sys.argv) > 1 else datetime.now(JST).strftime('%Y-%m-%d')
    outdir = f'data/tracking/work/{date}'
    arts = find_articles(date)
    if not arts:
        print(f'{date}: AI予測記事なし（開催なし、または未投稿）')
        return 1

    os.makedirs(f'{outdir}/img', exist_ok=True)
    man = {'date': date, 'preparedAt': datetime.now(JST).isoformat(timespec='seconds'),
           'venues': []}
    for a in arts:
        imgs = race_images(get(a['url']))
        print(f"{a['venue']}: {a['title']} / {len(imgs)}レース", flush=True)
        races = []
        for no in sorted(imgs):
            rid = f"{a['prefix']}{no:02d}"
            try:
                o = fetch_odds(rid)
            except Exception as e:
                print(f'  {no}R オッズ取得失敗 {e}', flush=True)
                continue
            if not o['odds']:
                print(f"  {no}R オッズ未発表 (status={o['status']}) スキップ", flush=True)
                continue
            p = f"{outdir}/img/{a['venue']}-{no:02d}R.png"
            if not os.path.exists(p):
                open(p, 'wb').write(get(imgs[no], binary=True))
                time.sleep(0.4)
            md5 = hashlib.md5(open(p, 'rb').read()).hexdigest()
            races.append({'race': f'{no}R', 'raceId': rid, 'field': len(o['odds']),
                          'placePositions': 3 if len(o['odds']) >= 8 else 2,
                          'image': p, 'imageMd5': md5,
                          'oddsStatus': o['status'], 'oddsAt': o['at'],
                          'placeOdds': {k: [float(v[0]), float(v[1])]
                                        for k, v in o['odds'].items()}})
            print(f"  {no}R {rid} {len(o['odds'])}頭 {o['status']}", flush=True)
            time.sleep(0.6)
        man['venues'].append({'venue': a['venue'], 'title': a['title'],
                              'article': a['url'], 'publishedAt': a['publishedAt'],
                              'races': races})

    print('\n前回のmanifestと画像を照合', flush=True)
    dup = flag_reused_images(man, date)
    json.dump(man, open(f'{outdir}/manifest.json', 'w'), ensure_ascii=False, indent=1)
    n = sum(len(v['races']) for v in man['venues'])
    started = sum(1 for v in man['venues'] for r in v['races']
                  if r['oddsStatus'] != 'middle')
    print(f'\n{outdir}/manifest.json に {n}レース分を書き出し')
    if started:
        print(f'注意: {started}レースは既に発走済み（status != middle）')
    if dup:
        print(f'\n中止: {dup}/{n}レースの予測表が前回と同じ画像だった。'
              f'記事に当日の表が載っていない。転記してはいけない。')
        return 2
    print(f'次: {outdir}/img/ の画像をモデルが読み、'
          f'{outdir}/predictions.json に書いてから vrs18_build.py')
    return 0


if __name__ == '__main__':
    sys.exit(main())
