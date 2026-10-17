"""Builds the "Seviye testim" block for /panel (page 5402) and the full page content.

    python3 level-test/panel/build_panel.py <current-panel-content.html> <out.html>

The block is added after the existing [bai_panel] shortcode block, which stays byte for byte.
Questions and level names come from the level-test page (staging/4011-seviye-testi-40.html), and the placement
rule from patches.PLACE_JS, so the panel always scores exactly like the test.
"""
import json
import os
import re
import sys

PANEL = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(PANEL)
sys.path.insert(0, BASE)
from cards import CARDS  # noqa: E402
from patches import PLACE_JS  # noqa: E402

START = "<!-- bai:seviye-testim -->"
END = "<!-- /bai:seviye-testim -->"


def test_data():
    page = open(os.path.join(BASE, "staging", "4011-seviye-testi-40.html"), encoding="utf-8").read()
    qs = json.loads(re.search(r"var QUESTIONS = (\[.*?\]);", page, re.S).group(1))
    meta = {}
    for lv, name, title in re.findall(r'(A1|A2|B1|B2|C1|C2):\{name:"([^"]+)",title:"([^"]+)"', page):
        meta[lv] = {"name": name, "title": title}
    if len(meta) != 6:
        raise SystemExit("could not read the six level names from the test page")
    return [{"id": q["id"], "level": q["level"], "prompt": q["prompt"], "options": q["options"], "answer": q["answer"]} for q in qs], meta


def strip_comments(src):
    return re.sub(r"/\*.*?\*/", "", src, flags=re.S)


def one_line(src):
    return " ".join(line.strip() for line in src.splitlines() if line.strip())


def build_block():
    qs, meta = test_data()
    cards = []
    for c in CARDS:
        cards.append({
            "id": c["id"], "level": c["level"], "items": c["items"], "lead": c["lead"],
            "t_tr": c["t_tr"], "t_en": c["t_en"], "tr": c["tr"], "en": c["en"], "pat": c["pat"], "ex": c["ex"],
            "check": [list(q) for q in c["check"]], "prac": [list(q) for q in c["prac"]],
        })
    data = json.dumps({"q": qs, "meta": meta, "cards": cards}, ensure_ascii=False, separators=(",", ":"))
    data = data.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    js = one_line(strip_comments(open(os.path.join(PANEL, "bai-ltp.js"), encoding="utf-8").read()))
    if js.count("__DATA__") != 1 or js.count("__PLACE_JS__") != 1:
        raise SystemExit("placeholders missing in bai-ltp.js")
    js = js.replace("__PLACE_JS__", PLACE_JS.strip()).replace("__DATA__", data)
    css = one_line(strip_comments(open(os.path.join(PANEL, "bai-ltp.css"), encoding="utf-8").read()))
    check_script_safety(js, "js")
    check_script_safety(css, "css")
    return (
        START + '<section id="seviye-testim" class="bai-ltp" aria-label="Seviye testim" hidden></section>'
        + '<style id="bai-ltp-css">' + css + "</style>"
        + '<script id="bai-ltp-js">' + js + "</script>" + END
    )


def check_script_safety(code, kind):
    problems = []
    if "&" in code:
        problems.append("ampersand")
    if "//" in code:
        problems.append("double slash")
    if re.search(r"<[A-Za-z/!]", code):
        problems.append("tag-like '<'")
    if "\n" in code:
        problems.append("line break")
    if problems:
        raise SystemExit(f"{kind}: unsafe for an inline block: {', '.join(problems)}")


def merge(current, block):
    wrapped = "<!-- wp:html -->" + block + "<!-- /wp:html -->"
    if START in current:
        pre = current[: current.index(START)]
        post = current[current.index(END) + len(END):]
        # the old block is wrapped in wp:html markers: drop the opening one at the end of pre and the closing one at the start of post
        if not (pre.endswith("<!-- wp:html -->") and post.startswith("<!-- /wp:html -->")):
            raise SystemExit("existing Seviye testim block is not wrapped as expected; not touching the page")
        return pre[: -len("<!-- wp:html -->")] + wrapped + post[len("<!-- /wp:html -->"):]
    if "[bai_panel]" not in current:
        raise SystemExit("[bai_panel] shortcode not found; refusing to build")
    return current.rstrip("\n") + "\n\n" + wrapped + "\n"


if __name__ == "__main__":
    current = open(sys.argv[1], encoding="utf-8").read()
    out = merge(current, build_block())
    open(sys.argv[2], "w", encoding="utf-8").write(out)
    print(f"built {sys.argv[2]}: {len(out)} bytes (block {len(out) - len(current)} bytes added)")
