// Checks the feedback change set on a site in a real browser (default: staging).
// Usage: node feedback-page/test/staging.test.js [base-url] [screenshot-dir]
const { chromium } = require("playwright");
const path = require("path");

const base = (process.argv[2] || process.env.WP_STAGING_URL).replace(/\/$/, "");
const shots = path.resolve(process.argv[3] || ".");
const proxy = process.env.HTTPS_PROXY ? { server: process.env.HTTPS_PROXY } : undefined;
let failures = 0;
const check = (ok, msg) => { console.log((ok ? "PASS " : "FAIL ") + msg); if (!ok) failures++; };
const bust = () => "?v=" + Date.now();

(async () => {
  const browser = await chromium.launch({ proxy });
  for (const [label, viewport] of [["390", { width: 390, height: 844 }], ["1280", { width: 1280, height: 900 }]]) {
    const ctx = await browser.newContext({ viewport, ignoreHTTPSErrors: false });
    const p = await ctx.newPage();
    const errors = [];
    p.on("pageerror", (e) => errors.push(e.message));

    const r = await p.goto(base + "/geri-bildirim/" + bust(), { waitUntil: "networkidle" });
    check(r.status() === 200, `[${label}] /geri-bildirim/ returns 200`);
    check((await p.locator("h1").count()) === 1, `[${label}] exactly one H1`);
    check(/Bir şey yolunda gitmediyse/.test(await p.locator("h1").innerText()), `[${label}] H1 text`);
    check((await p.locator("form.srfm-form, form[id^=srfm]").count()) === 1, `[${label}] SureForms form rendered`);
    for (const lbl of ["Bildirim türü", "Konu", "Kim olarak yazıyorsun?", "Ne oldu?", "Adın ve soyadın"]) {
      check((await p.getByText(lbl, { exact: false }).count()) > 0, `[${label}] form field "${lbl}"`);
    }
    check(!(await p.content()).includes("[sureforms"), `[${label}] no raw shortcode`);
    const overflow = await p.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    check(overflow <= 1, `[${label}] no horizontal scroll (${overflow}px)`);
    check((await p.locator("#guvenlik").count()) === 1 && (await p.locator("#geri-bildirim-formu").count()) === 1, `[${label}] anchors present`);
    const ld = await p.$$eval('script[type="application/ld+json"]', (s) => s.map((x) => x.textContent));
    check(ld.some((t) => { try { return JSON.parse(t)["@type"] === "FAQPage"; } catch { return false; } }), `[${label}] FAQPage JSON-LD parses`);
    const footer = p.locator('.bai-sitemap a[href*="/geri-bildirim/"]');
    check((await footer.count()) > 0, `[${label}] footer link to /geri-bildirim/`);
    check(errors.length === 0, `[${label}] no page errors ${errors.join(" | ")}`);
    const btn = p.getByRole("button", { name: "Yalnızca Gerekli" });
    if (await btn.count()) await btn.first().click().catch(() => {});
    // Scroll through so the scroll-reveal sections become visible before the full-page shot.
    await p.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += 400) { window.scrollTo(0, y); await new Promise((r) => setTimeout(r, 120)); } window.scrollTo(0, 0); });
    await p.waitForTimeout(800);
    await p.screenshot({ path: path.join(shots, `geri-bildirim-${label}.png`), fullPage: true });

    if (label === "1280") {
      const checks = [
        ["/iletisim/", ['a[href="/geri-bildirim/"]'], ["41 soru, altı başlıkta", "nereye yazmalıyım?"]],
        ["/sikca-sorulan-sorular/", ['a[href="/geri-bildirim/"]'], ["en sık gelen 41 soruyu", "memnun kalmazsam ne yapmalıyım?"]],
        ["/on-bilgilendirme-formu/", ['a[href="/geri-bildirim/"]'], ["Sürüm 1.3"]],
        ["/iptal-ve-iade/", ['a[href="/geri-bildirim/"]'], ["Sürüm 1.7", "kurucumuz tarafından"]],
        ["/cocuk-guvenligi-politikasi/", ['a[href="/geri-bildirim/#guvenlik"]'], ["aynı gün", "Sürüm 1.2"]],
        ["/kvkk-aydinlatma-metni/", [], ["Geri bildirim ve şikâyet kayıtları", "Sürüm 2.6"]],
        ["/uzmanlarimiz/", ['a[href="/geri-bildirim/"]'], []],
        ["/ingilizce-ogretmeni-bul-3/", ['a[href="/geri-bildirim/"]'], []],
      ];
      for (const [url, sels, texts] of checks) {
        const res = await p.goto(base + url + bust(), { waitUntil: "domcontentloaded" });
        const html = await p.content();
        check(res.status() === 200, `${url} returns 200`);
        for (const s of sels) check((await p.locator(".bai-v2 " + s).count()) > 0, `${url} has ${s}`);
        for (const t of texts) check(html.includes(t), `${url} shows "${t}"`);
      }
      await p.goto(base + "/iletisim/" + bust(), { waitUntil: "networkidle" });
      await p.locator(".bai-signature").screenshot({ path: path.join(shots, "iletisim-signature.png") });
    }
    await ctx.close();
  }
  await browser.close();
  console.log(failures ? `${failures} check(s) failed` : "all checks passed");
  process.exit(failures ? 1 : 0);
})();
