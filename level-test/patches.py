"""Edits to the 40-question level test (page 4011), applied to the page content as exact replacements.

Each patch is a list of (old, new) pairs. Every `old` must occur exactly once, so a patch fails loudly
instead of half-applying when the page has changed.
"""

MILESTONES = [
    # One message per finished level (keyed by level, not by array index). About progress, not performance.
    (
        'var MILES = [ ["Harika bir başlangıç","Her yanıtla birlikte profilin netleşiyor."], ["Tempo çok iyi","Bir bölümü daha tamamladın. Gerçekten bildiğini seçmeye devam et."], ["Orta seviye bölgesi","Sorular zorlaşıyor \\u2014 yerleştirme tam da böyle isabetli hale gelir."], ["Yarı yoldasın","Odağını koru. \\u201cI don\'t know\\u201d, rastgele tahminden her zaman daha iyidir."], ["Çok iyi gidiyorsun","Şimdi testin daha ileri bölümüne giriyorsun."], ["İleri seviye meydan okuması","Karmaşık sorular B2, C1 ve C2 performansını ayırmaya yarar."], ["Son düzlük","Birkaç soru daha ve CEFR profilin hazır olacak."] ]; ',
        'var MILES = { A1:["İlk bölüm tamam","Profilin şekillenmeye başladı. Bilmediğin soruda “I don\'t know” seçmek, tahmin etmekten daha doğru bir sonuç verir."], A2:["İki bölüm geride kaldı","Sırada B1 var; sorular biraz zorlaşacak. Yerleştirme tam da burada netleşmeye başlar."], B1:["Yarı yoldasın","Sırada B2: daha uzun yapılar ve kalıplaşmış ifadeler. Kendi hızında devam et."], B2:["İleri seviye bölümü başlıyor","C1 ve C2 soruları ileri kullanıcıları ayırmak için var; zorlanman çok doğal. Emin değilsen “I don\'t know” seç ya da testi burada bitir."], C1:["Son bölüm","Birkaç soru kaldı. Bitirdiğinde CEFR profilin hazır olacak."] }; ',
    ),
    (
        'var i = Math.min(bandIndex(doneBand), MILES.length-1); $("bai-lq-mile-t").textContent = MILES[i][0]; $("bai-lq-mile-p").textContent = MILES[i][1]; $("bai-lq-mile-xp").textContent = doneBand + " bölümü tamamlandı · sırada " + nextBand;',
        'var msg = MILES[doneBand] ? MILES[doneBand] : MILES.C1; $("bai-lq-mile-t").textContent = msg[0]; $("bai-lq-mile-p").textContent = msg[1]; $("bai-lq-mile-xp").textContent = doneBand + " bölümü tamamlandı · " + nx + "/" + QUESTIONS.length + " soru · sırada " + nextBand;',
    ),
    ('<h2 id="bai-lq-mile-t">Harika gidiyorsun</h2>', '<h2 id="bai-lq-mile-t">İlk bölüm tamam</h2>'),
]

BADGE = [
    # "Certificate" -> level badge. The badge is the level title the test already had (META[level].title).
    (
        '<em id="bai-lq-lvl-name">Orta</em></div>',
        '<em id="bai-lq-lvl-name">Orta</em><div class="bai-lq__rozet"><small>Seviye rozetin</small><strong id="bai-lq-rozet">B1 İletişimci</strong></div></div>',
    ),
    (
        '$("bai-lq-lvl-name").textContent = META[r.placed].name;',
        '$("bai-lq-lvl-name").textContent = META[r.placed].name; $("bai-lq-rozet").textContent = META[r.placed].title;',
    ),
    ('id="bai-lq-print">Sertifikayı indir / yazdır</button>', 'id="bai-lq-print">Sonucunu yazdır / PDF kaydet</button>'),
    (
        '<p class="bai-lq__note" style="margin-top:18px">Bu bir seviye tahminidir; resmî bir Cambridge English sınavı ya da sertifikası değildir.</p>',
        '<p class="bai-lq__note" style="margin-top:18px">Bu bir seviye tahminidir. Rozet, bu testteki sonucunu gösterir; resmî bir belge değildir ve Cambridge English sınavı ya da sertifikası yerine geçmez.</p>',
    ),
    (
        'var txt = "Bir Adım İleri seviye testini tamamladım. Tahmini CEFR seviyem: " + lvl + ".";',
        'var txt = "Bir Adım İleri seviye testini tamamladım. Tahmini CEFR seviyem: " + lvl + " · rozetim: " + $("bai-lq-rozet").textContent + ".";',
    ),
    (
        '.bai-lq__level em{font-style:normal;font-size:1.08rem;color:var(--ink)}',
        '.bai-lq__level em{font-style:normal;font-size:1.08rem;color:var(--ink)}.bai-lq__rozet{display:flex;width:fit-content;flex-direction:column;align-items:center;gap:2px;margin:14px auto 0;padding:8px 18px;border-radius:999px;border:1px solid rgba(185,138,46,.45);background:rgba(185,138,46,.14)}.bai-lq__rozet small{font-size:.7rem;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}.bai-lq__rozet strong{color:var(--gold);font-size:1rem}',
    ),
]

