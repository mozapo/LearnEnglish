"""Print the visible text around a phrase on public pages: python3 seo/context.py live PHRASE [url-substring]"""
import re, sys, requests
from bs4 import BeautifulSoup
sys.path.insert(0, __import__("os").path.dirname(__file__))
import wp, crawl

def text(url, sess):
    s = BeautifulSoup(sess.get(url, timeout=90).text, "lxml")
    for t in s(["script", "style", "noscript"]): t.decompose()
    return (s.find("main") or s.body).get_text(" ", strip=True)

if __name__ == "__main__":
    target, phrase = sys.argv[1], sys.argv[2]
    filt = sys.argv[3] if len(sys.argv) > 3 else ""
    sess = requests.Session(); sess.headers["User-Agent"] = crawl.UA
    urls = sorted(set(crawl.sitemap_urls(sess, wp.base(target))))
    for u in urls:
        if filt not in u or "/product/" in u: continue
        t = text(u, sess)
        for m in re.finditer(phrase, t):
            print(f"{u}\n   …{t[max(0,m.start()-160):m.end()+160]}…")
