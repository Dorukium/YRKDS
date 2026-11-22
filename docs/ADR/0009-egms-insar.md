# ADR-0009 — Copernicus EGMS InSAR erişimi

- Tarih: 2026-11-22
- Durum: Kabul (kısmi)

## Bağlam
D1, S bileşenini doldurmak için EGMS Ortho ürününden AOI LOS hızı istiyor.
EGMS ücretsiz olsa da indirme API'si kayıtlı Copernicus hesabı/GEP erişimi
gerektiriyor; bu ortamda kimlik bilgisi yok (`geohazards-tep.eu/geoserver/egms/ows`
404; EGMS Explorer etkileşimli oturum gerektiriyor).

## Karar
`insar_velocity_mm_yr` NULL kalır; S alt puanı hesaplanmaz, güven cezası uygulanır.
Hiçbir literatür/mm-yıl değeri Antalya için proxy olarak üretilmez (ADR-0003).

## Sonuçlar
D1 kabul kapası (AOI ≥%95) **karşılanamadı**; katalogda "Eksik" rozetiyle
etiketli. Kimlik sağlandığında `download_insar.py` EGMS akışına geçirilir.
