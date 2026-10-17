// Staging only: take the test and let the anonymous statistic reach the real endpoint (email still intercepted).
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--headless=new'] });
  const pg = await b.newPage({ viewport: { width: 390, height: 900 } });
  await pg.route('**/wp-json/bai/v1/level-test', r => r.fulfill({ status: 200, contentType: 'application/json', body: '{"ok":true}' }));
  let statStatus = null;
  pg.on('response', r => { if (r.url().includes('/bai/v1/lt-stat')) statStatus = r.status(); });
  for (let i = 0; i < 8; i++) { const r = await pg.goto(process.env.TARGET_URL + '/seviye-testi-40/?r=' + Date.now(), { waitUntil: 'load' }); if (r.status() === 200) break; await pg.waitForTimeout(4000); }
  console.log('form note:', (await pg.textContent('#bai-lq-form')).includes('anonim olarak saklanır'));
  await pg.fill('#bai-lq-name', 'QA'); await pg.fill('#bai-lq-email', 'qa@example.com'); await pg.check('#bai-lq-consent');
  await pg.click('#bai-lq-form button[type=submit]'); await pg.waitForSelector('#bai-lq-quiz.is-on');
  const key = [3,2,3,1,0,3,2,3,1,3,0,2,3,1];
  for (let i = 0; i < 40; i++) {
    if (await pg.isVisible('#bai-lq-mile')) await pg.click('#bai-lq-cont');
    const o = await pg.$$('#bai-lq-opts button'); await o[i < key.length ? key[i] : 4].click(); await pg.click('#bai-lq-next');
  }
  await pg.waitForSelector('#bai-lq-res.is-on'); await pg.waitForTimeout(2500);
  console.log('level:', await pg.textContent('#bai-lq-lvl'), '| stat request status:', statStatus);
  await b.close();
})();
