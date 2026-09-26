# -*- coding: utf-8 -*-
S = []
def add(html, narration='', **kw):
    d = {'html': html, 'narration': narration}; d.update(kw); S.append(d); return d

def cover(kicker, title, lead, meta):
    return ('<div class="slide cover"><div class="kicker">%s</div><h1>%s</h1>'
            '<div class="lead">%s</div><div class="meta">%s</div></div>') % (kicker, title, lead, meta)

def chap(no, title, lead):
    return ('<div class="slide chap"><div class="no">%s</div><h1>%s</h1>'
            '<div class="lead">%s</div></div>') % (no, title, lead)

def page(title, body, foot=''):
    f = '<div class="foot">%s</div>' % foot if foot else ''
    return '<div class="slide"><h2>%s</h2><div class="pad">%s</div>%s</div>' % (title, body, f)

def add_page(title, body, narration, foot='', **kw):
    return add(page(title, body, foot), narration, title=title, **kw)

def ul(items):
    out = []
    for it in items:
        cls, main, sub = it if len(it) == 3 else (it[0], it[1], '')
        s = '<span class="sub">%s</span>' % sub if sub else ''
        out.append('<li class="%s">%s%s</li>' % (cls, main, s))
    return '<ul>%s</ul>' % ''.join(out)

def cols(items):
    out = []
    for cls, head, body in items:
        out.append('<div class="col %s"><div class="ch">%s</div><div class="cb">%s</div></div>' % (cls, head, body))
    return '<div class="cols">%s</div>' % ''.join(out)

def box(cls, title, body):
    t = '<div class="t">%s</div>' % title if title else ''
    return '<div class="box %s">%s%s</div>' % (cls, t, body)

def node(cls, n1, n2=''):
    s = '<div class="n2">%s</div>' % n2 if n2 else ''
    return '<div class="node %s"><div class="n1">%s</div>%s</div>' % (cls, n1, s)

def arw(label='', cls=''):
    return ('<div class="arw %s"><div class="lb">%s</div><div class="tri"></div></div>') % (cls, label)

def flow(parts):
    return '<div class="flow">%s</div>' % ''.join(parts)

def truck(color, fill, cross=False):
    x = ('<path d="M8,6 L104,46 M104,6 L8,46" stroke="#a8261c" stroke-width="5" opacity=".9"/>'
         if cross else '')
    return ('<div class="tk"><svg viewBox="0 0 112 56">'
            '<rect x="2" y="4" width="70" height="30" rx="3" fill="%s" stroke="%s" stroke-width="3"/>'
            '<path d="M74,12 L96,12 L106,25 L106,34 L74,34 z" fill="%s" stroke="%s" stroke-width="3"/>'
            '<circle cx="22" cy="41" r="8" fill="#fff" stroke="%s" stroke-width="3.4"/>'
            '<circle cx="57" cy="41" r="8" fill="#fff" stroke="%s" stroke-width="3.4"/>'
            '<circle cx="92" cy="41" r="8" fill="#fff" stroke="%s" stroke-width="3.4"/>%s'
            '</svg></div>') % (fill, color, fill, color, color, color, color, x)

def seq(rows):
    out = []
    for cls, no, t, s, dir_ in rows:
        out.append('<div class="r %s"><div class="no">%s</div><div class="w">'
                   '<div class="t">%s</div><div class="s">%s</div></div>'
                   '<div class="dir">%s</div></div>' % (cls, no, t, s, dir_))
    return '<div class="seq">%s</div>' % ''.join(out)

def gate(t, s, xt, xs):
    return ('<div class="gate"><div class="q"><div class="t">%s</div><div class="s">%s</div></div>'
            '<div class="arw r"><div class="lb">いいえ</div><div class="tri"></div></div>'
            '<div class="x"><div class="t">%s</div><div class="s">%s</div></div></div>') % (t, s, xt, xs)

def table(head, rows, widths=None):
    w = widths or []
    th = ''.join('<th%s>%s</th>' % ((' style="width:%s"' % w[i]) if i < len(w) else '', h)
                 for i, h in enumerate(head))
    tr = ''.join('<tr>%s</tr>' % ''.join('<td%s>%s</td>' % (
        ' class="c"' if c.startswith('@') else '', c.lstrip('@')) for c in r) for r in rows)
    return '<table><tr>%s</tr>%s</table>' % (th, tr)
