# Çapraz Kontrol Raporu (Ek plan Bölüm 6)

Tarih: 2026-11-22. Manifest: `data/raw/enrichment_manifest.json` (URL + erişim tarihi + SHA256 + lisans).
Çıktılar birincil kaynakların **yerine geçmez**; yalnızca tutarlılık denetimidir.

| # | Veri | Kaynak | Durum | Sonuç |
|---|---|---|---|---|
| 1 | USGS Global Vs30 | earthquake.usgs.gov ArcGIS | Kısmi | Servis metadatası alındı (SHA256 var); nokta sorgusu 400 → ADR-0005. Vs30 vekili kullanılmıyor. |
| 1b | GEM GSHM v2023.1 PGA | Zenodo / OpenQuake (kullanıcı kararı) | Araştırma | 3 ilçede sapma %20–78 → ADR-0008; resmi TDTH yerine geçmez. |
| 1c | SoilGrids WCS 250 m | maps.isric.org | Otorite | 5 katman, soc %100, SHA256 manifest; IDW kaldırıldı. |
| 2 | NASA Global Landslide | GES DISC | Yok | Erişim/lisans doğrulanamadı → ADR-0006 (yalnızca referans). |
| 3 | JRC Global Flood Hazard | JRC Data Catalogue | Yok | Lisans kapısı (EC open data) doğrulanamadı → ADR-0007. |
| 2b | SYGM 100/500 yıllık pafta | webdosya.csb.gov.tr / USBS WMS | Yok | PDF 404, WMS erişilemedi → ADR-0011; F proxy olarak kalır. |
| 4 | ESA WorldCover 10 m | Planetary Computer STAC (`esa-worldcover`) | ✅ | CC-BY-4.0; çalışma alanında 5 STAC item. Arazi örtüsü katmanı referansı; primere girmez. |
| 5 | Microsoft Building Footprints | Planetary Computer STAC (`ms-buildings`) | ✅ | ODbL-1.0; çalışma alanında 5 STAC item. OSM boşlukları için referans. |
| 6 | UNESCO-IOC tsunami | IOC database | Yok | Bu turde erişilmedi; AD 68 olayı proje veri setinde mevcut. |
| 7 | MGM ekstrem kayıtları | mgm.gov.tr | Yok | Kamu sayfası erişimi doğrulanamadı → ADR-0012; 331.5 mm yalnızca proje veri setinde. |
| 8 | KOERI katalog | koeri.boun.edu.tr | ✅ | `koeri_katalog.txt` indirildi (SHA256); AFAD kataloğu ile karşılaştırmaya hazır. |
| 9 | VIIRS gece ışıkları | NOAA / Planetary Computer | Yok | Opsiyonel; bu turde entegre edilmedi. |

## Yöntem
Her kaynak için `app/data_pipeline/download_enrichment.py` ağ isteği yapar,
yanıtı `data/raw/` altına yazar ve SHA256 özetini manifeste ekler. Hata durumunda
`sha256: null` + hata metni yazılır (K3/K5).

## Sapma
Birincil sayısal katmanlarla karşılaştırma yapılamayan kaynaklarda sapma yüzdesi
hesaplanmaz; "veri yok" etiketi kullanılır. Sapma >%20 olsaydı ADR yazılacaktı.
