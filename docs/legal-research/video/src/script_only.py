# -*- coding: utf-8 -*-
import deck_e, kit, io, re, pathlib
D = pathlib.Path(__file__).resolve().parent
lines = ['# 傭車の考え方 ― 解説動画 ナレーション台本', '',
         '配車担当・現場向け／全%d枚' % len(kit.S), '',
         '読み上げの目安は1分あたり約270字です。', '']
for i, s in enumerate(kit.S):
    m = re.search(r'<h[12][^>]*>(.*?)</h[12]>', s['html'], re.S)
    t = re.sub('<[^>]+>', ' ', m.group(1)) if m else ''
    t = re.sub(r'\s+', ' ', t).strip()
    if 'slide chap' in s['html']:
        k = re.search(r'class="no">(.*?)</div>', s['html'])
        t = '【%s】%s' % (k.group(1), t) if k else t
    lines.append('## %02d　%s' % (i + 1, t)); lines.append('')
    lines.append(s.get('narration', '（ナレーションなし）')); lines.append('')
io.open(D / 'ナレーション台本.md', 'w', encoding='utf-8').write('\n'.join(lines))
print('台本 %d枚' % len(kit.S))
