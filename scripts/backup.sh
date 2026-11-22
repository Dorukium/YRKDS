#!/usr/bin/env bash
# Gece yedeği: PostGIS veritabanını sıkıştırılmış dump olarak alır.
set -euo pipefail
OUT="${1:-data/backups}"
mkdir -p "$OUT"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
docker compose exec -T db pg_dump -U yrkds -Fc yrkds > "$OUT/yrkds_${STAMP}.dump"
sha256sum "$OUT/yrkds_${STAMP}.dump" > "$OUT/yrkds_${STAMP}.sha256"
# Saklama: 7 günden eski yedekleri sil
find "$OUT" -name 'yrkds_*.dump' -mtime +7 -delete
find "$OUT" -name 'yrkds_*.sha256' -mtime +7 -delete
echo "$OUT/yrkds_${STAMP}.dump"
