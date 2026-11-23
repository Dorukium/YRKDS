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

## V5 son deneme (2026-11-22, U12)
11600 sayılı karar için 3 erişim yolu denendi: RG web araması, RG 2026/08–10
günlük indekslerinin taranması, haber + 1/25.000 plan kaynakları. Kararın
varlığı ve "ek sayısal sınırlar" içerdiği doğrulandı; ancak sınırlar kamuya
açık koordinat/polygon olarak yayınlanmadı. **Karar:** ADR güncellendi,
geocode-proxy geometriler korunur; "resmî sınır" iddiası yapılmaz. Gerçek
karar poligonu gelirse `legal_constraints` güncellenir. Kanıt: `docs/kanit.md`.

## V5.2 — gerçek vektör kaynağı bulundu (2026-11-23)
Antalya Valiliği AFAD yazısında (Konyaaltı Belediyesi arşivi,
`www.kas.bel.tr/Evraklar/5b56140d-5b1a-4443-8338-df6013fb9d6c.pdf`) tüm
afete maruz bölgelerin **sayısal KML/NCZ** verilerinin herkese açık paylaşımda
olduğu belirtiliyor:
`https://dosya.afad.gov.tr/index.php/s/YD7NnfBDZZzdscD` (şifre `afad123456`).
Bu, 11600 kararının resmî sınırını içeren **Otorite** kaynaktır. Sunucu bu
ortamdan `ERR_CONNECTION_CLOSED` döndüğü için indirme insan adımına alındı
(`docs/sop_tdth.md` benzeri): `docs/sop_afad_kml.md`. Veri gelince proxy →
Otorite yükseltmesi yapılır; o ana kadar ADR açık kalır. Kanıt: PDF metni
`docs/kanit.md`'de alıntılandı, SOP eklendi.
