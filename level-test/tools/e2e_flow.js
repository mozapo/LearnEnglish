// Full flow on staging: take the test -> result -> "Hatalarımı hesabımda çalış" -> register -> /panel "Seviye testim".
// The level-test email request is intercepted, so no result email is sent. The new account uses an
// @example.com address (reserved, never delivered). Run: TARGET_URL=$WP_STAGING_URL node tools/e2e_flow.js
const { chromium } = require('playwright');
const path = require('path');
const URL0 = process.env.TARGET_URL;

// Hostinger's bot check sometimes answers headless Chrome with a 403 "Checking your browser" page that injects
// the real content without the body classes. Retry until the real page (status 200) is served.
async function gotoReal(page, url) {
  for (let i = 0; i < 8; i++) {
    const r = await page.goto(url + (url.includes('?') ? '&' : '?') + 'r=' + Date.now() + i, { waitUntil: 'load' });
    if (r.status() === 200) return;
    await page.waitForTimeout(4000);
  }
  throw new Error('bot check never cleared for ' + url);
}
let failures = 0;
const check = (c, m) => { console.log((c ? 'ok   ' : 'FAIL ') + m); if (!c) failures++; };

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--headless=new'] });
  const ctx = await b.newContext({ viewport: { width: 390, height: 900 } });
  const pg = await ctx.newPage();
  const errs = [];
  pg.on('pageerror', e => errs.push(pg.url() + ' :: ' + e.message));
  let posted = null;
  await pg.route('**/wp-json/bai/v1/level-test', r => { posted = JSON.parse(r.request().postData()); r.fulfill({ status: 200, contentType: 'application/json', body: '{"ok":true}' }); });

  await gotoReal(pg, URL0 + '/seviye-testi-40/');
  check((await pg.textContent('#bai-lq-form')).includes('18 yaşından küçüksen'), 'under-18 note shown on the form');
  await pg.fill('#bai-lq-name', 'QA Test'); await pg.fill('#bai-lq-email', 'qa@example.com');
  await pg.check('#bai-lq-consent');
  await pg.click('#bai-lq-form button[type=submit]'); await pg.waitForSelector('#bai-lq-quiz.is-on');
  const key = await pg.evaluate(() => null);
  // A1-B1 right (21), the rest "I don't know"
  const answers = [3,2,3,1,0,3,2,3,1,3,0,2,3,1,0,3,1,3,0,2,1];
  for (let i = 0; i < 40; i++) {
    if (await pg.isVisible('#bai-lq-mile')) await pg.click('#bai-lq-cont');
    const opts = await pg.$$('#bai-lq-opts button');
    await opts[i < answers.length ? answers[i] : 4].click();
    await pg.click('#bai-lq-next');
  }
  await pg.waitForSelector('#bai-lq-res.is-on'); await pg.waitForTimeout(400);
  check((await pg.textContent('#bai-lq-lvl')) === 'B1', 'placed B1 (21/40, A1-B1 mastered)');
  check(await pg.isHidden('#bai-lq-near'), 'no "çok yakın" line at 21 (B2 needs 28)');
  check(posted ? posted.result.placed === 'B1' : false, 'email payload carries the new level');
  const link = await pg.getAttribute('#bai-lq-save-link', 'href');
  check(/^\/panel\/\?lt=1\d{8}[0-4x]{40}#seviye-testim$/.test(link), 'practice link carries the attempt code: ' + link.slice(0, 30) + '…');
  check(await pg.evaluate(() => !!localStorage.getItem('bai_lt_v1')), 'attempt saved in this browser');
  await pg.screenshot({ path: path.join(__dirname, 'flow-1-result.png'), fullPage: true });

  await pg.click('#bai-lq-save-link'); await pg.waitForLoadState('load');
  await pg.waitForSelector('#seviye-testim:not([hidden])');
  check((await pg.textContent('#seviye-testim')).includes('Seviye testi sonucun hazır'), 'logged out: /panel invites to register, badge shown');
  await pg.screenshot({ path: path.join(__dirname, 'flow-2-panel-logged-out.png'), fullPage: true });

  await pg.click('#seviye-testim a.bai-ltp__btn'); await pg.waitForLoadState('load');
  // Registration is protected by reCAPTCHA, which this sandbox cannot reach (and must not bypass).
  // So: check the registration form keeps the code, then check the logged-in view on the real staging page
  // with the body marked "logged-in" (the only thing the section reads).
  const rd = await pg.$eval('input[name=redirect_to]', e => e.value);
  check(/^\/panel\/\?lt=1\d{8}[0-4x]{40}#seviye-testim$/.test(rd), 'registration form will send the student back to /panel with the code');
  const ctx2 = await b.newContext({ viewport: { width: 390, height: 900 } });
  // add "logged-in" to the server's <body class>, exactly what WordPress does for a logged-in user
  await ctx2.route('**/panel/**', async route => {
    if (route.request().resourceType() !== 'document') return route.continue();
    const resp = await route.fetch();
    const body = (await resp.text()).replace('<body itemtype', '<body data-qa="1" itemtype').replace(/(<body[^>]*class=")/, '$1logged-in ');
    route.fulfill({ response: resp, body });
  });
  const p2 = await ctx2.newPage(); p2.on('pageerror', e => errs.push(p2.url() + ' :: ' + e.message));
  await gotoReal(p2, URL0 + link.replace('#seviye-testim', ''));
  await p2.waitForSelector('#seviye-testim:not([hidden])', { timeout: 15000 });
  const txt = await p2.textContent('#seviye-testim');
  check(txt.includes('B1 İletişimci') ? txt.includes('Öncelikli konular') : false, 'account view shows badge and priority topics');
  check((await p2.$$('.bai-ltp__card:not(.bai-ltp__later) .bai-ltp__row')).length === 7, '7 priority topics (the B2 mistakes)');
  check(await p2.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth), 'no horizontal scroll on the real page at 390px');
  await p2.evaluate(() => document.getElementById('seviye-testim').scrollIntoView()); await p2.waitForTimeout(1500);
  const op = await p2.evaluate(() => { let o = document.getElementById('seviye-testim'), v = 1; while (o) { v *= +getComputedStyle(o).opacity; o = o.parentElement; } const c = document.querySelector('.bai-ltp__card'); let w = 1; let x = c; while (x) { w *= +getComputedStyle(x).opacity; x = x.parentElement; } return [v, w]; });
  check(op[0] === 1 ? op[1] === 1 : false, 'section is actually visible (opacity ' + op.join(' / ') + '), not hidden by the theme animation');
  await p2.screenshot({ path: path.join(__dirname, 'flow-3-panel-logged-in.png'), fullPage: true });
  await p2.click('.bai-ltp__rowbtn');
  check(await p2.isVisible('.bai-ltp__q'), 'topic card opens with the quick check');
  await p2.screenshot({ path: path.join(__dirname, 'flow-4-card.png'), fullPage: true });
  check(errs.length === 0, 'no JavaScript errors ' + (errs.length ? JSON.stringify(errs) : ''));
  await b.close();
  console.log(failures ? `\n${failures} FAILED` : '\nall checks passed');
  process.exit(failures ? 1 : 0);
})();
