# WPCode snippets

PHP snippets that run on biradimileri.com through WPCode Lite. The REST API cannot create
WPCode snippets, so they are installed by hand: **Code Snippets → + Add Snippet → Add Your Custom
Code → PHP Snippet**, paste the whole file, **Insert Method: Auto Insert**, **Location: Run
Everywhere**, activate. Staging first, live only after approval.

| File | What it does |
|---|---|
| `bai-interview-reminder-once.php` | Stopgap (15 Oct 2026). bai-booking 0.8.0 re-sent the interview reminder every hourly run in the last 24 hours and titled the owner copy "Yarın görüşme" even on the day. This holds reminders until the interview is ≤75 min away (date read from the subject, Turkey time), lets each through once per recipient per interview time, and renames "Yarın görüşme:" to "Görüşme hatırlatması:". Remove when the plugin sends a single 1-hour-before reminder. |

Offline test (no WordPress needed): `php wpcode/test/interview-reminder-once.php`
