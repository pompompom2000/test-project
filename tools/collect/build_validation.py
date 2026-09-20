"""各レースについて、そのレース時点までの成績だけを使って入力JSONを作る。

未来のレース結果が混ざると検証が無意味になるため、
馬の戦績は必ず「対象レースの日付より前」に限定する。
"""
import re,json,subprocess,sys,os,time,html,datetime
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/125 Safari/537.36"
os.makedirs('horse_cache',exist_ok=True)

def get(url,enc='euc-jp'):
    for _ in range(2):
        r=subprocess.run(['curl','-sS','-L','--compressed','-m','25','-A',UA,url],capture_output=True)
        if r.returncode==0 and r.stdout: return r.stdout.decode(enc,'replace')
    return ''

def horse_data(hid):
    """血統（父）と全戦績を取得してキャッシュする。"""
    path=f'horse_cache/{hid}.json'
    if os.path.exists(path):
        return json.load(open(path))
    ped=get(f"https://db.netkeiba.com/horse/ped/{hid}/")
    cells=re.findall(r'(?is)<td[^>]*class="[^"]*b_ml[^"]*"[^>]*>(.*?)</td>',ped)
    sire=re.sub(r'\s+',' ',html.unescape(re.sub(r'(?is)<[^>]+>','',cells[0]))).strip().split()[0] if cells else ''
    time.sleep(0.2)
    res=get(f"https://db.netkeiba.com/horse/result/{hid}/")
    rows=[]
    tb=re.search(r'(?is)<table[^>]*db_h_race_results.*?>(.*?)</table>',res)
    if tb:
        for tr in re.findall(r'(?is)<tr>(.*?)</tr>',tb.group(1)):
            c=[re.sub(r'\s+',' ',html.unescape(re.sub(r'(?is)<[^>]+>','',t))).strip()
               for t in re.findall(r'(?is)<td[^>]*>(.*?)</td>',tr)]
            if len(c)>=26: rows.append(c)
    d={'id':hid,'sire':sire,'rows':rows}
    json.dump(d,open(path,'w'),ensure_ascii=False)
    time.sleep(0.2)
    return d

def num(x):
    m=re.match(r'^(\d+)',x or ''); return int(m.group(1)) if m else None

def prerace_stats(h, race_date):
    """対象レースより前の芝レースだけで、良馬場／道悪の成績と脚質を出す。"""
    firm=[0,0]; mud=[0,0]; ratios=[]
    for r in h['rows']:
        try:
            d=datetime.date(*map(int,r[0].split('/')))
        except Exception:
            continue
        if d >= race_date:       # 対象レース当日以降は使わない
            continue
        dist=r[14]; ba=r[16]; pos=num(r[11]); field=num(r[6]); passing=r[25]
        if not dist.startswith('芝') or pos is None: continue
        top3 = pos<=3
        if ba=='良': firm[0]+=1; firm[1]+=top3
        elif ba in ('稍','重','不'): mud[0]+=1; mud[1]+=top3
        if passing and field:
            try: ratios.append(int(passing.split('-')[0])/field)
            except Exception: pass
    use=ratios[:6]
    avg=sum(use)/len(use) if use else None
    style=None
    if avg is not None:
        style='逃げ' if avg<=0.12 else '先行' if avg<=0.38 else '差し' if avg<=0.70 else '追込'
    return firm,mud,style

COURSE={'中山-2200':'nakayama-turf-2200'}
SEX={'牡':'牡','牝':'牝','セ':'セン'}

races=json.load(open('races_raw.json'))
out_dir='/home/user/test-project/data/validation'
os.makedirs(out_dir,exist_ok=True)
built=0
for rid,r in sorted(races.items()):
    dest=os.path.join(out_dir,f"{r['date']}-{rid}.json")
    if os.path.exists(dest): built+=1; continue
    race_date=datetime.date(*map(int,r['date'].split('-')))
    horses=[]; ok=True
    for hr in r['horses']:
        if hr['odds'] is None or hr['popularity'] is None: ok=False; break
        hd=horse_data(hr['id'])
        firm,mud,style=prerace_stats(hd,race_date)
        horses.append(dict(no=hr['no'],name=hr['name'],sire=hd['sire'],
                           sex=SEX.get(hr['sexage'][:1]),jockey=hr['jockey'],
                           post=hr['waku'],style=style,weight=hr['weight'] or 0,
                           odds=hr['odds'],
                           firmStarts=firm[0],firmPlaces=firm[1],
                           mudStarts=mud[0],mudPlaces=mud[1]))
    if not ok or len(horses)<8: 
        print('skip',rid,file=sys.stderr); continue
    finish=[h['no'] for h in sorted(r['horses'],key=lambda x:x['place'])]
    doc=dict(title=f"{r['date']} {r['track']}{r['distance']}m {r['name']}",
             raceId=rid, surface='turf', surfaceLabel=f"芝{r['distance']}m（{r['track']}）",
             state=r['cond'], courseKey=COURSE.get(f"{r['track']}-{r['distance']}"),
             horses=horses, finish=finish,
             note='成績はレース当日より前の芝レースのみで集計。外厩・調教・厩舎コメント・パドック・当日傾向は履歴が取れないため未入力')
    json.dump(doc,open(dest,'w'),ensure_ascii=False,indent=1)
    built+=1
    print('built',dest,len(horses),file=sys.stderr)
print('total built:',built,file=sys.stderr)
