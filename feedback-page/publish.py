#!/usr/bin/env python3
"""Publish the "Geri Bildirim ve Şikâyet" change set to staging (default) or live.

What it does, in order (every step is safe to repeat):
  1. Creates or updates the SureForms form "Geri Bildirim ve Şikâyet" (src/form-blocks.html).
  2. Creates or updates the page /geri-bildirim/ (src/geri-bildirim.html), with Astra and SureRank settings.
  3. Applies the text edits in edits.py to the existing pages (legal pages, İletişim, SSS, expert FAQs).
  4. Adds "Geri Bildirim ve Şikâyet" under Kurumsal in the footer menu "Alt Menü (Dengeli)".

Before a page is changed for the first time, its content is saved to backup/<site>-<id>.html (or .json for SSS).
IDs the script created are kept in state-<site>.json.

Usage:
  python3 feedback-page/publish.py                  # staging
  python3 feedback-page/publish.py --site live --yes   # live, only after the owner approved it
"""
import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import edits  # noqa: E402

SITE = sys.argv[sys.argv.index("--site") + 1] if "--site" in sys.argv else "staging"
if SITE not in ("staging", "live"):
    sys.exit("publish: --site must be staging or live")
if SITE == "live" and "--yes" not in sys.argv:
    sys.exit("publish: live needs --yes (and the owner's approval for this change).")

base = os.environ["WP_STAGING_URL" if SITE == "staging" else "WP_URL"].rstrip("/")
pw = os.environ["WP_STAGING_APP_PASSWORD" if SITE == "staging" else "WP_APP_PASSWORD"]
if SITE == "staging" and urllib.parse.urlparse(base).hostname == urllib.parse.urlparse(os.environ.get("WP_URL", "")).hostname:
    sys.exit("publish: WP_STAGING_URL points at the live site; refusing.")
auth = base64.b64encode(f'{os.environ["WP_USER"]}:{pw}'.encode()).decode()
STATE = HERE / f"state-{SITE}.json"
BACKUP = HERE / "backup"
FOOTER_MENU = 90
KURUMSAL_ITEM_TITLE = "Kurumsal"
MENU_TITLE = "Geri Bildirim ve Şikâyet"
SLUG = "geri-bildirim"


