# ADR-0019 — What-If önlem katsayıları (B1)

- Tarih: 2026-11-22
- Durum: Kabul

## Bağlam
B1, dört önlemin skor deltasını ve maliyet etkisini istiyor. TBDY 2018 ve
İMO birim fiyatlarının resmi sayısal tabloları bu ortamda doğrulanamadı.

## Karar
Göreli azaltma katsayıları sabit uzman varsayımı olarak kullanılır:
kazıklı temel S×0.50 / L×0.60; zemin iyileştirme S×0.60 / L×0.50;
yüzey drenajı F×0.60; radye S×0.70. Maliyet **ordinal** seviyedir
(düşük/orta/yüksek), TL tutarı üretilmez.

## Sonuç
Tüm çıktılar "Tahmin" rozetlidir; kullanıcıya resmi etüt/birim fiyat
doğrulaması gerektiği açıkça bildirilir. Kaynak manifest: RES-0019 (TBDY2018
kamu sayfası, erişim 2026-11-22, sha256 yok — web sayfası).
