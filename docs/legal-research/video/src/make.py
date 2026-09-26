# -*- coding: utf-8 -*-
import deck_e, kit, build, io, re, pathlib
D = pathlib.Path(__file__).resolve().parent
# 台本（人が読む用）を書き出す
lines = ['# 傭車の考え方 ― 解説動画 ナレーション台本', '',
         '配車担当・現場向け／全%d枚' % len(kit.S), '']
for i, s in enumerate(kit.S):
    m = re.search(r'<h[12][^>]*>(.*?)</h[12]>', s['html'], re.S)
    t = re.sub('<[^>]+>', ' ', m.group(1)) if m else ''
    t = re.sub(r'\s+', ' ', t).strip()
    if 'slide chap' in s['html']:
        k = re.search(r'class="no">(.*?)</div>', s['html'])
        t = '【%s】%s' % (k.group(1), t) if k else t
    lines.append('## %02d　%s' % (i + 1, t))
    lines.append('')
    lines.append(s.get('narration', '（ナレーションなし）'))
    lines.append('')
io.open(D / 'ナレーション台本.md', 'w', encoding='utf-8').write('\n'.join(lines))
build.main(kit.S, name='傭車の考え方_解説動画')
