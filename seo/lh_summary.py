"""Median Lighthouse metrics per page and mode: python3 seo/lh_summary.py DIR"""
import glob, json, os, statistics as st, sys, collections
d = sys.argv[1]
runs = collections.defaultdict(list)
for f in glob.glob(os.path.join(d, "*.json")):
    slug, mode, _ = os.path.basename(f).rsplit(".", 3)[:3]
    r = json.load(open(f))
    if r.get("runtimeError") or not r["categories"]["performance"]["score"]:
        continue
    a = r["audits"]
    runs[(slug, mode)].append({
        "perf": r["categories"]["performance"]["score"] * 100, "lcp": a["largest-contentful-paint"]["numericValue"],
        "tbt": a["total-blocking-time"]["numericValue"], "cls": a["cumulative-layout-shift"]["numericValue"],
        "fcp": a["first-contentful-paint"]["numericValue"], "kib": a["total-byte-weight"]["numericValue"] / 1024,
        "seo": r["categories"]["seo"]["score"] * 100, "a11y": r["categories"]["accessibility"]["score"] * 100})
print(f"{'page':58} {'mode':7} n perf  LCP ms  TBT ms   CLS   FCP ms   KiB seo a11y")
for (slug, mode), rs in sorted(runs.items()):
    m = {k: st.median(x[k] for x in rs) for k in rs[0]}
    print(f"{slug[:58]:58} {mode:7} {len(rs)} {m['perf']:4.0f} {m['lcp']:7.0f} {m['tbt']:7.0f} {m['cls']:5.3f} {m['fcp']:7.0f} {m['kib']:5.0f} {m['seo']:3.0f} {m['a11y']:4.0f}")
