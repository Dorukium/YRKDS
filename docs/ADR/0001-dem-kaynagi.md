# ADR-0001 — DEM kaynağı: Copernicus GLO-30 yerine AWS Terrarium

- Tarih: 2026-11-22
- Durum: Kabul

## Bağlam
Spesifikasyon Copernicus GLO-30 DEM istiyor; DATASPACE erişim bilgisi sağlanmadı.
Kurumlara resmi veri talebi gönderilemez (orijinal görev kısıtı).

## Karar
Anahtarsız AWS Terrarium (SRTM-türevli, zoom 13) kullanıldı. Kaynak etiketi
hiçbir yerde "Copernicus" olarak yazılmıyor; `kaynak_dem` alanı ve kanıt
zincirinde "AWS Terrarium (SRTM-derived)" deniyor.

## Sonuçlar
- Copernicus'a özgü radyometrik farklar ve 30 m nominal çözünürlük yerine
  ~19 m SRTM türevi kullanılıyor.
- İlk uygulamada tile sınır hatası grid'in %22'sini NaN bıraktı; düzeltildi
  (120 tile, NaN=0), kanıt: `tests/test_hydro.py::test_gercek_gridde_turevler_sonlu_ve_aralikta`.
- K5 manifest: `data/raw/dem_kaynak.json`.
