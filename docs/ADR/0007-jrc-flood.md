# ADR-0007 — JRC Global Flood Hazard lisans kapısı

- Tarih: 2026-11-22
- Durum: Kabul

JRC Global Flood Hazard verisi EC open data kataloğunda; proje ticari ürün
hedefli olduğu için lisans koşulları (atıf/türev kullanımı) bu turde
doğrulanamadı. SYGM taşkın proxy'si korunur; JRC verisi ürüne gömülmez.
docs/capraz_kontrol.md'de "yok" etiketli.

## V5 son deneme (2026-11-22)
Üç basamak denendi: (1) `usbs.tarimorman.gov.tr/services/wms` GetCapabilities
60 sn timeout; (2) SYGM resmî TYP PDF 404, ÇB `webdosya` yansısı okundu
(313 K karakter) fakat haritalar raster, vektör 1/100–500 yıl paftası yok;
(3) JRC GloFAS verisi mevcut ancak GEE erişimi gerekiyor (kimlik bekliyor).
**Karar:** ADR kalıcı; F bileşeni TWI/HAND + OSM akarsu proxy olarak kalır.
2009 "Ağır" noktalarıyla ≥%60 çakışma testi gerçek poligon olmadan
yapılamadı; bu açıkça raporlanır. Kanıt: `docs/kanit.md` U12 kaydı.
