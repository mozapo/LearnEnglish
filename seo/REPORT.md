# SEO audit: verification, fixes and before/after report

biradimileri.com · 19 Oct 2026 · Starting point: the ChatGPT audit "biradimileri_SEO_audit_and_Claude_WordPress_brief_2026-10-19".

**Status:** all fixes below are **on staging and verified**. **Nothing has been changed on live.** Live needs your
approval for each group (section 4). Business and legal wording was not changed; it is listed in section 5 for
your decision.

## 1. Summary

The site's technical base is better than the audit assumed. HTTPS and host redirects, robots.txt, one sitemap,
self-referencing canonicals, one H1 per page, reciprocal TR/EN hreflang, `lang`/`og:locale`, and a correct
Organization schema with the legal identifiers are all in place. Several audit findings were already fixed before
today (the Beşiktaş address, "Lisanslı psikologlarla").

The real problems found and fixed on staging:

| Area | Before (live) | After (staging) |
|---|---|---|
| Templated meta descriptions on indexable pages ("… hakkında detaylı bilgi…", "… için hedef odaklı hazırlık…" etc.) | 68 | 0 |
| Description groups sharing the same opening words | 16 groups, 45 pages | 3 groups, 7 pages (shared opening only; the rest differs) |
| Marketing descriptions in formal "siz" | 38 | 0 (legal pages keep "siz", as required) |
| Page titles with overlapping intent (IELTS/TOEFL overview vs. program, 3 level tools) | 7 pairs/triples | each has its own search intent |
| Customer-visible editorial note ("…yayımlamayın") | 1 | 0 |
| "Detaylı rehber yakında" chips promising guides that do not exist | 23 | 0 |
| Blog page says "İlk kapsamlı rehberler hazırlanıyor" although an article is live | yes | shows the article |
| FAQ says online payment "henüz devrede değildir" (contradicts KVKK v2.5 and /guvenli-odeme) | yes | corrected (needs your OK) |
| Country cards on /yurt-disi-egitim linking to /iletisim instead of the country guide | 8 | 0 |
| "{Ülke} seçeneğini değerlendir" buttons on /universite-rehberi linking to the generic quiz | 8 | 0 |
| Page meant to be noindex but indexed and in the sitemap (/randevu-olustur, value "1" instead of "yes") | 1 | 0 |

Staging was re-crawled after the changes (209 URLs): all 200, and no change to canonicals, hreflang, H1s or
schema (199 indexable pages compared). The level-test end-to-end test passes on staging. Screenshots of the edited sections at 390 px were
checked.

## 2. The audit, finding by finding

| # | Audit claim | Verdict | Evidence |
|---|---|---|---|
| A1 | /kullanim-kosullari says Beşiktaş, company info "later" | **Already fixed** | Live page shows Kartal address, MERSİS, tax and registry numbers matching CLAUDE.md |
| A1 | /programlar: "Lisanslı psikologlarla" | **Already fixed** | Not on the page any more |
| A1 | /programlar: "UCAS Registered Centres" | **Confirmed, needs your decision** | Section 5 |
| A1 | Other stale legal text | **Found 1 more** | /kvkk-basvuru-formu: addresses "kurumsal kayıt işlemleri tamamlandığında eklenecektir" (section 5) |
| A2 | "Yayın ekibine not" on /gencler-icin-ingilizce-2, /bire-bir-ingilizce-dersleri-2 | **Not present any more** | Searched page content and Elementor data |
| A2 | Editor note on /…/ingilizce-konusma-programi | **Confirmed, fixed on staging** | Now: "Grup büyüklüğü, seviye eşleştirmesi ve güncel ders takvimi kayıttan önce seninle birlikte netleştirilir." |
| A2 | Other placeholders | **Found and fixed** | 23 × "Detaylı rehber yakında" (/universite-hazirlik-muafiyet-sinavlari), blog placeholder, SSS payment answer |
| A3 | Blog has no article feed | **Partly true** | 1 article was live but unlisted. Now listed as a card. More articles = content plan (section 8) |
| A4 | IELTS pages compete | **Confirmed (titles/descriptions)** | Same for TOEFL. Fixed in metadata; merging needs Search Console data first (section 6) |
| A5 | -2/-3 slugs | **No problem found; keep them** | Every suffixed page is the only version; the unsuffixed URL already 301s to it. One exception: /is-ingilizcesi/ **302s to the home page** instead of /is-ingilizcesi-2/ (section 7) |
| A6 | Self-assessment vs. teacher assessment unclear | **Confirmed, and a third tool exists** | /seviye-testi (3-min self-assessment), /seviye-testi-40 (40-question test), /ingilizce-seviye-tespit-sinavi-3 (live, with a teacher; its description was an exam-prep template). Each now has its own title and description |
| B1 | Crawl | **Done** | 215 URLs, all 200; 8 redirects, all correct; real 404s return 404 |
| B2 | robots/sitemap/canonical | **Correct** | One SureRank sitemap; noindex pages not in it; ?s= search noindexed; uppercase and ?utm URLs canonicalise to lowercase. One defect (/randevu-olustur) fixed |
| B3 | hreflang | **Correct** | 50+ TR/EN pairs, all reciprocal and self-referencing, x-default = EN version. `lang` and `og:locale` correct on both languages |
| B4 | One SEO owner, schema | **Correct** | SureRank only. Organization schema has legal name, Kartal address, MERSİS, tax and registry numbers, logo, sameAs. No fake ratings. FAQPage on ~130 pages matches visible FAQs (harmless; no rich result expected). Breadcrumb schema says "Home", hard-coded in SureRank |
| B5 | Titles/H1/images | **Mostly fine** | 1 H1 per page, no duplicate titles on indexable pages. Description quality was the problem (fixed) |
| B6 | Core Web Vitals | **Measured (lab)** | Section 6. No real-user data available (no Search Console connection) |
| B7 | Search Console/GA4 | **Blocked, needs your access** | SureRank reports no Search Console connection. GTM container GTM-T5FDGPQM is present; its configuration is not visible to me |

