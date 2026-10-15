# WPCode snippets

PHP snippets that run on biradimileri.com through the WPCode Lite plugin. The REST API cannot
create WPCode snippets, so they are installed by hand: **Code Snippets → + Add Snippet → Add Your
Custom Code → PHP Snippet**, paste the whole file, set **Insert Method: Auto Insert** and
**Location: Run Everywhere**, then activate. Staging first, live only after approval.

| File | What it does |
|---|---|
| `bai-job-application-once-a-year.php` | Lets each person send one job application (forms 3590 TR and 5609 EN) per 365 days, matched by e-mail or phone. Trashed or deleted entries don't count. |

Offline test (no WordPress needed): `php wpcode/test/run.php`
