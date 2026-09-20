"""秋G1の検証用データを作る。

道悪限定の検証と違い、良馬場が大半なので特徴量を広げている。
クラス実績・距離適性・ローテーション・前走内容など、馬場状態に
依存しない材料を各馬について「そのレースの当日より前」で集計する。
"""
import re, json, os, sys, datetime

CACHE = os.environ.get('HORSE_CACHE', 'horse_cache')
RACES = os.environ.get('G1_RACES', 'g1_races.json')
OUT = os.environ.get('G1_OUT', '/home/user/test-project/data/validation-g1')
os.makedirs(OUT, exist_ok=True)

SEX = {'牡': '牡', '牝': '牝', 'セ': 'セン'}
COURSE = {'中山-2200': 'nakayama-turf-2200'}


def num(x):
    m = re.match(r'^(\d+)', x or '')
    return int(m.group(1)) if m else None


def fnum(x):
    m = re.match(r'^(\d+(?:\.\d+)?)', x or '')
    return float(m.group(1)) if m else None


def stats(h, race_date, track, distance):
    """対象レース当日より前の芝成績をいろいろな切り口で集計する。"""
    s = dict(starts=0, places=0, wins=0,
             firmStarts=0, firmPlaces=0, mudStarts=0, mudPlaces=0,
             gradeStarts=0, gradePlaces=0, g1Starts=0, g1Places=0,
             distStarts=0, distPlaces=0, courseStarts=0, coursePlaces=0,
             lastFinish=None, lastPopularity=None, lastField=None,
             daysSinceLast=None, handicap=None, ratios=[])
    prev = None
    for r in h['rows']:
        try:
            d = datetime.date(*map(int, r[0].split('/')))
        except Exception:
            continue
        if d == race_date:
            s['handicap'] = fnum(r[13])   # 当日の斤量はレース前に分かる
            continue
        if d > race_date:
            continue
        dist, ba, pos = r[14], r[16], num(r[11])
        if not dist.startswith('芝') or pos is None:
            continue
        top3 = pos <= 3
        s['starts'] += 1
        s['places'] += top3
        s['wins'] += (pos == 1)
        if ba == '良':
            s['firmStarts'] += 1; s['firmPlaces'] += top3
        elif ba in ('稍', '重', '不'):
            s['mudStarts'] += 1; s['mudPlaces'] += top3

        # グレードはローマ数字表記（GI・GII・GIII）。アラビア数字の表記も許容する
        title = r[4]
        if re.search(r'\((?:J\.)?G(?:III|II|I|[123])\)', title):
            s['gradeStarts'] += 1; s['gradePlaces'] += top3
            if re.search(r'\((?:J\.)?G(?:I|1)\)', title):
                s['g1Starts'] += 1; s['g1Places'] += top3

        dm = num(dist[1:])
        if dm is not None and abs(dm - distance) <= 200:
            s['distStarts'] += 1; s['distPlaces'] += top3
        if track in r[1]:
            s['courseStarts'] += 1; s['coursePlaces'] += top3

        if prev is None or d > prev[0]:
            prev = (d, pos, num(r[10]), num(r[6]))
        field = num(r[6])
        if r[25] and field:
            try:
                s['ratios'].append(int(r[25].split('-')[0]) / field)
            except Exception:
                pass
    if prev:
        s['lastFinish'], s['lastPopularity'], s['lastField'] = prev[1], prev[2], prev[3]
        s['daysSinceLast'] = (race_date - prev[0]).days
    use = s.pop('ratios')[:6]
    avg = sum(use) / len(use) if use else None
    s['style'] = (None if avg is None else
                  '逃げ' if avg <= 0.12 else '先行' if avg <= 0.38 else
                  '差し' if avg <= 0.70 else '追込')
    return s


def main():
    races = json.load(open(RACES))
    built = skipped = 0
    for rid, r in sorted(races.items()):
        if r['surface'] != 'turf':      # ダートG1は別条件なので今回は除く
            skipped += 1; continue
        dest = os.path.join(OUT, f"{r['date']}-{rid}.json")
        if os.path.exists(dest):
            built += 1; continue
        race_date = datetime.date(*map(int, r['date'].split('-')))
        horses, ok = [], True
        for hr in r['horses']:
            if hr['odds'] is None:
                ok = False; break
            path = os.path.join(CACHE, f"{hr['id']}.json")
            if not os.path.exists(path):
                ok = False; break
            h = json.load(open(path))
            st = stats(h, race_date, r['track'], r['distance'])
            age = num(hr['sexage'][1:])
            horses.append(dict(no=hr['no'], name=hr['name'], sire=h['sire'],
                               sex=SEX.get(hr['sexage'][:1]), age=age,
                               jockey=hr['jockey'], post=hr['waku'],
                               weight=hr['weight'] or 0, odds=hr['odds'],
                               style=st.pop('style'), **st))
        if not ok or len(horses) < 8:
            skipped += 1
            print(f'skip {rid}', file=sys.stderr)
            continue
        finish = [h['no'] for h in sorted(r['horses'], key=lambda x: x['place'])]
        json.dump(dict(title=f"{r['date']} {r['track']}{r['distance']}m {r['name']}",
                       raceId=rid, surface='turf',
                       surfaceLabel=f"芝{r['distance']}m（{r['track']}）",
                       distance=r['distance'], track=r['track'],
                       state=r['cond'],
                       courseKey=COURSE.get(f"{r['track']}-{r['distance']}"),
                       horses=horses, finish=finish,
                       note='成績はレース当日より前の芝レースのみで集計'),
                  open(dest, 'w'), ensure_ascii=False, indent=1)
        built += 1
        print(f"built {r['date']} {r['name']} ({len(horses)}頭)", file=sys.stderr)
    print(f'built={built} skipped={skipped}', file=sys.stderr)


if __name__ == '__main__':
    main()
