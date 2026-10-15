"""Text changes to existing pages that point visitors to /geri-bildirim/.

Each edit is (old, new). `old` must occur exactly once in the page as it is now; an edit whose
`new` text is already present counts as done, so publishing twice is safe.
Page 1682 (SSS) is an Elementor page: its edits apply to the HTML widget inside _elementor_data.
"""

# Ön Bilgilendirme Formu — §8 Şikâyet ve uyuşmazlık
ON_BILGILENDIRME = [
    ('<p>Şikâyetlerinizi <a href="/iletisim/">iletişim sayfamız</a> üzerinden iletebilirsiniz.\n',
     '<p>Şikâyetlerinizi <a href="/geri-bildirim/">Geri Bildirim ve Şikâyet</a> sayfamız üzerinden iletebilirsiniz.\n'
     'Şikâyetiniz ilgili uzmandan bağımsız olarak incelenir; şikâyetinizin alındığı en geç bir iş günü içinde,\n'
     'yanıtımız en geç iki iş günü içinde size yazılı olarak bildirilir.\n'),
    ('<p class="bai-updated">Sürüm 1.2 — Son güncelleme: 7 Ekim 2026 (kartlı ödeme altyapısı belirtildi) · Sürüm 1.1:',
     '<p class="bai-updated">Sürüm 1.3 — Son güncelleme: 15 Ekim 2026 (şikâyet kanalı ve yanıt süreleri belirtildi, madde 8) · '
     'Sürüm 1.2: 7 Ekim 2026 (kartlı ödeme altyapısı belirtildi) · Sürüm 1.1:'),
]

# İptal ve İade Politikası — §7 Uyuşmazlık
IPTAL_IADE = [
    ("<p>Talebinizin sonucundan memnun kalmamanız hâlinde; Ticaret",
     '<p>Bir konudan memnun kalmadığınızda <a href="/geri-bildirim/">Geri Bildirim ve Şikâyet</a> sayfamız üzerinden\n'
     'bize yazabilir, yanıtımızı yeterli bulmazsanız konunun kurucumuz tarafından yeniden incelenmesini\n'
     'isteyebilirsiniz. Bu adımlar zorunlu değildir ve aşağıdaki haklarınızı sınırlamaz.</p>\n'
     "<p>Talebinizin sonucundan memnun kalmamanız hâlinde; Ticaret"),
    ('<p class="bai-updated">Sürüm 1.6 — Son güncelleme: 7 Ekim 2026 (karta iade kuralı netleştirildi, madde 6) · Sürüm 1.5:',
     '<p class="bai-updated">Sürüm 1.7 — Son güncelleme: 15 Ekim 2026 (şikâyet kanalı eklendi, madde 7) · '
     'Sürüm 1.6: 7 Ekim 2026 (karta iade kuralı netleştirildi, madde 6) · Sürüm 1.5:'),
]

# Çocuk Güvenliği Politikası — §8 Bildirim ve şikâyet kanalı (3 iş günü -> aynı gün)
COCUK_GUVENLIGI = [
    ('bize iletebilir. Bildirimler <a href="/iletisim/">iletişim sayfamız</a> üzerinden alınır ve\n'
     '<strong>en geç üç iş günü</strong> içinde değerlendirilir. Ciddi',
     'bize iletebilir. Bildirimler <a href="/geri-bildirim/#guvenlik">Geri Bildirim ve Şikâyet</a> sayfamız,\n'
     'telefon (<a href="tel:+902168881369">0216 888 13 69</a>) veya WhatsApp üzerinden alınır; ilgili uzmana değil\n'
     'koordinasyon ekibine ulaşır ve <strong>aynı gün</strong> değerlendirmeye alınır. Acil bir tehlike hâlinde\n'
     'önce 112 aranmalıdır. Ciddi'),
    ('<p class="bai-updated">Sürüm 1.1 — Yürürlük tarihi: 21 Eylül 2026 (değişiklik: hizmet adı güncellendi, kapsam aynı) · '
     'Önceki sürüm: 1.0 — 10 Eylül 2026</p>',
     '<p class="bai-updated">Sürüm 1.2 — Yürürlük tarihi: 15 Ekim 2026 (değişiklik: bildirim kanalı ve değerlendirme süresi '
     'güncellendi, madde 8) · Önceki sürümler: 1.1 — 21 Eylül 2026, 1.0 — 10 Eylül 2026</p>'),
]

