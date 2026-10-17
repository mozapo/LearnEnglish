"""Item analysis of the anonymous level-test records (PLAN.md §1, step 3).

    python3 level-test/tools/analyze_stats.py                 # live data
    python3 level-test/tools/analyze_stats.py --staging
    python3 level-test/tools/analyze_stats.py --file data.json   # a saved export, or synthetic data for testing
    python3 level-test/tools/analyze_stats.py --demo             # synthetic learners, to check the script

Reads GET /wp-json/bai/v1/lt-stats (administrators only) and reports:
  - how many usable tests there are (too-fast ones, under 90 seconds, are left out as not genuine)
  - per question: % correct, % "I don't know", discrimination (corrected item-total correlation), the most
    chosen wrong option, and flags for questions to review
  - level distribution under the current rule, and how many scores sit next to each cut point
  - Rasch item difficulties (simple JMLE) per question, checked against the level each question is meant to test
Unanswered questions after an early finish ("x") count as wrong for the score, as on the site, but are left
out of the per-question statistics. No personal data exists in these records.
"""
import argparse
import json
import math
import os
import re
import statistics
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]
CUTS = [0, 17, 23, 28, 33, 36]
MIN_SECONDS = 90


def questions():
    page = open(os.path.join(BASE, "staging", "4011-seviye-testi-40.html"), encoding="utf-8").read()
    return json.loads(re.search(r"var QUESTIONS = (\[.*?\]);", page, re.S).group(1))


def fetch(staging):
    url = os.environ["WP_STAGING_URL" if staging else "WP_URL"]
    pw = os.environ["WP_STAGING_APP_PASSWORD" if staging else "WP_APP_PASSWORD"]
    out = subprocess.run(["curl", "-sS", "-u", os.environ["WP_USER"] + ":" + pw, url + "/wp-json/bai/v1/lt-stats"],
                         capture_output=True, check=True).stdout
    return json.loads(out)


def place(correct, per_level, qs):
    totals = [sum(1 for q in qs if q["level"] == lv) for lv in LEVELS]
    lvl = max([0] + [i for i in range(1, 6) if correct >= CUTS[i]])
    floor = -1
    for i in range(6):
        if per_level[i] >= totals[i] - 1:
            floor = i
        else:
            break
    return max(lvl, floor)


def demo_records(qs, n=400):
    import random
    random.seed(3)
    center = {"A1": -2.5, "A2": -1.5, "B1": -0.5, "B2": 0.5, "C1": 1.5, "C2": 2.5}
    recs = []
    for _ in range(n):
        th = random.uniform(-3.5, 3.5)
        code = "120261101"
        for q in qs:
            p = 1 / (1 + math.exp(-(th - center[q["level"]])))
            if random.random() < p:
                code += str(q["answer"])
            elif random.random() < 0.5:
                code += "4"
            else:
                code += str(random.choice([i for i in range(4) if i != q["answer"]]))
        recs.append({"at": "2026-11-01 10:00:00", "code": code, "d": random.randint(300, 1100), "e": 0})
    return recs


def corr(xs, ys):
    if len(xs) < 3:
        return float("nan")
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return float("nan") if sx == 0 or sy == 0 else sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy)


