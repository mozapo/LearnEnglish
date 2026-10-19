// Blocking time on the home page (mobile, 4x CPU) with the inline contrast guard as-is vs. run once.
// "once" removes the load+300 ms and 1.5 s re-sweeps; the DOMContentLoaded sweep and the
// MutationObserver (for content added later, e.g. quiz results) stay. Also checks that the final
// inline colours are the same in both cases.
const { chromium } = require('playwright');
const url = process.argv[2] || 'https://biradimileri.com/', RUNS = 5;
const variants = {
  asis: s => s,
  once: s => s.replace("window.addEventListener('load', function () { setTimeout(sweep, 300); }); setTimeout(sweep, 1500);", ''),
};
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const finals = {};
  for (const [name, fn] of Object.entries(variants)) {
    const tbts = [];
    for (let i = 0; i < RUNS; i++) {
      const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true });
      const page = await ctx.newPage();
      let replaced = false;
      await page.route('**/*', async route => {
        if (route.request().resourceType() !== 'document') return route.continue();
        const r = await route.fetch(); const html = await r.text(); const out = fn(html);
        replaced = out !== html || name === 'asis';
        return route.fulfill({ response: r, body: out });
      });
      const cdp = await ctx.newCDPSession(page); await cdp.send('Emulation.setCPUThrottlingRate', { rate: 4 });
      await page.addInitScript(() => { window.__lt = []; new PerformanceObserver(l => l.getEntries().forEach(e => window.__lt.push(e.duration))).observe({ type: 'longtask', buffered: true }); });
      await page.goto(url, { waitUntil: 'load', timeout: 90000 }); await page.waitForTimeout(6000);
      tbts.push(await page.evaluate(() => window.__lt.reduce((s, d) => s + Math.max(0, d - 50), 0)));
      if (i === 0) finals[name] = await page.evaluate(() => [...document.querySelectorAll('body *')].map(e => [e.style.getPropertyValue('color'), e.style.getPropertyValue('background-color'), e.style.getPropertyValue('fill'), e.style.getPropertyValue('stroke')].join('|')).join('\n'));
      if (!replaced) throw new Error('variant ' + name + ' did not apply');
      await ctx.close();
    }
    tbts.sort((x, y) => x - y);
    console.log(name.padEnd(6), 'median blocking', Math.round(tbts[2]), 'ms  runs', tbts.map(Math.round).join(' '));
  }
  console.log('final inline colours identical:', finals.asis === finals.once);
  await b.close();
})();