FIXES_V1 = MILESTONES + BADGE

# Placement rule (PLAN.md §1). Shared verbatim by the test page and the "Seviye testim" section in /panel,
# so both always compute the same level. Total-score cut points per level (A1..C2), plus a floor: never below
# the highest level reached with every level up to it mastered (all but at most one item right).
# Returns [level index, index of the next level when the score is one point below its cut, else -1].
PLACE_JS = (
    "var LT_CUTS = [0,17,23,28,33,36]; "
    "function ltPlace(correct, perLevel){ var pi = 0, i; "
    "for(i=1; i < LT_CUTS.length; i++){ if(correct >= LT_CUTS[i]) pi = i; } "
    "var fl = -1; for(i=0; i < perLevel.length; i++){ if(perLevel[i][0] >= perLevel[i][1] - 1) fl = i; else break; } "
    "if(fl > pi) pi = fl; "
    "var near = -1; if(pi < LT_CUTS.length - 1){ if(LT_CUTS[pi+1] - correct === 1) near = pi + 1; } "
    "return [pi, near]; } "
)

PLACEMENT = [
    ("function calc(){ var byLevel = {}", PLACE_JS + "function calc(){ var byLevel = {}"),
    (
        'var placed = "A1"; for(i=0;i<ORDER.length;i++){ l = ORDER[i]; var band = byLevel[l]; var bandRate = band.correct / band.total; var lc = 0, lt = 0; for(var j=0;j<=i;j++){ lc += byLevel[ORDER[j]].correct; lt += byLevel[ORDER[j]].total; } var cum = lc / lt; if(bandRate >= 0.60 ? cum >= 0.60 : false) placed = l; }',
        'var pl = []; for(i=0;i<ORDER.length;i++) pl.push([byLevel[ORDER[i]].correct, byLevel[ORDER[i]].total]); var pr = ltPlace(correct, pl); var placed = ORDER[pr[0]]; var near = pr[1] >= 0 ? ORDER[pr[1]] : "";',
    ),
    ("confidence:confidence, placed:placed, byLevel:byLevel,", "confidence:confidence, placed:placed, near:near, byLevel:byLevel,"),
    (
        '<div class="bai-lq__rozet"><small>Seviye rozetin</small>',
        '<span class="bai-lq__near" id="bai-lq-near" hidden></span><div class="bai-lq__rozet"><small>Seviye rozetin</small>',
    ),
    (
        '$("bai-lq-rozet").textContent = META[r.placed].title;',
        '$("bai-lq-rozet").textContent = META[r.placed].title; var nearEl = $("bai-lq-near"); if(r.near){ nearEl.textContent = r.near + (r.near.charAt(1) === "1" ? "’e" : "’ye") + " çok yakın"; nearEl.hidden = false; } else { nearEl.textContent = ""; nearEl.hidden = true; }',
    ),
    (
        ".bai-lq__rozet{",
        ".bai-lq__near{display:block;margin-top:6px;font-size:.88rem;color:var(--gold)}.bai-lq__near[hidden]{display:none}.bai-lq__rozet{",
    ),
]

