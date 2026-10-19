"""Read-only crawl of the public site: every sitemap URL plus every published page/post/product.

    python3 seo/crawl.py live out.json      # or staging (staging is fetched logged in, it is not public)
Records per URL: status, final URL, robots, canonical, hreflang, lang, og:locale, title, description, H1/H2,
JSON-LD types, word count, internal links, images without alt / without size, lazy images in the first screen.
"""
import json
import re
import sys
import concurrent.futures as cf
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, __import__("os").path.dirname(__file__))
import wp  # noqa: E402

UA = "Mozilla/5.0 (Linux; Android 12) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125 Mobile Safari/537.36"


def sitemap_urls(sess, root):
    out, todo = [], [root + "/sitemap_index.xml"]
    while todo:
        x = sess.get(todo.pop(), timeout=60).text
        locs = re.findall(r"<loc>(.*?)</loc>", x)
        if "<sitemapindex" in x:
            todo += locs
        else:
            out += locs
    return out


def jsonld_types(soup):
    types = []
    for s in soup.find_all("script", type="application/ld+json"):
        try:
            d = json.loads(s.string or "")
        except Exception:
            types.append("INVALID")
            continue
        items = d.get("@graph", [d]) if isinstance(d, dict) else d
        for i in items:
            t = i.get("@type") if isinstance(i, dict) else None
            types += t if isinstance(t, list) else [t]
    return types


def audit(sess, root, url):
    host = urlparse(root).netloc
    try:
        r = sess.get(url, timeout=90, allow_redirects=True)
    except Exception as e:
        return {"url": url, "error": str(e)}
    rec = {"url": url, "status": r.status_code, "final": r.url, "hops": [h.status_code for h in r.history],
           "x_robots": r.headers.get("x-robots-tag", ""), "bytes": len(r.content)}
    if "text/html" not in r.headers.get("content-type", ""):
        return rec
    soup = BeautifulSoup(r.text, "lxml")
    m = lambda **a: [t.get("content", "") for t in soup.find_all("meta", attrs=a)]
    rec["robots"] = m(name="robots")
    rec["canonical"] = [l.get("href") for l in soup.find_all("link", rel="canonical")]
    rec["hreflang"] = {l.get("hreflang"): l.get("href") for l in soup.find_all("link", rel="alternate") if l.get("hreflang")}
    rec["lang"] = (soup.html or {}).get("lang", "")
    rec["og_locale"] = m(property="og:locale")
    rec["titles"] = [t.get_text() for t in soup.find_all("title")]
    rec["descriptions"] = m(name="description")
    body = soup.body or soup
    rec["h1"] = [h.get_text(" ", strip=True) for h in body.find_all("h1")]
    rec["h2"] = [h.get_text(" ", strip=True) for h in body.find_all("h2")][:25]
    rec["schema"] = jsonld_types(soup)
    for t in body(["script", "style", "noscript"]):
        t.decompose()
    main = body.find("main") or body
    text = main.get_text(" ", strip=True)
    rec["words"] = len(text.split())
    rec["text_flags"] = sorted({k for k in ["Yayın ekibine not", "yayımlamayın", "hazırlanıyor", "TODO", "lorem", "Lorem",
                                             "yakında", "Yakında", "eklenecek", "placeholder", "psikolog", "Psikolog",
                                             "Beşiktaş", "UCAS", "garanti", "danışmanlık", "Danışmanlık", "lisanslı"]
                                 if k in text})
    links = set()
    for a in body.find_all("a", href=True):
        h = urljoin(r.url, a["href"]).split("#")[0]
        if urlparse(h).netloc == host:
            links.add(h)
    rec["links"] = sorted(links)
    imgs = body.find_all("img")
    rec["imgs"] = len(imgs)
    rec["img_no_alt"] = sum(1 for i in imgs if i.get("alt") is None)
    rec["img_no_size"] = sum(1 for i in imgs if not (i.get("width") and i.get("height")))
    return rec


def main(target, out):
    root = wp.base(target)
    sess = wp.session(target) if target == "staging" else requests.Session()
    sess.headers["User-Agent"] = UA
    urls = set(sitemap_urls(sess, root))
    in_sitemap = set(urls)
    for kind in ["pages", "posts"]:
        for p in wp.all_items(target, kind, {"status": "publish"}):
            urls.add(p["link"])
    with cf.ThreadPoolExecutor(6) as ex:
        recs = list(ex.map(lambda u: audit(sess, root, u), sorted(urls)))
    for r in recs:
        r["in_sitemap"] = r["url"] in in_sitemap
    json.dump(recs, open(out, "w"), ensure_ascii=False, indent=1)
    print(len(recs), "urls")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
