# -*- coding: utf-8 -*-
u"""セキュリティの点検（読むだけ。書き込み・ログイン試行・総当たりは一切しない）。
自社サイト www.ishinazaka.co.jp に対する、外から見える範囲の確認。"""
import re, json, ssl, socket, sys, io, datetime
import urllib.request as ur, urllib.error as ue
B = 'https://www.ishinazaka.co.jp'
UA = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125.0 Safari/537.36','Accept-Language':'ja'}
R = {}
class NoRedirect(ur.HTTPRedirectHandler):
    def redirect_request(self, *a, **k): return None
op_nr = ur.build_opener(NoRedirect)
def get(u, redirect=True, method='GET', headers=None):
    h = dict(UA); h.update(headers or {})
    q = ur.Request(u, headers=h, method=method)
    try:
        r = (ur.urlopen if redirect else op_nr.open)(q, timeout=40)
        b = r.read(400000)
        return r.getcode(), dict(r.headers), b.decode('utf-8','replace'), r.geturl()
    except ue.HTTPError as e:
        try: b = e.read(400000).decode('utf-8','replace')
        except Exception: b = ''
        return e.code, dict(e.headers), b, u
    except Exception as e:
        return type(e).__name__, {}, '', u

# 1. 応答ヘッダ（トップ）
c, h, body, _ = get(B + '/')
hl = {k.lower(): v for k, v in h.items()}
R['headers'] = {k: hl.get(k) for k in ['strict-transport-security','content-security-policy','x-frame-options','x-content-type-options','referrer-policy','permissions-policy','server','x-powered-by','cache-control','cross-origin-opener-policy']}
R['set_cookie_top'] = hl.get('set-cookie')

# 2. http→https、www なし
R['redirects'] = {}
for u in ('http://www.ishinazaka.co.jp/', 'http://ishinazaka.co.jp/', 'https://ishinazaka.co.jp/'):
    c2, h2, _, _ = get(u, redirect=False)
    R['redirects'][u] = (c2, {k.lower(): v for k, v in h2.items()}.get('location'))

# 3. TLS
def tls(ver=None, host='www.ishinazaka.co.jp'):
    ctx = ssl.create_default_context()
    if ver is not None: ctx.minimum_version = ctx.maximum_version = ver
    try:
        with socket.create_connection((host, 443), timeout=20) as s, ctx.wrap_socket(s, server_hostname=host) as ss:
            cert = ss.getpeercert(); return True, ss.version(), cert
    except Exception as e: return False, type(e).__name__ + ':' + str(e)[:80], None
ok, ver, cert = tls()
R['tls'] = {'default': ver, 'ok': ok}
if cert:
    R['tls']['issuer'] = dict(x[0] for x in cert['issuer']).get('organizationName')
    R['tls']['notAfter'] = cert['notAfter']; R['tls']['san'] = [v for k, v in cert.get('subjectAltName', [])]
for name, v in (('TLSv1.0', ssl.TLSVersion.TLSv1), ('TLSv1.1', ssl.TLSVersion.TLSv1_1), ('TLSv1.2', ssl.TLSVersion.TLSv1_2), ('TLSv1.3', ssl.TLSVersion.TLSv1_3)):
    ok2, v2, _ = tls(v); R['tls'][name] = ok2

# 4. バージョンの露出
R['version'] = {}
R['version']['generator_meta'] = re.findall(r'<meta name="generator" content="([^"]+)"', body)
R['version']['ver_params'] = sorted(set(re.findall(r'wp-includes/[^"\']+\?ver=([0-9.]+)', body)))[:5]
c_rm, _, b_rm, _ = get(B + '/readme.html', redirect=False); R['version']['readme_html'] = (c_rm, re.search(r'Version ([0-9.]+)', b_rm).group(1) if 'Version' in b_rm else None)
c_rm2, _, b_rm2, _ = get(B + '/common/sys/readme.html', redirect=False); R['version']['readme_html_sys'] = (c_rm2, re.search(r'Version ([0-9.]+)', b_rm2).group(1) if 'Version' in b_rm2 else None)
R['version']['license_txt'] = get(B + '/license.txt', redirect=False)[0]
try:
    j = json.loads(get('https://api.wordpress.org/core/version-check/1.7/')[2]); R['version']['wp_latest'] = j['offers'][0]['current']
