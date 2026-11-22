#!/usr/bin/env bash
# Geri yükleme tatbikatı: yedeği geçici DB'ye geri yükler ve satır sayısını doğrular.
set -euo pipefail
DUMP="${1:?kullanım: restore_drill.sh <dump>}"
docker compose exec -T db psql -U yrkds -d postgres -c 'DROP DATABASE IF EXISTS yrkds_restore_test' >/dev/null
docker compose exec -T db psql -U yrkds -d postgres -c 'CREATE DATABASE yrkds_restore_test' >/dev/null
docker compose exec -T db psql -U yrkds -d yrkds_restore_test -c 'CREATE EXTENSION IF NOT EXISTS postgis' >/dev/null
cat "$DUMP" | docker compose exec -T db pg_restore -U yrkds -d yrkds_restore_test --no-owner 2>/dev/null || true
COUNT=$(docker compose exec -T db psql -U yrkds -d yrkds_restore_test -t -A -c 'SELECT count(*) FROM grid_cells')
echo "restore_edilen_hucre=$COUNT"
docker compose exec -T db psql -U yrkds -d postgres -c 'DROP DATABASE yrkds_restore_test' >/dev/null
test "$COUNT" -gt 700000
