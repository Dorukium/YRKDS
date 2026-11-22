# ADR-0011 — D2 SYGM 100/500 yıllık pafta sayısallaştırma

- Tarih: 2026-11-22
- Durum: Kabul (kısmi)

## Bağlam
D2, Antalya Havzası TYP PDF'inden 1/100 yıl paftalarını jeoreferansla
sayısallaştırmayı ve USBS WMS'i doğru capabilities ayrıştırmasıyla denemeyi
istiyor.

## Denemeler
- TYP PDF URL'si Firecrawl'da 404 sayfası; yerel indirme TLS/kesilme hatası.
- SÇD taslak PDF'i (149 sf) okundu; 100/500 yıllık sayısal tablo yok.
- USBS WMS GetCapabilities: curl ve Firecrawl proxy üzerinden erişilemedi.

## Karar
Otorite taşkın katmanı eklenemez. F bileşeni DEM TWI/HAND + OSM akarsu +
kayıtlı olay proxy'si olarak kalır; katalogda "Proxy" rozeti, yasal taşkın
yasağı "Eksik" rozeti. 2009 Ağır noktalarının ≥%60 kapsam hedefi
**doğrulanamadı**; sayısal iddia üretilmez.

## Kabul testi
Bu ADR + docs/capraz_kontrol.md + test_v2'de rozet/kapsam testleri.
