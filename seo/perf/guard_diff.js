// Show which elements the original guard styles but the sliced one does not (one page).
const { chromium } = require('playwright'); const fs = require('fs');
const ORIG = fs.readFileSync(__dirname + '/../menu/contrast-guard-original.js', 'utf8');
const NEW = fs.readFileSync(__dirname + '/../menu/' + (process.env.NEWFILE || 'contrast-guard-sliced.js'), 'utf8');
async function run(b, url, variant) {
  const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
  const page = await ctx.newPage();
  await page.route('**/*', async route => { const req = route.request();
    if (/googletagmanager/.test(req.url())) return route.abort();
    if (req.resourceType() !== 'document') return route.continue();
    const r = await route.fetch(); let html = await r.text(); if (variant === 'new') html = html.replace(ORIG, NEW);
    return route.fulfill({ response: r, body: html }); });
  const cdp = await ctx.newCDPSession(page); await cdp.send('Emulation.setCPUThrottlingRate', { rate: 4 });
  await page.goto(url, { waitUntil: 'load', timeout: 120000 }); await page.waitForTimeout(5000);
  const h = await page.evaluate(() => document.body.scrollHeight);
  for (let y = 0; y < h; y += 600) { await page.evaluate(v => window.scrollTo(0, v), y); await page.waitForTimeout(120); }
  await page.waitForTimeout(4000); await page.evaluate(() => window.scrollTo(0, 0)); await page.waitForTimeout(8000);
  const s = await page.evaluate(() => [...document.querySelectorAll('body *')].map((e, i) => { const st = e.style;
    const v = ['color', 'background-color', 'background-image', 'fill', 'stroke'].map(p => st.getPropertyValue(p)).join('|');
    return v === '||||' ? null : i + ' ' + e.tagName + '.' + (e.className && e.className.baseVal === undefined ? String(e.className).slice(0, 40) : '') + ' [' + v + '] orig=' + e.getAttribute('data-bai-orig-color') + ' "' + (e.textContent || '').trim().slice(0, 30) + '"'; }).filter(Boolean));
  await ctx.close(); return s;
}
(async () => { const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const o = await run(b, process.argv[2], 'orig'), n = await run(b, process.argv[2], 'new'); const N = new Set(n), O = new Set(o);
  console.log('orig', o.length, 'new', n.length); console.log('ONLY ORIG:'); o.filter(x => !N.has(x)).slice(0, 12).forEach(x => console.log('  ', x));
  console.log('ONLY NEW:'); n.filter(x => !O.has(x)).slice(0, 12).forEach(x => console.log('  ', x)); await b.close(); })();
