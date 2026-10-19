# CLAUDE.md — Bir Adım İleri (biradimileri.com)

This repo supports the WordPress site **biradimileri.com**. Most work happens on the
site itself through the WordPress REST API, not in local code.

## Business background

- **Brand:** Bir Adım İleri ("One Step Ahead"). Tagline: *Hedefine bir adım ileri atmak için yanındayız.*
- **Legal entity:** Bir Adım İleri Eğitim Danışmanlık Limited Şirketi, İstanbul
  (MERSİS 0177082693100001 · Kartal V.D. 1770826931 · İstanbul Ticaret Sicili No 1161599).
  These identifiers must match everywhere they appear: site, contracts, invoices.
- **What it is:** a fully online education platform that puts six support areas under one roof
  instead of splitting them across separate institutions:
  1. İngilizce Eğitimi: one-to-one and group English (general, speaking, academic, business; children, teens, adults)
  2. Sınav Hazırlığı: IELTS, TOEFL, SAT, PTE, YDS, Cambridge, Turkish university prep exemption exams
  3. Yurt Dışı Eğitim: university application guidance (bachelor's, master's, PhD), countries, scholarships, motivation letters
  4. Koçluk: academic, student, career, productivity coaching and study planning
  5. Öğrenme ve Motivasyon Desteği: study habits, exam anxiety, motivation, self-confidence
  6. Yaratıcı Atölyeler: watercolour, drawing, painting, digital art, creative writing, art workshops in English
  - Also: **Bir Adım İyilik** (free and discounted places funded by the company itself; no donations are collected) and
    **Eğitmen Akademisi / Öğretme Pusulası** (a 10-module teacher training course with a certification exam, in TR and EN).