## 3. What was changed on staging

All scripted, guarded and reversible (`seo/publish.py`). Full list of 89 metadata changes with old and new
values: `seo/metadata_changes.csv`.

**Content group A (wording only, no new claims)**
- 1571 /…/ingilizce-konusma-programi: editor instruction replaced with the customer-facing sentence above.
- 5518 /universite-hazirlik-muafiyet-sinavlari: 23 "Detaylı rehber yakında" chips removed (the "Resmi sayfa" and
  "Bu sınava hazırlan" links stay).
- 1579 /blog: placeholder card replaced with a card linking to the published article; "listelenecek" → "Yayımlanan
  yazılar, en yenisi başta."

**Content group B (factual correction, your OK needed)**
- 1682 /sikca-sorulan-sorular, "Sitede çevrim içi ödeme yapabiliyor muyum?" New answer: "Evet. Kartla ödeme,
  Türkiye İş Bankası'nın 3D Secure güvenli ödeme sayfasında alınır; istersen banka havalesi/EFT ile de
  ödeyebilirsin. Kart bilgilerin bize ulaşmaz ve hiçbir aşamada sunucularımızda saklanmaz. Ayrıntılar Güvenli
  Ödeme sayfasında." Every statement is taken from /guvenli-odeme and KVKK Aydınlatma Metni v2.5.

**Content group C (internal links, href only)**
- 1384 /yurt-disi-egitim: 8 country cards now link to their guides (were /iletisim/).
- 1686 /universite-rehberi: 8 "… seçeneğini değerlendir" buttons now link to their guides (were /ulke-secimi-2/).

**Metadata (SureRank; invisible on the page, visible in Google results)**
- New titles separate search intents. Overview vs. program: "Online IELTS Hazırlık: Academic ve General" vs.
  "Birebir IELTS Hazırlık Programı ve Ders Planı", and the same for TOEFL. Hubs: "Online Sınav Hazırlığı: IELTS,
  TOEFL, SAT, YDS", "Yurt Dışı Eğitim ve Başvuru Rehberliği", "Online Birebir İngilizce Dersleri (A1–C2)". Level
  tools: "İngilizce Seviyeni 3 Dakikada Tahmin Et", "Ücretsiz İngilizce Seviye Testi (40 Soru, A1–C2)",
  "Ücretsiz Canlı İngilizce Seviye Tespiti". Home: "Online İngilizce, IELTS ve Yurt Dışı Eğitim".
- 76 page-specific descriptions in the "sen" voice, each built only from facts on that page. No outcome
  promises; "rehberlik", not "danışmanlık"; health-adjacent pages keep "sağlık hizmeti değildir".
- English: /en/study-abroad title says "Guidance", not "Consulting". /en/ description: "student wellbeing" →
  "learning support".
- /randevu-olustur: noindex value corrected ("1" → "yes"); it drops out of the sitemap.

## 4. Going live (needs your approval, group by group)

Before the first live step, please also take a full backup in Hostinger hPanel (Backups). My backup covers page
content and SEO settings only (`seo/backup/live-2026-10-19.json.gz`), not the database and files.

```bash
python3 seo/publish.py live meta --yes        # titles, descriptions, /randevu-olustur noindex
python3 seo/publish.py live content A --yes   # editorial placeholders
python3 seo/publish.py live content C --yes   # country links
python3 seo/publish.py live content B --yes   # FAQ payment answer (business fact)
```
Each step writes only if the live page is still in the state recorded today, verifies what was saved, and purges
the Elementor and LiteSpeed caches.

