# Geri Bildirim ve Şikâyet

A single, clear place for complaints, suggestions and thanks, at `/geri-bildirim/`, plus links to it from
the pages where people look for one. Before this change, four legal texts said "send complaints through our contact page",
but the contact page had no way to do that.

**Owner decisions (15 Oct 2026):**
- Receipt is confirmed within 1 business day.
- A written reply comes within 2 business days.
- Safety reports are handled the same day.
- The expert concerned takes no part in the review; the coordination team handles it.
- The person can escalate to the founder.
- Anonymous reports are allowed but optional.
- Turkish only (no English pages).

**Status:** on **staging** since 15 Oct 2026 (form 5772, page 5773). **Not on live yet**: that needs the owner's approval.

## What changes

| Where | Change |
|---|---|
| New page `/geri-bildirim/` | How a report moves forward (4 steps), what to report, "you don't have to tell your expert", what we can and can't do, a safety box (same day, 112), no impact on lessons, the form, next steps (founder → Tüketici Hakem Heyeti → KVKK), FAQ + FAQPage JSON-LD |
| New SureForms form "Geri Bildirim ve Şikâyet" | Type, topic, who is writing, what happened, desired outcome, expert, order/date. Name, email and phone are optional, so a report can be anonymous. KVKK consent. Emails the same address as the intro-call form, and entries are deleted after 730 days |
| Ön Bilgilendirme Formu §8 | Link to the new page; independent review; 1 / 2 business days. Version 1.2 → **1.3** |
| İptal ve İade §7 | Optional internal step (feedback page → founder) before the legal routes. Version 1.6 → **1.7** |
| Çocuk Güvenliği Politikası §8 | New channel; goes to the coordination team; **same day** (was 3 business days); 112. Version 1.1 → **1.2** |
| KVKK Aydınlatma Metni | Retention row "Geri bildirim ve şikâyet kayıtları — 24 ay". Version 2.5 → **2.6** |
| İletişim | Note under the signature panel, a new FAQ item (+ JSON-LD), "40 soru" → "41 soru" |
| SSS (Elementor) | New question "Bir sorun yaşarsam ya da memnun kalmazsam ne yapmalıyım?", 40 → 41 |
| Uzmanlarımız, İngilizce Öğretmeni Bul | The "Uzmanımla anlaşamazsam ne olur?" answer links to the new page |
| Footer menu → Kurumsal | "Geri Bildirim ve Şikâyet" after İletişim |

## Files

| Path | What it is |
|---|---|
| `src/geri-bildirim.html` | Page content (bai-v2 components only, no page CSS/JS) |
| `src/form-blocks.html` | SureForms field blocks |
| `edits.py` | Exact text replacements for existing pages; each must match once, and repeat runs are safe |
| `publish.py` | Publishes everything to staging (default) or live (`--site live --yes`) |
| `state-staging.json` | IDs created on staging |
| `backup/` | Page content before the first change, per site |
| `test/staging.test.js` | Browser checks at 390 and 1280 px on the new page and every edited page |

```bash
python3 feedback-page/publish.py                    # staging
NODE_PATH=$(npm root -g) node feedback-page/test/staging.test.js "$WP_STAGING_URL" /tmp/shots
python3 feedback-page/publish.py --site live --yes  # live, after approval
NODE_PATH=$(npm root -g) node feedback-page/test/staging.test.js "$WP_URL" /tmp/shots
```

`publish.py` applies the edits to each site's own current content; it never copies staging content to live.

## Not automated
- **Acknowledging receipt is manual.** The form shows a confirmation on screen, but the "received within 1 business day"
  message is sent by the team. SureForms can email the sender automatically; set that up once a test submission shows
  the field tag for the email field.
- **Contract version labels.** If the checkout or `/sozlesmelerim` stores a hard-coded version label for the
  Ön Bilgilendirme Formu, it should now say 1.3.
- **LiteSpeed Cache.** The edited pages are purged on save. The footer menu appears on every page, so purge all
  once after going live.
