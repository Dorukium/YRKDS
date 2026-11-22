# Mimari

```
[Leaflet + Alpine + Chart.js] --HTTP--> [Nginx :80] --/api--> [FastAPI :8000]
                                                        |-- güvenlik (başlık, hız, API key)
                                                        |-- /api/hazirlik (veri doluluğu)
                                                   [PostGIS 16/3.4]
                                                        ^
                                  [25 m grid parquet] -- load_postgis.py
                                                        ^
        [Terrarium DEM] [SoilGrids REST] [OSM Overpass] [proje veri seti]
```

## Bileşenler

- `app/core/scoring.py` — tek referans formül (Python).
- `app/core/hydro.py` — havza doldurma, D8, TWI, akış yolu HAND.
- `skor_motoru/src/lib.rs` — aynı formülün PyO3 uygulaması. `engine.py`
  çalışma zamanında Rust'ı kullanır, bulunamazsa Python'a düşer.
  `tests/test_parity.py` birebir eşitliği sabit vektörlerle kanıtlar.
- `app/core/engine.py` — VETO → tamlık → alt puanlar → skor → kanıt sırası;
  kısmi skor ve doğrulanmamış yasal kısıt kuralları.
- `app/core/backtest.py` — mekansal blok doğrulama, Wilson CI, kalibrasyon ifşası.
- `app/api/grid_lookup.py` — poligonla kesişen hücrelerin zonal özeti.
- `app/security.py` — güvenlik başlıkları, IP hız sınırı, isteğe bağlı API key.
- `app/data_pipeline/ensure_schema.py` — boş veritabanında şema oluşturur,
  eski `sonuq_json` kolonunu göç ettirir; mevcut veriyi silmez.

## Kurulum

```bash
uv sync
docker compose up -d db
VIRTUAL_ENV=$PWD/.venv maturin develop --release --manifest-path skor_motoru/Cargo.toml
uv run python -m app.data_pipeline.download_dem
uv run python -m app.data_pipeline.download_soil      # ~10 dk (551 REST isteği)
uv run python -m app.data_pipeline.download_osm
uv run python -m app.data_pipeline.download_climate
uv run python -m app.data_pipeline.download_flood
uv run python -m app.data_pipeline.download_insar
uv run python -m app.data_pipeline.process_grid
uv run python -m app.data_pipeline.load_postgis
```

**Önemli:** `docker compose up` tek başına **boş veritabanı** açar. Grid verisi
~800k satır olduğu için imaja gömülmez; yukarıdaki pipeline çalıştırılmalıdır.
`/api/hazirlik` endpoint'i eksik katmanları raporlar.

## Çalışma

Geliştirme: `uv run uvicorn app.main:app --port 8000` + `cd frontend && python -m http.server 3000`

Üretim: `docker compose up -d --build` → Nginx :80, API :8000, DB :55432.

## Güvenlik ve dürüstlük

- CORS varsayılan olarak yalnızca bilinen yerel kökenlerle sınırlı.
- `YRKDS_API_KEY` ayarlanırsa tüm `/api/` istekleri anahtar ister.
- Çıktı olasılıksal ön-tarama riskidir; "bina yıkılır" iddiası içermez.
- Eksik veri `None`/`NULL` taşınır; 0 ikamesi yapılmaz.
- Yasal katman doğrulanmamışsa VETO `False` varsayılmaz, uyarı üretilir.
- PDF raporu saklanan `sonuc_json` kaydından üretilir; hesapla rapor arasında
  sapma olmaz.
