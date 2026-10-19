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

GROUPS = {"A": A, "B": B, "C": C}
