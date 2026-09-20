import re,json,subprocess,sys,os,time,html
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/125 Safari/537.36"
def get(url):
    r=subprocess.run(['curl','-sS','-L','--compressed','-m','20','-A',UA,url],capture_output=True)
    return r.stdout.decode('utf-8','replace') if r.returncode==0 else ''
def header(race_id):
    s=get(f"https://race.netkeiba.com/race/result.html?race_id={race_id}")
    m=re.search(r'(?is)<div class="RaceList_NameBox">(.*?)</div>\s*</div>',s)
    if not m: return None,s
    t=re.sub(r'\s+',' ',html.unescape(re.sub(r'(?is)<[^>]+>',' ',m.group(1))))
    return t,s

days=json.load(open('daylist.json'))
probe={}
if os.path.exists('probe.json'): probe=json.load(open('probe.json'))
pairs=[]
for ds,ids in days.items():
    tracks={}
    for rid in ids: tracks.setdefault(rid[4:6],[]).append(rid)
    for jyo,rids in tracks.items():
        pairs.append((ds,jyo,sorted(rids)))
print('track-days:',len(pairs),file=sys.stderr)
for n,(ds,jyo,rids) in enumerate(pairs):
    key=f"{ds}-{jyo}"
    if key in probe: continue
    target=[r for r in rids if r.endswith('11')] or rids[-1:]
    t,_=header(target[0])
    cond=''
    if t:
        m=re.search(r'馬場:(\S+)',t); cond=m.group(1) if m else ''
    probe[key]={'cond':cond,'races':rids}
    if n%25==0:
        print(n,key,cond,file=sys.stderr); json.dump(probe,open('probe.json','w'))
    time.sleep(0.15)
json.dump(probe,open('probe.json','w'))
from collections import Counter
print(Counter(v['cond'] for v in probe.values()),file=sys.stderr)
wet=[k for k,v in probe.items() if v['cond'] in ('重','不良')]
print('wet track-days:',len(wet),wet[:20],file=sys.stderr)
