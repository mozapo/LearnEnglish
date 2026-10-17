"""Install server/lt-stats.php into WPCode snippet 4012 (PHP, Run Everywhere) on staging or live.

    python3 level-test/server/install.py staging
    python3 level-test/server/install.py live --yes
    python3 level-test/server/install.py staging --deactivate     # turn it off (status draft), code kept

Uses the Hostinger "cpt-update" ability (the only API route that can write WPCode snippets). That route runs
content through the HTML filter, so the snippet is written without angle brackets, ampersands or backslashes,
and this script refuses to send code containing them. After writing, the stored code must match the file.
The old content of 4012 (an inactive, obsolete level-test backend) is in backup/wpcode-4012-old-level-test-backend.php.
"""
import argparse, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SNIPPET = 4012
TITLE = "BAI - Seviye testi: anonim yanıt istatistiği (lt-stats)"


def env(t):
    if t == "live":
        return os.environ["WP_URL"], os.environ["WP_USER"] + ":" + os.environ["WP_APP_PASSWORD"]
    return os.environ["WP_STAGING_URL"], os.environ["WP_USER"] + ":" + os.environ["WP_STAGING_APP_PASSWORD"]


def ability(t, name, payload):
    url, auth = env(t)
    out = subprocess.run(["curl", "-sS", "-u", auth, "-X", "POST", "-H", "Content-Type: application/json",
                          "--data-binary", "@-", f"{url}/wp-json/wp-abilities/v1/abilities/{name}/run"],
                         input=json.dumps({"input": payload}).encode(), capture_output=True, check=True).stdout
    return json.loads(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", choices=["staging", "live"])
    ap.add_argument("--yes", action="store_true")
    ap.add_argument("--deactivate", action="store_true")
    a = ap.parse_args()
    if a.target == "live" and not a.yes:
        sys.exit("live needs --yes (and the owner's approval)")
    code = open(os.path.join(HERE, "lt-stats.php"), encoding="utf-8").read()
    for bad in ("<", ">", "&", "\\"):
        if bad in code:
            sys.exit(f"lt-stats.php contains {bad!r}; the installer would corrupt it")
    cur = ability(a.target, "hostinger-ai/cpt-get", {"post_type": "wpcode", "id": SNIPPET})
    title = cur.get("post_title", "")
    if not (title.startswith("BAI - Seviye Testi backend") or title == TITLE):
        sys.exit(f"snippet {SNIPPET} is not the expected one ({title!r}); nothing sent")
    status = "draft" if a.deactivate else "publish"
    res = ability(a.target, "hostinger-ai/cpt-update",
                  {"post_type": "wpcode", "id": SNIPPET, "title": TITLE, "content": code, "status": status})
    stored = ability(a.target, "hostinger-ai/cpt-get", {"post_type": "wpcode", "id": SNIPPET})
    if stored.get("post_content", "").replace("\r", "") != code:
        sys.exit("stored code differs from lt-stats.php; deactivate with --deactivate and check")
    print(f"snippet {SNIPPET} on {a.target}: {stored.get('post_status')} ({stored.get('post_modified')}), code matches the file")


if __name__ == "__main__":
    main()