except Exception as e: R['version']['wp_latest'] = str(e)

# 5. 入口・API
R['entry'] = {}
for p in ('/wp-login.php', '/wp-admin/', '/common/sys/wp-login.php', '/common/sys/wp-admin/', '/xmlrpc.php', '/common/sys/xmlrpc.php', '/wp-cron.php', '/common/sys/wp-admin/admin-ajax.php', '/wp-json/', '/?rest_route=/', '/wp-json/wp/v2/users', '/?rest_route=/wp/v2/users', '/wp-json/wp/v2/users/1', '/wp-json/wp/v2/posts?per_page=1', '/wp-json/wp/v2/media?per_page=1', '/wp-json/wp/v2/comments?per_page=1', '/wp-json/wp/v2/search?search=a', '/wp-json/oembed/1.0/embed?url=' + B + '/butsuryu-taiko-2026/', '/feed/', '/?feed=rss2', '/wp-sitemap.xml', '/robots.txt', '/.well-known/security.txt', '/security.txt', '/ads.txt', '/?s=%3Cscript%3E'):
    c3, h3, b3, fin = get(B + p, redirect=False)
    hl3 = {k.lower(): v for k, v in h3.items()}
    R['entry'][p] = {'code': c3, 'location': hl3.get('location'), 'ctype': (hl3.get('content-type') or '')[:40], 'len': len(b3), 'cors': hl3.get('access-control-allow-origin'), 'set_cookie': hl3.get('set-cookie'), 'snip': re.sub(r'\s+', ' ', b3[:220])}
# xmlrpc は POST で有効か（害のない system.listMethods を1回だけ）
for p in ('/xmlrpc.php',):
    c4, h4, b4, _ = get(B + p, method='POST', headers={'Content-Type': 'text/xml'})
    R['entry'][p + ' POST'] = {'code': c4, 'snip': re.sub(r'\s+', ' ', b4[:200])}

# 6. 著者名の漏れ
R['author'] = {}
for i in (1, 2, 3, 4, 5):
    c5, h5, b5, _ = get(B + '/?author=%d' % i, redirect=False)
    R['author'][i] = (c5, {k.lower(): v for k, v in h5.items()}.get('location'))
c6, _, b6, _ = get(B + '/feed/')
R['author']['feed_creators'] = sorted(set(re.findall(r'<dc:creator><!\[CDATA\[(.*?)\]\]>', b6)))
R['author']['oembed_author'] = re.findall(r'"author_name":"([^"]*)"', R['entry']['/wp-json/oembed/1.0/embed?url=' + B + '/butsuryu-taiko-2026/']['snip'] + get(B + '/wp-json/oembed/1.0/embed?url=' + B + '/butsuryu-taiko-2026/')[2])

# 7. 置き忘れファイル・一覧表示
R['files'] = {}
for p in ('/common/files/uploads/', '/common/files/uploads/2026/10/', '/common/files/func/', '/common/files/themes/', '/common/sys/wp-includes/', '/wp-content/uploads/', '/wp-config.php.bak', '/wp-config.php~', '/wp-config.php.old', '/wp-config.txt', '/.env', '/.git/HEAD', '/.git/config', '/common/files/debug.log', '/wp-content/debug.log', '/backup.zip', '/backup.sql', '/www.ishinazaka.co.jp.zip', '/.htaccess', '/phpinfo.php', '/info.php', '/.DS_Store', '/common/files/func/ai-engine/readme.txt', '/common/files/func/contact-form-7/readme.txt'):
    c7, h7, b7, _ = get(B + p, redirect=False)
    R['files'][p] = {'code': c7, 'len': len(b7), 'listing': ('Index of' in b7 or '<title>Index' in b7), 'snip': re.sub(r'\s+', ' ', b7[:120])}