**Rollback:** `python3 seo/publish.py live meta --rollback --yes`; `… content C --rollback --yes`; for any page,
`python3 seo/publish.py live restore --only <id> --yes` restores the 19 Oct backup. (Restore was tested on
staging: page 5518 restored, verified, re-patched.)

## 5. Business and legal wording: your decision (not changed)

| Page | Text | Why it matters | Suggestion |
|---|---|---|---|
| /programlar | "UCAS Registered Centres ve Common App kabul odaklı … paket" | Reads as an official UCAS affiliation | Remove unless the company is a registered UCAS centre. "UCAS ve Common App başvurularına yönelik …" is factual |
| /programlar vs /yurt-disi-egitim | Package lists "Konsolosluk vize si(…)" support; FAQ says "Vize desteğinin hizmet kapsamında olup olmadığı ayrıca doğrulanmalıdır" | Contradiction, and the FAQ reads unfinished | Decide whether visa paperwork support is in scope, then align both |
| /hakkimizda, /en/about | "British Council IELTS, ETS TOEFL ve UCAS gibi … standartlarla ilerliyoruz" | Can be read as a partnership | e.g. "IELTS, TOEFL ve UCAS'ın resmî ölçüt ve kılavuzlarını esas alıyoruz" |
| /hakkimizda, /en/about, /misyon-vizyon, /programlar, /en/ | "zihinsel esenlik / zihinsel denge / mental wellbeing" | Sits close to the "not a health service" line | Use "öğrenme ve motivasyon desteği" |
| /kvkk-basvuru-formu (legal) | "resmî başvuru adresleri, kurumsal kayıt işlemleri tamamlandığında bu tabloya eklenecektir" | Company is registered; legal text still says pending | Add the registered address (and KEP if you have one); legal review |
| /yaratici-atolyeler/nefes-zindelik-atolyesi | "lisanslı/sertifikalı olması şartıyla seçilen bir eğitmen … adı duyuru ile paylaşılır" | Bookable without a named instructor | Name the instructor or mark it as "next date to be announced" |

## 6. Performance (measured, lab data)

Lighthouse 12.8, 3 runs each, median, against live. Lab numbers, not real-user Core Web Vitals; those need
Search Console (section 7). Full table: `seo/baseline/lighthouse-live-2026-10-19.txt`.

| Page (mobile) | Score | LCP | TBT | CLS |
|---|---|---|---|---|
| / | 75 | 2.9 s | 714 ms | 0.000 |
| /ingilizce-egitimi | 84 | 2.7 s | 408 ms | 0.001 |
| /sinav-hazirligi | 67 | 2.9 s | 1005 ms | 0.000 |
| /ielts-hazirlik-3 | 85 | 2.9 s | 328 ms | 0.001 |
| IELTS program | 77 | 2.7 s | 722 ms | 0.000 |
| /en/ | 85 | 3.0 s | 342 ms | 0.001 |
| /blog | 79 | 3.0 s | 506 ms | 0.001 |
| /burs-rehberi | 64 | 2.9 s | 2174 ms | 0.000 |
| /ucretler | 64 | 3.2 s | 1502 ms | 0.000 |
| /seviye-testi | 74 | 5.4 s | 238 ms | 0.001 |

Desktop is 93–100 on all ten. Server response is fast (TTFB ~60 ms, Brotli, CDN, 7-day asset cache). Layout
shift is essentially zero. **The weak point is mobile main-thread time.** Measured on the home page (mobile, 4×
CPU, 5 runs), with one script removed at a time:

| Script (in the child theme `bai-astra-child`) | Blocking time without it |
|---|---|
| none removed (baseline) | ~3.0 s |
| `assets/bai-motion.js` (scroll animations, analytics, "bai-flatten" colour fixer; 120 KB) | ~1.2 s |
| inline "contrast guard" (`__baiContrastGuard`) | ~2.1 s |
| contrast guard, re-sweeps removed (runs once) | ~2.3 s, **but some final colours differ**, so not safe without design review |

Why: the contrast guard and bai-flatten walk every element after load, reading `getComputedStyle` and
`getBoundingClientRect` between style writes (forced re-layout), and repeat on every DOM change. Recommended
fix (needs theme file access, which the API does not give):
1. Move the colour corrections into `bai-components.css` (the scripts already know which colours they fix) and
   delete both runtime fixers. Biggest single win; the design should not change, but it needs a visual check.
2. In `bai-motion.js`, load the analytics, exit-intent and WhatsApp modules after idle (`requestIdleCallback`), and
   read layout once per frame.
