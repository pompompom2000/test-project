"""石名坂：全154ページを機械的に洗い出す（読むだけ）"""
import json, io, glob, re, html

PAGES = []
for f in sorted(glob.glob('all/*.json')):
    try:
        d = json.load(io.open(f, encoding='utf-8'))
    except Exception:
        continue
    if not isinstance(d, list):
        continue
    for p in d:
        PAGES.append(dict(
            id=p['id'], slug=p['slug'],
            title=re.sub(r'<[^>]+>', '', p['title']['raw']),
            raw=p['content']['raw'], link=p['link']))

def text(raw):
    t = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', raw, flags=re.S)
    t = re.sub(r'<!--.*?-->', '', t, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', t)
    return re.sub(r'\s+', ' ', html.unescape(t))

# 今日、実際に問題だったものと同じ種類だけを探す
RULES = [
    ('A 言い切り', r'半永久|永久に|絶対に[^」]{0,8}(ありません|しません)|100[％%]|完全に防|必ず[^。]{0,12}(できます|なります)|保証します|一切[^。]{0,10}ありません'),
    ('B 他社への断定', r'(業者|工場|会社)[^。]{0,14}(おりません|ありません|一社のみ|のみです)'),
    ('C 根拠なき数値', r'約?\s?\d+\s?(デシベル|dB)|\d+倍以上|\d+[％%]以上の[^。]{0,10}(効果|削減)'),
    ('D 貼り付けの痕跡', r'\s。|\[\d{1,3}\]|提供された資料|場ふ合|「O」|扱われま\s'),
    ('E 個人の特定', r'(市|町|村)\s?[A-Zア-ンｱ-ﾝ]\s?様|[都道府県市町村]立[^\s、。]{2,10}(中学校|小学校|高校)'),
    ('F 壊れた参照', r'上記の表|下記の表|以下の表|上の表'),
    ('G 出典なしWikipedia', r'Wikipedia'),
]

hits = {}
for p in PAGES:
    t = text(p['raw'])
    for name, pat in RULES:
        for m in re.finditer(pat, t):
            s = t[max(0, m.start()-55):m.end()+55].strip()
            hits.setdefault(name, []).append((p['id'], p['slug'], p['title'][:26], m.group(0)[:22], s))

print("対象:", len(PAGES), "ページ\n")
for name, _ in RULES:
    h = hits.get(name, [])
    print("=" * 74)
    print(f"{name}  {len(h)} 件")
    print("=" * 74)
    seen = set()
    for pid, slug, title, kw, ctx in h:
        key = (pid, kw)
        if key in seen:
            continue
        seen.add(key)
        print(f"  [{pid}] {slug[:26]:28} 「{kw}」")
        print(f"      …{ctx}…")
    print()
