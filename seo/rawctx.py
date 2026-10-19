"""Show raw stored markup around a phrase: python3 seo/rawctx.py PAGE_ID PHRASE [width]  (live pages snapshot)"""
import json, sys
P = {p["id"]: p for p in json.load(open(sys.argv[4] if len(sys.argv) > 4 else
     "/tmp/claude-0/-home-user-LearnEnglish/b05444d1-5a3b-5457-978b-939efa4058e0/scratchpad/live_pages2.json"))}
pid, phrase = int(sys.argv[1]), sys.argv[2]
w = int(sys.argv[3]) if len(sys.argv) > 3 else 300
for f, raw in (("content", P[pid]["content"]["raw"] or ""), ("elementor", P[pid]["meta"].get("_elementor_data") or "")):
    i = raw.find(phrase); n = raw.count(phrase)
    while i != -1:
        print(f"--- {pid} {f} (x{n}) ---\n{raw[max(0, i - w):i + len(phrase) + w]}\n")
        i = raw.find(phrase, i + 1)
