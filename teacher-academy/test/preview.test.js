// Renders the built preview inside a saved copy of the staging page and checks the new sections.
// Usage: node teacher-academy/test/preview.test.js <page.html | https://url> <screenshot-dir>
const { chromium } = require("playwright");
const path = require("path");

const target = /^https?:/.test(process.argv[2]) ? process.argv[2] : "file://" + path.resolve(process.argv[2]);
const shots = path.resolve(process.argv[3] || ".");
const proxy = process.env.HTTPS_PROXY ? { server: process.env.HTTPS_PROXY } : undefined;
let failures = 0;
const check = (ok, msg) => { console.log((ok ? "PASS " : "FAIL ") + msg); if (!ok) failures++; };

async function open(browser, opts) {
  const ctx = await browser.newContext(opts);
  const p = await ctx.newPage();
  const errors = [];
  p.on("pageerror", (e) => errors.push(e.message));
  p.on("console", (m) => { if (m.type() === "error" && /bai-ta|bai_ta/.test(m.text())) errors.push(m.text()); });
  if (opts.progress) {
    await p.addInitScript((st) => { try { localStorage.setItem("bai_ac_tr", JSON.stringify(st)); } catch (e) {} }, opts.progress);
  }
  // Never write to a real site from a test: block every non-GET request to WordPress.
  await ctx.route(/\/wp-json\/|admin-ajax\.php/, (r) => (r.request().method() === "GET" ? r.continue() : r.abort()));
  await p.goto(target, { waitUntil: "load", timeout: 90000 });
  await p.waitForTimeout(800);
  const reject = await p.$("text=Yalnızca Gerekli");
  if (reject) { await reject.click().catch(() => {}); await p.waitForTimeout(300); }
  return { ctx, p, errors };
}

async function scrollThrough(p) {
  await p.evaluate(async () => {
    for (let y = 0; y < document.body.scrollHeight; y += 400) { window.scrollTo(0, y); await new Promise((r) => setTimeout(r, 60)); }
  });
  await p.waitForTimeout(1600);
}

