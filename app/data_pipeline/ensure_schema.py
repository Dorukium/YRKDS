"""API açılışında şemanın varlığını garanti et (Faz F / Alembic öncesi).

Tablolar zaten varsa init.sql çalıştırılmaz; veri silinmez. Idempotent
migrations (`sql/migrations/*.sql`) her açılışta uygulanır.
"""
from __future__ import annotations

from app.config import ROOT
from app.db import get_conn


def _migrations() -> None:
    klasor = ROOT / "sql" / "migrations"
    if not klasor.exists():
        return
    for dosya in sorted(klasor.glob("*.sql")):
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(dosya.read_text(encoding="utf-8"))


def ensure_schema() -> bool:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT to_regclass('public.grid_cells')")
        satir = cur.fetchone()
        assert satir is not None
        varsa = satir[0] is not None
    if varsa:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                """SELECT to_regclass('public.parcel_queries') IS NOT NULL,
                          to_regclass('public.parcel_queries') IS NOT NULL
                          AND EXISTS (SELECT 1 FROM information_schema.columns
                                      WHERE table_name='parcel_queries'
                                      AND column_name='sonuq_json')"""
            )
            satir = cur.fetchone()
            assert satir is not None
            var, eski = satir
            if var and eski:
                cur.execute("ALTER TABLE parcel_queries RENAME COLUMN sonuq_json TO sonuc_json")
        _migrations()
        return False
    sql = (ROOT / "sql" / "init.sql").read_text(encoding="utf-8")
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql)
    _migrations()
    return True


if __name__ == "__main__":
    print({"yeni_sema": ensure_schema()})