# KVKK Aydınlatma Metni — saklama süreleri tablosu
KVKK = [
    ("<tr><td>İletişim ve ön görüşme formu kayıtları</td><td>Son temastan itibaren 24 ay</td>\n"
     "    <td>Meşru menfaat — talebin takibi</td></tr>\n",
     "<tr><td>İletişim ve ön görüşme formu kayıtları</td><td>Son temastan itibaren 24 ay</td>\n"
     "    <td>Meşru menfaat — talebin takibi</td></tr>\n"
     "<tr><td>Geri bildirim ve şikâyet kayıtları</td><td>Bildirimden itibaren 24 ay</td>\n"
     "    <td>Meşru menfaat ve bir hakkın tesisi, kullanılması veya korunması — şikâyetin incelenmesi ve olası uyuşmazlıkta ispat</td></tr>\n"),
    ('<p class="bai-updated">Sürüm 2.5 — Yürürlük tarihi: 13 Ekim 2026 (değişiklik: kartla ödeme için Türkiye İş Bankası A.Ş. '
     'veri aktarım tablosuna eklendi) · Önceki sürümler: 2.4 — 11 Ekim 2026,',
     '<p class="bai-updated">Sürüm 2.6 — Yürürlük tarihi: 15 Ekim 2026 (değişiklik: geri bildirim ve şikâyet kayıtları saklama '
     'tablosuna eklendi) · Önceki sürümler: 2.5 — 13 Ekim 2026 (kartla ödeme için Türkiye İş Bankası A.Ş. veri aktarım '
     'tablosuna eklendi), 2.4 — 11 Ekim 2026,'),
]

_ILETISIM_FAQ_Q = "Bir sorun yaşarsam ya da memnun kalmazsam nereye yazmalıyım?"
_ILETISIM_FAQ_A = ("Geri Bildirim ve Şikâyet sayfasındaki formu kullanabilir ya da bizi arayabilirsin. Bildirimin ilgili "
                   "uzmana değil koordinasyon ekibine ulaşır; aldığımızı 1 iş günü, yanıtımızı 2 iş günü içinde iletiriz.")

# İletişim — signature panel note, FAQ item (+ JSON-LD), FAQ count on the "next" card
ILETISIM = [
    ("</span></div></li>\n          </ol>\n        </aside>",
     "</span></div></li>\n          </ol>\n"
     '          <p class="bai-signature__foot">Bir sorun mu yaşadın? <a href="/geri-bildirim/">Geri bildirim ve şikâyet</a> '
     "sayfasından bize yaz; bildirimin ilgili uzmana değil, koordinasyon ekibine ulaşır.</p>\n        </aside>"),
    ("<summary>Forma yazdıktan sonra ne zaman dönüş yapılır?</summary><div class=\"bai-faq__a\"><p>Taleplerine 2 iş günü içinde dönüş yapılır.</p></div></details>\n",
     "<summary>Forma yazdıktan sonra ne zaman dönüş yapılır?</summary><div class=\"bai-faq__a\"><p>Taleplerine 2 iş günü içinde dönüş yapılır.</p></div></details>\n"
     f'        <details class="bai-faq__item"><summary>{_ILETISIM_FAQ_Q}</summary><div class="bai-faq__a"><p>'
     '<a href="/geri-bildirim/">Geri Bildirim ve Şikâyet</a> sayfasındaki formu kullanabilir ya da bizi arayabilirsin. '
     "Bildirimin ilgili uzmana değil koordinasyon ekibine ulaşır; aldığımızı 1 iş günü, yanıtımızı 2 iş günü içinde iletiriz."
     "</p></div></details>\n"),
    ('"text":"Taleplerine 2 iş günü içinde dönüş yapılır."}}]}',
     '"text":"Taleplerine 2 iş günü içinde dönüş yapılır."}},'
     f'{{"@type":"Question","name":"{_ILETISIM_FAQ_Q}","acceptedAnswer":{{"@type":"Answer","text":"{_ILETISIM_FAQ_A}"}}}}]}}'),
    ("<span>40 soru, altı başlıkta</span>", "<span>41 soru, altı başlıkta</span>"),
]

