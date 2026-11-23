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

## V5.1 — JRC gerçek rasteri (2026-11-23)
GEE projesi sağlandıktan sonra `JRC/CEMS_GLOFAS/FloodHazard/v2_1` erişilebildi
(264 tile; lisans: kullanım/dağıtım kısıtsız → **Otorite** rozeti). RP100 ve
RP500 tehlike maskeleri AOI için 93 m GeoTIFF olarak indirildi
(`data/processed/jrc_flood_rp{100,500}.tif`, SHA256 manifest'te);
`make data-jrc` tekrarlanabilir.

**Çakışma testi sonucu:** 2009 "Ağır" noktalarının **0/6**'sı JRC RP100 alanı
içinde (oran %0.00; en yakın tehlike hücresi 1.0–2.8 km uzakta). Küresel
nehir-taşkın modeli, Boğaçay'daki yerel plüvyal/ani taşkını temsil etmiyor.
**DoD (≥%60) sağlanmadı** → ADR açık kalır; uydurma çakışma üretilmedi.
Kanıt: `data/processed/jrc_overlap_report.json`, `docs/kanit.md`.
