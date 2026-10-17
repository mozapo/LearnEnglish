"""KVKK Aydınlatma Metni (page 2345) v2.7 and Çerez Politikası (page 4066) v1.2: the level test and "Seviye testim".

Legal texts keep the formal "siz". Every `old` must occur exactly once (see patches.apply).
EFFECTIVE is the date shown in the version lines; set it to the live publish date.
"""

EFFECTIVE = "17 Ekim 2026"

KVKK = [
    # 2. İşlenen kişisel veriler
    (
        "<tr><td>Doğum günü (isteğe bağlı)</td>",
        "<tr><td>Seviye testi</td><td>Ad, soyad, e-posta adresi, isteğe bağlı telefon numarası; test yanıtları, tahmini seviye, puan ve test süresi</td></tr>\n<tr><td>Doğum günü (isteğe bağlı)</td>",
    ),
    # 3. İşleme amaçları
    (
        "<li>Yasal yükümlülüklerin yerine getirilmesi.</li>",
        "<li>Yasal yükümlülüklerin yerine getirilmesi.</li>\n"
        "<li>Seviye testi sonucunuzun size e-postayla gönderilmesi; size uygun program önerisi ve ücretsiz ön görüşmenin hazırlanabilmesi için ekibimize iletilmesi.</li>\n"
        "<li>Hesabınızdaki “Seviye testim” alanında sonucunuzun, seviye rozetinizin ve konu alıştırmalarınızın gösterilmesi. Bu alan için test yanıtlarınız ve çalışma ilerlemeniz yalnızca kullandığınız tarayıcıda (yerel depolama) tutulur, sunucularımıza gönderilmez ve 12 ay sonra silinir; alandaki “Sonucu bu tarayıcıdan sil” bağlantısıyla dilediğiniz an silebilirsiniz.</li>",
    ),
    # 4. Hukuki sebepler
    (
        "<li><strong>Meşru menfaat</strong> — site güvenliği ve hizmet iyileştirme.</li>",
        "<li><strong>Bir sözleşmenin kurulmasıyla doğrudan ilgili olması</strong> — talebiniz üzerine çözdüğünüz seviye testinin sonucunun size ve ekibimize iletilmesi.</li>\n"
        "<li><strong>Meşru menfaat</strong> — site güvenliği ve hizmet iyileştirme.</li>",
    ),
    # 5. Toplama yöntemi
    (
        "site üzerindeki üyelik ve iletişim formları, sipariş süreçleri,",
        "site üzerindeki üyelik, iletişim ve seviye testi formları, sipariş süreçleri,",
    ),
    # 7. Saklama süreleri
    (
        "<tr><td>Eğitim desteği (burs) başvuruları</td>",
        "<tr><td>Seviye testi sonuçları</td><td>Testten itibaren 24 ay</td>\n    <td>Bir sözleşmenin kurulmasıyla doğrudan ilgili olması — ön görüşmenin hazırlanması ve talebin takibi</td></tr>\n"
        "<tr><td>Eğitim desteği (burs) başvuruları</td>",
    ),
    # 9. On sekiz yaşından küçükler
    (
        "    pazarlama amacıyla kullanılmaz.</li>",
        "    pazarlama amacıyla kullanılmaz.</li>\n"
        "<li>Seviye testini 18 yaşından küçük bir kullanıcı çözüyorsa testin veliyle birlikte çözülmesini ve velinin e-posta adresinin yazılmasını isteriz; sonuç bu adrese gönderilir.</li>",
    ),
    # version line
    (
        "Sürüm 2.6 — Yürürlük tarihi: 15 Ekim 2026 (değişiklik: geri bildirim ve şikâyet kayıtları saklama tablosuna eklendi) · Önceki sürümler: 2.5",
        "Sürüm 2.7 — Yürürlük tarihi: " + EFFECTIVE + " (değişiklik: seviye testi ve hesaptaki “Seviye testim” alanı eklendi) · Önceki sürümler: 2.6 — 15 Ekim 2026 (geri bildirim ve şikâyet kayıtları saklama tablosuna eklendi), 2.5",
    ),
]

CEREZ = [
    (
        "<td>Oturum açma, güvenlik, sepet, form gönderimi ve çerez tercihinizin hatırlanması.</td>",
        "<td>Oturum açma, güvenlik, sepet, form gönderimi, çerez tercihinizin hatırlanması ve seviye testini çözdüğünüzde sonucunuzun ve çalışma ilerlemenizin “Seviye testim” alanı için tarayıcınızda tutulması.</td>",
    ),
    (
        "<code>woocommerce_cart_hash</code>, <code>wp_woocommerce_session_*</code></td>",
        "<code>woocommerce_cart_hash</code>, <code>wp_woocommerce_session_*</code>;\n      yerel depolama: <code>bai_lt_v1</code>, <code>bai_lt_prog_v1</code> (en fazla 12 ay)</td>",
    ),
    (
        "Sürüm 1.1 — Son güncelleme: 25 Eylül 2026 (şirket kimlik bilgileri eklendi) · İlk yürürlük: 10 Eylül 2026",
        "Sürüm 1.2 — Son güncelleme: " + EFFECTIVE + " (seviye testi sonucu ve çalışma ilerlemesi için yerel depolama eklendi) · Önceki sürüm: 1.1 — 25 Eylül 2026 (şirket kimlik bilgileri eklendi) · İlk yürürlük: 10 Eylül 2026",
    ),
]
