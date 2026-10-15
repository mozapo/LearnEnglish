#!/usr/bin/env python3
"""Build the Teacher Academy page content (Turkish /egitmen-akademisi or English /en/educator-academy).

Takes the untouched hub HTML in original/ and inserts the new .bai-ta sections, CSS and JS at
fixed anchors. Output goes to dist/, ready to be used as page content.

Usage: python3 teacher-academy/build.py [--lang tr|en] [--live]
  --lang  tr (default): page 4358 · en: page 4359
  --live  build on the live page content instead of the staging copy (keeps live URLs)
"""
import html as html_lib
import json
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIVE = "--live" in sys.argv
LANG = sys.argv[sys.argv.index("--lang") + 1] if "--lang" in sys.argv else "tr"

# Module titles, read times and ledes come from the live module pages (ledes quoted, some cut to their first sentences).
MODS_TR = [
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
     "Her eğitmenin karşılaştığı ama hiçbir müfredatın anlatmadığı anlar: kapanan öğrenen, araya giren veli, duran ilerleme, ve bir öğrenenin sana zor bir şey anlattığı an."),
    (8, "Kapsayıcılık, Etik ve Güvenlik", 16, "modul-8-kapsayicilik-etik-guvenlik",
     "İyi öğretmenlik yalnızca etkili olmak değil, güvenli ve adil olmaktır. Bu modül farklı öğrenen profillerini, mesleki sınırları, çocuk güvenliğini ve veri sorumluluğunu kapsar."),
    (9, "Çevrimiçi Öğretmek", 18, "modul-9-cevrimici-ogretmek",
     "Çevrimiçi ders, ekrana taşınmış yüz yüze ders değildir: bakış, dikkat, ortam ve güven burada başka kurallarla çalışır."),
    (10, "Profesyonellik ve İş Ahlakı", 17, "modul-10-profesyonellik-ve-is-ahlaki",
     "Bir eğitmenin kalitesi yalnızca ders içindeki bilgisiyle ölçülmez. Zamanında gelmek, hazırlıklı olmak, sözünü tutmak, hata yaptığında sahiplenmek ve her öğrenene aynı özenle davranmak da mesleğin parçasıdır."),
]