_UZMAN_OLD = "Bu, iade hakkının yerine sunulan bir alternatiftir; iade hakkını ortadan kaldırmaz."
# Uzmanlarımız / İngilizce Öğretmeni Bul — "Uzmanımla anlaşamazsam ne olur?" (HTML answer and JSON-LD)
UZMAN_FAQ = [
    (f"{_UZMAN_OLD}</p></div></details>",
     f'{_UZMAN_OLD} Yaşadığın bir sorunu bize iletmek istersen <a href="/geri-bildirim/">Geri Bildirim ve Şikâyet</a> '
     "sayfasını kullanabilirsin; bildirimin uzmana değil, koordinasyon ekibine ulaşır.</p></div></details>"),
    (f'{_UZMAN_OLD}"}}}}, {{"@type": "Question", "name": "Ön görüşme ücretli mi?"',
     f"{_UZMAN_OLD} Yaşadığın bir sorunu bize iletmek istersen Geri Bildirim ve Şikâyet sayfasını kullanabilirsin; "
     'bildirimin uzmana değil, koordinasyon ekibine ulaşır."}}, {"@type": "Question", "name": "Ön görüşme ücretli mi?"'),
]

_SSS_Q = "Bir sorun yaşarsam ya da memnun kalmazsam ne yapmalıyım?"
# Sıkça Sorulan Sorular (Elementor HTML widget) — new question after the expert-change answer, count 40 -> 41
SSS = [
    ("en sık gelen 40 soruyu altı başlıkta", "en sık gelen 41 soruyu altı başlıkta"),
    (f"{_UZMAN_OLD}</p></div></details>\n",
     f"{_UZMAN_OLD}</p></div></details>\n"
     f'        <details class="bai-faq__item"><summary>{_SSS_Q}</summary><div class="bai-faq__a"><p>'
     '<a href="/geri-bildirim/">Geri Bildirim ve Şikâyet</a> sayfasından bize yazabilirsin; istersen isimsiz. '
     "Şikâyetini ilgili uzman değil, koordinasyon ekibimiz inceler. Aldığımızı 1 iş günü, ne yapacağımızı 2 iş günü "
     "içinde yazılı olarak bildiririz. Yanıtımızı yeterli bulmazsan konuyu kurucumuza iletebilirsin.</p></div></details>\n"),
]

PAGES = {
    4070: ("Ön Bilgilendirme Formu", ON_BILGILENDIRME),
    4069: ("İptal ve İade Politikası", IPTAL_IADE),
    4068: ("Çocuk Güvenliği Politikası", COCUK_GUVENLIGI),
    2345: ("KVKK Aydınlatma Metni", KVKK),
    1594: ("İletişim", ILETISIM),
    1519: ("Uzmanlarımız", UZMAN_FAQ),
    1454: ("İngilizce Öğretmeni Bul", UZMAN_FAQ),
}
ELEMENTOR_PAGES = {1682: ("Sıkça Sorulan Sorular", SSS)}


def apply(text, edits, label):
    """Return text with every edit applied; raise if an edit can't be placed exactly once."""
    for old, new in edits:
        if new in text:
            continue  # already applied
        n = text.count(old)
        if n != 1:
            raise SystemExit(f"{label}: expected the text once, found {n}: {old[:80]!r}")
        text = text.replace(old, new)
    return text
