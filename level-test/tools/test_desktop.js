// Desktop width (1280px) and keyboard-only use of "Seviye testim", locally.
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
const panel = fs.readFileSync(path.join(__dirname, '..', 'staging', '5402-panel.html'), 'utf8');
const block = panel.slice(panel.indexOf('<!-- bai:seviye-testim -->'), panel.indexOf('<!-- /bai:seviye-testim -->'));
const QS = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'staging', '4011-seviye-testi-40.html'), 'utf8').match(/var QUESTIONS = (\[.*?\]);/s)[1]);
const code = '120261017' + QS.map(q => (['A1', 'A2'].includes(q.level) ? String(q.answer) : '4')).join('');
let fail = 0; const check = (c, m) => { console.log((c ? 'ok   ' : 'FAIL ') + m); if (!c) fail++; };
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--headless=new'] });
  const ctx = await b.newContext({ viewport: { width: 1280, height: 900 } });
  await ctx.route('https://bai.test/**', r => r.fulfill({ contentType: 'text/html; charset=utf-8', body: `<!doctype html><html><head><meta charset="utf-8"></head><body class="logged-in" style="background:#16233F;margin:0">${block}</body></html>` }));
  const pg = await ctx.newPage();
  await pg.goto('https://bai.test/panel/?lt=' + code);
  check((await pg.textContent('.bai-ltp__badge strong')) === 'A2 Kurucu', 'A1-A2 mastered, rest unknown -> A2 Kurucu');
  const pri = await pg.$$eval('.bai-ltp__card:not(.bai-ltp__later) .bai-ltp__row', r => r.length);
  check(pri === 7, `priority = the 7 B1 topics (got ${pri})`);
  const w = await pg.$eval('#seviye-testim', e => e.getBoundingClientRect().width);
  check(w <= 820, 'section width capped at 820px on desktop (' + Math.round(w) + ')');
  await pg.screenshot({ path: path.join(__dirname, 'desktop-home.png'), fullPage: true });
  // keyboard only: Tab to the first "Çalış" button, Enter, then answer with Tab+Enter
  await pg.focus('.bai-ltp__rowbtn'); await pg.keyboard.press('Enter');
  const focused = await pg.evaluate(() => document.activeElement.tagName + ' ' + document.activeElement.textContent.slice(0, 30));
  check(focused.startsWith('H2'), 'focus moves to the topic title after opening (' + focused + ')');
  await pg.keyboard.press('Tab'); await pg.keyboard.press('Tab');
  let tag = await pg.evaluate(() => document.activeElement.className);
  for (let i = 0; i < 6 ? !tag.includes('bai-ltp__opt') : false; i++) { await pg.keyboard.press('Tab'); tag = await pg.evaluate(() => document.activeElement.className); }
  check(tag.includes('bai-ltp__opt'), 'answer options reachable with Tab');
  await pg.keyboard.press('Enter');
  check((await pg.$$('.bai-ltp__opt:disabled')).length >= 3, 'Enter picks an answer and locks the question');
  check((await pg.textContent('.bai-ltp__fb')).length > 3, 'feedback announced (aria-live) after answering');
  await pg.screenshot({ path: path.join(__dirname, 'desktop-card.png'), fullPage: true });
  await b.close(); console.log(fail ? fail + ' FAILED' : 'all checks passed'); process.exit(fail ? 1 : 0);
})();
