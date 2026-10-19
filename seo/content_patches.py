"""Exact-string content fixes from the SEO audit (19 Oct 2026). Applied by seo/publish.py.

Each patch: (field, old, new, expected_count). field is "content" (post_content) or "elementor" (_elementor_data,
which is a JSON string, so quotes inside it are written as \\" here). A page is written only when every old string
occurs exactly expected_count times (original state) or every new string is already there (nothing to do).
"""

# Group A: customer-visible editorial notes and placeholders. Wording only; no claims added.
A = {
    # /programlar/bireysel-programlar/ingilizce-programlari/ingilizce-konusma-programi/ : an instruction to editors was
    # visible to visitors. The customer-facing part (capacity and schedule are confirmed before enrolment) is kept.
    1571: [("content",
            "<p>Grup kapasitesi, seviye eşleştirmesi ve güncel ders takvimi kayıt öncesinde doğrulanmalıdır. "
            "Sayfada doğrulanmamış sabit grup mevcudu veya ücret avantajı yayımlamayın.</p>",
            "<p>Grup büyüklüğü, seviye eşleştirmesi ve güncel ders takvimi kayıttan önce seninle birlikte netleştirilir.</p>",
            1)],
    # /universite-hazirlik-muafiyet-sinavlari/ : 23 "Detaylı rehber yakında" chips promised guides that do not exist.
    5518: [("content",
            '<p class="hmx-card__soon"><span class="bai-chip">Detaylı rehber yakında</span></p>',
            "",
            23)],
    # /blog/ : "İlk kapsamlı rehberler hazırlanıyor" although an article is published. Shows the real article instead.
    1579: [("content",
            "<p>Burada en yeni blog içerikleri yayın tarihine göre listelenecek.</p>",
            "<p>Yayımlanan yazılar, en yenisi başta.</p>",
            1),
           ("content",
            '<div class="bai-card"><h3>İlk kapsamlı rehberler hazırlanıyor</h3><p>Bu alan, blog yazıları yayınlandığında '
            'otomatik içerik akışıyla değiştirilecek. Şimdilik ücretsiz kaynaklardan başlayabilirsin.</p></div>',
            '<a class="bai-card" href="/skor-garantisi-neden-verilmez/"><ul class="bai-chips"><li class="bai-chip">'
            'Sınav hazırlığı</li></ul><h3>IELTS, TOEFL veya SAT hazırlığında skor garantisi neden verilmez?</h3>'
            '<p>Sınav skorunu belirleyen etkenlerin çoğu bir kursun kontrolünde değildir. Neden sonucu değil, '
            'süreci söz verdiğimizi açıklıyoruz.</p></a>',
            1)],
}

# Group B: factual correction that follows the legal pages (needs the owner's OK before live).
B = {
    # /sikca-sorulan-sorular/ : said online payment is not active yet. KVKK Aydınlatma Metni v2.5 (13 Oct 2026) and
    # /guvenli-odeme already describe İş Bankası 3D Secure card payment.
    1682: [("elementor",
            "<p>Ödeme altyapısı henüz devrede değildir. Devreye alındığında ilgili ödeme kuruluşu "
            "<a href=\\\"/kvkk-aydinlatma-metni/\\\">KVKK Aydınlatma Metni</a>'ndeki sağlayıcı tablosuna eklenecektir; "
            "kart bilgilerin hiçbir aşamada sunucularımızda saklanmaz.</p>",
            "<p>Evet. Kartla ödeme, Türkiye İş Bankası'nın 3D Secure güvenli ödeme sayfasında alınır; istersen banka "
            "havalesi/EFT ile de ödeyebilirsin. Kart bilgilerin bize ulaşmaz ve hiçbir aşamada sunucularımızda "
            "saklanmaz. Ayrıntılar <a href=\\\"/guvenli-odeme/\\\">Güvenli Ödeme</a> sayfasında.</p>",
            1)],
}

# Group C: internal links. The country cards and "… seçeneğini değerlendir" buttons pointed to the contact page or
# the generic country quiz although a full guide exists for each country. Only href values change.
_COUNTRIES = [("Amerika", "amerika"), ("İngiltere", "ingiltere"), ("Kanada", "kanada"), ("İtalya", "italya"),
              ("Almanya", "almanya"), ("Hollanda", "hollanda"), ("Fransa", "fransa"), ("İrlanda", "irlanda")]
