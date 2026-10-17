"""Publish the level-test work to staging or live, or roll it back.

    python3 level-test/publish.py staging                 # build + push all pages to staging
    python3 level-test/publish.py live --yes              # same on live (only after explicit approval)
    python3 level-test/publish.py staging --rollback      # restore the backups taken on 17 Oct 2026
    python3 level-test/publish.py staging --only 4011     # one page

Pages: 4011 (/seviye-testi-40), 5402 (/panel), 2345 (/kvkk-aydinlatma-metni), 4066 (/cerez-politikasi).
Every page is built from its backup in backup/ (taken before any change this session). A page is written only if
its current content is a known state: the backup, an intermediate state we published, or the final build
(then nothing is sent). After writing, the saved content must equal the build byte for byte, and the public
page must show the change. Credentials come from the environment and are never printed.
"""
import argparse
import json
import os
import subprocess
import sys
import time

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
sys.path.insert(0, os.path.join(BASE, "panel"))
import patches  # noqa: E402
import legal_patches  # noqa: E402
import build_panel  # noqa: E402

DAY = "2026-10-17"
PAGES = {
    4011: ("seviye-testi-40", "/seviye-testi-40/", "bai/v1/lt-stat"),
    5402: ("panel", "/panel/", "bai-ltp-js"),
    2345: ("kvkk-aydinlatma-metni", "/kvkk-aydinlatma-metni/", "Sürüm 2.8"),
    4066: ("cerez-politikasi", "/cerez-politikasi/", "bai_lt_prog_v1"),
}


def env(target):
    if target == "live":
        return os.environ["WP_URL"], os.environ["WP_USER"] + ":" + os.environ["WP_APP_PASSWORD"]
    return os.environ["WP_STAGING_URL"], os.environ["WP_USER"] + ":" + os.environ["WP_STAGING_APP_PASSWORD"]


def api(target, method, path, body=None):
    url, auth = env(target)
    cmd = ["curl", "-sS", "-u", auth, "-X", method, url + path]
    data = None
    if body is not None:
        cmd += ["-H", "Content-Type: application/json", "--data-binary", "@-"]
        data = json.dumps(body).encode()
    out = subprocess.run(cmd, input=data, capture_output=True, check=True).stdout
    return json.loads(out)


def backup_name(target, pid):
    prefix = {4011: "seviye-testi-40", 5402: "panel", 2345: "kvkk-aydinlatma-metni", 4066: "cerez-politikasi"}[pid]
    return os.path.join(BASE, "backup", f"{target}-{pid}-{prefix}-{DAY}.html")


def states(target, pid):
    """(original, list of acceptable intermediate states, final build)."""
    base = open(backup_name(target, pid), encoding="utf-8").read()
    if pid == 4011:
        v1 = patches.apply(base, patches.FIXES_V1)
        v2 = patches.apply(v1, patches.FIXES_V2)
        return base, [v1, v2], patches.apply(v2, patches.FIXES_V3)
    if pid == 5402:
        return base, [], build_panel.merge(base, build_panel.build_block())
    if pid == 2345:
        v27 = patches.apply(base, legal_patches.KVKK)
        return base, [v27], patches.apply(v27, legal_patches.KVKK_V28)
    return base, [], patches.apply(base, legal_patches.CEREZ)


def strip_panel_block(content):
    s, e = build_panel.START, build_panel.END
    if s not in content:
        return content
    pre = content[: content.index(s)]
    post = content[content.index(e) + len(e):]
    return (pre[: -len("<!-- wp:html -->")] + post[len("<!-- /wp:html -->"):]).rstrip("\n").rstrip() if pre.endswith("<!-- wp:html -->") else content


def publish(target, pid, rollback):
    slug, path, marker = PAGES[pid]
    base, middle, final = states(target, pid)
    want = base if rollback else final
    page = api(target, "GET", f"/wp-json/wp/v2/pages/{pid}?context=edit")
    current = page["content"]["raw"]
    known = current in [base, final] + middle
    if pid == 5402 and not known:
        # an older build of the panel block: fine if the rest of the page is untouched
        known = strip_panel_block(current) == base.rstrip("\n").rstrip()
    if not known:
        raise SystemExit(f"{pid} {slug}: current content is not a known state (changed by someone else?). Nothing sent.")
    if current == want:
        print(f"{pid} {slug}: already up to date")
    else:
        saved = api(target, "POST", f"/wp-json/wp/v2/pages/{pid}?context=edit", {"content": want})
        if saved.get("content", {}).get("raw") != want:
            raise SystemExit(f"{pid} {slug}: saved content differs from the build. Check the page and roll back.")
        print(f"{pid} {slug}: {'restored' if rollback else 'published'} (modified {saved['modified']})")
    url, _ = env(target)
    for attempt in range(3):
        html = subprocess.run(["curl", "-sS", f"{url}{path}?nocache={int(time.time())}"], capture_output=True, check=True).stdout.decode()
        visible = marker in html
        if visible != rollback:
            print(f"   public page {'shows' if visible else 'no longer shows'} {marker!r}")
            return
        time.sleep(3)
    raise SystemExit(f"{pid} {slug}: public page does not reflect the change yet (cache?). Purge LiteSpeed and check.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", choices=["staging", "live"])
    ap.add_argument("--rollback", action="store_true")
    ap.add_argument("--yes", action="store_true", help="required for live")
    ap.add_argument("--only", type=int, choices=sorted(PAGES))
    a = ap.parse_args()
    if a.target == "live" and not a.yes:
        raise SystemExit("live needs --yes (and the owner's approval for this change)")
    for pid in ([a.only] if a.only else [4011, 5402, 2345, 4066]):
        publish(a.target, pid, a.rollback)


if __name__ == "__main__":
    main()
