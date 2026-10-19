"""SureRank title/description/robots changes from the SEO audit (19 Oct 2026). Applied by seo/publish.py meta.

NEW holds the new values per page. BEFORE is read from the live backup of 19 Oct 2026, so rollback restores
exactly what was there. Social titles/descriptions follow the page values only where they mirrored them before.
Wording: Turkish marketing voice "sen", no outcome promises, "rehberlik" not "danışmanlık", every fact taken from
the page itself.
"""
import gzip
import json
import os

D = "page_description"
T = "page_title"

NEW = {
    # Hubs and intent split (title + description)
    923: {T: "Online İngilizce, IELTS ve Yurt Dışı Eğitim | Bir Adım İleri"},
    1613: {T: "Online Birebir İngilizce Dersleri (A1–C2) | Bir Adım İleri"},
    1460: {T: "Online Sınav Hazırlığı: IELTS, TOEFL, SAT, YDS | Bir Adım İleri",
           D: "IELTS, TOEFL, SAT, PTE, YDS, Cambridge ve hazırlık muafiyet sınavlarına online hazırlık. Hangi sınavın "
              "sana uygun olduğunu karşılaştır, hedefine göre plan kur."},
    1462: {T: "Online IELTS Hazırlık: Academic ve General | Bir Adım İleri",
           D: "IELTS Academic ve General Training için dört beceriye online hazırlık: iki modülün farkı, seviye "
              "tespitinden sınav gününe adımlar ve Writing/Speaking odağı."},
    1564: {T: "Birebir IELTS Hazırlık Programı ve Ders Planı | Bir Adım İleri",
           D: "Hedef band puanına ve sınav tarihine göre birebir IELTS programı: seviye ve beceri analizi, "
              "Academic/General seçimi ve sınav gününe yol haritası."},
    1464: {T: "Online TOEFL iBT Hazırlık | Bir Adım İleri",
           D: "TOEFL iBT'nin okuma, dinleme, konuşma ve yazma bölümlerine online hazırlık: bölüm stratejileri, "
              "düzenli deneme ve sınav tarihine göre çalışma planı."},
    1565: {T: "Birebir TOEFL iBT Hazırlık Programı | Bir Adım İleri",
           D: "Başlangıç düzeyine, hedef puanına ve sınav tarihine göre birebir TOEFL iBT programı: beş aşamalı "
              "yol haritası ve deneme puanının ötesinde takip."},
    1384: {T: "Yurt Dışı Eğitim ve Başvuru Rehberliği | Bir Adım İleri",
           D: "Lisans, yüksek lisans, doktora ve dil okulu başvurularında ülke ve program seçimi, belge planı ve "
              "başvuru metni rehberliği. Kabul veya vize garantisi yok."},
    # Three different assessment tools, three different intents
    1688: {T: "İngilizce Seviyeni 3 Dakikada Tahmin Et | Bir Adım İleri",
           D: "11 kısa soruluk, 3 dakikalık ücretsiz İngilizce öz değerlendirmesi: tahmini CEFR aralığını ve "
              "gelişim alanını gör. Resmî sınav veya sertifika değildir."},
    4011: {T: "Ücretsiz İngilizce Seviye Testi (40 Soru, A1–C2) | Bir Adım İleri",
           D: "A1'den C2'ye 40 soruluk ücretsiz İngilizce seviye testi: yaklaşık 12 dakika, anında sonuç ve seviye "
              "seviye analiz. Resmî bir Cambridge sınavı değildir."},
    1458: {T: "Ücretsiz Canlı İngilizce Seviye Tespiti | Bir Adım İleri",
           D: "Öğretmenle 15–20 dakikalık ücretsiz canlı İngilizce seviye değerlendirmesi: konuşmanı dinler, sana "
              "uygun programı önerir. Resmî sınav veya sertifika değildir."},
    # English pages: "guidance" (rehberlik), not "consulting"; no wellbeing/health wording
    2368: {T: "Study Abroad and University Application Guidance | Bir Adım İleri"},
    2361: {D: "English lessons, IELTS/TOEFL/SAT preparation, study abroad guidance, coaching and learning support "
              "in one place. Start with a free 15-minute consultation."},
    # Templated descriptions replaced with page-specific ones
    1906: {D: "Sıfırdan başlayanlar ve tekniğini geliştirmek isteyenler için online çizim atölyesi: görmeyi, "
              "oranlamayı ve karakter çizmeyi öğren; İngilizce pratiği de yap."},
    1907: {D: "Tuvalle ilk kez tanışanlar ve yaratıcı bir mola arayanlar için online resim atölyesi. 2 dakikalık "
              "yön bulmayla sana uygun resim stilini keşfet."},
    1905: {D: "Daha önce fırça tutmamış olsan da başlayabileceğin online suluboya atölyesi: renk, su ve kâğıtla "
              "denemeler. Atölye İngilizce yürütülür."},
    1900: {D: "Çalışma alışkanlığı, zaman yönetimi ve sınav öncesi kaygı için öğrencilere gizlilik odaklı öğrenme "
              "desteği. Eğitim temellidir, sağlık hizmeti değildir."},
    1631: {D: "Çalışma düzeni, motivasyon, sınav kaygısı ve özgüven için yargılanmadan konuşabileceğin, eğitim "
              "temelli destek. Tanı ve tedavi sunmaz; sağlık hizmeti değildir."},
    1898: {D: "Erteleme, dağınık çalışma ve zaman yönetimi için birebir verimlilik koçluğu. 2 dakikalık yön "
              "bulmayla çalışma düzeninin hangi aşamada olduğunu gör."},
    1897: {D: "Çalışma düzeni, hedef belirleme ve motivasyon için öğrencilere birebir koçluk. Kısa öz "
              "değerlendirmeyle programa ne kadar hazır olduğunu gör."},
    1896: {D: "Kariyer yönünü netleştirmek ve sonraki adımını planlamak için birebir kariyer koçluğu. Kısa öz "
              "değerlendirmeyle bugün nerede olduğunu gör."},
    1619: {D: "Soru çözme tekniği, zaman yönetimi, sınav kaygısı ve haftalık deneme takibiyle sınav koçluğu. 60 "
              "saniyelik öz değerlendirmeyle stratejinin nerede olduğunu gör."},
    1729: {D: "İrlanda'da üniversite: NFQ düzeyleri, CAO ve doğrudan başvuru, toplam bütçe ve ayrı vize süreci. "
              "Dublin, Cork veya Galway'de doğru programı seçmek için rehber."},
    1727: {D: "Fransa'da üniversite: Études en France, Parcoursup ve kurum portalları, diploma yapısı ve gerçek "
              "bütçe. Doğru platform ve belgeyle planlı başvuru için rehber."},
    1725: {D: "Hollanda'da üniversite: araştırma ve uygulamalı bilimler kurumları, Studielink kaydı, uygunluk "
              "koşulları, bütçe ve kabul sonrası hazırlık için rehber."},
    1723: {D: "Almanya'da üniversite: Vorlesung ve seminer sistemi, programa göre değişen akademik ve dil koşulları "
              "ve “ücretsiz üniversite”nin gerçek bütçesi için rehber."},
    1721: {D: "İtalya'da lisans, yüksek lisans ve doktora: Universitaly ön kaydı, gelire göre değişen ücretler, "
              "burslar ve vize. Başvurunu görünür adımlara ayıran rehber."},
    1719: {D: "Kanada'da üniversite ve kolej: kurum ve program seçimi, eyalet ve şehir, başvuru adımları, bütçe "
              "ve mezuniyet sonrası çalışma izni koşulları için rehber."},
    1717: {D: "İngiltere'de üniversite: UCAS ile en fazla beş tercih, üç soruluk yeni personal statement, 2027 "
              "giriş takvimi, maliyet ve öğrenci vizesi için güncel rehber."},
    1715: {D: "Amerika'da üniversite: liberal arts modeli, kredi ve GPA sistemi, SAT/ACT ve Common App başvurusu. "
              "ABD eğitim sistemini kendi hedefinle karşılaştır."},
    1636: {D: "Suluboya, çizim, resim, dijital sanat ve yaratıcı yazarlık: ön deneyim gerektirmeyen, küçük gruplu "
              "online atölyelerde üreterek keşfet ve İngilizceyi kullan."},
    1633: {D: "Bir Adım İleri'nin kurucusu 2006'dan beri iki ülkede öğretmen, öğretmen eğitmeni ve müfredat "
              "tasarımcısı olarak çalıştı. Markanın nasıl doğduğunu oku."},
    1579: {D: "İngilizce, IELTS/TOEFL/SAT hazırlığı ve yurt dışı eğitim üzerine resmî kaynaklarla "
              "doğrulanan, uygulanabilir yazılar. Her yazı bir sonraki adımı gösterir."},
    1560: {D: "İngilizce, sınav hazırlığı, yurt dışı başvuru, koçluk ve yaratıcı atölyelerde bireysel, grup ve "
              "paket programlar. Üç soruyla sana en yakın programı bul."},
    1624: {D: "Writing ve Speaking için uzman mock değerlendirmesi ve yazılı geri bildirim; resmî kaynaklardan "
              "ücretsiz denemeler. Sınavdan önce nerede olduğunu gör."},
    1470: {D: "B1 Preliminary, B2 First, C1 Advanced ve C2 Proficiency: seviyene uygun Cambridge English sınavını "
              "3 soruda bul, dört beceriyi sınav formatına göre geliştir."},
    1578: {D: "Toplantı, sunum, e-posta ve mülakat İngilizcesi ile kariyer desteği: yoğun iş temposuna uyan bire "
              "bir, mikro grup veya birleşik profesyonel programlar."},
    1576: {D: "13–18 yaş için İngilizce, sınav hazırlığı, koçluk ve atölyeleri bir araya getiren programlar. Kısa "
              "yön bulmayla gencin şu anki ihtiyacına en uygun yolu gör."},
    1575: {D: "Birden fazla hedefi tek planda birleştiren paket programlar: İngilizce, sınav, başvuru ve koçluk tek "
              "koordinasyonla. Paket fiyatları KDV dâhil sayfada."},
    1562: {D: "İngilizce, sınav hazırlığı, başvuru ve koçlukta seni tanıyan bir uzmanla birebir ilerlediğin "
              "bireysel programlar. Kısa yön bulmayla sana uygun olanı gör."},
    1572: {D: "Akademik metin okuma, paragraf ve makale yazma, kaynak kullanımı ve sunum: üniversite ve araştırma "
              "ortamı için birebir Akademik İngilizce Programı."},
    1569: {D: "Yeni başlayanlar, ara verenler ve sınav öncesi temelini güçlendirmek isteyenler için birebir Genel "
              "İngilizce Programı. Seviyen ücretsiz görüşmede belirlenir."},
    1392: {D: "Daha sık ders, dersler arası uygulama ve düzenli geri bildirimle Yoğun İngilizce Programı: "
              "İngilizceyi ertelemeden haftalık düzenine yerleştir."},
    1500: {D: "8–19 yaş için yurt dışı yaz okulları ve İngilizce kampları: yaşa göre gözetim ve konaklama, "
              "akademik dil dersleri ve kültürel programları karşılaştır."},
    1502: {D: "Yurt dışında kısa süreli İngilizce dil okulu: sınav öncesi hızlandırma, üniversite öncesi deneyim "
              "veya iş İngilizcesi için okul, süre ve konaklama seçimi."},
    1494: {D: "İş ve aile temposuna uyan esnek takvimle yetişkinler için birebir İngilizce: seyahat, iş "
              "e-postaları ve günlük konuşma, yargılamayan bir ortamda."},
    1492: {D: "Gençler için İngilizce: konuşma, okul ve sınav hedeflerine göre bire bir, mikro grup veya birleşik "
              "dersler. Öğrenci derste aktif, veli süreçten haberdar."},
    1488: {D: "Toplantı, mülakat, e-posta ve müzakere için sektörüne özel İş İngilizcesi. 60 saniyelik öz "
              "değerlendirmeyle nereden başlaman gerektiğini gör."},
    1479: {D: "“Anlıyorum ama konuşamıyorum” diyorsan: birebir konuşma pratiği, telaffuz çalışması ve konuşmayı "
              "kesmeden düzeltmeyle Konuşma İngilizcesi dersleri."},
    1476: {D: "TOEFL Speaking için kısa hazırlık süresinde net yanıt kurma, entegre görevlerde özetleme ve zaman "
              "yönetimi. 2 dakikada hazırlık aşamanı gör."},
    1474: {D: "IELTS Speaking'in dört ölçütü (akıcılık ve tutarlılık, kelime, dilbilgisi, telaffuz) üzerine "
              "birebir pratik ve geri bildirim."},
    1472: {D: "ÖSYM YDS için dilbilgisi, kelime bilgisi ve çeviri odaklı sistemli hazırlık. 3 kısa soruyla hedef "
              "puan aralığına göre nerede olduğunu gör."},
    1466: {D: "Dijital SAT'ın Reading & Writing ve Math modüllerine, adaptif yapıya uygun hazırlık: konu tekrarı, "
              "düzenli deneme ve sınav tarihine göre haftalık plan."},
    1913: {D: "Üniversite ödevi, makale, araştırma önerisi ve tez yazımı için birebir akademik yazma desteği; kendi "
              "taslağınla çalışabilirsin."},
    1638: {D: "Dil eğitimi, yurt dışı başvurusu, koçluk ve sanatı tek, şeffaf bir çatı altında sunma misyonumuz "
              "ve 2026–2036 yol haritamız."},
    1581: {D: "Üniversite adayları için sınav, başvuru ve akademik İngilizceyi tek rehberle yöneten program. Hangi "
              "aşamadaysan oradan başla; aile süreci görebilir."},
    1574: {D: "Seviyesi ve hedefi uyumlu küçük gruplarda konuşma kulübü ve IELTS bootcamp. Grup mu birebir mi, "
              "kısa yön bulmayla sana uygun olanı gör."},
    1516: {D: "Niyet mektubu, motivasyon mektubu ve personal statement için senin sesini koruyan, kanıta dayalı "
              "yapı ve geri bildirim desteği. Metin her zaman sana ait kalır."},
    1512: {D: "Göndermeden önce niyet mektubu, CV, transkript ve formlar arasında tutarlılık kontrolü: sekiz "
              "katmanlı başvuru dosyası incelemesi. Kabul tahmini değildir."},
    1503: {D: "Doktora başvurusu: araştırma önerisi, danışman teması, finansman ve zaman çizelgesi. Bir "
              "üniversiteye değil, bir danışmana başvurduğun süreci planla."},
    1505: {D: "Hangi ülke sana uygun? Bütçe, akademik geçmiş, dil ve kariyer hedefine göre 5 soruda yön bul; "
              "ülkelerin eğitim ve göç sistemlerini karşılaştır."},
    1468: {D: "PTE Academic için otomatik değerlendirmeye uygun net konuşma, özetleme ve zamanlama stratejileri; "
              "gerçek arayüze benzer denemelerle hazırlık."},
    1895: {D: "Hedef netliği, çalışma düzeni ve dönem planı için birebir akademik koçluk. 4 kısa soruyla programın "
              "hangi bileşeninden en çok fayda göreceğini gör."},
    1911: {D: "Suluboya, çizim, resim, dijital sanat veya yaratıcı yazarlık: katılmak istediğin online atölyeyi seç, "
              "kısa yön bulmayla sana uygun olanı belirle."},
    3609: {D: "Bütçen yetmediği için eğitimin yarım kalmasın: Bir Adım İyilik ücretsiz ve indirimli kontenjanına "
              "kısa bir formla başvur. 18 yaş altında veli onayı gerekir."},
    1496: {D: "Hedefine, seviyene ve tempona göre online bire bir İngilizce: sana uygun öğretmen, amacı belli "
              "dersler ve kullanabildiğin İngilizceyle ölçülen gelişim."},
    1899: {D: "IELTS, TOEFL, SAT gibi sınavlar ya da yoğun bir okul dönemi için gerçekçi, haftalık çalışma planı "
              "desteği. Plan ilerlemene göre düzenli güncellenir."},
    1908: {D: "Tablet ve dijital araçlarla illüstrasyon ve karakter tasarımı: gençler için online dijital sanat "
              "atölyesi. Atölye İngilizce yürütülür; çizim tableti gerekir."},
    1498: {D: "4–6 kişilik mikro gruplarda online İngilizce: konuşma alanı geniş, seviyesi uyumlu gruplar. 4 kısa "
              "soruyla hangi grup formatının sana uygun olduğunu gör."},
    1912: {D: "IELTS Writing Task 1 ve Task 2 için resmî ölçütlere göre kriter bazlı geri bildirim, ezber kalıp "
              "yerine esnek yapı ve tekrarlı pratik."},
    1910: {D: "Suluboya, çizim, resim, dijital sanat ve yaratıcı yazarlığı İngilizceyle birleştiren online "
              "atölyeler. 5 soruda hangi atölyenin sana uygun olduğunu gör."},
    1893: {D: "Yurt dışında lisans başvurusu: sınav takvimi, erken ve normal başvuru dönemleri, burs takvimi ve "
              "dosya hazırlığı. Genellikle 10–11. sınıfta planlamaya başlanır."},
    1566: {D: "Genel, akademik, iş ve konuşma İngilizcesi: kullanım amacına, yaşına ve öğrenme biçimine göre "
              "İngilizce programını seç; bire bir mi mikro grup mu karar ver."},
    1571: {D: "“Anlıyorum ama konuşamıyorum” diyorsan: akıcılık, telaffuz ve anlık iletişim üzerine "
              "birebir İngilizce Konuşma Programı; hatalar konuşmayı kesmeden ele alınır."},
    1573: {D: "Toplantı, sunum, iş görüşmesi ve yazışma için sektörüne uygun birebir İş İngilizcesi Programı: "
              "gerçekçi simülasyonlarla iş hayatını derste prova et."},
    1563: {D: "IELTS, TOEFL, SAT ve diğer sınavlar için hangi sınava, hangi takvimle ve hangi yoğunlukta "
              "hazırlanacağını belirleyen bireysel sınav programları."},
    1577: {D: "İngilizce, sınav hazırlığı, yurt dışı eğitim ve burs için seçilmiş ücretsiz araçlar ve rehberler. "
              "İki soruyu yanıtla, sana uygun başlangıç noktasını gör."},
    1909: {D: "Kendi hikâyelerini İngilizce yazmak isteyen gençler için online yaratıcı yazarlık atölyesi: "
              "kurgu, kelime ve anlatım becerisi bir arada."},
    1894: {D: "Yüksek lisans başvurusu: program seçimi, SOP, referanslar ve belgeler. 4 kısa soruyla dosyanın "
              "nerede olduğunu ve sıradaki adımı gör."},
    # Technical: noindex was saved as "1", which SureRank ignores (it expects "yes")
    4008: {"post_no_index": "yes"},
}

_BACKUP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backup", "live-2026-10-19.json.gz")


def _changes():
    b = json.load(gzip.open(_BACKUP, "rt", encoding="utf-8"))
    types = {p["id"]: p["type"] for p in b["pages"] + b["posts"]}
    out = {}
    for pid, new in NEW.items():
        old = b["surerank_post"][str(pid)]
        before, after = {}, {}
        for k, v in new.items():
            before[k], after[k] = old.get(k), v
            social = {T: ("facebook_title", "twitter_title"), D: ("facebook_description", "twitter_description")}
            for s in social.get(k, ()):
                if old.get(s) == old.get(k):
                    before[s], after[s] = old.get(s), v
        out[pid] = (types[pid], before, after)
    return out


CHANGES = _changes()
