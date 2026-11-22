# ADR-0008 — GEM PGA ile proje TDTH değerleri sapması

- Tarih: 2026-11-22
- Durum: Kabul
- Kullanıcı kararı: AFAD kamu WMS'e erişilemediği için GEM **araştırma** etiketiyle kullanılacak.

## Bulgu
GEM GSHM v2023.1 PGA (475 yıl, Vs30=800 kaya) ile proje veri setindeki
ilçe PGA değerleri:

| İlçe | GEM (g) | Proje (g) | Sapma |
|---|---|---|---|
| Kepez | 0.233 | 0.28 | %20.2 |
| Muratpaşa | 0.236 | 0.33 | %56.8 |
| Konyaaltı | 0.233 | 0.42 | %77.8 |

## Açıklama
GEM değeri **kaya referansı (Vs30=800)** içindir; proje değerleri TBDY2018
zemin sınıfına göre büyütülmüş (Kepez ZB, Muratpaşa ZC, Konyaaltı ZD/ZE)
sonuçlardır. Bu nedenle sapmanın büyük olması beklenir ve modellerin
çeliştiği anlamına gelmez. Yine de >%20 olduğu için bu ADR zorunludur (plan D3).

## Karar
GEM yalnızca **araştırma rozeti** ile çapraz kontrol olarak saklanır; resmi
TDTH grid'i gelene kadar PGA hücre bazında NULL kalır, güven cezası sürer.
Aksu/Döşemealtı için proje PGA değeri yok → sapma hesaplanamadı ("bilinmiyor").