- **Audience:** learners in Türkiye, from age 5 (children's English) through teens, university candidates and professionals.
  For under-18s the parent or guardian is the contracting party.
- **Founder:** about 20 years in education since 2006 (teacher, teacher trainer, academic coordinator, curriculum designer, manager)
  in two countries, with Cambridge DELTA and CELTA qualifications. Their story is on `/hikayemiz`.
- **Values:** human warmth and empathy · transparency and ethics ("no over-promising") · evidence-based and sustainable ·
  holistic development. Technology (AI) is used, but people stay at the centre.
- **Customer journey:** free 15-min intro call → expert matching → written price and scope → Ön Bilgilendirme Formu +
  Mesafeli Satış Sözleşmesi approved before payment → payment (İş Bankası 3D Secure or bank transfer/EFT) →
  scheduling within 48 hours → lessons logged in the student panel. Enquiries are answered within 2 business days.
- **Commercial terms (from `/ucretler` and `/iptal-ve-iade`):** all prices in TRY, VAT included. Lessons are 40 minutes, live and online.
  14-day right of withdrawal; unused lessons are refunded. A lesson postponed with 12+ hours' notice is free.
  Changing to a different expert is free.

## Site structure

- **Stack:** WordPress (tr_TR, Europe/Istanbul) on Hostinger with LiteSpeed Cache. Theme: **Astra** with the child theme
  `bai-astra-child` (v1.0.18).
- **Page builders:** three kinds (published pages on live, Oct 2026):
  - **72 Elementor**: home, all service detail pages, teacher listings, FAQ, `/hikayemiz`, `/nasil-calisir`, `/en`.
  - **88 Gutenberg blocks**: legal pages, `/ucretler`, `/hakkimizda`, `/kocluk`, `/yaratici-atolyeler`, `/programlar/*`.
  - **31 hand-coded HTML in classic `post_content`**: all Eğitmen Akademisi / Educator Academy pages (TR and EN),
    and `/sozlesmelerim`. One minified block each, with its own `<style>`/`<script>` (prefix `bai-ac`).
- **Hand-coded HTML pages:** keep them on one line (wpautop turns line breaks into `<p>`/`<br>`). In inline scripts avoid
  `&&`, `//` comments and tag-like `<` in strings (write `\x3C`). Do not open them in the visual editor; it breaks the scripts.
  Progress for the academy lives in the visitor's browser under `bai_ac_tr` / `bai_ac_en`.
- **Key plugins:** WooCommerce (21 products = the price list), Tutor LMS (no courses yet), FluentCRM, SureForms, SureMail,
  SureRank SEO, SureCookie, Uncanny Automator, AI Engine, WPCode Lite, Limit Login Attempts.
  **Custom plugins:** *BAI İş Bankası Sanal POS* (payments), *Bir Adım İleri — Ders Planlama* (lesson scheduling and the
  `/panel` lesson panel), *Bir Adım İleri — Çalışma Planları* (study plans). These register the REST namespaces `bai/v1` and
  `bai-study/v1` and the roles `bai_teacher`, `bai_educator`, `bai_coordinator`.
  Inactive: iyzico, 3CX Live Chat, Starter Templates, SureDonation.
- **Level tests (`/seviye-testi`, `/seviye-testi-40`) and "Seviye testim" in `/panel`:** built and published from
  `level-test/` (read `level-test/README.md` first). The anonymous answer statistics run in WPCode snippet 4012; after any
  change to server code installed over the API, the owner must click **Update** on that snippet in WPCode, or the old
  cached code keeps running.
- **SEO:** SureRank is the only SEO plugin (titles, descriptions, schema, sitemap). The Oct 2026 audit, its tools and
  the approval status are in `seo/` (read `seo/REPORT.md` first).
- **Front page:** `/home` (ID 923), with a 7-question "Yön Bulma" quiz that runs only in the browser. There is no posts page;
  the blog is the `/blog` page, with 1 published post so far.
- **Footer menu ("Alt Menü (Dengeli)") is the real sitemap:**
  - **Hizmetler** → İngilizce Eğitimi · Sınav Hazırlığı · Yurt Dışı Eğitim · Koçluk · Öğrenme ve Motivasyon Desteği · Yaratıcı Atölyeler · Bir Adım İyilik
  - **Programlar** (`/programlar/…`) → Bireysel · Grup · Paket · Gençler İçin · Üniversite Adayları İçin · Profesyoneller İçin · Ücretler ve Paketler (`/ucretler`)
  - **Kaynaklar** → Seviye Testi · Üniversite Rehberi · Burs Rehberi · Ücretsiz Kaynaklar · Rehberler · Blog · SSS
  - **Kurumsal** (`/hakkimizda`) → Uzmanlarımız · Ekibimiz · Nasıl Çalışır? · Ekibimize Katıl
  - The primary menu holds only Ana Sayfa and Hizmetler (with 3 children). There is also a separate mobile menu.
- **Legal pages (`/yasal`):** KVKK Aydınlatma Metni, KVKK Başvuru Formu, Gizlilik, Çerez, Kullanım Koşulları,
  Mesafeli Satış Sözleşmesi, Ön Bilgilendirme Formu, İptal ve İade, Güvenli Ödeme, Çocuk Güvenliği Politikası.
- **English section:** `/en/…` (about, services, english-courses, test-prep, study-abroad, prices, educator-academy, contact, …).
- **Accounts and commerce pages:** `/sepet`, `/odeme`, `/hesabim`, `/dashboard`, `/panel`, `/sozlesmelerim`, login and registration pages.
  Pages titled **"[Kullanılmıyor] …"** are retired drafts. Leave them alone and never link to them.
- **Slug quirk:** many older pages have suffixes (`-2`, `-3`, such as `/ielts-hazirlik-3`). They are live URLs, so do not "clean"
  them without adding a redirect.

## Rules

### Working on the site
- **Staging first.** Make every change on staging (`$WP_STAGING_URL`, https://stg15oct.biradimileri.com) and verify it there.
  Touch **live** (`$WP_URL`) only after explicit approval for that specific change. Reading live is fine.
- Credentials are in env vars (`WP_USER`, `WP_APP_PASSWORD`, `WP_STAGING_APP_PASSWORD`). Application passwords contain
  spaces, so always quote them: `curl -u "$WP_USER:$WP_APP_PASSWORD"`. Never print them or commit them.
- The `claude` account is an administrator on both sites. Do not change settings, plugins, themes, users, products or prices
  unless asked.
- **Elementor pages:** what visitors see is stored in `_elementor_data`, not `post_content`. Editing `content` through
  `/wp/v2/pages` will not change those pages. Use Elementor's own data or tools, and purge LiteSpeed Cache after changes.
- Never delete pages. Set unwanted ones to draft, and add a redirect when you change a slug.
- Prices on pages must match the WooCommerce products, and both must match the legal documents.

### Content and voice
- Write in **Turkish**, using the informal **"sen"** on marketing pages. Legal texts use the formal "siz"; keep that.
- Tone: warm, calm, honest, specific. No hype, no exclamation-mark marketing, no pressure tactics. The brand says outright
  what it does **not** offer.
- **Never promise outcomes:** no guarantee of an exam score, admission, scholarship, job or visa. The brand promises the
  *process*, not the result.
- **Not a health service:** coaching and "Öğrenme ve Motivasyon Desteği" are not therapy, diagnosis or treatment. Do not call
  staff psychologists or the service psychological support. (The `psikolojik-destek` and `psikologlar` pages were retired for this
  reason.) Refer clinical needs to licensed professionals.
- **Say "rehberlik", not "danışmanlık",** for services (Üniversite Başvuru Rehberliği, Burs Rehberliği, Eğitim Rehberliği Ekibi).
  "Danışmanlık" appears only in the legal company name.
- Every service page ends with the main CTA, **"Ücretsiz ön görüşme planla"** (free 15-minute intro call), and usually a
  secondary CTA such as "Ücretleri gör" or "Önce soru sor".
- Prices: Turkish format, VAT included, in Turkish lira, e.g. `₺16.999`, `₺1.699,90`.
- Children's safety: under-18s are contacted only through company channels, and records and communication stay visible to
  parents. Content must not contradict `/cocuk-guvenligi-politikasi`.
- Collecting personal data means a KVKK notice and a link to `/kvkk-aydinlatma-metni`.
- Brand design guidance is in the `biradimileri-brand` skill (and the motion and UX skill `biradimileri-apple-motion`).
  Load it before designing new pages.
