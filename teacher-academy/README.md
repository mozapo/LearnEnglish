# Teacher Academy – Preview

New sections for the Eğitmen Akademisi page (`/egitmen-akademisi`, page ID 4358). They are added
around the existing page without changing it. The existing modules, quizzes, login, exam and
certificate logic are carried over byte for byte. All new code is scoped under `.bai-ta`.

- **Staging draft:** page ID in `staging-page.json`. Preview it after logging in to staging admin:
  `https://stg15oct.biradimileri.com/?page_id=5762&preview=true`
- **Live:** nothing has been changed.

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

## Moving it to the live site (when you are happy)

**Never use Hostinger's "Publish staging".** It copies the whole staging site over the live site.

**Easiest:** tell Claude "move the Teacher Academy preview to live". Claude will then:

1. Snapshot the **live** `/egitmen-akademisi` content as a backup in `original/`. The live page
   may differ from staging, and its search-engine data must keep live URLs.
2. Rebuild on top of that live content and show you the diff.
3. Replace only the content of live page 4358, check what WordPress actually outputs, and purge
   LiteSpeed Cache.

To undo, put the backup content back.

**By hand:**

1. On the **live** site, open Pages → Eğitmen Akademisi → ⋮ → Code editor. Copy everything into a
   text file as a backup.
2. Rebuild against the live content: replace `original/egitmen-akademisi-4358.html` with that
   backup and run `python3 teacher-academy/build.py`.
3. Paste `dist/teacher-academy-preview.html` into the Code editor in place of the old content and
   click **Update**. Do not switch to the visual editor: it can break the scripts.
4. LiteSpeed Cache → Purge All, then check the page on a phone and a computer.
5. To undo, paste the backup back in and click Update.