C = {
    # /yurt-disi-egitim/
    1384: [("content", f'<a class="bai-card" href="/iletisim/"><h3>{name}’da eğitim</h3>'.replace("’da", suffix),
            f'<a class="bai-card" href="/{slug}-egitim/"><h3>{name}’da eğitim</h3>'.replace("’da", suffix), 1)
           for (name, slug), suffix in zip(_COUNTRIES, ["’da", "’de", "’da", "’da", "’da", "’da", "’da", "’da"])],
    # /universite-rehberi/
    1686: [("content", f'href="/ulke-secimi-2/">{name} seçeneğini değerlendir</a>',
            f'href="/{slug}-egitim/">{name} seçeneğini değerlendir</a>', 1) for name, slug in _COUNTRIES],
}

# Group D: owner decisions of 19 Oct 2026. (1) No UCAS affiliation wording. (2) Visa applications are not a service;
# partners can be suggested, with no responsibility for them. (3) "zihinsel esenlik / mental wellbeing" becomes
# "öğrenme ve motivasyon desteği". (4) KVKK form: the "addresses will be added" note is obsolete.
# Elementor pages are patched in _elementor_data (what visitors see), where quotes are written as \".
VISA_TR = ("Vize başvurusu hizmetlerimiz arasında değildir; istersen seni iş ortaklarımıza yönlendirebiliriz, ancak "
           "onların hizmetlerinden Bir Adım İleri sorumlu değildir.")
VISA_FAQ_TR = ("Hayır. Vize başvurusu hizmetlerimiz arasında değildir. İstersen seni bu konuda destek veren iş "
               "ortaklarımıza yönlendirebiliriz; iş ortaklarının sunduğu hizmetlerden ve vize sonucundan Bir Adım İleri "
               "sorumlu değildir. Vize kararı yalnızca ilgili ülkenin resmî makamlarına aittir; güncel koşulları her "
               "zaman resmî kaynaklardan kontrol et.")
VISA_FAQ_EN = ("No. Visa applications are not part of our services. If you wish, we can refer you to partners who help "
               "with the visa process; Bir Adım İleri is not responsible for the services they provide or for any visa "
               "outcome. Visa decisions are made only by the relevant authorities, so always check current requirements "
               "with official sources.")
_OLD_1384 = ("Vize desteğinin hizmet kapsamında olup olmadığı ayrıca doğrulanmalıdır. Vize koşulları değişebildiği için "
             "güncel gereklilikler her zaman ilgili ülkenin resmî makamlarından kontrol edilmelidir. Hiçbir rehber vize "
             "sonucunu garanti edemez.")
_OLD_1510 = ("Kapsam kayıt öncesinde açıklanmalıdır. Genel süreç ve resmî kaynak yönlendirmesi sunulabilir. Hukuki veya "
             "düzenlemeye tabi danışmanlık gerekiyorsa yetkili profesyonele başvurulmalıdır.")
_OLD_2368 = ("Whether visa support falls within the scope of the service must be confirmed separately. Because visa "
             "conditions can change, current requirements should always be checked with the official authorities of the "
             "country concerned. No adviser can guarantee a visa outcome.")
_STD_EN = ('We work to internationally recognised standards such as <a href="https://takeielts.britishcouncil.org/">'
           'British Council IELTS</a>, <a href="https://www.ets.org/toefl.html">ETS TOEFL</a> and '
           '<a href="https://www.ucas.com/">UCAS</a>.')
_STD_TR = ('<a href="https://takeielts.britishcouncil.org/">British Council IELTS</a>, <a href="https://www.ets.org/'
           'toefl.html">ETS TOEFL</a> ve <a href="https://www.ucas.com/">UCAS</a> gibi uluslararası kabul görmüş '
           'standartlarla ilerliyoruz.')
_ALL_SERVICES_EN = ("<p>The full ecosystem, from language to wellbeing, on one page.</p>",
                    "<p>The full ecosystem, from language to learning support, on one page.</p>", 1)
