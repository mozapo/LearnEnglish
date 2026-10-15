#!/usr/bin/env python3
"""Build the "Teacher Academy – Preview" page content.

Takes the untouched hub HTML in original/ and inserts the new .bai-ta sections, CSS and JS at
fixed anchors. Output: dist/teacher-academy-preview.html, ready to be used as page content.

Usage: python3 teacher-academy/build.py
"""
import json
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ORIGINAL = HERE / "original" / "egitmen-akademisi-4358.html"
OUT = HERE / "dist" / "teacher-academy-preview.html"

# Module titles, ledes and read times are copied from the live module pages.
MODS = [
    (1, "Öğrenen Kim?", 14, "modul-1-ogrenen-kim",
     "İyi öğretmenin başladığı yer konu değil, karşındaki insandır. Bu modül, ilk dersten önce ve ilk dersin içinde öğrenenini nasıl gerçekten tanıyacağını anlatır."),
    (2, "Öğrenme Nasıl Çalışır?", 16, "modul-2-ogrenme-nasil-calisir",
     "Öğrenme sezgisel değildir. İyi hissettiren çoğu çalışma yöntemi işe yaramaz; işe yarayan yöntemlerin çoğu zor hissettirir."),
    (3, "Dersi Tasarlamak", 15, "modul-3-dersi-tasarlamak",
     "Hazırlıksız ders, sohbet olur. İyi bir ders bir başlangıcı, bir yükselişi ve bir kapanışı olan tasarlanmış bir yapıdır."),
    (4, "Motivasyon ve Psikolojik Güvenlik", 17, "modul-4-motivasyon-ve-psikolojik-guvenlik",
     "Öğrenenlerin çoğu yeteneksiz olduğu için değil, güvende hissetmediği için ilerlemez."),
    (5, "Yaş Gruplarını Anlamak", 16, "modul-5-yas-gruplarini-anlamak",
     "Yedi yaşındaki bir çocuk, on beş yaşındaki bir ergen ve kırk yaşındaki bir profesyonel aynı yöntemle öğrenmez. Aynı içerik, üç farklı ders demektir."),
    (6, "Geri Bildirim ve Değerlendirme", 15, "modul-6-geri-bildirim-ve-degerlendirme",
     "Geri bildirimin amacı yapılmış işi puanlamak değil, bir sonraki işi daha iyi yapabilmeyi sağlamaktır."),
    (7, "Zor Anlar", 17, "modul-7-zor-anlar",
     "Kapanan öğrenen, araya giren veli, duran ilerleme, ve bir öğrenenin sana zor bir şey anlattığı an."),
    (8, "Kapsayıcılık, Etik ve Güvenlik", 16, "modul-8-kapsayicilik-etik-guvenlik",
     "İyi öğretmenlik yalnızca etkili olmak değil, güvenli ve adil olmaktır: mesleki sınırlar, çocuk güvenliği ve veri sorumluluğu."),
    (9, "Çevrimiçi Öğretmek", 18, "modul-9-cevrimici-ogretmek",
     "Çevrimiçi ders, ekrana taşınmış yüz yüze ders değildir: bakış, dikkat, ortam ve güven burada başka kurallarla çalışır."),
    (10, "Profesyonellik ve İş Ahlakı", 17, "modul-10-profesyonellik-ve-is-ahlaki",
     "Zamanında gelmek, hazırlıklı olmak, sözünü tutmak ve hata yaptığında sahiplenmek de mesleğin parçasıdır."),
]

