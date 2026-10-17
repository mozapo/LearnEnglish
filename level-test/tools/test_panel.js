// Local browser test of the "Seviye testim" block (no WordPress needed).
// Serves the built block on a fake origin, simulates logged-in / logged-out, and walks through the flows.
// Run from level-test/:  NODE_PATH=<dir with playwright> node tools/test_panel.js
const { chromium } = require('playwright');
const fs = require('fs'); const path = require('path');
const BASE = path.join(__dirname, '..');
const panel = fs.readFileSync(path.join(BASE, 'staging', '5402-panel.html'), 'utf8');
const block = panel.slice(panel.indexOf('<!-- bai:seviye-testim -->'), panel.indexOf('<!-- /bai:seviye-testim -->'));
const testPage = fs.readFileSync(path.join(BASE, 'staging', '4011-seviye-testi-40.html'), 'utf8');
const QS = JSON.parse(testPage.match(/var QUESTIONS = (\[.*?\]);/s)[1]);

const ORIGIN = 'https://bai.test';
function page(loggedIn) {
  return `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"></head>` +
    `<body class="page ${loggedIn ? 'logged-in' : ''}" style="background:#0f1a30;margin:0"><div id="bai-panel">[bai_panel]</div>${block}</body></html>`;
}
// answers: correct for levels in `good`, "I don't know" (4) elsewhere
function code(good) {
  return '120261017' + QS.map(q => (good.includes(q.level) ? String(q.answer) : '4')).join('');
}