D = {
    # /programlar/
    1560: [("content", '<p><a href="https://www.ucas.com/">UCAS Registered Centres</a> ve Common App kabul odaklı bütünsel '
                       'üniversite başvuru paketi.</p>',
            "<p>Ülke ve program seçiminden başvuru dosyasına bütünsel üniversite başvuru rehberliği paketi.</p>", 1),
           ("content", "<li>Konsolosluk vize simülasyonu</li>", "<li>Vize için iş ortaklarımıza yönlendirme</li>", 1),
           ("content", "dil, akademi, kariyer, zihinsel denge ve yaratıcılığı bir araya getirerek hedeflerine ulaştıran "
                       "modüler programlar.",
            "dil, akademi, kariyer, öğrenme ve motivasyon desteği ile yaratıcılığı bir araya getiren modüler programlar.", 1),
           ("content", "<li>Zihinsel dinlenme ve üretim</li>", "<li>Rahatlatıcı bir üretim molası</li>", 1),
           ("content", "akademik koçluk ve zihinsel esenliği tek bir yıllık pakette",
            "akademik koçluk ile öğrenme ve motivasyon desteğini tek bir yıllık pakette", 1)],
    # /hakkimizda/
    1595: [("content", _STD_TR, "Sınav kurumlarının ve üniversitelerin yayımladığı resmî ölçütleri ve güncel kaynakları "
                                "esas alıyoruz.", 1),
           ("content", "Dil, akademi, kariyer, zihinsel esenlik ve sanatı tek bir güvenli çatı altında birleştiriyoruz.",
            "Dil, akademi, kariyer, öğrenme ve motivasyon desteği ile sanatı tek bir güvenli çatı altında birleştiriyoruz.", 1)],
    # /kaynaklar/
    1580: [("content", "verimlilik şablonlarından zihinsel esenlik egzersizlerine kadar",
            "verimlilik şablonlarından motivasyon ve çalışma düzeni araçlarına kadar", 1)],
    # /misyon-vizyon/ (visible text and its FAQ schema)
    1638: [("content", "akademik koçluk, zihinsel esenlik ve sanatı tek bir",
            "akademik koçluk, öğrenme ve motivasyon desteği ile sanatı tek bir", 1),
           ("content", "zihinsel esenliğini, dil becerisini ve akademik gelişimini",
            "motivasyonunu, dil becerisini ve akademik gelişimini", 2)],
    # / (Elementor: service card and the quiz data)
    923: [("elementor", "burs araştırmasından vize sürecine kadar destek.", "burs araştırmasına kadar destek.", 2)],
    # /sikca-sorulan-sorular/ (Elementor)
    1682: [("elementor", "burs araştırmasından vize sürecine kadar destek veriyoruz.</p>",
            "burs araştırmasına kadar destek veriyoruz. " + VISA_TR + "</p>", 1)],
    # /hizmetler/ (Elementor)
    1598: [("elementor", '<li class=\\"bai-chip\\">Vize provası</li>', '<li class=\\"bai-chip\\">Başvuru dosyası</li>', 1),
           ("elementor", "<h3>Burs ve vize stratejisi</h3><p>Devlet ve üniversite burs olanaklarının analizi, eksiksiz "
                         "vize evrak hazırlığı ve görüşme provaları.</p>",
            "<h3>Burs stratejisi</h3><p>Devlet ve üniversite burs olanaklarının analizi. " + VISA_TR + "</p>", 1)],
    # /yurt-disi-egitim/ FAQ (visible + schema)
    1384: [("content", _OLD_1384, VISA_FAQ_TR, 2)],
    # /universite-basvuru-danismanligi-2/ FAQ (visible + schema)
    1510: [("content", _OLD_1510, VISA_FAQ_TR, 2)],
    # Country guides
    1727: [("content", "<p>Vize dosyası organizasyonu, bütçe, konaklama araştırması ve Fransa’ya varış kontrol listesi "
                       "oluştururuz.</p>",
            "<p>Bütçe, konaklama araştırması ve Fransa’ya varış kontrol listesi oluştururuz. " + VISA_TR + "</p>", 1)],
    1729: [("content", "Teklif karşılaştırma, konaklama, bütçe, vize kontrol listesi ve İrlanda'ya varış öncelikleri için "
                       "yol haritası hazırlanır.",
            "Teklif karşılaştırma, konaklama, bütçe ve İrlanda'ya varış öncelikleri için yol haritası hazırlanır. " + VISA_TR, 1)],
    1725: [("content", "Teklif karşılaştırma, bütçe, konaklama, vize kontrol listesi ve taşınma öncelikleri için yol "
                       "haritası oluşturulur.",
            "Teklif karşılaştırma, bütçe, konaklama ve taşınma öncelikleri için yol haritası oluşturulur. " + VISA_TR, 1)],
    1721: [("elementor", "<h3>Vize hazırlığı</h3><p>Güncel konsolosluk şartları doğrulanarak finans, konaklama, sigorta ve "
                         "diğer vize belgeleri planlanır.</p>",
            "<h3>Vize için yönlendirme</h3><p>" + VISA_TR + " Vize kararı konsolosluğa aittir.</p>", 1),
           ("elementor", "<h3>Vize dosyası hazırlık rehberliği</h3><p>Güncel resmî kontrol listesine göre görev ve belge "
                         "planı oluşturulur; nihai kararın konsolosluğa ait olduğu açıkça belirtilir.</p>",
            "<h3>Vize için yönlendirme</h3><p>İstersen seni vize sürecinde iş ortaklarımıza yönlendirebiliriz; onların "
            "hizmetlerinden Bir Adım İleri sorumlu değildir ve nihai karar konsolosluğa aittir.</p>", 1),
           ("elementor", "burs araştırması, Universitaly ve vize hazırlık rehberliği.",
            "burs araştırması ve Universitaly rehberliği.", 1),
           ("elementor", "burs araştırması, Universitaly ve vize dosyası hazırlık rehberliği.",
            "burs araştırması ve Universitaly rehberliği.", 1)],
    # English
    2368: [("content", _OLD_2368, VISA_FAQ_EN, 2)],
    2361: [("elementor", "to the application file, scholarship research and the visa process.</p>",
            "to the application file and scholarship research.</p>", 1)],
    2364: [("content", _STD_EN, "We work from the official criteria and current guidance published by exam boards and "
                                "universities.", 1),
           ("content", "We bring language, academics, career, mental wellbeing and the arts together under one safe roof.",
            "We bring language, academics, career, learning and motivation support and the arts together under one safe "
            "roof.", 1),
           ("content",) + _ALL_SERVICES_EN],
    2367: [("content",) + _ALL_SERVICES_EN],
    2366: [("content",) + _ALL_SERVICES_EN],
    # /kvkk-basvuru-formu/ (legal, formal "siz"): addresses are already in the table; the note said they would come later
    4067: [("content", '<p class="bai-legal-note">Yukarıdaki resmî başvuru adresleri, kurumsal kayıt işlemleri\n'
                       'tamamlandığında bu tabloya eklenecektir. Bu tamamlanana kadar taleplerinizi\n'
                       '<a href="/iletisim/">iletişim sayfamız</a> üzerinden iletebilirsiniz; başvurunuz aynı\n'
                       'sürede ve aynı özenle sonuçlandırılır.</p>',
            '<p class="bai-legal-note">Başvurunuzu yukarıdaki kanallardan biriyle iletebilirsiniz. Başvuru süreciyle '
            'ilgili sorularınız için <a href="/iletisim/">iletişim sayfamızı</a> da kullanabilirsiniz.</p>', 1),
           ("content", '<p class="bai-updated">Sürüm 1.2 — Son güncelleme: 8 Ekim 2026 (KEP adresi eklendi)',
            '<p class="bai-updated">Sürüm 1.3 — Son güncelleme: 19 Ekim 2026 (başvuru kanalları notu güncellendi) · '
            'Sürüm 1.2: 8 Ekim 2026 (KEP adresi eklendi)', 1)],
}

