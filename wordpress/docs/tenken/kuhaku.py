# -*- coding: utf-8 -*-
u"""
題名と説明文の、不自然な半角スペースを詰める。

  ・鍵は環境変数 IZK_AUTH からしか読まない。標準出力にも出さない。
  ・--apply と --yes の両方がなければ、何も書き込まない。
  ・直す前の値を seo-mae.json に控えてある（元に戻せる）。
  ・取るのは半角スペースだけ。全角スペース（　）には触らない。
  ・隣が日本語の文字のときだけ取る。英語どうしの間（Claude Code）は残す。
  ・語がくっついて読みにくくなる6件は、機械では直さない（YOKERU）。
  ・記事の綴り（URL）は変えない。status も変えない。
  ・1ページごとに、書き込んだあと読み返して確かめる。
"""
import os, sys, io, json, re, time, base64
import urllib.request as ur

# 詰めると語がくっついて読みにくくなるもの。人が考えて直す。
YOKERU = {
    'kikouhendou-2050-iwate-nougyou',
    'kikouhendou-2050-keizai',
    'kikouhendou-2050-kurashi',
    'kikouhendou-2050-shokutaku',
    'kikouhendou-2050-tekiou-business',
    'nougyou-energy-shisetsu-engei',
}

NIHON = re.compile(u'[぀-ゟ゠-ヿ一-鿿、-〿！-｠・]')


def tsumeru(s):
    if not s:
        return s
    out = []
    for i, ch in enumerate(s):
        if ch == u' ':
            mae = s[i-1] if i > 0 else u''
            ato = s[i+1] if i+1 < len(s) else u''
            if (mae and NIHON.match(mae)) or (ato and NIHON.match(ato)):
                continue
        out.append(ch)
    return re.sub(u'  +', u' ', u''.join(out)).strip()


kagi = os.environ.get('IZK_AUTH')
if not kagi:
    print(u'環境変数 IZK_AUTH がありません。'); sys.exit(1)
ATAMA = {'Authorization': 'Basic ' + base64.b64encode(kagi.encode()).decode()}


def yobu(p, obj=None):
    q = ur.Request('https://www.ishinazaka.co.jp/wp-json' + p,
                   data=json.dumps(obj).encode('utf-8') if obj else None,
                   method='POST' if obj else 'GET')
    for k, v in ATAMA.items():
        q.add_header(k, v)
    if obj:
        q.add_header('Content-Type', 'application/json; charset=utf-8')
    return json.load(ur.urlopen(q, timeout=90))


def main():
    yaru = ('--apply' in sys.argv) and ('--yes' in sys.argv)
    print(u'書き込み:', u'する' if yaru else u'しない（調べるだけ）')

    S = json.load(io.open('/tmp/claude-0/site/seo-mae.json', encoding='utf-8'))
    print(u'控えてある件数:', len(S))

    shigoto = []
    for r in S:
        if r['slug'] in YOKERU:
            continue
        t2 = tsumeru(r['seo_title'])
        d2 = tsumeru(r['seo_desc'])
        p2 = tsumeru(r['post_title'])
        if t2 != r['seo_title'] or d2 != r['seo_desc'] or p2 != r['post_title']:
            shigoto.append((r, t2, d2, p2))

    print(u'直すページ:', len(shigoto))
    print(u'  SEOの題名:', sum(1 for r,t,d,p in shigoto if t != r['seo_title']))
    print(u'  SEOの説明文:', sum(1 for r,t,d,p in shigoto if d != r['seo_desc']))
    print(u'  記事の題名:', sum(1 for r,t,d,p in shigoto if p != r['post_title']))
    print(u'  人が直すもの（除外）:', len(YOKERU))

    if not yaru:
        print(u'--apply --yes が無いので、ここで終わります。')
        return

    ok = ng = 0
    for i, (r, t2, d2, p2) in enumerate(shigoto, 1):
        time.sleep(0.12)
        try:
            # 1) 記事そのものの題名（URLは変えない）
            if p2 != r['post_title']:
                n = yobu('/wp/v2/%s/%d' % (r['type'], r['id']), {'title': p2})
                assert n['slug'] == r['slug'], u'綴りが変わった'
            # 2) SEOの題名と説明文（送らない項目は消えるので、まとめて送る）
            if t2 != r['seo_title'] or d2 != r['seo_desc']:
                okuri = {'id': r['id'], 'title': t2, 'description': d2}
                if r.get('keyphrases'):
                    okuri['keyphrases'] = r['keyphrases']
                yobu('/aioseo/v1/post', okuri)
            # 3) 読み返して確かめる
            c = yobu('/aioseo/v1/post?postId=%d' % r['id'])['data']['currentPost']
            assert (c.get('title') or '') == t2, u'SEOの題名が違う'
            assert (c.get('description') or '') == d2, u'SEOの説明文が違う'
            w = yobu('/wp/v2/%s/%d?context=edit' % (r['type'], r['id']))
            assert w['title']['raw'] == p2, u'記事の題名が違う'
            assert w['slug'] == r['slug'], u'綴りが変わった'
            assert w['status'] == 'publish', u'公開状態が変わった'
            ok += 1
        except Exception as e:
            ng += 1
            print(u'  × %s -> %s %s' % (r['slug'], type(e).__name__, str(e)[:90]))
        if i % 25 == 0:
            print(u'  %d / %d（成功%d 失敗%d）' % (i, len(shigoto), ok, ng))

    print(u'\n直し終えました。成功 %d ／ 失敗 %d' % (ok, ng))


if __name__ == '__main__':
    main()
