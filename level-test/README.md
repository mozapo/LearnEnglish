# Level tests

The two free English level tests on biradimileri.com, the placement rule, and the "Seviye testim" practice area.

| Page | ID | What changed |
|---|---|---|
| `/seviye-testi-40` | 4011 | Milestones + badge (**live since 17 Oct**); placement rule, "close to next level" label, "Hatalarınla çalış" link, under-18 note (**staging**) |
| `/panel` | 5402 | New "Seviye testim" section after `[bai_panel]` (**staging**) |
| `/kvkk-aydinlatma-metni` | 2345 | v2.7: level test + "Seviye testim" (**staging**) |
| `/cerez-politikasi` | 4066 | v1.2: the two browser-storage keys (**staging**) |
| `/seviye-testi` | 1688 | Unchanged (Elementor) |

## Publishing

```bash
python3 level-test/publish.py staging            # all four pages
python3 level-test/publish.py live --yes         # only after the owner approves this specific change
python3 level-test/publish.py live --rollback --yes
```
Each page is built from its backup in `backup/` (taken 17 Oct 2026, before any change). The script writes only if
the page is in a known state, checks that WordPress saved the build byte for byte, and checks the public page.
Before going live, set `EFFECTIVE` in `legal_patches.py` to the publish date (it appears in the version lines).

## How it works

- **Placement** (`patches.PLACE_JS`, PLAN.md §1): total-score cut points A2 17 · B1 23 · B2 28 · C1 33 · C2 36, plus a
  floor at the highest level reached with every level up to it mastered (all but one item right). "B2’ye çok yakın"
  shows when the score is one point below the next cut. The same code runs in the test and in `/panel`.
- **Hand-over without server code:** at the end of the test, the answers are kept in the browser (`bai_lt_v1`) and put
  in the link `/panel/?lt=<code>#seviye-testim`. Code = `1` + yyyymmdd + one character per question (`0`–`4`, `x`).
  Login and registration keep `redirect_to`, so the code survives sign-up and works on another device.
- **"Seviye testim"** (`panel/bai-ltp.js`, `.css`, built by `panel/build_panel.py`): logged out → badge + register / log-in
  buttons; logged in → badge, score, priority topics (mistakes at or below the student’s level + 1), the rest folded
  under "İleride". Each topic: 3-question quick check (3/3 → "biliyorsun"), TR/EN explanation, pattern, examples,
  5–6 practice questions with feedback (≥60% → done). Progress lives in `bai_lt_prog_v1`, and the result expires after 12 months.
  "Sonucu bu tarayıcıdan sil" deletes both keys. Nothing is sent to the server.
- **Cards:** `cards.py`, 35 topics / 281 questions covering all 40 test items. Practice items never reuse a test sentence.

### Things to know
- The CSS prefix is `bai-ltp`. **Do not use `bai-st`**: the theme’s story animation uses that class and hides it
  (opacity 0) until it scrolls into view. That clash hid the whole section on the first staging build.
- Hostinger’s bot check sometimes answers headless browsers with a 403 "Checking your browser" page, so the tests retry.
- Registration has reCAPTCHA, which the test sandbox can’t reach, so the real sign-up was not automated. The test
  checks that the registration form carries the code back to `/panel`, then checks the logged-in view by adding
  `logged-in` to the server’s `<body>` class (the only thing the section reads).
- Content is in Turkish (sen) on the site, and the legal text stays formal (siz).

## Tests (run from `level-test/`, Playwright from any `node_modules` via `NODE_PATH`)

| Command | Checks |
|---|---|
| `python3 tools/validate_cards.py` | card structure, coverage of all 40 items, no reused test sentence, script-safe text |
| `node tools/test_place.js` | JS placement rule = reference rule on all 200,704 score patterns |
| `node tools/test_panel.js` | "Seviye testim" locally: logged out/in, priorities, quick check, practice, progress, expiry, delete, 390px |
| `TARGET_URL=$WP_STAGING_URL node tools/e2e_flow.js` | full flow on staging: test → result → link → register form → panel; section really visible |
| `TARGET_URL=$WP_STAGING_URL node tools/e2e_staging.js` | milestone texts and badge on the result screen |
| `python3 tools/placement_sim.py`, `tools/placement_sensitivity.py` | placement simulations (PLAN.md §1) |

The level-test email request is intercepted in every browser test, so no email is sent.
