# ADR-0004 — GEM sismik çapraz kontrol ve lisans

- Tarih: 2026-11-22
- Güncelleme: 2026-11-22 (V5 — TDTH kaynağı deaktif)
- Durum: **Kalıcı açık — kaynak deaktif, alternatif çapraz kontrol kullanıldı**

## V5 Güncellemesi — TDTH deaktif
`tdth.afad.gov.tr` erişilemiyor/deaktif. Kullanıcı kararı gereği **başka erişim
denemesi yapılmaz** (U12: 3 deneme şartı bu kaynak için geçerli değildir;
kaynakın kendisi kapalıdır). Bu ADR kalıcı açık kalır.

- PGA katmanı: **GEM OpenQuake + USGS Vs30 çapraz kontrol**, "Araştırma" rozeti.
- `docs/sop_tdth.md` site geri geldiğinde uygulanmak üzere **hazır tutulur**;
  `make data-tdth` o an otorite katmanına yükseltir.
- DoD: yeni TDTH denemesi yok; alternatif rozetli katman korunur.

Kanıt (U11): `make check-auth` → `tdth: deaktif`; komut `git log -1`;
commit hash kanıt günlüğünde.

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
