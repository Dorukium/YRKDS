# ADR-0018 — A2 bağımsız 2003/2008 etiketleri (ADR-0003 güncelleme)

- Tarih: 2026-11-22
- Durum: Kabul (kısmi — K2 alternatif ölçüm)

## Denenen yöntemler
1. **Global Flood Database (Dartmouth/MODIS):** GEE `GLOBAL_FLOOD_DB/MODIS_EVENTS/V1`
   koleksiyonu yalnızca Earth Engine kimlik doğrulamasıyla erişilebilir; bu
   ortamda GEE hesabı/yetkilendirmesi yok.
2. **Sentinel-1 SAR değişim tespiti:** aynı şekilde GEE (`COPERNICUS/S1_GRD`)
   gerektirir; yerel alternatif indirilmedi.
3. **Literatür jeoreferans:** 2003 Boğaçay / 2008 Kundu için mahalle düzeyi
   koordinatlı etki haritası bulunamadı (Firecrawl, 2026-11-22).

## Karar
2003/2008 için **etiket üretilmedi** (uydurma yasak). `bagimsiz_mi=False` açık
kalır. K2 alternatif ölçüm olarak 2009 etiketleri üzerinde **ilçe bloklarıyla
leave-one-district-out** mekansal ayrım kullanılır ve Wilson CI raporlanır; bu,
olay bazlı bağımsız doğrulama **değildir**.

## DoD durumu
Recall ≥0.60 hedefi 2003+2008 için **doğrulanamadı**. Test bunu kanıtlar;
eşik kaydırma yapılmadı (git geçmişi: kalibrasyon eşikleri 0.7/6/5/2 sabit).

## V5 güncellemesi (2026-11-22)
L1 artık iki yolla denendi: GEE (hesap EE'ye kayıtlı değil) **ve** GFD GeoTIFF
bucket'ının doğrudan taranması (913 olay, AOI'de 0). L2 fiziksel olarak
olanaksız (S1 2014+), L3 literatürde koordinatlı etiket yok. 4 denemeli kanıt:
`data/labels/gfd_2003_2008_manifest.json`. Etiket üretilmedi; ADR kalıcı.
