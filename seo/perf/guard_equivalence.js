// Original vs. sliced contrast guard: final inline colours and blocking time.
// The page HTML is fetched live and the guard script is swapped in the browser only.
//   node seo/perf/guard_equivalence.js BASE path...
const { chromium } = require('playwright');
const fs = require('fs');
const ORIG = fs.readFileSync(__dirname + '/../menu/contrast-guard-original.js', 'utf8');
const NEW = fs.readFileSync(__dirname + '/../menu/contrast-guard-sliced.js', 'utf8');
const [base, ...paths] = process.argv.slice(2);
async function run(browser, url, variant) {
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
  const page = await ctx.newPage();
  await page.route('**/*', async route => {
    const req = route.request(); const u = req.url();
    if (/googletagmanager|google-analytics|\/bai\/v1\/(level-test|lt-stat)/.test(u)) return route.abort();
    if (req.resourceType() !== 'document') return route.continue();
    const r = await route.fetch(); let html = await r.text();
    if (!html.includes(ORIG)) throw new Error('original guard not found in ' + u);
    if (variant === 'new') html = html.replace(ORIG, NEW);
    return route.fulfill({ response: r, body: html });
  });
  const cdp = await ctx.newCDPSession(page); await cdp.send('Emulation.setCPUThrottlingRate', { rate: 4 });
  await page.addInitScript(() => { window.__lt = []; new PerformanceObserver(l => l.getEntries().forEach(e => window.__lt.push(e.duration))).observe({ type: 'longtask', buffered: true }); });
  await page.goto(url, { waitUntil: 'load', timeout: 120000 });
  await page.waitForTimeout(5000);
  const tbt = await page.evaluate(() => window.__lt.reduce((s, d) => s + Math.max(0, d - 50), 0));
  const h = await page.evaluate(() => document.body.scrollHeight);
  for (let y = 0; y < h; y += 600) { await page.evaluate(v => window.scrollTo(0, v), y); await page.waitForTimeout(120); }
  await page.waitForTimeout(4000); await page.evaluate(() => window.scrollTo(0, 0)); await page.waitForTimeout(+(process.env.SETTLE || 3000));
  const state = await page.evaluate(() => [...document.querySelectorAll('body *')].map((e, i) => {
    const s = e.style; const v = ['color', 'background-color', 'background-image', 'fill', 'stroke'].map(p => s.getPropertyValue(p) + (s.getPropertyPriority(p) ? '!' : '')).join('|');
    return v === '||||' ? null : i + ':' + e.tagName + ':' + v; }).filter(Boolean));
  await ctx.close();
  return { tbt, state };
}
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  let tot = { o: 0, n: 0 };
  for (const p of paths) {
    const o1 = await run(b, base + p, 'orig'), o2 = await run(b, base + p, 'orig'), n1 = await run(b, base + p, 'new');
    const diff = (a, c) => { const A = new Set(a.state), C = new Set(c.state); return [...A].filter(x => !C.has(x)).length + [...C].filter(x => !A.has(x)).length; };
    const noise = diff(o1, o2), d = Math.min(diff(o1, n1), diff(o2, n1));
    tot.o += (o1.tbt + o2.tbt) / 2; tot.n += n1.tbt;
    console.log(p.padEnd(32), 'styled', String(o1.state.length).padStart(4), '| orig-vs-orig', String(noise).padStart(3), '| orig-vs-new', String(d).padStart(3),
      '| blocking orig', Math.round((o1.tbt + o2.tbt) / 2), 'new', Math.round(n1.tbt));
    if (d > noise) { const A = new Set(o1.state); console.log('   new-only sample:', n1.state.filter(x => !A.has(x)).slice(0, 4)); }
  }
  console.log('TOTAL blocking orig', Math.round(tot.o), 'new', Math.round(tot.n));
  await b.close();
})();
