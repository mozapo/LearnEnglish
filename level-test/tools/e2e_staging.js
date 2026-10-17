const { chromium } = require('playwright');
(async () => {
  const exe = require('fs').existsSync('/opt/pw-browsers/chromium-1134/chrome-linux/chrome') ? undefined : '/opt/pw-browsers/chromium';
  const b = await chromium.launch({ executablePath: exe, args:['--headless=new'] });
  const ctx = await b.newContext({ viewport: { width: 390, height: 900 } }); await ctx.addCookies([]); const pg = await ctx.newPage();
  const errs = []; pg.on('pageerror', e => errs.push(e.message));
  let posted = 0;
  await pg.route('**/wp-json/bai/v1/lt-stat', r => r.fulfill({ status: 200, contentType: 'application/json', body: '{"ok":true}' }));
  await pg.route('**/wp-json/bai/v1/level-test', r => { posted++; r.fulfill({ status: 200, contentType: 'application/json', body: '{"ok":true}' }); });
  await pg.goto((process.env.TARGET_URL || process.env.WP_STAGING_URL) + '/seviye-testi-40/?nocache=' + Date.now(), { waitUntil: 'load' });
  await pg.fill('#bai-lq-name', 'Test Öğrenci'); await pg.fill('#bai-lq-email', 'noreply@example.com');
  const cb = await pg.$('#bai-lq-form input[type=checkbox]'); if (cb) await cb.check();
  await pg.click('#bai-lq-form button[type=submit]'); await pg.waitForSelector('#bai-lq-quiz.is-on');
  const qs = await pg.evaluate(() => null);
  // answer: correct for A1-B1, wrong for B2+ (pick "I don't know")
  const key = [3,2,3,1,0,3,2,3,1,3,0,2,3,1,0,3,1,3,0,2,1];
  for (let i = 0; i < 40; i++) {
    if (await pg.isVisible('#bai-lq-mile')) {
      console.log('MILE:', await pg.textContent('#bai-lq-mile-t'), '|', await pg.textContent('#bai-lq-mile-p'), '|', await pg.textContent('#bai-lq-mile-xp'));
      await pg.click('#bai-lq-cont');
    }
    const opts = await pg.$$('#bai-lq-opts button');
    await opts[i < key.length ? key[i] : 4].click();
    await pg.click('#bai-lq-next');
  }
  await pg.waitForSelector('#bai-lq-res.is-on');
  await pg.waitForTimeout(500);
  console.log('LEVEL', await pg.textContent('#bai-lq-lvl'), '|', await pg.textContent('#bai-lq-rozet'), '| print btn:', await pg.textContent('#bai-lq-print'));
  console.log('NOTE', await pg.textContent('#bai-lq-res .bai-lq__acts + p'));
  console.log('posted', posted, 'errors', errs);
  await pg.evaluate(()=>{document.querySelectorAll('[class*=surecookie],[id*=surecookie],#bai-lq-confetti').forEach(e=>e.remove())}); await pg.locator('#bai-lq-res .bai-lq__level').first().screenshot({ path: __dirname + '/result.png' });
  await b.close();
})();
