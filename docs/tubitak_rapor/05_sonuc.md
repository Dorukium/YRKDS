# 5. Sonuç, Öneriler ve Gelecek İş

## 5.1 Sonuç

Proje, Antalya merkez üç ilçede parsel bazlı afet riski ön-tarama yapabilen
deterministik bir karar destek platformu üretmiştir. Sistem 25 metrelik
ortak ızgarada beş tehlike bileşeni hesaplar, yasal kısıt kurallarını
skordan bağımsız uygular, her sayının kaynağını kanıt zincirinde gösterir
ve eksik veriyi güven cezasıyla raporlar. ML modeli eğitilmemiş, uydurma
sayı üretilmemiştir.

Teknik açıdan sistem olgun bir prototiptir: FastAPI arka uç, PostGIS
veritabanı, PyO3 ile bağlanmış Rust skor motoru, Leaflet tabanlı harita,
sunucu tarafı tile'lar, PDF raporları, portföy raporu, what-if önlemler,
gömme widget ve PWA saha modu çalışır durumdadır. Tüm kalite kapıları tek
komutla yeşil döner; kod, dokümantasyon ve kanıt günlüğü birlikte
sürdürülür.

Bilimsel açıdan sonuçlar temkinli yorumlanmalıdır. 2009 seli için elde
edilen yüksek Recall değeri, aynı olaydan gelen 17 noktaya dayanır ve geniş
güven aralığına sahiptir. Bağımsız 2003/2008 doğrulaması gerçekleştirilememiştir.
InSAR hızı, resmi taşkın paftaları ve TDTH ızgara verisi erişilemediği için
S bileşeni ve bazı F/PGA girdileri NULL kalmıştır. Bu eksiklikler gizlenmemiş;
ADR'ler, yetkinlik rozetleri ve kullanıcı arayüzündeki uyarılarla açıkça
bildirilmiştir.

## 5.2 Öneriler

Belediye pilotuna geçiş öncesinde üç öncelik önerilir. Birincisi,
Copernicus EGMS kimlik bilgilerinin temin edilmesi ve Ortho LOS hız
ürününün AOI'ye indirilmesidir. Bu, S bileşenini gerçek ölçüme
kavuşturacak ve skorun en zayıf halkasını güçlendirecektir. İkincisi, SYGM
Antalya Havzası Taşkın Yönetim Planı'nın 1/100 yıllık paftalarının
jeoreferanslı olarak temin edilmesidir; böylece F bileşeni proxy'den
otorite katmana yükseltilebilecektir. Üçüncüsü, e-Devlet TDTH hizmetinden
2 km çözünürlüklü PGA/Ss/S1 ızgarasının alınmasıdır; mevcut GEM verisi
yalnızca araştırma etiketiyle çapraz kontrol olarak kalmalıdır.

Yasal VETO katmanları için geocode proxy geometrileri geçici çözümdür.
Resmî Gazete ek haritalarının veya belediye imar planlarının temini ile
bu geometriler gerçek sınırlarla değiştirilmelidir. What-if önlem
katsayıları ve beklenen kayıp katsayıları da uzman varsayımıdır; resmi
birim fiyatlar ve hasar fonksiyonlarıyla güncellenmelidir.

## 5.3 Gelecek iş planı

Kısa vadede A1 (EGMS), A2 (bağımsız olay etiketi) ve resmi VETO geometrileri
tamamlanmalı; her tamamlanan veri katmanı için yetkinlik rozeti "Otorite"
seviyesine yükseltilmelidir. Orta vadede portföy raporuna resmi hasar
eğrileri entegre edilmeli, belediye iç kullanıcıları için rol tabanlı
erişim genişletilmeli ve saha mobil uygulaması çevrimdışı senkronizasyonla
test edilmelidir. Uzun vadede, birikmiş sorgu ve etiket verileriyle
denetimli bir model değil, yalnızca eşik optimizasyonu yapılabilir; ML
eğitimi, ancak yeterli ve bağımsız etiket oluştuğunda gündeme alınmalıdır.

Projenin ticari ürüne dönüştürülmesi hedefi göz önüne alındığında,
lisans yönetimi ayrı bir önem taşımaktadır. GEM verisi CC BY-NC-SA olduğu
için ürüne gömülmemiş, yalnızca araştırma etiketiyle referans verilmiştir.
Ticari dağıtım öncesinde veri lisanslarının yeniden denetlenmesi gerekir.
Zenodo DOI alınmış, `CITATION.cff` ve CHANGELOG v5.0.0 ile güncellenmiştir
(bkz. `10.5281/zenodo.24449066`). Bağımsız 2003/2008 etiketi bulunamadığı
için Recall ≥0.60 hedefi doğrulanmamıştır; bu eksiklik sonuç bölümünde
açıkça belirtilmiştir.

## 5.4 Kapanış

Bu çalışma, bilimsel dürüstlüğün bir ürün özelliği olabileceğini göstermiştir.
Eksik veriyi gizlemek yerine etiketlemek, belirsizliği gizlemek yerine
aralıkla sunmak ve her kararın gerekçesini kaydetmek, sistemin güvenilirliğini
azaltmaz; aksine onu denetlenebilir kılar. Jüri değerlendirmesinde ve
belediye pilotunda bu yaklaşımın korunması önerilir.
