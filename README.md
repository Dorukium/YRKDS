# YRKDS — Antalya Yatırım Riski Karar Destek Sistemi

[![version](https://img.shields.io/badge/version-0.2.0-blue)](CHANGELOG.md)
[![license](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![gates](https://img.shields.io/badge/gates-make%20gate--all-brightgreen)](docs/kanit.md)

Antalya merkez üç ilçede parsel bazlı afet riski **ön-tarama** aracı.
Deterministik, kural tabanlı; **ML eğitilmez**. Eksik veri varsa sahte kesinlik
üretmez, `KARARSIZ` veya `Koşullu` der.

> **Ürün durumu:** çalışan prototip. Resmi InSAR/SYGM/TDTH ve yasal VETO
> geometrileri olmadığı için karar destek ürünü seviyesinde değildir.
> Bkz. `docs/veri_envanteri.md`.

## Hızlı başlangıç

```bash
uv python install 3.12 && uv sync
cargo install maturin
docker compose up -d db
VIRTUAL_ENV="$PWD/.venv" maturin develop --release --manifest-path skor_motoru/Cargo.toml

# Veri pipeline'ı (zorunlu; docker compose tek başına veri getirmez)
uv run python -m app.data_pipeline.download_dem
uv run python -m app.data_pipeline.download_soil       # ~10 dk
uv run python -m app.data_pipeline.download_osm
uv run python -m app.data_pipeline.download_climate
uv run python -m app.data_pipeline.download_flood
uv run python -m app.data_pipeline.download_insar
uv run python -m app.data_pipeline.process_grid
uv run python -m app.data_pipeline.load_postgis

uv run uvicorn app.main:app --port 8000
# frontend: cd frontend && python -m http.server 3000
```

Üretim: `docker compose up -d --build` → Nginx `:80`, API `:8000`, DB `:55432`.

**Tüm kalite kapıları tek komutla:** `make gate-all`
(lint → mypy → test → kapsam → E2E → erişilebilirlik → yük → güvenlik → SBOM).
Sonuçlar: `docs/kanit.md`.

Testler: `uv run pytest` (66+ test: skor, VETO, yasal VETO, parity, hidroloji,
API, pipeline, bağımsızlık denetimi, sismik durum, backtest).

## API

| Metod | Yol | Açıklama |
|---|---|---|
| POST | `/api/analyze` | GeoJSON poligon → skor, kapsam, güven, kanıt |
| GET | `/api/layers/{ad}` | GeoJSON katman |
| GET | `/api/events?bbox=&tur=` | Olay listesi |
| GET | `/api/report/{id}.pdf` | PDF rapor |
| GET | `/api/stats/ilce/{ad}` | İlçe özeti |
| GET | `/api/backtest/2009` | Doğrulama metrikleri + CI + kalibrasyon ifşası |
| GET | `/api/hazirlik` | Katman doluluk raporu |
| GET | `/api/saglik`, `/health` | Sağlık |

Örnek:

```bash
curl -X POST localhost:8000/api/analyze -H 'Content-Type: application/json' \
 -d '{"geojson":{"type":"Polygon","coordinates":[[[30.70,36.90],[30.701,36.90],[30.701,36.901],[30.70,36.901],[30.70,36.90]]]}}'
```

Yanıtta `skor_kapsami` alanı skorun tam mı kısmi mi olduğunu, `yasal_kisit_durumu`
yasal katmanların doğrulanıp doğrulanmadığını gösterir.

## Güvenlik

`YRKDS_API_KEY` ayarlanırsa `/api/` isteklerinde `X-API-Key` zorunludur.
`YRKDS_RATE_LIMIT` (varsayılan 30/dakika/IP) ve `CORS_ORIGINS` env ile
yapılandırılır. Güvenlik başlıkları middleware ile eklenir.

## Bilimsel sınırlar

- Gerçek InSAR, SYGM taşkın ve TDTH grid verisi yok → ilgili bileşenler NULL.
- Yasal VETO katmanlarının hiçbiri jeoreferanslı değil → VETO üretilmez,
  "yasal kısıt doğrulanamadı" uyarısı verilir.
- Vs30/fay/YASS/jeoloji ilçe bazlı türetilmiş değerlerdir; parsel ölçümü değil.
- 2009 backtest recall 0.941, Wilson CI [0.730, 0.990], 17 etiket; eşikler
  aynı etiketlerle kalibre edildiği için **bağımsız doğrulama değildir**.

TÜBİTAK 2204-A bağlamında geliştirilmiştir.

**Zenodo DOI:** [10.5281/zenodo.24449066](https://doi.org/10.5281/zenodo.24449066)
