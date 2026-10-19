// Screenshots of the edited sections at 390px on a target site (staging is fetched logged out).
//   node seo/perf/shots.js BASE OUTDIR
const { chromium } = require('playwright');
const [base, out] = process.argv.slice(2);
const shots = [
  ['blog', '/blog/', 'text=skor garantisi neden verilmez?'],
  ['sss', '/sikca-sorulan-sorular/', 'summary:has-text("çevrim içi ödeme")'],
  ['muafiyet', '/universite-hazirlik-muafiyet-sinavlari/', '.hmx-card__acts >> nth=0'],
  ['konusma', '/programlar/bireysel-programlar/ingilizce-programlari/ingilizce-konusma-programi/', 'text=seninle birlikte netleştirilir'],
  ['yurtdisi', '/yurt-disi-egitim/', 'text=Kanada’da eğitim'],
  ['unirehber', '/universite-rehberi/', 'text=Kanada seçeneğini değerlendir'],
];
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
  const page = await ctx.newPage();
  let dismissed = false;
  for (const [name, path, sel] of shots) {
    await page.goto(base + path, { waitUntil: 'load', timeout: 90000 });
    if (!dismissed) { const btn = page.getByRole('button', { name: 'Yalnızca Gerekli' }); if (await btn.isVisible().catch(() => false)) { await btn.click(); dismissed = true; } }
    const el = page.locator(sel).first();
    if (name === 'sss') { await el.click(); }
    await el.scrollIntoViewIfNeeded(); await page.waitForTimeout(1500);
    await page.screenshot({ path: `${out}/${name}.png` });
    console.log(name, 'ok');
  }
  await b.close();
})();