(async () => {
  const browser = await chromium.launch({ executablePath: "/opt/pw-browsers/chromium-1194/chrome-linux/chrome", proxy });

  for (const vp of [{ name: "mobile-320", width: 320, height: 720 }, { name: "mobile-390", width: 390, height: 844 }, { name: "desktop-1280", width: 1280, height: 900 }]) {
    const { ctx, p, errors } = await open(browser, { viewport: vp, progress: { m: { 1: { done: 1 }, 2: { done: 1 }, 3: { done: 1 } }, tk: {} } });
    await scrollThrough(p);
    const overflow = await p.evaluate(() => [...document.querySelectorAll(".bai-ta, .bai-ta *")].filter((e) => e.getBoundingClientRect().right > document.documentElement.clientWidth + 1).map((e) => e.className).slice(0, 5));
    check(overflow.length === 0, `${vp.name}: no new element wider than the screen ${overflow.length ? JSON.stringify(overflow) : ""}`);
    check(errors.length === 0, `${vp.name}: no script errors ${errors.join(" | ")}`);
    const ring = await p.evaluate(() => [document.getElementById("bai-ta-ringn").textContent, document.querySelectorAll(".bai-ta-ring path.is-done").length, document.getElementById("bai-ta-pathprog").textContent]);
    check(ring[0] === "3" && ring[1] === 3, `${vp.name}: ring shows real progress 3/10 (${ring[0]}, ${ring[1]} segments)`);
    check(ring[2] === "3 / 10 modül tamamlandı.", `${vp.name}: path step shows progress ("${ring[2]}")`);
    const visible = await p.evaluate(() => [...document.querySelectorAll(".bai-ta-rv")].every((e) => e.classList.contains("is-in")));
    check(visible, `${vp.name}: all sections revealed after scrolling`);
    const done = await p.evaluate(() => document.querySelectorAll(".bai-ta-journey a.is-done").length);
    check(done === 4, `${vp.name}: journey bar reached 4/4 chapters (${done})`);
    const mirror = await p.evaluate(() => [...document.querySelectorAll(".bai-ta-cta-mirror")].map((a) => a.textContent + "→" + a.getAttribute("href")));
    console.log(`      CTA mirror: ${mirror[0]}`);
    const pool = await p.evaluate(() => document.querySelectorAll("#bai-ta-pool i.is-on").length);
    check(pool === 30, `${vp.name}: exam pool highlights 30 of 64 (${pool})`);
    for (const id of ["bai-ta-ch1", "bai-ta-quiz", "bai-ta-ch2", "bai-ta-time", "bai-ta-ch3", "bai-ta-ch4"]) {
      const el = await p.$("#" + id);
      await el.screenshot({ path: `${shots}/${vp.name}-${id}.png` });
    }
    await p.evaluate(() => window.scrollTo(0, document.getElementById("bai-ta-ch2").offsetTop + 200));
    await p.waitForTimeout(500);
    await p.screenshot({ path: `${shots}/${vp.name}-viewport-sticky.png` });
    await ctx.close();
  }

  // Journey links land below the sticky bar; shuffle is announced to screen readers
  {
    const { ctx, p } = await open(browser, { viewport: { width: 390, height: 844 }, reducedMotion: "reduce" });
    await p.evaluate(() => window.scrollTo(0, document.getElementById("bai-ta-ch1").offsetTop + 50));
    // Same scroll an anchor jump makes (clicking is avoided: the local copy's <base> tag sends #links to staging).
    await p.evaluate(() => document.getElementById(document.querySelector('.bai-ta-journey a[data-ch="3"]').getAttribute("href").slice(1)).scrollIntoView());
    await p.waitForTimeout(400);
    const pos = await p.evaluate(() => ({ bar: document.getElementById("bai-ta-journey").getBoundingClientRect().bottom, sec: document.getElementById("bai-ta-ch3").getBoundingClientRect().top }));
    check(pos.sec >= pos.bar - 1, `journey link: section starts below the sticky bar (bar ${Math.round(pos.bar)}px, section ${Math.round(pos.sec)}px)`);
    await p.click("#bai-ta-shuffle");
    await p.waitForTimeout(200);
    const live = await p.evaluate(() => document.getElementById("bai-ta-poollive").textContent);
    check(/30 soru/.test(live), `exam pool: shuffle announced ("${live}")`);
    await ctx.close();
  }

  // Keyboard-only quiz run
  {
    const { ctx, p, errors } = await open(browser, { viewport: { width: 390, height: 844 } });
    await p.focus("#bai-ta-qstart");
    await p.keyboard.press("Enter");
    for (let i = 0; i < 5; i++) {
      const focused = await p.evaluate(() => document.activeElement.id);
      check(focused === "bai-ta-qtext", `quiz q${i + 1}: focus moves to the question (${focused})`);
      await p.keyboard.press("Tab");
      await p.keyboard.press("Tab");
      await p.keyboard.press("Enter");
      await p.waitForTimeout(150);
    }
    const result = await p.evaluate(() => ({ shown: !document.getElementById("bai-ta-qresult").hidden, cards: [...document.querySelectorAll(".bai-ta-rcard b")].map((b) => b.textContent), focus: document.activeElement.id }));
    check(result.shown && result.cards.length === 2, `quiz: result shows 2 modules (${result.cards.join(", ")})`);
    check(result.focus === "bai-ta-rtitle", "quiz: focus moves to the result heading");
    await (await p.$("#bai-ta-quiz")).screenshot({ path: `${shots}/quiz-result.png` });
    check(errors.length === 0, "quiz: no script errors " + errors.join(" | "));
    await ctx.close();
  }

  // Reduced motion: everything visible immediately, no counters
  {
    const { ctx, p, errors } = await open(browser, { viewport: { width: 1280, height: 900 }, reducedMotion: "reduce" });
    const st = await p.evaluate(() => ({
      anim: document.documentElement.classList.contains("bai-ta-anim"),
      hidden: [...document.querySelectorAll(".bai-ta-rv")].filter((e) => getComputedStyle(e).opacity !== "1").length,
      badge: document.querySelector(".bai-ac__badges .bai-ac__badge span").textContent,
    }));
    check(!st.anim && st.hidden === 0, `reduced motion: no reveal animation, all sections visible (${st.hidden} hidden)`);
    check(st.badge === "10 Modül", `reduced motion: hero badge not animated ("${st.badge}")`);
    check(errors.length === 0, "reduced motion: no script errors");
    await ctx.close();
  }

  // Contrast of new text colours on the navy background
  {
    const lum = (hex) => { const c = hex.match(/\w\w/g).map((h) => parseInt(h, 16) / 255).map((v) => (v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4)); return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]; };
    const ratio = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((m, n) => n - m); return (x + 0.05) / (y + 0.05); };
    for (const [name, fg, bg] of [["muted text", "A6B6D0", "16233F"], ["gold-light text", "E7C77E", "16233F"], ["button text", "1A1206", "B98A2E"], ["tag text", "1A1206", "E7C77E"]]) {
      const r = ratio(fg, bg);
      check(r >= 4.5, `contrast ${name}: ${r.toFixed(2)}:1`);
    }
  }

  await browser.close();
  console.log(failures ? `\n${failures} check(s) failed` : "\nall checks passed");
  process.exit(failures ? 1 : 0);
})();
