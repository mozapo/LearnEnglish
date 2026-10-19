"""Apply the SEO audit fixes to staging or live, or roll them back.

    python3 seo/publish.py staging content A          # content patch group A (see content_patches.py)
    python3 seo/publish.py staging meta               # SureRank titles/descriptions/robots (seo_meta.py)
    python3 seo/publish.py live content A --yes       # live only after the owner approved that group
    python3 seo/publish.py staging content A --rollback
    python3 seo/publish.py live restore --only 5518 --yes   # page content back to the 19 Oct backup

Content: a page is written only if its current text is the known original (every old string present the expected
number of times) or already patched. Afterwards the stored text must equal the build, and LiteSpeed is purged.
Meta: each SureRank field is written only if it still holds the value recorded in seo_meta.py (BEFORE) or already
holds the new value. Rollback restores BEFORE. Credentials come from the environment and are never printed.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import content_patches  # noqa: E402
import seo_meta  # noqa: E402
import wp  # noqa: E402


def field_get(page, field):
    return page["content"]["raw"] if field == "content" else page["meta"].get("_elementor_data") or ""


def field_body(field, text):
    return {"content": text} if field == "content" else {"meta": {"_elementor_data": text}}


def build(text, patches, reverse=False):
    for _, old, new, n in patches:
        a, b = (new, old) if reverse else (old, new)
        if reverse and new == "":
            raise SystemExit("cannot roll back a deletion by string; restore from seo/backup instead")
        if text.count(a) != n:
            return None
        text = text.replace(a, b)
    return text


def purge(target):
    # Elementor serves cached element output until its cache is cleared (same as Tools > Clear Files & Data).
    wp.session(target).delete(wp.base(target) + "/wp-json/elementor/v1/cache", timeout=120).raise_for_status()
    wp.api(target, "POST", "/wp-abilities/v1/abilities/hostinger-ai/litespeed-cache-flush/run", json={"input": {}})


def content(target, group, rollback):
    for pid, patches in content_patches.GROUPS[group].items():
        page = wp.api(target, "GET", f"/wp/v2/pages/{pid}?context=edit")
        for field in sorted({p[0] for p in patches}):
            ps = [p for p in patches if p[0] == field]
            cur = field_get(page, field)
            if rollback:
                done = build(cur, ps, reverse=True)
                if done is None:
                    print(f"{pid} {field}: not in the patched state, left alone")
                    continue
            else:
                # Patched: each new text is present and the old text no longer appears outside it.
                if all((not new or new in cur) and old not in (cur.replace(new, "") if new else cur) for _, old, new, _ in ps):
                    print(f"{pid} {field}: already patched")
                    continue
                done = build(cur, ps)
                if done is None:
                    sys.exit(f"{pid} {field}: page is not in the known state; nothing sent")
            wp.api(target, "POST", f"/wp/v2/pages/{pid}", json=field_body(field, done))
            stored = field_get(wp.api(target, "GET", f"/wp/v2/pages/{pid}?context=edit"), field)
            if stored != done:
                sys.exit(f"{pid} {field}: stored text differs from the build; check the page")
            print(f"{pid} {field}: {'rolled back' if rollback else 'patched'} and verified")
    purge(target)
    print("LiteSpeed cache purged")


def restore(target, pids):
    """Put back post_content and _elementor_data from the backup taken on 19 Oct 2026 (before any change)."""
    import gzip, json
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backup", f"{target}-2026-10-19.json.gz")
    pages = {p["id"]: p for p in json.load(gzip.open(path, "rt", encoding="utf-8"))["pages"]}
    for pid in pids:
        old = pages[pid]
        body = {"content": old["content"]["raw"]}
        if old["meta"].get("_elementor_data"):
            body["meta"] = {"_elementor_data": old["meta"]["_elementor_data"]}
        wp.api(target, "POST", f"/wp/v2/pages/{pid}", json=body)
        now = wp.api(target, "GET", f"/wp/v2/pages/{pid}?context=edit")
        ok = now["content"]["raw"] == old["content"]["raw"] and \
            (now["meta"].get("_elementor_data") or "") == (old["meta"].get("_elementor_data") or "")
        print(f"{pid}: {'restored from backup and verified' if ok else 'RESTORE MISMATCH, check the page'}")
    purge(target)


def meta(target, rollback, only=None):
    s = wp.session(target)
    url = wp.base(target) + "/wp-json/surerank/v1/post/settings"
    for pid, (ptype, before, after) in seo_meta.CHANGES.items():
        if only and pid not in only:
            continue
        want, expect = (before, after) if rollback else (after, before)
        cur = s.get(url, params={"post_id": pid, "post_type": ptype}, timeout=60).json()["data"]
        if all(cur.get(k) == v for k, v in want.items()):
            print(f"{pid}: already {'original' if rollback else 'updated'}")
            continue
        wrong = {k: cur.get(k) for k, v in expect.items() if cur.get(k) != v and cur.get(k) != want[k]}
        if wrong:
            print(f"{pid}: changed by someone else, skipped: {wrong}")
            continue
        r = s.post(url, json={"post_id": pid, "metaData": want}, timeout=60)
        r.raise_for_status()
        cur = s.get(url, params={"post_id": pid, "post_type": ptype}, timeout=60).json()["data"]
        bad = {k: cur.get(k) for k, v in want.items() if cur.get(k) != v}
        print(f"{pid}: {'FAILED ' + str(bad) if bad else 'written and verified'}")
    purge(target)
    print("LiteSpeed cache purged")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", choices=["staging", "live"])
    ap.add_argument("what", choices=["content", "meta", "restore"])
    ap.add_argument("group", nargs="?")
    ap.add_argument("--only", type=int, nargs="*")
    ap.add_argument("--rollback", action="store_true")
    ap.add_argument("--yes", action="store_true")
    a = ap.parse_args()
    if a.target == "live" and not a.yes:
        sys.exit("live needs --yes (and the owner's approval for this change)")
    if a.what == "restore":
        restore(a.target, a.only or [])
    elif a.what == "content":
        content(a.target, a.group, a.rollback)
    else:
        meta(a.target, a.rollback, a.only)


if __name__ == "__main__":
    main()
