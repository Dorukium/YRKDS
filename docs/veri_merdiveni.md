# U9 — Veri Erişim Merdiveni

Her veri görevi için en az 3 basamak tanımlıdır. Bir basamak başarısızsa
bir sonrakine geçilir; karar ve sonuç bu dosyaya kaydedilir (K1/K2).

| Görev | 1. basamak (Otorite) | 2. basamak (Proxy) | 3. basamak (Eksik) | Durum |
|---|---|---|---|---|
| A1 InSAR (S) | NASA Earthdata ARIA S1 GUNW (kimlik var) | COMET LiCSAR / JASMIN arşivi | NULL + güven cezası | 1. basamak denendi |
| A2 2003/2008 etiket | GFD MODIS extent (GEE, 2000+) | Literatür jeoreferansı (2003/2008 raporları) | NULL + ADR-0003 (U12) | GEE kimliği kullanıcı onayında; S1 basamağı tarihsel olarak olanaksız |
| A3 yasal VETO | Resmî Gazete ek harita koordinatları | Nominatim geocode + 300 m tampon (Tahmin) | NULL VETO + önlem bölgesi | 2. basamak (3 karar) |
| A4 maruziyet | MS Buildings + WorldPop (STAC) | OSM bina + TÜİK ilçe nüfusu | NULL | 1. kısmi bina / 2. nüfus |
| A5 iklim ekstremi | MGM istasyon günlük serisi | ERA5/Open-Meteo ızgara (Proxy) | NULL | 2. basamak |
| A6 PGA | e-Devlet TDTH 2 km ızgara (insan adımı) | GEM/OpenQuake (Araştırma) + USGS Vs30 | NULL | 2. basamak |
| A7 taşkın | SYGM 100/500 yıllık pafta / WMS | SYGM/ÇB TYP PDF aynaları → JRC GloFAS (GEE, gerçek raster) | DEM TWI/HAND proxy (mevcut) | 3/3 denendi + JRC raster; çakışma 0/6 → ADR-0007 kalıcı |
| A8 parsel | TKGM WFS/REST | Tarayıcıdan WKT/GeoJSON aktarım sihirbazı | Manuel koordinat girişi | 1. basamak araştırılıyor |
| DEM | Copernicus GLO-30 (ANAHTARSIZ S3) | AWS Terrarium (mevcut, Proxy) | NULL | 2. basamak |

## Karar kayıtları
- 2026-11-22: A1 için kullanıcı NASA Earthdata hesabını sağladı; ASF DAAC EULA programatik kabul edildi, granül erişimi HTTP 206 ile doğrulandı.
- 2026-11-22: A2 için GEE kimliği yok; `earthengine-api 1.7.53` kuruldu, kullanıcı `uv run earthengine authenticate` onayını vermeli.
- 2026-11-22: **Teknik uyarı** — Sentinel-1 2014'te fırlatıldı; 2003-12-10 ve 2008-01-27 olayları için S1 verisi yok. Bu nedenle v5 merdiveninde S1 basamağı yerine literatür jeoreferansı (L2′) kullanılacak. GFD MODIS (2000+) L1 olarak geçerli.
- 2026-11-22: A6/TDTH kaynağı deaktif; ADR-0004 kalıcı açık, alternatif GEM+USGS "Araştırma" rozetli. Yeni erişim denemesi yapılmadı.
- 2026-11-22: A7 3 basamak denendi (WMS timeout, PDF 404/raster, JRC→GEE bekliyor); vektör pafta yok, F proxy kalır (ADR-0007).
- 2026-11-23: JRC GloFAS v2.1 RP100/RP500 gerçek rasteri indirildi (Otorite, 93 m). 2009 "Ağır" noktalarıyla çakışma **0/6 (%0)** → ≥%60 DoD sağlanamadı; ADR açık, F proxy kalır (data/processed/jrc_overlap_report.json).
- 2026-11-22: A3 3 basamak denendi; 11600 kararı doğrulandı ama ek sayısal sınırlar yayınlanmadı, Nominatim geocode-proxy korunur (ADR-0017).
- 2026-11-22: A6 için e-Devlet insan adımı; ajan beklerken GEM+USGS çapraz kontrolü kuruldu (docs/sop_tdth.md).