# 8. プラグインとテーマの版
plugs = sorted(set(re.findall(r'/common/files/func/([a-z0-9\-]+)/', body)))
R['plugins'] = {}
for s_ in plugs + ['all-in-one-seo-pack', 'broken-link-checker-seo', 'easy-accordion-free', 'wpconsent', 'ai-engine']:
    if s_ in R['plugins']: continue
    c8, _, b8, _ = get(B + '/common/files/func/%s/readme.txt' % s_)
    st = re.search(r'Stable tag:\s*([0-9.]+)', b8) if c8 == 200 else None
    tested = re.search(r'Tested up to:\s*([0-9.]+)', b8) if c8 == 200 else None
    try:
        j = json.loads(get('https://api.wordpress.org/plugins/info/1.0/%s.json' % s_)[2])
        latest, last_upd, tested_latest = j.get('version'), j.get('last_updated'), j.get('tested')
    except Exception: latest = last_upd = tested_latest = None
    R['plugins'][s_] = {'readme': c8, 'installed': st.group(1) if st else None, 'latest': latest, 'last_updated': last_upd, 'tested_up_to_installed': tested.group(1) if tested else None}
themes = sorted(set(re.findall(r'/common/files/themes/([a-z0-9\-_]+)/', body)))
R['themes'] = {}
for t in themes:
    c9, _, b9, _ = get(B + '/common/files/themes/%s/style.css' % t)
    R['themes'][t] = {'code': c9, 'version': (re.search(r'Version:\s*([0-9.]+)', b9).group(1) if re.search(r'Version:\s*([0-9.]+)', b9) else None), 'name': (re.search(r'Theme Name:\s*(.+)', b9).group(1).strip() if re.search(r'Theme Name:\s*(.+)', b9) else None)}

# 9. ページ内の気になる点
R['page'] = {}
R['page']['mixed_http'] = sorted(set(re.findall(r'(?:src|href)=["\'](http://[^"\']+)', body)))[:10]
R['page']['emails'] = sorted(set(re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', body)))
R['page']['xmlns'] = re.findall(r'<html[^>]*xmlns="([^"]+)"', body)
R['page']['inline_scripts'] = len(re.findall(r'<script(?![^>]*src=)[^>]*>', body))
R['page']['ext_script_hosts'] = sorted(set(re.findall(r'<script[^>]+src=["\']https?://([^/"\']+)', body)))
R['page']['chat_guest_user'] = re.findall(r'&quot;userData&quot;:(.{0,80})', body)[:1]
R['page']['chat_rest'] = bool(re.search(r'mwai-chatbot-container', body))
# お問い合わせフォーム
c10, _, b10, _ = get(B + '/contact/')
R['form'] = {'cf7': 'wpcf7' in b10, 'recaptcha': 'recaptcha' in b10.lower(), 'turnstile': 'turnstile' in b10.lower(), 'honeypot': ('wpcf7-honeypot' in b10 or 'honeypot' in b10.lower()), 'akismet': 'akismet' in b10.lower(), 'quiz': 'wpcf7-quiz' in b10, 'autop': True}
R['contact_headers'] = {k.lower(): v for k, v in get(B + '/contact/')[1].items() if k.lower() in ('set-cookie', 'x-frame-options', 'content-security-policy')}
# 404ページの中身
c11, _, b11, _ = get(B + '/kore-wa-nai-page-xyz/')
R['notfound'] = {'code': c11, 'php_error': bool(re.search(r'(Warning|Fatal error|Notice): .* on line \d+', b11)), 'len': len(b11)}
json.dump(R, io.open(sys.argv[1] + '/anzen.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
print(json.dumps(R, ensure_ascii=False, indent=1, default=str)[:12000])
