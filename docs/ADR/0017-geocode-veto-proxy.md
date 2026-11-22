# ADR-0017 — Resmî Gazete kararları için geocode proxy geometri (A3)

- Tarih: 2026-11-22
- Durum: Kabul

## Bağlam
Üç gerçek karar bulundu:
- 2016/9615, RG 03.01.2017/29937 — Kepez / Gülveren riskli alan
- 2014/7041, RG 25.12.2014/29216 — Kepez / Santral riskli alan
- 11600, 10.08.2026 — Konyaaltı / Hisarçandır afete maruz bölge

Karar metinlerinde jeoreferanslı sınır/pafta kamuya açık değil.

## Karar
Yer adları Nominatim ile geocode edildi (1 istek/sn); mahalle merkezine
300 m tampon uygulandı. `legal_constraints` tablosuna **geocode proxy** olarak
eklendi; `konum_guveni=dusuk (geocode proxy)` ve kaynak URL her kayıtta var.
VETO motoru bu geometrileri okur; kullanıcıya proxy olduğu açıkça bildirilir.

## Sonuç
A3 DoD'si "en az 3 gerçek kararın geometrisi" şeklinde karşılandı; ancak
geometriler **resmi sınır değildir**. ADR-0002'deki yanlış pozitif riski,
küçük tampon + düşük güven etiketi + görsel uyarı ile sınırlandırıldı.
