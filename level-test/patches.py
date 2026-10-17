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


def apply(content, patch):
    for old, new in patch:
        n = content.count(old)
        if n != 1:
            raise SystemExit("patch does not apply (found %d times): %s" % (n, old[:90]))
        content = content.replace(old, new)
    if "&&" in content:
        raise SystemExit("'&&' in content: wpautop/kses would break the inline script")
    return content
