import re,json,subprocess,sys,os,time,html
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/125 Safari/537.36"
JYO={'01':'札幌','02':'函館','03':'福島','04':'新潟','05':'東京','06':'中山','07':'中京','08':'京都','09':'阪神','10':'小倉'}
def get(url):
    for _ in range(2):
        r=subprocess.run(['curl','-sS','-L','--compressed','-m','20','-A',UA,url],capture_output=True)
        if r.returncode==0 and r.stdout: return r.stdout.decode('utf-8','replace')
    return ''

def parse_result(rid):
    s=get(f"https://race.netkeiba.com/race/result.html?race_id={rid}")
    m=re.search(r'(?is)<div class="RaceList_NameBox">(.*?)</div>\s*</div>',s)
    if not m: return None
    head=re.sub(r'\s+',' ',html.unescape(re.sub(r'(?is)<[^>]+>',' ',m.group(1))))
    surf=re.search(r'(芝|ダ)(\d+)m',head)
    cond=re.search(r'馬場:(良|稍重|重|不良|稍|不)',head)
    name=re.search(r'\d+R\s+(\S+)',head)
    if not surf or not cond: return None
    rows=re.findall(r'(?is)<tr[^>]*class="[^"]*HorseList[^"]*"[^>]*>(.*?)</tr>',s)
    horses=[]
    for r in rows:
        hid=re.search(r'/horse/(\d{10})',r)
        c=[re.sub(r'\s+',' ',html.unescape(re.sub(r'(?is)<[^>]+>',' ',t))).strip() for t in re.findall(r'(?is)<td[^>]*>(.*?)</td>',r)]
        c=[x for x in c if x]
        if len(c)<10 or not hid: continue
        try:
            place=int(c[0]); waku=int(c[1]); no=int(c[2])
        except ValueError:
            continue
        nm=c[3]; sexage=c[4]; jockey=c[6]
        pop=None; od=None
        for x in c[7:]:
            if re.fullmatch(r'\d{1,2}',x) and pop is None and int(x)<=18: pop=int(x)
            elif re.fullmatch(r'\d+\.\d',x) and od is None and float(x)>=1: od=float(x)
        wt=None
        mw=re.search(r'(\d{3})\s*\([-+]?\d+\)',' '.join(c))
        if mw: wt=int(mw.group(1))
        horses.append(dict(place=place,waku=waku,no=no,name=nm,id=hid.group(1),
                           sexage=sexage,jockey=jockey,popularity=pop,odds=od,weight=wt))
    if len(horses)<8: return None
    return dict(race_id=rid, date=None, track=JYO.get(rid[4:6],rid[4:6]),
                surface='turf' if surf.group(1)=='芝' else 'dirt',
                distance=int(surf.group(2)),
                cond={'良':'firm','稍重':'good','稍':'good','重':'yielding','不良':'soft','不':'soft'}[cond.group(1)],
                name=name.group(1) if name else '', head=head, horses=horses)

probe=json.load(open('probe.json'))
wet=[(k,v) for k,v in probe.items() if v['cond'] in ('重','不良','不')]
print('wet track-days:',len(wet),file=sys.stderr)
races={}
if os.path.exists('races_raw.json'): races=json.load(open('races_raw.json'))
for k,v in wet:
    ds=k.split('-')[0]
    for rid in v['races']:
        if rid in races: continue
        r=parse_result(rid)
        time.sleep(0.15)
        if not r: continue
        r['date']=f"{ds[:4]}-{ds[4:6]}-{ds[6:]}"
        if r['surface']=='turf' and r['cond'] in ('yielding','soft'):
            races[rid]=r
            print('keep',rid,r['date'],r['track'],r['distance'],r['cond'],r['name'],len(r['horses']),file=sys.stderr)
    json.dump(races,open('races_raw.json','w'),ensure_ascii=False)
print('kept turf wet races:',len(races),file=sys.stderr)