let failures = 0;
function check(cond, msg) { if (!cond) { failures++; console.log('FAIL', msg); } else console.log('ok  ', msg); }

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--headless=new'] });
  const ctx = await b.newContext({ viewport: { width: 390, height: 860 } });
  let loggedIn = false;
  await ctx.route(ORIGIN + '/**', r => r.fulfill({ status: 200, contentType: 'text/html; charset=utf-8', body: page(loggedIn) }));
  const pg = await ctx.newPage();
  const errs = []; pg.on('pageerror', e => errs.push(e.message)); pg.on('console', m => { if (m.type() === 'error' && !m.text().startsWith('Failed to load resource')) errs.push(m.text()); });

  // 1. logged out, nothing stored: section stays hidden
  await pg.goto(ORIGIN + '/panel/');
  check(await pg.$eval('#seviye-testim', e => e.hidden), 'logged out without a result: section hidden');

  // 2. logged out, arriving with ?lt= (A1-B1 correct): badge + login/register links that carry the code
  const c1 = code(['A1', 'A2', 'B1']);
  await pg.goto(ORIGIN + '/panel/?lt=' + c1 + '#seviye-testim');
  check(!(await pg.$eval('#seviye-testim', e => e.hidden)), 'logged out with ?lt: section shown');
  check((await pg.textContent('.bai-ltp__badge strong')) === 'B1 İletişimci', 'badge shows B1 İletişimci for 21/40 with A1-B1 mastered');
  const reg = await pg.getAttribute('a.bai-ltp__btn', 'href');
  check(reg.startsWith('/giris-yap/?islem=kayit&redirect_to=') && decodeURIComponent(reg).includes('/panel/?lt=' + c1 + '#seviye-testim'), 'register link keeps the code in redirect_to');
  check(!(await pg.evaluate(() => location.search)).includes('lt='), 'lt is removed from the address bar');
  check((await pg.evaluate(() => JSON.parse(localStorage.getItem('bai_lt_v1')).code)) === c1, 'code saved in localStorage');

  // 3. logged in: home view with priority cards = mistakes at level <= B2 (placed B1 + 1) -> the 7 B2 cards; C1/C2 later
  loggedIn = true;
  await pg.goto(ORIGIN + '/panel/');
  const pri = await pg.$$eval('.bai-ltp__card:not(.bai-ltp__later) .bai-ltp__list .bai-ltp__row', r => r.length);
  const later = await pg.$$eval('.bai-ltp__later .bai-ltp__row', r => r.length);
  check(pri === 7, `priority topics = 7 B2 cards (got ${pri})`);
  check(later === 7, `later topics = 5 C1 + 2 C2 cards (got ${later})`);
  check((await pg.textContent('.bai-ltp__facts')).includes('21 / 40'), 'score 21 / 40 shown');

  // 4. open first card; answer the quick check all correct -> "known"
  await pg.click('.bai-ltp__rowbtn');
  const title = await pg.textContent('.bai-ltp__cardtitle h2');
  check(title.length > 3, 'card opened: ' + title);
  check((await pg.$$('.bai-ltp__mistakes li')).length >= 1, 'card shows the test item that was missed');
  const correctTexts = await pg.evaluate(() => null);
  async function answerAll(right) {
    const qs = await pg.$$('.bai-ltp__q');
    for (const q of qs) {
      const done = await q.$('button:disabled'); if (done) continue;
      const data = await q.evaluate(el => el.querySelector('.bai-ltp__qtext').textContent);
      // find the matching question in the card data to know the right option
      const ans = await pg.evaluate(t => { const s = document.getElementById('bai-ltp-js').textContent; return s; }, data);
      const btns = await q.$$('button');
      let clicked = false;
      for (const bt of btns) {
        const txt = await bt.textContent();
        const isRight = await pg.evaluate(([qt, ot]) => {
          const m = document.getElementById('bai-ltp-js').textContent.match(/var DATA = (\{.*?\});\s*var ORDER/s);
          const D = JSON.parse(m[1]);
          const all = [].concat(...D.cards.map(c => c.check.concat(c.prac)));
          const qq = all.find(x => qt.endsWith(x[0]));
          return qq ? qq[1][qq[2]] === ot : null;
        }, [data, txt]);
        if (isRight === right) { await bt.click(); clicked = true; break; }
      }
      if (!clicked) throw new Error('could not pick an option for ' + data);
    }
  }
  await answerAll(true);
  check((await pg.textContent('.bai-ltp__result')).includes('biliyorsun'), 'quick check 3/3 -> "aslında biliyorsun"');
  await pg.click('text=Sıradaki konu →');
  // 5. next card: miss the quick check -> lesson + practice; pass practice -> done
  await answerAll(false);
  check(await pg.isVisible('.bai-ltp__expl'), 'quick check missed -> explanation shown');
  const lead = await pg.textContent('.bai-ltp__expl');
  await pg.click('.bai-ltp__tab:not([aria-pressed="true"])');
  check((await pg.textContent('.bai-ltp__expl')) !== lead, 'language toggle switches the explanation');
  await answerAll(true);
  check((await pg.textContent('.bai-ltp__card:last-child .bai-ltp__result')).includes('Konu tamamlandı'), 'practice passed -> topic done');
  // 6. back home: progress 2 / 7, persisted after reload
  await pg.goto(ORIGIN + '/panel/');
  check((await pg.textContent('.bai-ltp__card:nth-of-type(2) .bai-ltp__note')).includes('2 / 7'), 'progress 2 / 7 after reload');
  // 7. a new attempt resets progress; an invalid code is ignored
  await pg.goto(ORIGIN + '/panel/?lt=1BAD');
  check((await pg.evaluate(() => JSON.parse(localStorage.getItem('bai_lt_v1')).code)) === c1, 'invalid code ignored');
  const c2 = code(['A1', 'A2', 'B1', 'B2', 'C1', 'C2']);
  await pg.goto(ORIGIN + '/panel/?lt=' + c2);
  check((await pg.textContent('.bai-ltp__badge strong')) === 'C2 Usta', 'perfect test -> C2 Usta');
  check((await pg.textContent('#seviye-testim')).includes('Hiç hatan yok'), 'no mistakes -> "Hiç hatan yok"');
  // 8. expired result (older than 12 months) is dropped
  await pg.evaluate(() => { const v = JSON.parse(localStorage.getItem('bai_lt_v1')); v.saved = Date.now() - 400 * 864e5; localStorage.setItem('bai_lt_v1', JSON.stringify(v)); });
  await pg.goto(ORIGIN + '/panel/');
  check((await pg.$eval('#seviye-testim', e => e.hidden)) ? (await pg.evaluate(() => localStorage.getItem('bai_lt_v1'))) === null : false, 'result older than 12 months is removed (section hidden, storage cleared)');
  // 8b. logged in, nothing stored (a teacher opening /panel): nothing shown
  await pg.evaluate(() => localStorage.clear()); await pg.goto(ORIGIN + '/panel/');
  check(await pg.$eval('#seviye-testim', e => e.hidden), 'logged in without any result: section hidden');
  // 9. delete button
  await pg.goto(ORIGIN + '/panel/?lt=' + c1);
  pg.once('dialog', d => d.accept());
  await pg.click('text=Sonucu bu tarayıcıdan sil');
  check((await pg.evaluate(() => localStorage.getItem('bai_lt_v1'))) === null, '"Sonucu sil" clears the browser storage');
  check((await pg.textContent('#seviye-testim')).includes('Henüz bir seviye testi sonucun yok'), 'after deleting, the student sees a short confirmation state');
  // 10. no horizontal scroll at phone width, desktop screenshot
  await pg.goto(ORIGIN + '/panel/?lt=' + c1);
  check(await pg.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth), 'no horizontal scroll at 390px');
  await pg.screenshot({ path: path.join(__dirname, 'panel-home.png'), fullPage: true });
  await pg.click('.bai-ltp__rowbtn');
  await pg.screenshot({ path: path.join(__dirname, 'panel-card.png'), fullPage: true });
  check(errs.length === 0, 'no console errors ' + (errs.length ? JSON.stringify(errs) : ''));
  await b.close();
  console.log(failures ? `\n${failures} FAILED` : '\nall checks passed');
  process.exit(failures ? 1 : 0);
})();