# Group E: Terms of use clause for visa referrals (legal text; on staging, waits for the owner's OK before live).
E = {
    # /kullanim-kosullari/ (legal, formal "siz"): visa referrals to partners, no responsibility for them
    2346: [("content", "veya vize başvurusu gibi sonuçlar birçok bağımsız etkene bağlı olduğundan garanti edilmez.</p>",
            "veya vize başvurusu gibi sonuçlar birçok bağımsız etkene bağlı olduğundan garanti edilmez.</p>\n"
            "<p>Vize başvurusu Bir Adım İleri'nin sunduğu hizmetler arasında değildir. Talep etmeniz hâlinde sizi vize "
            "sürecinde destek veren bağımsız iş ortaklarına yönlendirebiliriz. Bu iş ortakları hizmetlerini kendi "
            "adlarına ve kendi sorumlulukları altında sunar; söz konusu hizmetlerden, ücretlerinden ve vize başvurusunun "
            "sonucundan Bir Adım İleri sorumlu değildir. Bu hüküm, kanundan doğan sorumluluk hâllerini ve tüketici "
            "haklarınızı sınırlamaz.</p>", 1),
           ("content", '<p class="bai-updated">Sürüm 1.2 — Yürürlük tarihi: 10 Eylül 2026 (önceki sürümler: 1.1 — 10 Eylül '
                       '2026, 1.0 — 14 Ağustos 2026)</p>',
            '<p class="bai-updated">Sürüm 1.3 — Yürürlük tarihi: 19 Ekim 2026 (vize başvurusunda iş ortaklarına '
            'yönlendirme eklendi; önceki sürümler: 1.2 — 10 Eylül 2026, 1.1 — 10 Eylül 2026, 1.0 — 14 Ağustos 2026)</p>', 1)],
}

GROUPS = {"A": A, "B": B, "C": C, "D": D, "E": E}