# Self-reflection quiz. "m" lists the modules an answer points to; the first one weighs double.
QUIZ = [
    {"q": "Yeni bir öğrenenle ilk dersinde en çok neyi merak edersin?", "o": [
        {"t": "Söylediği hedefin altında gerçekte neye ihtiyaç duyduğunu", "m": [1]},
        {"t": "Öğrendiklerini nasıl kalıcı hâle getireceğini", "m": [2]},
        {"t": "Kırk dakikayı nasıl bir akışla kuracağımı", "m": [3]},
        {"t": "Kendini rahat ve güvende hissedip hissetmediğini", "m": [4]}]},
    {"q": "Hangisi sana daha zor gelir?", "o": [
        {"t": "Aynı konuyu yedi yaşındaki bir çocuğa ve bir yetişkine anlatmak", "m": [5]},
        {"t": "Hatayı düzeltirken öğrenenin hevesini kırmamak", "m": [6, 4]},
        {"t": "Ders ortasında kapanan ya da zorlanan bir öğrenenle kalmak", "m": [7]},
        {"t": "Ekran başında dikkati ve teması canlı tutmak", "m": [9]}]},
    {"q": "Bir öğrenenin ilerlemesi durdu. İlk adımın ne olur?", "o": [
        {"t": "Nasıl çalıştığını ve neyi nasıl tekrar ettiğini incelerim", "m": [2]},
        {"t": "İlerlemeyi nasıl ölçtüğümü gözden geçiririm", "m": [6]},
        {"t": "Onunla, gerekirse velisiyle açıkça konuşurum", "m": [7]},
        {"t": "Ders planımı baştan kurarım", "m": [3]}]},
    {"q": "Bir eğitmen olarak seni en çok ne düşündürür?", "o": [
        {"t": "Her öğrenenin kendini derse ait hissetmesi", "m": [8, 4]},
        {"t": "Mesleki sınırlarımı doğru çizmek", "m": [8, 7]},
        {"t": "Zamanında, hazırlıklı ve sözümde durarak çalışmak", "m": [10]},
        {"t": "Karşımdaki insanın gerçek hikâyesini anlamak", "m": [1]}]},
    {"q": "En çok hangi öğrenenlerle çalışmak istiyorsun?", "o": [
        {"t": "Çocuklar", "m": [5, 8]},
        {"t": "Gençler", "m": [5, 4]},
        {"t": "Yetişkinler ve profesyoneller", "m": [5, 1]},
        {"t": "Çevrim içi, farklı yaşlardan öğrenenler", "m": [9, 5]}]},
]

# Each new block goes right before (or after) an exact string in the original HTML.
ANCHORS = [
    ("journey",   "after",  '<hr class="bai-ac__rule">'),
    ("framework", "after",  "</span></li></ul>" + '<div class="bai-ac__sec bai-ac__rv"><h2>Bu program neyi değiştirir?</h2>'),
    ("quiz",      "before", '<div class="bai-ac__sec bai-ac__rv"><h2>Program</h2>'),
    ("roadmap",   "before", '<div class="bai-ac__sec bai-ac__rv"><h2>Program</h2>'),
    ("minutes",   "before", '<div class="bai-ac__sec bai-ac__rv"><h2>Sertifika ve rozet</h2>'),
    ("exam",      "before", '<div class="bai-ac__sec bai-ac__rv"><h2>Sık sorulanlar</h2>'),
    ("path",      "before", '<div class="bai-ac__sec bai-ac__rv"><h2>Sık sorulanlar</h2>'),
]


def ring_segments():
    out = []
    for i in range(10):
        a0, a1 = math.radians(i * 36 + 3), math.radians(i * 36 + 33)
        x0, y0 = 60 + 50 * math.cos(a0), 60 + 50 * math.sin(a0)
        x1, y1 = 60 + 50 * math.cos(a1), 60 + 50 * math.sin(a1)
        out.append(f'<path data-i="{i + 1}" d="M{x0:.2f} {y0:.2f}A50 50 0 0 1 {x1:.2f} {y1:.2f}"/>')
    return "".join(out)


def minute_rows():
    rows = []
    for i, (n, title, mins, _slug, _d) in enumerate(MODS):
        rows.append(
            f'<li data-m="{n}" style="--w:{mins / 18 * 100:.1f}%;--i:{i}">'
            f'<span class="bai-ta-chart__lab"><b>{n}</b>{title}</span>'
            f'<span class="bai-ta-chart__bar" aria-hidden="true"><i></i></span>'
            f'<span class="bai-ta-chart__val">{mins} dk</span></li>')
    return "".join(rows)