3. jQuery UI Sortable + touch-punch load on every public page and nothing on those pages uses them. Find the
   plugin that enqueues them (likely the scheduling or LMS plugin) and load them only on /panel.
4. React stays: the SureCookie consent banner needs it.
5. /seviye-testi LCP of 5.4 s: the hero waits for the quiz script. Render the first screen in HTML.

No performance change was deployed, so there are no "after" scores yet. Measure again with
`seo/lighthouse.sh` after the theme work.

## 7. Blocked: needs your access

| Item | What to do |
|---|---|
| **Google Search Console** (rankings, impressions, indexing, real CWV) | WP Admin → SureRank → Search Console → connect with the Google account that owns the domain. Then submit `https://biradimileri.com/sitemap_index.xml`. Bing Webmaster Tools can import from Search Console |
| GA4/GTM audit (lead and purchase events, consent) | Read access to GTM container GTM-T5FDGPQM and the GA4 property |
| Full backup before live | Hostinger hPanel → Backups |
| Child-theme performance work | SFTP/File Manager access, or a developer, for `wp-content/themes/bai-astra-child` |
| /is-ingilizcesi/ 302 → home | Should be a 301 to /is-ingilizcesi-2/. The rule is not in WordPress content; check hPanel redirects or `.htaccess` |
| http://www → https://www → apex (2 hops) | Minor; one hop is possible in Hostinger CDN/redirect settings |
| Staging differences | Live /iptal-ve-iade is newer than staging, and /geri-bildirim is missing on staging. Neither was touched |

## 8. Search intent map (key URLs)

| URL | Primary intent | Not this (goes to) |
|---|---|---|
| / | online İngilizce + sınav + yurt dışı (brand) | — |
| /ingilizce-egitimi | online birebir İngilizce dersi | prices → /ucretler |
| /sinav-hazirligi | sınav seçimi, online sınav hazırlığı | one exam → its page |
| /ielts-hazirlik-3 | IELTS hazırlık (Academic/General overview) | birebir program → program page |
| /programlar/…/ielts-hazirlik-programi | birebir IELTS hazırlık programı | — |
| /toefl-hazirlik-3 · /programlar/…/toefl-hazirlik-programi | TOEFL iBT hazırlık · birebir TOEFL programı | — |
| /seviye-testi | 3 dakikalık İngilizce öz değerlendirme | real test → /seviye-testi-40 |
| /seviye-testi-40 | ücretsiz İngilizce seviye testi (40 soru) | — |
| /ingilizce-seviye-tespit-sinavi-3 | öğretmenle canlı seviye tespiti | — |
| /yurt-disi-egitim | yurt dışı eğitim + başvuru rehberliği | each country → its guide |
| /{ülke}-egitim (8) | "{Ülke}'de üniversite" | — |
| /ucretler | İngilizce özel ders fiyatları, paketler | — |

**Overlap to review with Search Console data before merging anything:** the short Elementor pages
/konusma-ingilizcesi-2 (212 words), /is-ingilizcesi-2 (254), /yetiskinler-icin-ingilizce-2 (228) and
/grup-ingilizce-dersleri-2 sit next to deep program pages (1,600–2,900 words) on the same topic. If Search Console
shows them competing for the same queries, merge each into its program page with a 301. Until then their
metadata is differentiated.

## 9. 30/60/90 days

- **Days 1–30:** approve and publish sections 4 and 5; connect Search Console and submit the sitemap; take the
  baseline export; theme performance items 1 and 3.
- **Days 31–60:** first 3 articles from the audit's list, written or reviewed by your educators: (1) IELTS
  Academic vs General Training, (2) seviye testi vs. canlı değerlendirme, (3) yurt dışı başvuru belge kontrol
  listesi. Each links to its service page, cites official sources and shows a review date. I can draft them on
  staging as drafts for review. Decide the four short-page overlaps using Search Console data.
- **Days 61–90:** 3–4 more articles; review Search Console queries per landing page and adjust titles that get
  impressions but few clicks; re-measure Lighthouse and real-user CWV.
- **Every week for 6 weeks, then monthly:** Search Console indexing report, impressions and clicks for non-brand
  queries, leads by landing page.

## Files

`seo/publish.py` (apply/rollback/restore) · `seo/content_patches.py` · `seo/seo_meta.py` ·
`seo/metadata_changes.csv` · `seo/crawl.py` · `seo/backup.py` · `seo/backup/` (19 Oct content backups) ·
`seo/baseline/` (crawls and Lighthouse) · `seo/lighthouse.sh`, `seo/lh_summary.py` · `seo/perf/` (script
attribution, profile, screenshots).
