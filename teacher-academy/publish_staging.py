#!/usr/bin/env python3
"""Create or update the "Teacher Academy – Preview" DRAFT page on the STAGING site.

Safety:
  * Talks only to $WP_STAGING_URL and refuses to run if it points at the live host ($WP_URL).
  * Always saves with status "draft"; never publishes.
  * Only touches the page ID it created itself (stored in staging-page.json); never edits
    the original /egitmen-akademisi page (ID 4358).

Usage: python3 teacher-academy/build.py && python3 teacher-academy/publish_staging.py
       python3 teacher-academy/build.py --lang en && python3 teacher-academy/publish_staging.py --lang en
"""
import base64
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
LANG = sys.argv[sys.argv.index("--lang") + 1] if "--lang" in sys.argv else "tr"
CONTENT = HERE / "dist" / ("educator-academy-preview.html" if LANG == "en" else "teacher-academy-preview.html")
STATE = HERE / ("staging-page-en.json" if LANG == "en" else "staging-page.json")
ORIGINAL_ID = 4359 if LANG == "en" else 4358
TITLE = "Educator Academy – Preview" if LANG == "en" else "Teacher Academy – Preview"

base = os.environ["WP_STAGING_URL"].rstrip("/")
live = os.environ.get("WP_URL", "").rstrip("/")
if not base or urllib.parse.urlparse(base).hostname == urllib.parse.urlparse(live).hostname:
    sys.exit("publish: WP_STAGING_URL is empty or points at the live site; refusing.")
auth = base64.b64encode(f'{os.environ["WP_USER"]}:{os.environ["WP_STAGING_APP_PASSWORD"]}'.encode()).decode()


def api(method, path, body=None):
    req = urllib.request.Request(base + "/wp-json/wp/v2" + path, method=method,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Authorization": "Basic " + auth, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"publish: {method} {path} -> HTTP {e.code}: {e.read()[:400]!r}")


content = CONTENT.read_text(encoding="utf-8")

# Same Astra layout settings as the original page, so the preview renders the same way.
orig = api("GET", f"/pages/{ORIGINAL_ID}?context=edit&_fields=meta")
meta = {k: v for k, v in orig["meta"].items() if not k.startswith("_elementor") and k != "footnotes"}

page_id = json.loads(STATE.read_text())["id"] if STATE.exists() else None
if page_id == ORIGINAL_ID:
    sys.exit("publish: refusing to write to the original page")
body = {"title": TITLE, "status": "draft", "content": content, "meta": meta}
if page_id:
    current = api("GET", f"/pages/{page_id}?context=edit&_fields=id,status,title")
    if current["status"] != "draft":
        sys.exit(f"publish: page {page_id} is '{current['status']}', not a draft; refusing to touch it.")
    saved = api("POST", f"/pages/{page_id}", body)
else:
    saved = api("POST", "/pages", body)
    STATE.write_text(json.dumps({"id": saved["id"], "site": base}, indent=2) + "\n")

check = api("GET", f"/pages/{saved['id']}?context=edit&_fields=id,status,content,link")
problems = []
if check["status"] != "draft":
    problems.append(f"status is {check['status']}")
if check["content"]["raw"] != content:
    problems.append("stored content differs from the build (a WordPress filter changed it)")
rendered = check["content"]["rendered"]
# wpautop also wraps the trailing <script> tags in <p> on the original page; that is harmless.
# What must not happen: stray <br>, or anything injected inside our script.
js = re.search(r'id="bai-ta-js">(.*?)</script>', rendered, flags=re.S)
if "&#038;" in rendered or "<br" in rendered or not js or re.search(r"<(p|br)\b", js.group(1)):
    problems.append("rendered output was altered by content filters")
if problems:
    sys.exit("publish: saved, but verification failed: " + "; ".join(problems))

print(f"publish: draft page {saved['id']} saved and verified on {base}")
print(f"preview (log in to staging first): {base}/?page_id={saved['id']}&preview=true")
