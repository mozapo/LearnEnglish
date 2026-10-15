# Teacher Academy – Preview

New sections for the Eğitmen Akademisi page (`/egitmen-akademisi`, page ID 4358). They are added
around the existing page without changing it. The existing modules, quizzes, login, exam and
certificate logic are carried over byte for byte. All new code is scoped under `.bai-ta`.

- **Live since 15 Oct 2026 (13:13, Istanbul time):** https://biradimileri.com/egitmen-akademisi/ (page 4358, content only).
  The page before the switch is in `backup/`.
- **Staging draft:** page ID in `staging-page.json`; preview after logging in to staging admin:
  `https://stg15oct.biradimileri.com/?page_id=5762&preview=true`

### Existing learners
The new sections only **read** progress from the visitor's browser (`bai_ac_tr`). They never write it
and never call the server, so learners who are midway or certified keep everything they had.
`test/learner-safety.test.js` compares the page before and after for four learner states (0/10, 3/10,
10/10, certified). The hub output and saved progress must be identical, and they were on the live page.

### Undo
```bash
python3 teacher-academy/publish_live.py --rollback --yes   # restores backup/live-4358-content.html
```

## Files

| Path | What it is |
|---|---|
| `original/egitmen-akademisi-4358.html` | Untouched copy of the current page content (from staging, 15 Oct 2026) |
| `src/sections.html` | Markup for the new sections (Turkish) |
| `src/bai-ta.css` | Styles for the new sections, scoped under `.bai-ta` |
| `src/bai-ta.js` | Behaviour: reveal, counters, journey bar, quiz, progress, exam pool |
| `build.py` | Inserts the new sections into the original page; quiz and module data live here |
| `dist/teacher-academy-preview.html` | Built page content, ready to paste |
| `publish_staging.py` | Creates or updates the **draft** on **staging** only |
| `publish_live.py` | Replaces only the content of live page 4358, with guards and `--rollback` |
| `backup/` | The live page content and settings before the switch |
| `test/learner-safety.test.js` | Before/after comparison for learners at every stage |
| `test/preview.test.js` | Browser checks: 320/390/1280 px, keyboard quiz, reduced motion, contrast |

## What was added

1. **Journey bar.** A sticky bar with four steps (Keşfet → Yol haritası → Sertifika → Sonraki adım);
   each step ticks off as the visitor reaches that part of the page.
2. **Hero counters.** "10 Modül" and "~3 saat" count up once.
3. **"Bu program nerede duruyor?"** The four stages of the Cambridge English teacher framework,
   with Foundation highlighted.
4. **"Hangi modül sana en çok yarar?"** Five scenario questions that point to two real modules.
   Nothing is stored or sent.
5. **Roadmap.** A 10-segment ring showing the visitor's real module progress, plus a line that
   draws itself through the stops: modules → module quizzes → exam → certificate → interview.
6. **Time chart.** Estimated reading minutes per module (14–18), with "~3 saat" in total including quizzes and
   your own pace. This matches the page's FAQ, which says about three hours.
7. **Exam at a glance.** A 64-question pool with 30 drawn at random (try "Başka bir soru kâğıdı
   çek"), an 80% gauge (24 of 30) and a note that retakes are unlimited.
8. **Path to the team.** The four steps from `/ekibimize-katil`, with the academy as step 3
   ("Bu sayfadasın"). Step 4 is the interview and contract. The buttons follow the hub's own
   state (Programa başla / Kaldığın yerden devam et / Sertifika sınavına gir), and there is a
   secondary link to the application form.

Every number comes from the existing pages, and there are no invented statistics or testimonials.
The new sections only read progress from the visitor's browser (`bai_ac_tr`) and never write to it.

## Rebuild and update the staging draft

```bash
python3 teacher-academy/build.py              # checks that the original markup is untouched
python3 teacher-academy/publish_staging.py    # draft only, staging only, verifies the result
```

## Updating live later

1. Change `src/`, then run `python3 teacher-academy/build.py`, update the staging draft and check it.
2. Refresh `backup/` and `original/egitmen-akademisi-4358-live.html` from the live page, then run `build.py --live`.
3. Run `test/learner-safety.test.js` (the current live page vs the new one).
4. With approval: `python3 teacher-academy/publish_live.py --yes`. LiteSpeed purges the page automatically on save.

**Never use Hostinger's "Publish staging".** It copies the whole staging site over the live site.

Testing the live URL directly in a headless browser hits Hostinger's bot check. Fetch the page with curl
and test the saved HTML instead.
