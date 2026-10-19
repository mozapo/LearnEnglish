"""Small REST helper for the SEO work. Credentials come from the environment and are never printed."""
import os
import requests

SITES = {
    "live": ("WP_URL", "WP_APP_PASSWORD"),
    "staging": ("WP_STAGING_URL", "WP_STAGING_APP_PASSWORD"),
}


def base(target):
    return os.environ[SITES[target][0]].rstrip("/")


def session(target):
    s = requests.Session()
    s.auth = (os.environ["WP_USER"], os.environ[SITES[target][1]])
    s.headers["User-Agent"] = "Mozilla/5.0 (bai-seo-audit)"
    return s


def api(target, method, path, **kw):
    r = session(target).request(method, base(target) + "/wp-json/" + path.lstrip("/"), timeout=90, **kw)
    r.raise_for_status()
    return r.json()


def all_items(target, kind, params=None):
    out, page = [], 1
    while True:
        p = {"per_page": 100, "page": page, "context": "edit", "status": "any"}
        p.update(params or {})
        r = session(target).get(base(target) + f"/wp-json/wp/v2/{kind}", params=p, timeout=120)
        if r.status_code == 400 and page > 1:
            break
        r.raise_for_status()
        out += r.json()
        if page >= int(r.headers.get("X-WP-TotalPages", 1)):
            break
        page += 1
    return out
