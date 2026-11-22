# U9 — Veri Erişim Merdiveni

Her veri görevi için en az 3 basamak tanımlıdır. Bir basamak başarısızsa
bir sonrakine geçilir; karar ve sonuç bu dosyaya kaydedilir (K1/K2).

| Görev | 1. basamak (Otorite) | 2. basamak (Proxy) | 3. basamak (Eksik) | Durum |
|---|---|---|---|---|
| A1 InSAR (S) | NASA Earthdata ARIA S1 GUNW (kimlik var) | COMET LiCSAR / JASMIN arşivi | NULL + güven cezası | 1. basamak denendi |
| A2 2003/2008 etiket | GFD MODIS extent (GEE) | Sentinel-1 SAR değişim tespiti (ASF) | Literatür jeoreferans → yoksa NULL | GEE kimliği yok, 2. basamak denenecek |
| A3 yasal VETO | Resmî Gazete ek harita koordinatları | Nominatim geocode + 300 m tampon (Tahmin) | NULL VETO + önlem bölgesi | 2. basamak (3 karar) |
| A4 maruziyet | MS Buildings + WorldPop (STAC) | OSM bina + TÜİK ilçe nüfusu | NULL | 1. kısmi bina / 2. nüfus |
| A5 iklim ekstremi | MGM istasyon günlük serisi | ERA5/Open-Meteo ızgara (Proxy) | NULL | 2. basamak |
| A6 PGA | e-Devlet TDTH 2 km ızgara (insan adımı) | GEM/OpenQuake (Araştırma) + USGS Vs30 | NULL | 2. basamak |
| A7 taşkın | SYGM 100/500 yıllık pafta / WMS | JRC Global Flood + DFO | DEM TWI/HAND proxy (mevcut) | 2/3. basamak |
| A8 parsel | TKGM WFS/REST | Tarayıcıdan WKT/GeoJSON aktarım sihirbazı | Manuel koordinat girişi | 1. basamak araştırılıyor |
| DEM | Copernicus GLO-30 (ANAHTARSIZ S3) | AWS Terrarium (mevcut, Proxy) | NULL | 2. basamak |

## Karar kayıtları
- 2026-11-22: A1 için kullanıcı NASA Earthdata hesabını sağladı; ASF DAAC EULA programatik kabul edildi, granül erişimi HTTP 206 ile doğrulandı.
- 2026-11-22: A2 için GEE kimliği yok; Sentinel-1 alternatifi ASF üzerinden denenecek.
- 2026-11-22: A6 için e-Devlet insan adımı; ajan beklerken GEM+USGS çapraz kontrolü kuruldu (docs/sop_tdth.md).
