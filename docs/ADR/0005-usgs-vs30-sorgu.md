# ADR-0005 — USGS Vs30 nokta sorgusu

- Tarih: 2026-11-22
- Durum: Kabul

## Bağlam
Ek plan, USGS Global Vs30 harita servisini Vs30 vekil çapraz kontrolü için
istedi. Servis metadatasına erişildi; `query` ve `identify` uçları bu ortamda
400 "Invalid or missing input parameters" döndürdü.

## Karar
Yalnızca servis metadatası indirilir ve manifest'te SHA256 ile saklanır.
Vs30 değeri olarak kullanılmaz; proje mikrobölgeleme/TBDY2018 sınıfı birincil
kaynak olarak kalır.

## Sonuçlar
Çapraz kontrol sayısal olarak yapılamadı; docs/capraz_kontrol.md'de "kısmi"
etiketli.
