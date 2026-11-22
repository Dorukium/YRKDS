# Veri Envanteri ve Kaynak Dürüstlüğü

`data/raw/manifest.json` tüm ham dosyaları SHA256 özetleriyle listeler.
Ham veri elle değiştirilmez; tüm türetim script'lerle yapılır.

## 1. Proje veri seti

`data/raw/*.csv` (15 dosya). Kaynak: **"Proje veri seti (kullanıcı tarafından
sağlandı)"** — resmi kurumdan doğrudan indirilmiş gibi sunulmaz.
TÜİK/TDTH/AFAD/MTA/MGM atıfları orijinal brief'deki gibidir.

**AVC-1999-xxx (İstanbul Avcılar) ingest'te regex ile reddedilir.**

## 2. Açık veri indirmeleri — gerçek durum

| Katman | Kaynak | Durum | Dürüst not |
|---|---|---|---|
| DEM | AWS Terrarium zoom 13 | ✅ 120 tile | Copernicus hesabı yok. **İlk sürümde tile sınır hatası nedeniyle grid'in %22'si DEM kapsamı dışındaydı (NaN); düzeltildi, artık NaN=0.** |
| Toprak | SoilGrids v2 REST | ✅ 551 nokta | ~1.1 km aralık; geçerli oran **%32.8** (null değerler enterpolasyondan çıkarılır). 25 m hücre değerleri ölçüm değil tahmin. |
| Bina/su | OSM Overpass bbox | ✅ 68.810 / 384 | HDX 650 MB paket yerine bbox. |
| İklim | MGM + CMIP6 | ✅ | ERA5-Land CDS anahtarı yok → trend verisi yok. |
| InSAR | COMET LiCSAR | ❌ | Kimlik/LiCSBAS yok → `insar_hiz=NULL`, S bileşeni hesaplanmaz. |
| Taşkın haritası | SYGM WMS | ❌ | 100/500 yıllık bölge `NULL`. |
| TDTH grid | e-Devlet | ❌ | PGA/Ss/S1 hücre bazında `NULL`. |
| Yasal VETOkatmanları | resmi geometri | ❌ | **Dört katman da NULL.** DEM proxy'si yanlış pozitif ürettiği için kaldırıldı. |

## 3. Türetilmiş 25 m grid (799.594 hücre)

- `dem_egim`: orijinal DEM'den gradyan.
- `dem_twi`: havza doldurmalı D8 / ln(a/tanβ).
- `dem_hand`: akış yolu HAND (kanal eşiği 100 hücre).
- `soil_*`: SoilGrids noktalarından bilineer enterpolasyon + ilçe profili fallback.
- `vs30`, `zemin_sinifi`, `fay_mesafe_km`, `yass_m`, `karst_alan`,
  `gecmis_taskin_sayisi`: **ilçe bazlı türetilmiş** — parsel ölçümü değil.
- `akarsu_mesafe_m`: OSM su yolları rasterleştirme + chamfer mesafe.
- `taskin_100y/500y`, `taskin_yapi_yasagi`, `falez_cekme_mesafesi`,
  `afete_maruz_bolge`, `fay_sakinim_bandi`: **NULL (bilinmiyor)**.

## 4. Kırmızı çizgi uyumu

Uydurma sayı yok; eksik alanlar NULL. AVC-1999 hiçbir tabloya girmez.
Ham veri değiştirilmez. Mekansal blok doğrulama, rastgele CV yok.
Backtest eşiklerinin aynı etiketlerle kalibre edildiği açıkça raporlanır.
