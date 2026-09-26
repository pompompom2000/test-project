# -*- coding: utf-8 -*-
import io, sys, importlib
F = {}
for m in sys.argv[1:]:
    mod = importlib.import_module(m); F.update(mod.F)
p = 'body.html'; s = io.open(p, encoding='utf-8').read()
import anchors
n = 0
for key, anc in anchors.A:
    if key not in F: continue
    if s.count(anc) != 1:
        print('ANCHOR MISMATCH x%d :: %s :: %s' % (s.count(anc), key, anc[:70])); sys.exit(1)
    if F[key] in s:
        print('already present:', key); continue
    s = s.replace(anc, anc + '\n  ' + F[key].strip() + '\n')
    n += 1
io.open(p, 'w', encoding='utf-8').write(s)
print('inserted', n, 'figures')