# "Hatalarınla çalış": the attempt is kept in this browser and handed to /panel in the link (?lt=…).
# Code format: "1" + yyyymmdd + one character per question ("0"–"4" = chosen option, "x" = not answered).
ACCOUNT_LINK = [
    (
        '<div class="bai-lq__panel bai-lq__rev">',
        '<div class="bai-lq__panel bai-lq__save"><h3>Hatalarınla çalış</h3><p>Ücretsiz hesabında yanlış yaptığın konuları kısa açıklamalar ve alıştırmalarla çalışabilir, seviye rozetini görebilirsin. Önce seviyene en uygun konular gelir.</p><a class="bai-lq__btn" id="bai-lq-save-link" href="/panel/#seviye-testim" data-bai-cta="level-test-practice">Hatalarımı hesabımda çalış</a><p class="bai-lq__note" style="margin-top:12px">Hesabın yoksa bir dakikada ücretsiz oluşturabilirsin. Sonucun bu tarayıcıda saklanır; başka bir cihazda devam etmek için <button type="button" class="bai-lq__linkbtn" id="bai-lq-copy">bağlantıyı kopyala</button> ve orada aç.</p></div>\n<div class="bai-lq__panel bai-lq__rev">',
    ),
    (
        "function finish(early){",
        'function attemptCode(){ var d = new Date(); var s = "1" + d.getFullYear() + (d.getMonth() + 1 > 9 ? "" : "0") + (d.getMonth() + 1) + (d.getDate() > 9 ? "" : "0") + d.getDate(); for(var i=0;i<state.answers.length;i++){ s += state.answers[i] === null ? "x" : String(state.answers[i]); } return s; } '
        'function saveAttempt(){ var code = attemptCode(); var url = "/panel/?lt=" + code + "#seviye-testim"; $("bai-lq-save-link").href = url; state.practiceUrl = location.origin + url; try{ localStorage.setItem("bai_lt_v1", JSON.stringify({ code:code, saved:Date.now() })); }catch(e){} } '
        "function finish(early){",
    ),
    ("var r = calc(); paint(r);", "var r = calc(); paint(r); saveAttempt();"),
    (
        '$("bai-lq-print").addEventListener("click", function(){ window.print(); });',
        '$("bai-lq-print").addEventListener("click", function(){ window.print(); }); '
        '$("bai-lq-save-link").addEventListener("click", function(){ track("level_test_practice_click",{}); }); '
        '$("bai-lq-copy").addEventListener("click", function(){ var u = state.practiceUrl ? state.practiceUrl : location.origin + "/panel/"; var box = $("bai-lq-status"); var done = function(){ box.className = "bai-lq__status is-ok"; box.textContent = "Bağlantı kopyalandı. Diğer cihazda açtığında sonucun hesabına gelir."; }; if(navigator.clipboard){ navigator.clipboard.writeText(u).then(done, function(){ box.className = "bai-lq__status"; box.textContent = u; }); } else { box.className = "bai-lq__status"; box.textContent = u; } });',
    ),
    (
        ".bai-lq__near{",
        ".bai-lq__save{border-color:rgba(185,138,46,.45)}.bai-lq__linkbtn{background:none;border:0;padding:0;color:var(--gold);text-decoration:underline;font:inherit;cursor:pointer}.bai-lq__near{",
    ),
    ("@media print{.bai-lq__acts,", "@media print{.bai-lq__save,.bai-lq__acts,"),
    # Children: results go to a parent (child-safety policy, KVKK §9).
    (
        '<button class="bai-lq__btn" type="submit">Teste başla</button>',
        '<p class="bai-lq__note" style="margin:0 0 14px">18 yaşından küçüksen testi velinle birlikte çöz ve velinin e-posta adresini yaz; sonuç o adrese gönderilir.</p>\n<button class="bai-lq__btn" type="submit">Teste başla</button>',
    ),
]

FIXES_V2 = PLACEMENT + ACCOUNT_LINK


def apply(content, patch):
    for old, new in patch:
        n = content.count(old)
        if n != 1:
            raise SystemExit("patch does not apply (found %d times): %s" % (n, old[:90]))
        content = content.replace(old, new)
    if "&&" in content:
        raise SystemExit("'&&' in content: wpautop/kses would break the inline script")
    return content

# Anonymous answer statistics (server/lt-stats.php, WPCode snippet 4012). Fire-and-forget: a failed or blocked
# request never affects the student. No name, e-mail or account is sent, only the answer code and timing.
STATS = [
    (
        "function saveAttempt(){",
        'function sendStat(r, early){ try{ fetch("/wp-json/bai/v1/lt-stat", { method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({ code: attemptCode(), d: r.durationSeconds, e: early ? 1 : 0 }), keepalive: true })["catch"](function(){}); }catch(e){} } '
        "function saveAttempt(){",
    ),
    ("paint(r); saveAttempt();", "paint(r); saveAttempt(); sendStat(r, early);"),
    (
        "sonuç o adrese gönderilir.</p>",
        "sonuç o adrese gönderilir. Testi geliştirmek için yanıtların adın ve e-postan olmadan, anonim olarak saklanır.</p>",
    ),
]

FIXES_V3 = STATS