def minify_html(s):
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    s = re.sub(r">\s+<", "><", s)
    return re.sub(r"\s*\n\s*", " ", s).strip()


def minify_css(s):
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    s = re.sub(r"\s*\n\s*", "", s)
    return re.sub(r"\s*([{};])\s*", r"\1", s).strip()


def minify_js(s):
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    return " ".join(line.strip() for line in s.splitlines() if line.strip())


def json_for_script(obj):
    s = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    return s.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")


def check_wp_safe(name, s):
    """WordPress content filters mangle these inside inline scripts; the original avoids them too."""
    bad = [t for t in ("&&", "\n", "//") if t in s]
    if re.search(r"<[A-Za-z/!]", s):
        bad.append("<tag-like")
    if bad:
        sys.exit(f"build: {name} contains WordPress-unsafe sequences: {bad}")


def main():
    original = ORIGINAL.read_text(encoding="utf-8")
    parts = {}
    src = (HERE / "src" / "sections.html").read_text(encoding="utf-8")
    for m in re.finditer(r"<!-- @section (\w+) -->(.*?)(?=<!-- @section |\Z)", src, flags=re.S):
        parts[m.group(1)] = minify_html(m.group(2))
    parts["roadmap"] = parts["roadmap"].replace("{{RING_SEGMENTS}}", ring_segments())
    parts["minutes"] = parts["minutes"].replace("{{MINUTE_ROWS}}", minute_rows())
    parts["exam"] = parts["exam"].replace("{{POOL_CELLS}}", "<i></i>" * 64)

    html = original
    for name, where, anchor in ANCHORS:
        if html.count(anchor) != 1:
            sys.exit(f"build: anchor for '{name}' found {html.count(anchor)} times, expected 1")
        if where == "after":
            html = html.replace(anchor, anchor + parts[name])
        else:
            html = html.replace(anchor, parts[name] + anchor)

    css = minify_css((HERE / "src" / "bai-ta.css").read_text(encoding="utf-8"))
    js = minify_js((HERE / "src" / "bai-ta.js").read_text(encoding="utf-8"))
    data = json_for_script({
        "mods": [{"n": n, "t": t, "min": mins, "u": f"/egitmen-akademisi/{slug}/", "d": d}
                 for n, t, mins, slug, d in MODS],
        "quiz": QUIZ,
    })
    check_wp_safe("bai-ta.js", js)
    check_wp_safe("bai-ta-data", data)

    first_style_end = html.index("</style>") + len("</style>")
    html = html[:first_style_end] + f'<style id="bai-ta-css">{css}</style>' + html[first_style_end:]
    html += (f'<script type="application/json" id="bai-ta-data">{data}</script>'
             f'<script id="bai-ta-js">{js}</script>')

    if "\n" in html:
        sys.exit("build: output contains a newline; wpautop would add <p>/<br> tags")
    if re.search(r"\{\{[A-Z_]+\}\}", html):
        sys.exit("build: unreplaced placeholder left in output")
    # The original hub markup must survive untouched: removing our additions gives it back.
    stripped = re.sub(r'<style id="bai-ta-css">.*?</style>', "", html, flags=re.S)
    stripped = re.sub(r'<script type="application/json" id="bai-ta-data">.*?</script><script id="bai-ta-js">.*?</script>$', "", stripped, flags=re.S)
    for name, _w, _a in ANCHORS:
        stripped = stripped.replace(parts[name], "", 1)
    if stripped != original:
        sys.exit("build: original hub markup was altered")

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(f"build: wrote {OUT.relative_to(HERE.parent)} ({len(html):,} bytes; additions {len(html) - len(original):,} bytes)")


if __name__ == "__main__":
    main()
