// CPU profile of a page load (mobile, 4x CPU). Prints functions with the most self time, by script.
//   node seo/perf/profile.js URL
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true });
  const page = await ctx.newPage(); const cdp = await ctx.newCDPSession(page);
  await cdp.send('Emulation.setCPUThrottlingRate', { rate: 4 });
  await cdp.send('Profiler.enable'); await cdp.send('Profiler.setSamplingInterval', { interval: 200 }); await cdp.send('Profiler.start');
  await page.goto(process.argv[2], { waitUntil: 'load', timeout: 90000 }); await page.waitForTimeout(6000);
  const { profile } = await cdp.send('Profiler.stop');
  const dt = {}; const ids = profile.samples; const deltas = profile.timeDeltas; const byId = {};
  profile.nodes.forEach(n => byId[n.id] = n);
  ids.forEach((id, i) => { const n = byId[id]; const f = n.callFrame; const k = `${(f.url || '(native)').split('/').pop().split('?')[0]}:${f.lineNumber + 1}:${f.columnNumber} ${f.functionName || '(anon)'}`; dt[k] = (dt[k] || 0) + deltas[i] / 1000; });
  Object.entries(dt).sort((a, b) => b[1] - a[1]).slice(0, 25).forEach(([k, v]) => console.log(v.toFixed(0).padStart(6), 'ms', k));
  await b.close();
})();
