# ADR-0003 — Bağımsız doğrulama verisi ve Antalya InSAR eksikliği

- Tarih: 2026-11-22
- Durum: Kabul (kısmi)

## Bağlam
K4 uyarınca kalibrasyon (2009) ve doğrulama (2003+2008) verileri ayrık
olmalı. 2003/2008 olayları için mahalle düzeyi etiket listesi bulunamadı
(3.13'te yalnızca "500 ev", "3000 dekar sera" gibi toplu etki ifadeleri var).
Antalya'ya özgü yayınlanmış InSAR mm/yıl değeri de bulunamadı.

## Karar
- 2009 etiketleri kalibrasyon olarak dondurulur; doğrulama seti için
  **etiket üretilmez** (uydurma yasak).
- Mevcut `tests/test_2009_backtest.py` açıkça "kalibrasyon + bağımsız olmayan
  doğrulama" olarak etiketlenir; yeni `test_independent_validation.py` bu
  durumu test eder ve gerçek doğrulama verisi gelene kadar KIRMIZI/beklenen
  uyarı üretir.
- S bileşeni için literatür proxy'si (Karapınar 15–70 mm/yıl) **kullanılmaz**;
  coğrafi olarak yanlış olurdu. `insar_hiz=NULL` kalır.

## Sonuçlar
K2 alternatif ölçüm: sentetik HAND vadi testleri (`tests/test_hydro.py`) ve
2009 kalibrasyon metrikleri üretildi. Bağımsız Recall hedefi (≥0.60) bu ADR
kapsamında **doğrulanamadı**; raporda dürüstçe belirtilir.

## V5 son durum (2026-11-22)
GEE kimlik dosyası oluştu fakat hesap Earth Engine'e kayıtlı değil
(`ee.Initialize()` → "project is not registered"). Bu nedenle L1 GFD erişilemedi.
GEE'siz alternatif olarak GFD GeoTIFF bucket'ı (`gfd_v1_4`) doğrudan tarandı:
**913 olayın hiçbiri Antalya AOI'sinde değil**; tarih eşleşenler Endonezya
(2403) ve Avustralya'ya (3257) ait. Sentinel-1 2014 öncesi veri içermez;
literatürde jeoreferanslı nokta etiketi yok. 4 deneme kaydı
`data/labels/gfd_2003_2008_manifest.json`'de. K4 korundu: 2009 (18 nokta)
yalnızca kalibrasyon, doğrulama etiket sayısı 0 → Recall hesaplanmadı.
**Karar:** ADR kalıcı açık; Zenodo DOI `10.5281/zenodo.24449066` ile yayımlanan
sürümde bu eksiklik açıkça belirtilir.
