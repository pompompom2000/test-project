import re,json,subprocess,datetime,sys,os,html
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/125 Safari/537.36"
def get(url, retries=2):
    for _ in range(retries):
        r=subprocess.run(['curl','-sS','-L','--compressed','-m','25','-A',UA,url],capture_output=True)
        if r.returncode==0 and r.stdout: return r.stdout.decode('utf-8','replace')
    return ''

start=datetime.date(2025,6,1); end=datetime.date(2026,9,13)
dates=[]
d=start
while d<=end:
    if d.weekday() in (5,6): dates.append(d.strftime('%Y%m%d'))
    d+=datetime.timedelta(days=1)
print('candidate dates:',len(dates),file=sys.stderr)

cache={}
if os.path.exists('daylist.json'): cache=json.load(open('daylist.json'))
for i,ds in enumerate(dates):
    if ds in cache: continue
    s=get(f"https://race.netkeiba.com/top/race_list_sub.html?kaisai_date={ds}")
    ids=sorted(set(re.findall(r'race_id=(\d{12})',s)))
    cache[ds]=ids
    if i%20==0: print(i,ds,len(ids),file=sys.stderr)
json.dump(cache,open('daylist.json','w'))
tot=sum(len(v) for v in cache.values())
print('days with races:',sum(1 for v in cache.values() if v),'total races:',tot,file=sys.stderr)