def api(method, path, body=None, prefix="/wp-json/wp/v2"):
    req = urllib.request.Request(base + prefix + path, method=method,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Authorization": "Basic " + auth, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"publish: {method} {path} -> HTTP {e.code}: {e.read()[:500]!r}")


state = json.loads(STATE.read_text()) if STATE.exists() else {}


def save_state():
    STATE.write_text(json.dumps(state, indent=2) + "\n")


def backup(name, text):
    BACKUP.mkdir(exist_ok=True)
    f = BACKUP / f"{SITE}-{name}"
    if not f.exists():
        f.write_text(text, encoding="utf-8")


# 1. Form ---------------------------------------------------------------------------------------
template = api("GET", "/sureforms_form/2012?context=edit")
form_meta = {k: v for k, v in template["meta"].items() if k.startswith("_srfm_")}
notification = dict(template["meta"]["_srfm_email_notification"][0])
notification.update({"name": "Yeni geri bildirim / şikâyet", "email_reply_to": "",
                     "subject": "Geri bildirim / şikâyet — {form_title}", "email_body": "{all_data}"})
form_meta.update({
    "_srfm_submit_button_text": "Bildirimi gönder",
    "_srfm_email_notification": [notification],
    "_srfm_compliance": [{"id": "gdpr", "gdpr": False, "do_not_store_entries": False,
                          "auto_delete_entries": True, "auto_delete_days": "730"}],
    "_srfm_form_confirmation": [{
        "id": 1, "confirmation_type": "same page", "page_url": "", "custom_url": "",
        "message": "<h3>Bildirimin bize ulaştı. Teşekkür ederiz.</h3>"
                   "<p>Bildirimini ilgili uzman değil, koordinasyon ekibimiz inceleyecek. İletişim bilgisi bıraktıysan "
                   "aldığımızı en geç 1 iş günü içinde, ne yapacağımızı en geç 2 iş günü içinde yazılı olarak bildiririz.</p>"
                   "<p>Acil bir güvenlik durumu varsa beklemeden 0216 888 13 69 numarasını ara.</p>",
        "submission_action": "hide form", "enable_query_params": False, "query_params": []}],
})
blocks = (HERE / "src" / "form-blocks.html").read_text(encoding="utf-8")
host = urllib.parse.urlparse(base).hostname
blocks = blocks.replace("biradimileri.com/kvkk-aydinlatma-metni", f"{host}/kvkk-aydinlatma-metni")
form_id = state.get("form_id")
if not form_id:
    created = api("POST", "/sureforms_form", {"title": "Geri Bildirim ve Şikâyet", "status": "publish",
                                              "content": blocks.replace("{FORM_ID}", "0"), "meta": form_meta})
    form_id = state["form_id"] = created["id"]
    save_state()
api("POST", f"/sureforms_form/{form_id}", {"title": "Geri Bildirim ve Şikâyet", "status": "publish",
                                           "content": blocks.replace("{FORM_ID}", str(form_id)), "meta": form_meta})
print(f"form {form_id}: ok")

# 2. Page ---------------------------------------------------------------------------------------
html = (HERE / "src" / "geri-bildirim.html").read_text(encoding="utf-8").replace("{FORM_ID}", str(form_id))
html = html.replace("Canonical: /geri-bildirim/", f"Canonical: {base}/geri-bildirim/")
if SITE == "staging":
    html = html.replace("info@biradimileri.com", f"info@{host}")  # staging's search-replace convention
astra = api("GET", "/pages/4069?context=edit&_fields=meta")["meta"]
page_meta = {k: v for k, v in astra.items() if not k.startswith("_elementor") and k != "footnotes"}
page_id = state.get("page_id")
if not page_id:
    clash = api("GET", f"/pages?slug={SLUG}&status=publish,draft,private,pending&_fields=id")
    if clash:
        sys.exit(f"publish: a page with slug {SLUG} already exists (id {clash[0]['id']}); refusing to overwrite.")
body = {"title": "Geri Bildirim ve Şikâyet", "slug": SLUG, "status": "publish", "content": html,
        "meta": page_meta, "comment_status": "closed", "parent": 0}
page = api("POST", f"/pages/{page_id}" if page_id else "/pages", body)
page_id = state["page_id"] = page["id"]
save_state()
seo = api("GET", f"/post/settings?post_id={page_id}&post_type=page", prefix="/wp-json/surerank/v1")["data"]
title = "Geri Bildirim ve Şikâyet | Bir Adım İleri"
desc = ("Bir dersten, uzmandan, planlamadan ya da ödemeden memnun kalmadıysan bize yaz. Şikâyetini ilgili uzman "
        "değil koordinasyon ekibi inceler; 2 iş günü içinde yazılı yanıt verilir.")
seo.update({"page_title": title, "page_description": desc, "auto_generate_description": False,
            "facebook_title": title, "facebook_description": desc, "canonical_url": f"{base}/{SLUG}/"})
api("POST", "/post/settings", {"post_id": page_id, "metaData": seo}, prefix="/wp-json/surerank/v1")
print(f"page {page_id}: {page['link']}")

# 3. Edits to existing pages --------------------------------------------------------------------
for pid, (name, page_edits) in edits.PAGES.items():
    cur = api("GET", f"/pages/{pid}?context=edit&_fields=content")["content"]["raw"]
    new = edits.apply(cur, page_edits, name)
    if new != cur:
        backup(f"{pid}.html", cur)
        api("POST", f"/pages/{pid}", {"content": new})
        print(f"{pid} {name}: updated")
    else:
        print(f"{pid} {name}: already up to date")

for pid, (name, page_edits) in edits.ELEMENTOR_PAGES.items():
    raw = api("GET", f"/pages/{pid}?context=edit&_fields=meta")["meta"]["_elementor_data"]
    data = json.loads(raw)
    widgets = [w for c in data for w in c.get("elements", []) if w.get("widgetType") == "html"]
    if len(widgets) != 1:
        sys.exit(f"{name}: expected one HTML widget, found {len(widgets)}")
    cur = widgets[0]["settings"]["html"]
    new = edits.apply(cur, page_edits, name)
    if new != cur:
        backup(f"{pid}-elementor.json", raw)
        widgets[0]["settings"]["html"] = new
        api("POST", f"/pages/{pid}", {"meta": {"_elementor_data": json.dumps(data, ensure_ascii=False)}})
        print(f"{pid} {name}: updated (Elementor)")
    else:
        print(f"{pid} {name}: already up to date")

# 4. Footer menu --------------------------------------------------------------------------------
items = api("GET", f"/menu-items?menus={FOOTER_MENU}&per_page=100&context=edit&_fields=id,title,url,parent,menu_order,object_id")
kurumsal = [i for i in items if i["parent"] == 0 and i["title"]["raw"] == KURUMSAL_ITEM_TITLE]
if len(kurumsal) != 1:
    sys.exit("menu: could not find the Kurumsal item")
kurumsal = kurumsal[0]
if not any(i["object_id"] == page_id for i in items):
    children = sorted((i for i in items if i["parent"] == kurumsal["id"]), key=lambda i: i["menu_order"])
    after = children[-1]["menu_order"]  # last Kurumsal child (İletişim)
    for i in sorted(items, key=lambda i: -i["menu_order"]):
        if i["menu_order"] > after:
            api("POST", f"/menu-items/{i['id']}", {"menu_order": i["menu_order"] + 1})
    api("POST", "/menu-items", {"title": MENU_TITLE, "type": "post_type", "object": "page", "object_id": page_id,
                                "parent": kurumsal["id"], "menus": FOOTER_MENU, "menu_order": after + 1,
                                "status": "publish"})
    print("menu: item added under Kurumsal")
else:
    print("menu: already has the item")

# Elementor regenerates its CSS/HTML cache for the SSS page on next view.
try:
    api("DELETE", "/cache", prefix="/wp-json/elementor/v1")
except (SystemExit, ValueError) as e:
    print(f"note: Elementor cache not cleared ({e})")
print("done")
