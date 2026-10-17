# Level test: plans (17 Oct 2026)

## 1. Placement rule (issue 2)

**Problem.** Today a learner is placed at the highest level where they score ≥60% on that level *and* ≥60% overall
up to it. Lower levels may be failed in between. With only 6–7 items per level, lucky guesses or a few known words
at a high level can lift the result.

**What the literature says**
- Placement means classification, and short sections misclassify more. Accuracy depends on test length, item
  discrimination and how close cut scores sit to where most learners are (simulation studies on classification
  accuracy; Rudner's expected-classification-accuracy work).
- Under the Rasch model, the **total score** carries all the information about ability. Cut scores belong on the
  total score and are set by standard setting, then checked against real data. This is the Council of Europe
  *Manual for Relating Language Examinations to the CEFR* (2009): specification → standardisation → standard
  setting → empirical validation. Clark (2004) argues for Rasch in placement testing.
- Commercial placement tests (Oxford Placement Test, Cambridge English Placement Test) are adaptive and report one
  score mapped to CEFR bands, not per-section pass/fail ladders.
- An "I don't know" option reduces guessing (*TESOL Quarterly* study on the vocabulary size test). We already
  have it, which is good.

**Our simulation** (`tools/placement_sim.py`, 40,000 simulated learners; illustrative, not real data):

| Rule | Exact level | Within one level | Over-placed | Over-placed by 2+ levels |
|---|---|---|---|---|
| Current | 57% | 92% | 35% | 8.0% |
| Consecutive levels only | 61% | 95% | 26% | 3.0% |
| **Total-score cut points** | **71%** | **99%** | **15%** | **0.4%** |

**Plan**
1. **Now (staging, no data needed):** place by total score with provisional cut points
   from the model (A1 0–16 · A2 17–22 · B1 23–27 · B2 28–32 · C1 33–35 · C2 36–40, assuming low guessing thanks
   to "I don't know"; with more guessing each cut rises by about one point). Keep the level bars as a *profile*, not the
   decision. Show "sınırda" (e.g. "B1, B2'ye yakın") when the score is within one point of a cut. Keep the
   confidence rating.
2. **Collect:** the endpoint already receives every answer, so store them anonymously. Add one field in the
   teacher panel for the CEFR level the teacher judges in the intro call. This becomes our outside check.
3. **After ~300 completions:** item analysis (difficulty, discrimination, distractors). Rewrite weak items. Reset
   the cut points from real data and teacher judgements (Manual, ch. 6–7).
4. **Later:** more items per level, a parallel form for retakes, then a two-stage test (10 routing items → an
   easier or harder block). This keeps the test short and makes it more accurate.

## 2. "Hatalarımla çalış": practising mistakes in the student account

### Final proposal
After the result, show **"Hatalarını hesabında çalış"**. One click → register or log in → a **"Seviye testim"**
tab in the existing `/panel`. No new public pages.

- **Saving the result:** the attempt is stored on the server with a random token when the test finishes. The
  result screen and the result email both carry the link. On registration or login the token attaches the
  attempt to the account. Not by email alone: anyone could type someone else's email.
- **The tab:** badge ("B1 İletişimci", date, "site testi, resmî belge değildir"), score history, and a
  **prioritised list** of mistakes:
  1. Mistakes at or below the learner's level.
  2. Then the next level.
  3. Higher levels folded under "İleride".
- **Each topic card (~5 minutes, TR + EN):** 3-question quick check → short explanation (Turkish-led up to B1,
  English-led from B2) → 2–3 examples → 5 new practice items with instant feedback → "Tamamlandı". If the quick
  check is all correct: "Bunu aslında biliyorsun", and the card is closed.
- **About 30 cards, not 40:** test items that check the same point within a level share a card (inversion,
  C2 academic vocabulary, reported speech). Practice items are **never** the test items, so a retake stays valid.
- **Progress badge** when every priority card is done, plus an invitation to retake (parallel form, see §1 step 4).
- **Teacher view:** when the student books an intro call or lessons, the teacher sees the error profile in their
  panel. One click turns it into a `bai-study` plan.
- **CTA on every card:** "Bu konuyu bir eğitmenle çalış" → free intro call. Calm, no pressure.

### What I changed after critiquing the first idea
| First idea | Problem | Fix |
|---|---|---|
| 40 questions = 40 lessons | Several items test the same point; 40 lessons is a lot of content to write and keep accurate | ~30 cards, grouped within a level |
| Every wrong answer = a gap | One wrong answer can be a slip or a guess | 3-question quick check first |
| Show all mistakes | An A2 learner with 12 C1/C2 "mistakes" is discouraged and is not ready for them | Priority order, higher levels folded |
| Practise the test questions | Retakes become memory tests, not level tests | New practice items; parallel form for retakes |
| Link only on the result screen | Users register later or on another phone | Token link in the email too, saved on the server |
| Register to see anything | Drop-off; feels like a trap | Result and answer review stay free; the account adds practice, badge and history |
| Badge on the profile now | Nothing stores it yet | Badge is shown on the result now; "keep it in your account" arrives with the tab |

### From each angle
- **Business:** turns an anonymous test-taker into a registered learner with a known level and known gaps.
  Intro calls start from real data, which should mean better matching and higher conversion. FluentCRM tags by
  level and topic allow relevant follow-ups. Cost: content (I draft, a teacher checks) plus one plugin feature.
  Measure each step: result → register → first card → all cards → intro call → purchase.
- **Educational:** diagnosis is only useful when it leads to action (Alderson, DIALANG), and the cards are that
  action. Short, focused practice with immediate feedback and retrieval. Honest limit: the test covers grammar
  and vocabulary only; speaking and writing still need a teacher. The tab says so.
- **Student:** free result as today, a clear reason to register, 5-minute cards on the phone, visible progress,
  no flood of red marks.
- **Long-term:** item-level data feeds the placement fix (§1). The card bank is reused in lessons, group courses
  and later Tutor LMS. Bilingual cards also serve the `/en` side. Teachers see the profile.

### Must-haves / risks
- **KVKK:** the stored attempt is personal data. Update the aydınlatma metni and set a retention period.
  Marketing emails need separate ETK/İYS consent.
- **Under-18s:** registration follows `/cocuk-guvenligi-politikasi` (parent or guardian as the contracting
  party, visible records).
- **Content accuracy:** every card is reviewed by a qualified teacher before going live.
- **Volume:** only 3 student accounts exist today. Check how many people finish the test each month before
  building everything. Start with A1–B2 (~22 cards).
- **Dependency:** the custom plugins' PHP source is not in any repository this workspace can reach. The feature
  needs server code (saving attempts, token claim, panel tab). The source and a deployment route are needed.

### Phases
0. **Done on staging:** encouragement screens and the badge wording.
1. Placement rule (§1 step 1) and saving attempts on the server.
2. Token link, "Seviye testim" tab, badge, A1–B2 cards.
3. C1–C2 cards, teacher view, parallel form and retake, calibration after ~300 attempts.

## Sources
- Council of Europe: *Relating Language Examinations to the CEFR, A Manual* (2009): https://rm.coe.int/1680667a2d
- Clark (2004), Rasch in placement testing, University of Hawai'i: https://www.hawaii.edu/sls/wp-content/uploads/2014/09/Clark.pdf
- "The 'I don't know' option in the Vocabulary Size Test", *TESOL Quarterly*: https://metatoc.com/papers/21412-the-i-don-t-know-option-in-the-vocabulary-size-test
- Holster & Lake, guessing and vocabulary size tests, JALT: https://teval.jalt.org/sites/default/files/26_01_01_Holster_Lake_vocab_size_0.pdf
- Huhta & Alderson (2005), DIALANG, *Language Testing*: https://eprints.lancs.ac.uk/id/eprint/1017/
- Alderson (2005), *Diagnosing Foreign Language Proficiency* (review): https://asian-efl-journal.com/book-reviews/diagnosing-foreign-language-proficiency-the-interface-between-learning-and-assessment-2/index.htm
- Item discrimination and misclassification: https://revistas.unc.edu.ar/index.php/revaluar/article/download/36294/36588/128683
- Rudner, expected classification accuracy: https://www.academia.edu/17019963/Expected_Classification_Accuracy
- Mokken / Guttman scaling (non-monotonic patterns): https://en.wikipedia.org/wiki/Mokken_scale
- Oxford Placement Test: https://en.wikipedia.org/wiki/Oxford_Placement_Test
- Cambridge English Placement Test: https://swiss-exams.ch/exams-and-certifications/cambridge/info/cambridge-english-placement-test
- ETS, TOEFL Junior mapped to the CEFR: https://www.ets.org/research/policy_research_reports/publications/report/2011/islr.html
