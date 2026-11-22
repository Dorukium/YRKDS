# ADR-0025 — V4 kalan veri eksiklikleri

- Tarih: 2026-11-22
- Durum: Kabul (dürüst etiketli)

## A2 — 2003/2008 bağımsız doğrulama
GEE kimlik bilgisi yok; ARIA S1 GUNW (A1) yardımıyla 2003/2008 için
SAR değişim tespiti bu sprintte tamamlanamadı. Koordinatlı etiket
üretilmedi; `bagimsiz_mi=False` ve Recall hedefi doğrulanmadı kalır
(ADR-0003/0018 güncel).

## A7 — SYGM/JRC taşkın paftası
SYGM WMS erişilemedi, TYP PDF'i 404; JRC lisans kapısı doğrulanamadı
(ADR-0011/0007). F bileşeni TWI/HAND + OSM akarsu proxy'si olarak kalır.

## A3 — yasal geometri
Üç gerçek kararın geometrisi Nominatim tabanlı **geocode proxy** olarak
üretildi (ADR-0017); resmi ek harita sınırları temin edilince değiştirilir.

Tüm eksikler katalog rozetleriyle ("Eksik"/"Proxy"/"Araştırma") kullanıcıya
gösterilir; uydurma sayı üretilmez (K3).
