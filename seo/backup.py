"""Content-level backup over the REST API (not a database/file backup; that is in Hostinger hPanel).

    python3 seo/backup.py live|staging
Writes seo/backup/<target>-<date>.json.gz: every page and post (raw content + all meta, incl. _elementor_data),
the per-page SureRank SEO settings, SureRank global settings, and the WooCommerce products.
"""
import datetime, gzip, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wp  # noqa: E402

def main(target):
    s = wp.session(target); B = wp.base(target) + "/wp-json"
    out = {"target": target, "taken": datetime.datetime.now().isoformat(timespec="seconds")}
    out["pages"] = wp.all_items(target, "pages")
    out["posts"] = wp.all_items(target, "posts")
    out["surerank_global"] = s.get(B + "/surerank/v1/admin/global-settings", timeout=60).json()
    out["surerank_post"] = {}
    for p in out["pages"] + out["posts"]:
        r = s.get(B + "/surerank/v1/post/settings", params={"post_id": p["id"], "post_type": p["type"]}, timeout=60)
        out["surerank_post"][p["id"]] = r.json().get("data")
    out["products"] = s.get(B + "/wc/v3/products", params={"per_page": 100, "status": "any"}, timeout=60).json()
    os.makedirs(os.path.join(os.path.dirname(__file__), "backup"), exist_ok=True)
    suffix = os.environ.get("BACKUP_SUFFIX", "")
    path = os.path.join(os.path.dirname(__file__), "backup", f"{target}-{datetime.date.today()}{suffix}.json.gz")
    with gzip.open(path, "wt", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)
    print(path, len(out["pages"]), "pages", len(out["posts"]), "posts", len(out["products"]), "products",
          os.path.getsize(path) // 1024, "KiB")

if __name__ == "__main__":
    main(sys.argv[1])
