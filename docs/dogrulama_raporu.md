# Doğrulama Raporu (Faz C + D)

Tarih: 2026-11-22. K1 kanıt günlüğü bu raporu takip eder.

## 1. Taksonomi

| Terim | Anlamı | Bu projede durumu |
|---|---|---|
| Kalibrasyon | Eşikleri belirlemek için kullanılan veri | 2009 ANT-2009 etiketleri (17 pozitif) |
| Doğrulama | Eşikler dondurulduktan sonra kullanılan ayrık veri | **YOK** — 2003/2008 mahalle etiketi bulunamadı (ADR-0003) |
| Mekansal hold-out | Aynı olayın farklı ilçelerde ayrılması | Var; olay bazlı bağımsız değil |

**K4 ihlali yok:** Eşikler hiçbir zaman "doğrulama" olarak adlandırılan bir
sette değiştirilmedi; çünkü böyle bir set oluşturulmadı. `bagimsiz_mi=False`
açıkça raporlanır.

## 2. 2009 kalibrasyon + mekansal blok sonuçları

Precision 0.941 · Recall 0.941 · F1 0.941 · Wilson %95 CI [0.730, 0.990].
İlçe blokları (leave-one-district-out): Kepez, Muratpaşa, Konyaaltı, Aksu,
Döşemealtı.

## 3. 2003 Boğaçay / 2008 Kundu

3.13'te yalnızca toplu etki ifadeleri var ("500 ev su bastı", "3000 dekar
sera"). Faz A'da yapılan aramalarda mahalle düzeyi koordinatlı etiket
bulunamadı. Etiket üretilmedi (uydurma yasak). Bu nedenle **bağımsız Recall
≥0.60 hedefi doğrulanamadı**; ADR-0003'te dürüstçe kaydedildi.

## 4. Sismik çapraz kontrol (Faz D)

GEM GSHM v2026.1 PGA haritası Zenodo'da CC BY-NC-SA 4.0 ile yayımlandı
(DOI 10.5281/zenodo.8409646). Proje ticari ürün hedefli olduğu için bu
lisansla sayısal raster gömülemez (ADR-0004). Sonuç: **bağımsız PGA sapma
yüzdesi hesaplanamadı**; proje PGA değerlerinin iç tutarlılığı test edildi.
