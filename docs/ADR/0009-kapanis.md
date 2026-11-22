# ADR-0009 Kapanış — A1 NASA Earthdata / ARIA S1 GUNW

- Tarih: 2026-11-22
- Durum: **KAPANDI** (ADR-0009 yerine bu kayıt geçerlidir)

## Uygulama
- NASA Earthdata hesabı (.env) ile `earthaccess` girişi yapıldı.
- ASF DAAC EULA'sı programatik olarak kabul edildi; granül erişimi HTTP 206 doğrulandı.
- `ARIA-S1_GUNW` koleksiyonundan Antalya AOI (30.58–30.86D, 36.82–37.00K),
  2021–2026 için **40 granül** indirildi (4.9 GB, SHA256 manifest'te).
- Her interferogramda AOI kırpma, koherens maskesi (≥0.15), düzlemsel yörünge
  rampası çıkarımı, C-band λ=0.05546576 m ile LOS displacement ve mm/yıl hız.
- 40 granül ağırlıklı yığınlandı; 25 m grid'e warplandı.
- Radar gölgesi boşlukları en yakın komşu ile dolduruldu ve ayrı
  `insar_aria_validity.tif` maskesiyle **Proxy** etiketlendi (K3).

## Sonuç
- Toplam kapsam **%100**, otorite kapsamı **%79.19**, proxy %20.81.
- Örnek hücreler: -7.83, -6.25, +12.54 mm/yıl.
- S alt puanı artık gerçek ölçümle hesaplanıyor; `skor_kapsami.tur = "tam"`.
- Proxy hücrelerde güven ek %10 cezalandırılıyor ve kanıt rozeti "Proxy".

Kanıt: `docs/kanit.md`, `docs/kanit/insar_kapsam.png`, `data/processed/insar_aria.json`.
