// Which scripts cost main-thread time? Loads a page on a throttled mobile profile (4x CPU, 390px),
// once as-is and once per variant with one script disabled, and reports median total blocking time
// (sum of long-task time over 50 ms until 6 s after load) and the time of the last long task.
//   NODE_PATH=... node seo/perf/attribute.js https://biradimileri.com/ [runs]
const { chromium } = require('playwright');
const url = process.argv[2], RUNS = +(process.argv[3] || 3);
const INLINE = ['__baiContrastGuard', '__baiMegaEnrich', '__baiMegaCtl', '__baiMobileEnrich', '__baiFooterCss',
  '__baiFooterAcc', '__baiFaqCss', '__baiLegalBar', "var Q = [", 'surecookieGuard', 'lazyloadRunObserver'];
const EXTERNAL = ['bai-motion.js', 'surecookie/build/public.js', 'jquery-ui/sortable', 'touch-punch', 'elementor/assets/js/frontend.min.js', 'googletagmanager'];
const variants = [['baseline', null], ...INLINE.map(k => ['inline:' + k, k]), ...EXTERNAL.map(k => ['file:' + k, k])];
(async () => {
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const out = [];
  for (const [name, key] of variants) {
    const tbts = [], lasts = [];
    for (let i = 0; i < RUNS; i++) {
      const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true,
        userAgent: 'Mozilla/5.0 (Linux; Android 12) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125 Mobile Safari/537.36' });
      const page = await ctx.newPage();
      await page.route('**/*', async route => {
        const req = route.request(), u = req.url();
        if (/\/(bai\/v1\/level-test|bai\/v1\/lt-stat)/.test(u)) return route.abort();
        if (key && name.startsWith('file:') && u.includes(key)) return route.fulfill({ status: 200, contentType: 'application/javascript', body: '' });
        if (key && name.startsWith('inline:') && req.resourceType() === 'document') {
          const r = await route.fetch(); let html = await r.text();
          html = html.replace(/<script(?![^>]*\bsrc=)([^>]*)>([\s\S]*?)<\/script>/g, (m, a, body) => body.includes(key) && !/ld\+json/.test(a) ? `<script${a}></script>` : m);
          return route.fulfill({ response: r, body: html });
        }
        return route.continue();
      });
      const cdp = await ctx.newCDPSession(page);
      await cdp.send('Emulation.setCPUThrottlingRate', { rate: 4 });
      await page.addInitScript(() => { window.__lt = []; new PerformanceObserver(l => l.getEntries().forEach(e => window.__lt.push([e.startTime, e.duration]))).observe({ type: 'longtask', buffered: true }); });
      await page.goto(url, { waitUntil: 'load', timeout: 90000 });
      await page.waitForTimeout(6000);
      const lt = await page.evaluate(() => window.__lt);
      tbts.push(lt.reduce((s, [, d]) => s + Math.max(0, d - 50), 0));
      lasts.push(lt.length ? Math.max(...lt.map(([s, d]) => s + d)) : 0);
      await ctx.close();
    }
    const med = a => a.sort((x, y) => x - y)[Math.floor(a.length / 2)];
    out.push([name, Math.round(med(tbts)), Math.round(med(lasts))]);
    console.log(name.padEnd(48), 'blocking', String(Math.round(med(tbts))).padStart(5), 'ms   last long task ends', Math.round(med(lasts)), 'ms');
  }
  await browser.close();
})();