# Self-reflection quiz. "m" lists the modules an answer points to; the first one weighs double.
QUIZ_TR = [
    {"q": "Yeni bir öğrenenle ilk dersinde en çok neyi merak edersin?", "o": [
        {"t": "Söylediği hedefin altında gerçekte neye ihtiyaç duyduğunu", "m": [1]},
        {"t": "Öğrendiklerini nasıl kalıcı hâle getireceğini", "m": [2]},
        {"t": "Kırk dakikayı nasıl bir akışla kuracağımı", "m": [3]},
        {"t": "Kendini rahat ve güvende hissedip hissetmediğini", "m": [4]}]},
    {"q": "Hangisi sana en zor gelir?", "o": [
        {"t": "Aynı konuyu yedi yaşındaki bir çocuğa ve bir yetişkine anlatmak", "m": [5]},
        {"t": "Hatayı düzeltirken öğrenenin hevesini kırmamak", "m": [6, 4]},
        {"t": "Ders ortasında kapanan ya da zorlanan bir öğrenenle ne yapacağını bilmek", "m": [7]},
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
def anchors(changes, programme, certificate, faq):
    sec = '<div class="bai-ac__sec bai-ac__rv"><h2>{}</h2>'.format
    return [
        ("journey",   "after",  '<hr class="bai-ac__rule">'),
        ("framework", "after",  "</span></li></ul>" + sec(changes)),
        ("quiz",      "before", sec(programme)),
        ("roadmap",   "before", sec(programme)),
        ("minutes",   "before", sec(certificate)),
        ("exam",      "before", sec(faq)),
        ("path",      "before", sec(faq)),
    ]


# English twin. Titles, read times and ledes are quoted from the live /en/educator-academy module pages.
MODS_EN = [
    (1, "Who Is the Learner?", 14, "module-1-who-is-the-learner",
     "Good teaching does not begin with the subject. It begins with the person in front of you. This module is about how to actually know your learner — before the first lesson, and inside it."),
    (2, "How Learning Works", 16, "module-2-how-learning-works",
     "Learning is counter-intuitive. Most study methods that feel good do not work, and most methods that work feel hard."),
    (3, "Designing a Session", 15, "module-3-designing-a-session",
     "An unplanned lesson becomes a conversation. A good lesson is a designed structure with an opening, a rise and a close."),
    (4, "Motivation & Psychological Safety", 17, "module-4-motivation-and-psychological-safety",
     "Most learners stall not because they lack ability but because they do not feel safe."),
    (5, "Understanding Age Groups", 16, "module-5-understanding-age-groups",
     "A seven-year-old, a fifteen-year-old and a forty-year-old professional do not learn the same way. The same content means three different lessons."),
    (6, "Feedback & Assessment", 15, "module-6-feedback-and-assessment",
     "The purpose of feedback is not to grade work already done but to make the next piece of work better."),
    (7, "Difficult Moments", 17, "module-7-difficult-moments",
     "The moments every educator meets and no syllabus covers: the learner who shuts down, the parent who intervenes, progress that stops, and the moment a learner tells you something hard."),
    (8, "Inclusion, Ethics & Safeguarding", 16, "module-8-inclusion-ethics-safeguarding",
     "Good teaching is not only effective teaching. It is safe and fair teaching. This module covers different learner profiles, professional boundaries, child protection and your responsibility for data."),
    (9, "Teaching Online", 18, "module-9-teaching-online",
     "An online lesson is not an in-person lesson moved to a screen: gaze, attention, setting and trust all work by different rules here."),
    (10, "Professionalism & Work Ethic", 17, "module-10-professionalism-and-work-ethic",
     "An educator's quality is not measured only by what they know inside the lesson. Arriving on time, being prepared, keeping your word, owning your mistakes and treating every learner with the same care are part of the job too."),
]

QUIZ_EN = [
    {"q": "In a first lesson with a new learner, what are you most curious about?", "o": [
        {"t": "What they really need beneath the goal they state", "m": [1]},
        {"t": "How to make what they learn stick", "m": [2]},
        {"t": "How to shape the forty minutes", "m": [3]},
        {"t": "Whether they feel comfortable and safe", "m": [4]}]},
    {"q": "Which of these do you find hardest?", "o": [
        {"t": "Explaining the same topic to a seven-year-old and to an adult", "m": [5]},
        {"t": "Correcting mistakes without dampening a learner's enthusiasm", "m": [6, 4]},
        {"t": "Knowing what to do when a learner shuts down or struggles mid-lesson", "m": [7]},
        {"t": "Keeping attention and connection alive on screen", "m": [9]}]},
    {"q": "A learner's progress has stalled. What is your first step?", "o": [
        {"t": "Look at how they study and what they review", "m": [2]},
        {"t": "Rethink how I measure progress", "m": [6]},
        {"t": "Talk openly with them, and with a parent if needed", "m": [7]},
        {"t": "Rebuild my lesson plan", "m": [3]}]},
    {"q": "As an educator, what do you think about most?", "o": [
        {"t": "Every learner feeling they belong in the lesson", "m": [8, 4]},
        {"t": "Drawing my professional boundaries well", "m": [8, 7]},
        {"t": "Being on time, prepared and true to my word", "m": [10]},
        {"t": "Understanding the real story of the person in front of me", "m": [1]}]},
    {"q": "Which learners do you most want to work with?", "o": [
        {"t": "Children", "m": [5, 8]},
        {"t": "Teenagers", "m": [5, 4]},
        {"t": "Adults and professionals", "m": [5, 1]},
        {"t": "Learners of different ages, online", "m": [9, 5]}]},
]

LANGS = {
    "tr": {
        "page": "egitmen-akademisi-4358", "out": "teacher-academy", "sections": "sections.html",
        "prefix": "/egitmen-akademisi/", "unit": "dk", "mods": MODS_TR, "quiz": QUIZ_TR,
        "anchors": anchors("Bu program neyi değiştirir?", "Program", "Sertifika ve rozet", "Sık sorulanlar"),
        "s": {"ring0": "henüz başlamadın", "ringAll": "tüm modüller tamamlandı", "ringOne": "{n} modül tamamlandı",
              "ringN": "{n} modül tamamlandı", "certReady": "Sertifikan hazır.", "pathN": "{n} / 10 modül tamamlandı.",
              "question": "Soru", "module": "Modül", "minRead": "dk okuma",
              "newPaper": "Yeni bir soru kâğıdı: 64 sorudan rastgele 30 soru seçildi."},
    },
    "en": {
        "page": "educator-academy-4359", "out": "educator-academy", "sections": "sections.en.html",
        "prefix": "/en/educator-academy/", "unit": "min", "mods": MODS_EN, "quiz": QUIZ_EN,
        "anchors": anchors("What this programme changes", "The programme", "Certificate and badge", "Frequently asked"),
        "s": {"ring0": "not started yet", "ringAll": "all modules complete", "ringOne": "{n} module complete",
              "ringN": "{n} modules complete", "certReady": "Your certificate is ready.", "pathN": "{n} / 10 modules complete.",
              "question": "Question", "module": "Module", "minRead": "min read",
              "newPaper": "New paper: 30 questions drawn at random from the 64-item bank."},
    },
}
L = LANGS[LANG]
ORIGINAL = HERE / "original" / (L["page"] + ("-live" if LIVE else "") + ".html")
OUT = HERE / "dist" / (L["out"] + ("-live" if LIVE else "-preview") + ".html")
ANCHORS = L["anchors"]


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
    for i, (n, title, mins, _slug, _d) in enumerate(L["mods"]):
        rows.append(
            f'<li data-m="{n}" style="--w:{mins / 18 * 100:.1f}%;--i:{i}">'
            f'<span class="bai-ta-chart__lab"><b>{n}</b>{html_lib.escape(title, quote=False)}</span>'
            f'<span class="bai-ta-chart__bar" aria-hidden="true"><i></i></span>'
            f'<span class="bai-ta-chart__val">{mins} {L["unit"]}</span></li>')
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


def check_wp_safe(name, s, is_js=False):
    """WordPress content filters mangle these inside inline scripts; the original avoids them too."""
    bad = [t for t in ("&&", "\n") + (("//",) if is_js else ()) if t in s]
    if re.search(r"<[A-Za-z/!]", s):
        bad.append("<tag-like")
    if bad:
        sys.exit(f"build: {name} contains WordPress-unsafe sequences: {bad}")


def main():
    original = ORIGINAL.read_text(encoding="utf-8")
    parts = {}
    src = (HERE / "src" / L["sections"]).read_text(encoding="utf-8")
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
        "lang": LANG,
        "s": L["s"],
        "mods": [{"n": n, "t": t, "min": mins, "u": f'{L["prefix"]}{slug}/', "d": d}
                 for n, t, mins, slug, d in L["mods"]],
        "quiz": L["quiz"],
    })
    hub_lang = json.loads(re.search(r'id="bai-ac-data"[^>]*>(.*?)</script>', original, flags=re.S).group(1))["lang"]
    if hub_lang != LANG:
        sys.exit(f"build: original page is the '{hub_lang}' hub, but --lang is '{LANG}'")
    check_wp_safe("bai-ta.js", js, is_js=True)
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