def rasch(matrix, iters=60):
    """Joint maximum likelihood for complete-ish 0/1 data (None = missing). Returns item difficulties (logits)."""
    n_items = len(matrix[0])
    rows = [r for r in matrix if 0 < sum(v for v in r if v is not None) < sum(1 for v in r if v is not None)]
    if len(rows) < 30:
        return None
    theta = [0.0] * len(rows)
    b = [0.0] * n_items
    for _ in range(iters):
        for i in range(n_items):
            num, den = 0.0, 0.0
            for r, t in zip(rows, theta):
                if r[i] is None:
                    continue
                p = 1 / (1 + math.exp(-(t - b[i])))
                num += r[i] - p
                den += p * (1 - p)
            if den:
                b[i] -= num / den
        mean_b = statistics.fmean(b)
        b = [x - mean_b for x in b]
        for k, r in enumerate(rows):
            num, den = 0.0, 0.0
            for i, v in enumerate(r):
                if v is None:
                    continue
                p = 1 / (1 + math.exp(-(theta[k] - b[i])))
                num += v - p
                den += p * (1 - p)
            if den:
                theta[k] = max(-6, min(6, theta[k] + num / den))
    return b


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--staging", action="store_true")
    ap.add_argument("--file")
    ap.add_argument("--demo", action="store_true")
    a = ap.parse_args()
    qs = questions()
    if a.demo:
        recs = demo_records(qs)
    elif a.file:
        recs = json.load(open(a.file))
    else:
        recs = fetch(a.staging)

    usable = [r for r in recs if re.fullmatch(r"1\d{8}[0-4x]{%d}" % len(qs), r["code"]) and r["d"] >= MIN_SECONDS]
    print(f"records: {len(recs)}, usable: {len(usable)} (left out: {len(recs) - len(usable)} under {MIN_SECONDS}s or malformed)")
    if not usable:
        return
    print(f"early finish: {sum(r['e'] for r in usable) / len(usable):.0%} · median duration: {statistics.median(r['d'] for r in usable) / 60:.1f} min")
    if len(usable) < 300:
        print(f"NOTE: {len(usable)} usable tests. Item statistics are only indicative below ~300.")

    answers = [[None if ch == "x" else int(ch) for ch in r["code"][9:]] for r in usable]
    scored = [[None if a_ is None else int(a_ == q["answer"]) for a_, q in zip(row, qs)] for row in answers]
    totals = [sum(v or 0 for v in row) for row in scored]

    print("\nlevel distribution (current rule):")
    dist = [0] * 6
    near = [0] * 6
    for row, tot in zip(scored, totals):
        per = [sum(row[i] or 0 for i, q in enumerate(qs) if q["level"] == lv) for lv in LEVELS]
        lv = place(tot, per, qs)
        dist[lv] += 1
        if lv < 5 and CUTS[lv + 1] - tot == 1:
            near[lv + 1] += 1
    for i, lv in enumerate(LEVELS):
        print(f"  {lv}: {dist[i]:4d} ({dist[i] / len(usable):.0%})" + (f"   one point below the {lv} cut: {near[i]}" if i else ""))

    b = rasch(scored)
    print("\nper question (flag: too easy/hard for its level, weak discrimination, popular wrong option):")
    print("  id lvl  correct  idk   discr  rasch  most-chosen wrong     flags")
    flags_total = 0
    for i, q in enumerate(qs):
        col = [(row[i], tot) for row, tot in zip(scored, totals) if row[i] is not None]
        if not col:
            continue
        p = statistics.fmean(v for v, _ in col)
        idk = statistics.fmean(1 if row[i] == 4 else 0 for row in answers if row[i] is not None)
        disc = corr([v for v, _ in col], [t - v for v, t in col])
        wrong = {}
        for row in answers:
            if row[i] is not None and row[i] not in (q["answer"], 4):
                wrong[row[i]] = wrong.get(row[i], 0) + 1
        top = max(wrong, key=wrong.get) if wrong else None
        top_share = wrong[top] / len(col) if top is not None else 0
        flags = []
        if disc == disc and disc < 0.2:
            flags.append("weak discrimination")
        if top_share > p and top is not None:
            flags.append("wrong option beats the key")
        lvl_i = LEVELS.index(q["level"])
        if b is not None:
            expected = [-2.5, -1.5, -0.5, 0.5, 1.5, 2.5][lvl_i]
            if abs(b[i] - expected) > 1.2:
                flags.append("difficulty off for its level")
        flags_total += bool(flags)
        rb = f"{b[i]:+.1f}" if b is not None else "  -"
        top_txt = (q["options"][top][:16] + f" {top_share:.0%}") if top is not None else "-"
        print(f"  {q['id']:2d} {q['level']}  {p:6.0%}  {idk:5.0%}  {disc:5.2f}  {rb:>5}  {top_txt:20s}  {', '.join(flags)}")
    print(f"\nquestions to review: {flags_total}. Rewrite or replace flagged items before resetting the cut points.")
    if b is None:
        print("Rasch difficulties need at least 30 tests with a mixed score.")


if __name__ == "__main__":
    main()
