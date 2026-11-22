# Güvenlik (OWASP ASVS L1 kontrol listesi)

| Kontrol | Durum | Kanıt |
|---|---|---|
| Girdi şema doğrulama | ✅ | Pydantic `SkorInput`, `AnalyzeRequest`; hatalı GeoJSON → 422 |
| Hız sınırı | ✅ | `app/security.py`, Redis (REDIS_URL) veya yerel sayaç |
| Güvenlik başlıkları | ✅ | nosniff, SAMEORIGIN, CSP |
| CORS | ✅ | env `CORS_ORIGINS` ile sınırlı kökenler |
| API anahtarı | ✅ | `YRKDS_API_KEY` ayarlıysa X-API-Key zorunlu |
| Bağımlılık taraması | ✅ | `pip-audit --strict`, `cargo audit --deny warnings` (0 açık) |
| SBOM | ✅ | `docs/sbom.json` (CycloneDX) |
| Yedek + geri yükleme | ✅ | `scripts/backup.sh`, `scripts/restore_drill.sh` |
| İzleme | ✅ | Prometheus `/metrics`, `/healthz`, `/readyz` |
| Migration | ✅ | Alembic `0001_initial` + idempotent SQL |

Not: Kimlik doğrulama/kullanıcı rolleri (ASVS L2) kapsam dışıdır; K7 uyarınca
ancak ADR ile eklenir.
