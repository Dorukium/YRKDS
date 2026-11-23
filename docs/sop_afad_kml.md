# SOP — AFAD Afete Maruz Bölge sayısal sınırları (A3 / 11600)

Kaynak (Antalya Valiliği AFAD yazısı, `www.kas.bel.tr/Evraklar/5b56140d-...pdf`):

> "İlimizde bulunan bütün afete maruz bölgelere ait sayısal veriler (ncz, kml)
> https://dosya.afad.gov.tr/index.php/s/YD7NnfBDZZzdscD bağlantısı
> (Şifre: `afad123456`) ile paylaşılmaktadır."

Bu paylaşım, 7717 sayılı CK (16.10.2023) ve 11600 sayılı CK (10.08.2026)
kapsamındaki afete maruz bölge sınırlarının **resmî vektör** kaynağıdır.
Şu an bu ortamdan `dosya.afad.gov.tr` (193.140.127.213) bağlantısı
`ERR_CONNECTION_CLOSED` veriyor; erişim kullanıcı tarayıcısından yapılmalı.

## İnsan adımı
1. https://dosya.afad.gov.tr/index.php/s/YD7NnfBDZZzdscD adresini aç.
2. Şifre: `afad123456`.
3. Antalya / Konyaaltı / Hisarçandır–Üçoluk–Gökdere ilgili `.kml` (veya `.ncz`) dosyasını indir.
4. Dosyayı `data/raw/afad_amz_kml/` altına kopyala. **Düzenleme.**
5. Ajan: `ogr2ogr` / GeoPandas ile GeoJSON'a çevir, `legal_constraints`
   tablosundaki `11600` kaydının `geom` alanını gerçek poligonla değiştir,
   `konum_guveni='yuksek'`, `rozet='Otorite'` yap.
6. `uv run pytest -q tests/test_veto_legal.py` + `make gate-all`.

## DoD
En az 1 gerçek karar geometrisi (11600) Otorite rozetiyle üretildiğinde
ADR-0017 kapanır. Gelmezse mevcut Nominatim geocode-proxy korunur (K3).
