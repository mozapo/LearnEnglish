// Learner-safety check: the existing academy hub must look and behave exactly the same with the
// new sections added, for learners at every stage, and their saved progress must not change.
// Usage: node teacher-academy/test/learner-safety.test.js <current-page.html> <new-page.html>
// All requests to the site's REST API are blocked, so the test can never write to the server.
const { chromium } = require("playwright");
const path = require("path");

const [currentFile, newFile] = process.argv.slice(2).map((f) => path.resolve(f));
const LANG = process.env.TA_LANG || "tr"; // TA_LANG=en for /en/educator-academy
const KEY = "bai_ac_" + LANG;
const proxy = process.env.HTTPS_PROXY ? { server: process.env.HTTPS_PROXY } : undefined;
let failures = 0;
const sorted = (o) => JSON.stringify(Object.keys(o).sort().map((k) => [k, o[k]]));
const check = (ok, msg) => { console.log((ok ? "PASS " : "FAIL ") + msg); if (!ok) failures++; };

const all = (n) => Object.fromEntries(Array.from({ length: n }, (_, i) => [String(i + 1), { done: 1, score: 5, ts: 1760000000000 }]));
const timers = (n) => Object.fromEntries(Array.from({ length: n }, (_, i) => [`bai_ac_t_${LANG}_${i + 1}`, "900"]));
const STATES = {
  "new visitor (0/10)": {},
  "in progress (3/10)": { [KEY]: { m: all(3), tk: { 1: [0, 1] } }, ...timers(3) },
  "all modules done, no certificate (10/10)": { [KEY]: { m: all(10), tk: {} }, ...timers(10) },
  "certified (10/10 + certificate)": { [KEY]: { m: all(10), tk: {}, cert: { code: "BAI-TEST-1234", name: "Test Eğitmen", date: "2026-10-01", score: 27 } }, ...timers(10) },
};

async function snapshot(browser, file, state) {
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  await ctx.route(/\/wp-json\//, (r) => r.abort());
  await ctx.route(/admin-ajax\.php/, (r) => r.abort());
  const p = await ctx.newPage();
  const errors = [];
  p.on("pageerror", (e) => errors.push(e.message));
  await p.addInitScript((st) => {
    if (sessionStorage.getItem("seeded")) return;
    for (const [k, v] of Object.entries(st)) localStorage.setItem(k, typeof v === "string" ? v : JSON.stringify(v));
    sessionStorage.setItem("seeded", "1");
  }, state);
  await p.goto("file://" + file, { waitUntil: "load", timeout: 90000 });
  await p.waitForTimeout(3000); // let hub boot and our counters finish
  const snap = await p.evaluate(() => {
    const root = document.getElementById("bai-ac").cloneNode(true);
    root.querySelectorAll('[class*="bai-ta"], [id^="bai-ta"]').forEach((e) => e.remove());
    root.querySelectorAll("[class]").forEach((e) => e.setAttribute("class", e.getAttribute("class").replace(/\bis-in\b/g, "").replace(/\s+/g, " ").trim()));
    const storage = {};
    // bai_seen is a site-wide visit timestamp from the child theme (bai-motion.js), written on every page.
    for (let i = 0; i < localStorage.length; i++) { const k = localStorage.key(i); if (k !== "bai_seen") storage[k] = localStorage.getItem(k); }
    const cta = document.getElementById("bai-ac-cta");
    // WordPress adds line breaks between tags when it renders; they don't change anything visible.
    return { hub: root.outerHTML.replace(/>\s+</g, "><"), storage, cta: cta.textContent + " → " + cta.getAttribute("href"), dash: document.querySelector(".bai-ac__dash").innerText.replace(/\s+/g, " ") };
  });
  await ctx.close();
  return { ...snap, errors };
}

(async () => {
  const browser = await chromium.launch({ executablePath: "/opt/pw-browsers/chromium-1194/chrome-linux/chrome", proxy });
  for (const [name, state] of Object.entries(STATES)) {
    const before = await snapshot(browser, currentFile, state);
    const after = await snapshot(browser, newFile, state);
    const seeded = Object.fromEntries(Object.entries(state).map(([k, v]) => [k, typeof v === "string" ? v : JSON.stringify(v)]));
    console.log(`\n${name}\n      hub CTA: ${after.cta}\n      hub dashboard: ${after.dash.slice(0, 110)}`);
    check(before.hub === after.hub, `${name}: hub looks and behaves the same as on the current page`);
    if (before.hub !== after.hub) {
      let i = 0; while (i < before.hub.length && before.hub[i] === after.hub[i]) i++;
      console.log(`      lengths ${before.hub.length} vs ${after.hub.length}; first difference at ${i}:\n        current: ${before.hub.slice(Math.max(0, i - 100), i + 150)}\n        new:     ${after.hub.slice(Math.max(0, i - 100), i + 150)}`);
    }
    if (sorted(after.storage) !== sorted(seeded)) {
      for (const k of new Set([...Object.keys(before.storage), ...Object.keys(after.storage), ...Object.keys(seeded)]))
        if (before.storage[k] !== after.storage[k] || after.storage[k] !== seeded[k]) console.log(`      storage ${k}:\n        seeded:  ${String(seeded[k]).slice(0, 160)}\n        current: ${String(before.storage[k]).slice(0, 160)}\n        new:     ${String(after.storage[k]).slice(0, 160)}`);
    }
    check(sorted(after.storage) === sorted(before.storage), `${name}: saved progress identical to the current page's`);
    check(sorted(after.storage) === sorted(seeded), `${name}: saved progress not modified at all`);
    check(after.errors.length === 0, `${name}: no script errors ${after.errors.join(" | ")}`);
  }
  await browser.close();
  console.log(failures ? `\n${failures} check(s) failed` : "\nall learner-safety checks passed");
  process.exit(failures ? 1 : 0);
})();
