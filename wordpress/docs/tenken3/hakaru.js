// スマホの大きさで開いて、読み込みの重さと速さ、スクリプトの誤りを測る（読むだけ）
const { chromium, devices } = require('/opt/node-tools/node_modules/playwright');
const fs = require('fs');
const OUT = process.argv[2];
const PAGES = [['home', 'https://www.ishinazaka.co.jp/'], ['kiji', 'https://www.ishinazaka.co.jp/shiro-tora-shobun-kijun-kakutei/'], ['saiseki', 'https://www.ishinazaka.co.jp/saiseki-hanbai/']];
(async () => {
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--no-sandbox'] });
  const result = {};
  for (const [name, url] of PAGES) {
    const ctx = await browser.newContext({ ...devices['Pixel 7'], locale: 'ja-JP' });
    const page = await ctx.newPage();
    const reqs = []; const errors = []; const failed = [];
    page.on('response', async r => { let n = 0; try { const b = await r.body(); n = b.length; } catch (e) {} reqs.push({ url: r.url(), status: r.status(), type: r.request().resourceType(), bytes: n }); });
    page.on('requestfailed', r => failed.push(r.url() + ' ' + (r.failure() || {}).errorText));
    page.on('console', m => { if (m.type() === 'error') errors.push(m.text().slice(0, 160)); });
    page.on('pageerror', e => errors.push('pageerror: ' + String(e).slice(0, 160)));
    await page.addInitScript(() => {
      window.__lcp = 0; window.__cls = 0;
      new PerformanceObserver(l => { for (const e of l.getEntries()) window.__lcp = e.startTime; }).observe({ type: 'largest-contentful-paint', buffered: true });
      new PerformanceObserver(l => { for (const e of l.getEntries()) if (!e.hadRecentInput) window.__cls += e.value; }).observe({ type: 'layout-shift', buffered: true });
    });
    const t0 = Date.now();
    await page.goto(url, { waitUntil: 'load', timeout: 90000 });
    const loadMs = Date.now() - t0;
    await page.waitForTimeout(4000);
    const m = await page.evaluate(() => { const n = performance.getEntriesByType('navigation')[0]; return { ttfb: n.responseStart, dcl: n.domContentLoadedEventEnd, load: n.loadEventEnd, lcp: window.__lcp, cls: window.__cls, h1: document.querySelectorAll('h1').length, imgs: document.images.length, fontPx: getComputedStyle(document.body).fontSize, docH: document.documentElement.scrollHeight, scrollW: document.documentElement.scrollWidth, vw: innerWidth, tapSmall: [...document.querySelectorAll('a,button')].filter(a => { const r = a.getBoundingClientRect(); return r.width > 0 && (r.width < 24 || r.height < 24); }).length }; });
    const byType = {}; for (const r of reqs) { byType[r.type] = byType[r.type] || { n: 0, kb: 0 }; byType[r.type].n++; byType[r.type].kb += r.bytes / 1024; }
    const big = reqs.filter(r => r.bytes > 150000).sort((a, b) => b.bytes - a.bytes).slice(0, 8).map(r => [Math.round(r.bytes / 1024) + 'KB', r.type, r.url.replace('https://www.ishinazaka.co.jp', '').slice(0, 80)]);
    const third = {}; for (const r of reqs) { const h = new URL(r.url).host; if (!h.includes('ishinazaka')) third[h] = (third[h] || 0) + 1; }
    result[name] = { url, loadMs, ...m, requests: reqs.length, totalKB: Math.round(reqs.reduce((s, r) => s + r.bytes, 0) / 1024), byType: Object.fromEntries(Object.entries(byType).map(([k, v]) => [k, [v.n, Math.round(v.kb)]])), big, third, errors: errors.slice(0, 10), failed: failed.slice(0, 10), horizontalScroll: m.scrollW > m.vw };
    await page.screenshot({ path: `${OUT}/${name}-phone.png`, fullPage: false });
    if (name === 'home') { await page.screenshot({ path: `${OUT}/${name}-phone-full.png`, fullPage: true }); }
    await ctx.close();
  }
  const ctx = await browser.newContext({ viewport: { width: 1366, height: 800 }, locale: 'ja-JP' }); const page = await ctx.newPage();
  await page.goto('https://www.ishinazaka.co.jp/', { waitUntil: 'load', timeout: 90000 }); await page.waitForTimeout(2000);
  await page.screenshot({ path: `${OUT}/home-pc.png`, fullPage: false }); await ctx.close();
  await browser.close();
  fs.writeFileSync(`${OUT}/hakaru.json`, JSON.stringify(result, null, 1));
  console.log(JSON.stringify(result, null, 1));
})().catch(e => { console.error('ERR', e); process.exit(1); });
