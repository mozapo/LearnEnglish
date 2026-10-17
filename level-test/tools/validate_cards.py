"""Checks cards.py against the live test questions. Exit code 1 on any problem.

Usage: python3 level-test/tools/validate_cards.py [page-content.html]
The default page is level-test/staging/4011-seviye-testi-40.html.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from cards import CARDS  # noqa: E402

LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]


def test_questions(page_html):
    m = re.search(r"var QUESTIONS = (\[.*?\]);", page_html, re.S)
    return json.loads(m.group(1))


def norm(s):
    return re.sub(r"[^a-z]+", " ", s.lower()).strip()


def main():
    page = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(HERE), "staging", "4011-seviye-testi-40.html")
    qs = {q["id"]: q for q in test_questions(open(page, encoding="utf-8").read())}
    errors = []
    seen_ids, covered = set(), {}
    test_prompts = {norm(q["prompt"]) for q in qs.values()}
    for c in CARDS:
        cid = c["id"]
        if cid in seen_ids:
            errors.append(f"{cid}: duplicate id")
        seen_ids.add(cid)
        for key in ("level", "items", "lead", "t_tr", "t_en", "tr", "en", "pat", "ex", "check", "prac"):
            if key not in c:
                errors.append(f"{cid}: missing {key}")
        if c["level"] not in LEVELS:
            errors.append(f"{cid}: bad level")
        if c["lead"] != ("tr" if LEVELS.index(c["level"]) <= 2 else "en"):
            errors.append(f"{cid}: lead language should be tr up to B1, en from B2")
        for i in c["items"]:
            if i in covered:
                errors.append(f"{cid}: item {i} already covered by {covered[i]}")
            covered[i] = cid
            if i not in qs:
                errors.append(f"{cid}: item {i} is not a test question")
            elif qs[i]["level"] != c["level"]:
                errors.append(f"{cid}: item {i} is {qs[i]['level']}, card is {c['level']}")
        if len(c["check"]) != 3:
            errors.append(f"{cid}: needs exactly 3 check questions")
        if len(c["prac"]) < 5:
            errors.append(f"{cid}: needs at least 5 practice questions")
        if len(c["ex"]) < 2:
            errors.append(f"{cid}: needs examples")
        all_q = [(q, "check") for q in c["check"]] + [(q, "prac") for q in c["prac"]]
        sentences = set()
        for q, kind in all_q:
            text, opts, ans = q[0], q[1], q[2]
            if "___" not in text and not text.startswith("one "):
                errors.append(f"{cid}: no gap in {text!r}")
            if kind == "prac" and (len(q) < 4 or not q[3].strip()):
                errors.append(f"{cid}: practice question without feedback: {text!r}")
            if len(opts) != 3 or len(set(o.lower() for o in opts)) != 3:
                errors.append(f"{cid}: options must be 3 distinct values: {text!r}")
            if not (0 <= ans < len(opts)):
                errors.append(f"{cid}: answer index out of range: {text!r}")
            if norm(text) in test_prompts:
                errors.append(f"{cid}: reuses a test sentence: {text!r}")
            if norm(text) in sentences:
                errors.append(f"{cid}: repeated sentence: {text!r}")
            sentences.add(norm(text))
    blob = json.dumps(CARDS, ensure_ascii=False)
    for bad in ("<", ">", "&", "//", "\\"):
        if bad in blob.replace("\\\"", ""):
            errors.append(f"forbidden character sequence {bad!r} in card text (breaks inline scripts or wpautop)")
    missing = sorted(set(qs) - set(covered))
    if missing:
        errors.append(f"test questions without a card: {missing}")
    n_items = sum(len(c["check"]) + len(c["prac"]) for c in CARDS)
    if errors:
        print("\n".join(errors))
        sys.exit(1)
    print(f"ok: {len(CARDS)} cards, {n_items} questions, all 40 test items covered once, no test sentence reused")


if __name__ == "__main__":
    main()
