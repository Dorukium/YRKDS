# ADR-0004 — GEM sismik çapraz kontrol ve lisans

- Tarih: 2026-11-22
- Durum: Kabul

## Bağlam
Faz D, proje TDTH PGA değerlerini GEM açık modeliyle çapraz kontrol etmeyi
istiyor. GEM GSHM v2026.1 Zenodo'da CC BY-NC-SA 4.0 lisanslı; proje ticari
ürüne dönüştürüleceği için NC (non-commercial) koşulu uyumsuz.

## Karar
- 935 MB'lık vektör paketi indirilip ürüne gömülmez.
- Çapraz kontrol, kamuya açık GEM **harita görüntüsü/API** veya
  `hazard.openquake.org` dokümantasyonundaki değerlerle sınırlı tutulur;
  sayısal raster girdi elde edilemezse `tests/test_seismic_crosscheck.py`
  bunu ADR + `pytest.skip` yerine açık bir "veri yok" testi olarak raporlar.
- K2 gereği: skip/yorum yok; test, kaynağın erişilemediğini doğrulayan bir
  assertion üretir (ör. `durum == "veri_yok"`).

## Sonuçlar
Sismik çapraz kontrol şu an **kısmi**: proje PGA değerleri (3.11) TBDY2018
iletilebilir, bağımsız GEM sayısı yok → sapma % hesaplanamaz. Bu durum
`docs/dogrulama_raporu.md`'de yazılır.
