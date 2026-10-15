#!/usr/bin/env python3
"""Replace the content of the LIVE Eğitmen Akademisi page (ID 4358) with the new build.

Only run after explicit approval. Safety:
  * Writes to exactly one page (4358) and only its "content" field: title, slug, status,
    template and settings are left alone. Learners' progress (browser and server) is not touched.
  * Refuses unless the live content still equals the backup in backup/ (nobody edited it since).
  * Verifies the stored and rendered result afterwards.
  * --rollback puts the backup back.

Usage: python3 teacher-academy/build.py --live && python3 teacher-academy/publish_live.py --yes
       python3 teacher-academy/publish_live.py --rollback --yes
       --staging: same for the STAGING copy of the page (backup = its file in original/)
       --lang en: the English page /en/educator-academy (ID 4359) instead of 4358
"""
import base64
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
LANG = sys.argv[sys.argv.index("--lang") + 1] if "--lang" in sys.argv else "tr"
PAGE_ID, SLUG, NAME, OUT = {"tr": (4358, "egitmen-akademisi", "egitmen-akademisi-4358", "teacher-academy"),
                            "en": (4359, "educator-academy", "educator-academy-4359", "educator-academy")}[LANG]
STAGING = "--staging" in sys.argv
if STAGING:
    BACKUP = HERE / "original" / f"{NAME}.html"
    BUILD = HERE / "dist" / f"{OUT}-preview.html"
    base = os.environ["WP_STAGING_URL"].rstrip("/")
    password = os.environ["WP_STAGING_APP_PASSWORD"]
else:
    BACKUP = HERE / "backup" / f"live-{PAGE_ID}-content.html"
    BUILD = HERE / "dist" / f"{OUT}-live.html"
    base = os.environ["WP_URL"].rstrip("/")
    password = os.environ["WP_APP_PASSWORD"]

if "--yes" not in sys.argv:
    sys.exit("publish_live: this writes to the site; re-run with --yes once approved.")
rollback = "--rollback" in sys.argv
auth = base64.b64encode(f'{os.environ["WP_USER"]}:{password}'.encode()).decode()


def api(method, path, body=None):
    req = urllib.request.Request(base + "/wp-json/wp/v2" + path, method=method,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Authorization": "Basic " + auth, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"publish_live: {method} {path} -> HTTP {e.code}: {e.read()[:400]!r}")


backup = BACKUP.read_text(encoding="utf-8")
new = backup if rollback else BUILD.read_text(encoding="utf-8")
expected_now = BUILD.read_text(encoding="utf-8") if rollback else backup

before = api("GET", f"/pages/{PAGE_ID}?context=edit&_fields=id,slug,status,template,title,content")
if before["slug"] != SLUG or before["status"] != "publish":
    sys.exit(f"publish_live: page {PAGE_ID} is not the published {SLUG} page; stopping.")
if before["content"]["raw"] == new:
    print("publish_live: live content is already this version; nothing to do.")
    sys.exit(0)
if before["content"]["raw"] != expected_now:
    sys.exit("publish_live: live content changed since the backup was taken; stopping so nothing is overwritten.")

api("POST", f"/pages/{PAGE_ID}", {"content": new})

after = api("GET", f"/pages/{PAGE_ID}?context=edit&_fields=id,slug,status,template,title,content")
problems = []
for k in ("slug", "status", "template"):
    if after[k] != before[k]:
        problems.append(f"{k} changed")
if after["title"]["raw"] != before["title"]["raw"]:
    problems.append("title changed")
if after["content"]["raw"] != new:
    problems.append("stored content differs from what was sent")
rendered = after["content"]["rendered"]
if not rollback:
    js = re.search(r'id="bai-ta-js">(.*?)</script>', rendered, flags=re.S)
    if "&#038;" in rendered or "<br" in rendered or not js or re.search(r"<(p|br)\b", js.group(1)):
        problems.append("rendered output was altered by content filters")
if 'id="bai-ac-js"' not in rendered:
    problems.append("hub script missing from rendered output")
if problems:
    sys.exit("publish_live: WRITTEN BUT VERIFICATION FAILED: " + "; ".join(problems)
             + "\n  Roll back with: python3 teacher-academy/publish_live.py --rollback --yes")

print(f"publish_live: {'rolled back' if rollback else 'updated'} {'staging' if STAGING else 'live'} page {PAGE_ID} and verified (page {SLUG})")
