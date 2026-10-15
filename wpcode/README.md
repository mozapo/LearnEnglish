# WPCode snippets

PHP snippets that run on biradimileri.com through WPCode Lite. The REST API cannot create
WPCode snippets, so they are installed by hand: **Code Snippets → + Add Snippet → Add Your Custom
Code → PHP Snippet**, paste the whole file, **Insert Method: Auto Insert**, **Location: Run
Everywhere**, activate. Staging first, live only after approval.

| File | What it does |
|---|---|
| `bai-interview-reminder-once.php` | Stopgap (15 Oct 2026). The bai-booking plugin re-sent the interview reminder on every hourly run in the last 24 hours (6× each to candidate and owner). This lets each interview reminder through once per recipient per interview time and blocks repeats. Remove when the plugin sends a single 1-hour-before reminder. |

Offline test (no WordPress needed): `php wpcode/test/interview-reminder-once.php`
