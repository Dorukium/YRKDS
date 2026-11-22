"""API açılışında şemanın varlığını garanti et (Faz F / Alembic öncesi).

Tablolar zaten varsa init.sql çalıştırılmaz; veri silinmez. Idempotent
migrations (`sql/migrations/*.sql`) her açılışta uygulanır.

K6 REGRESYON: 8 uvicorn worker aynı anda açıldığında DDL'ler birbirini
deadlock'a sokuyordu (legal_constraints ALTER TABLE). Tüm şema işlemleri
artık tek bir oturum düzeyi advisory lock altında serileştirilir.
"""
from __future__ import annotations

from typing import Any

from app.config import ROOT
from app.db import get_conn

LOCK_KEY = 0x59524B44  # "YRKD" — sabit advisory lock anahtarı


def _migrations(cur: Any) -> None:
    klasor = ROOT / "sql" / "migrations"
    if not klasor.exists():
        return
    for dosya in sorted(klasor.glob("*.sql")):
        icerik = dosya.read_text(encoding="utf-8").strip()
        if icerik:
            cur.execute(icerik)


def ensure_schema() -> bool:
    """Şemayı garanti eder; çoklu worker'larda deadlock olmadan serileşir."""
    with get_conn() as conn, conn.cursor() as cur:
        # İşlem düzeyi kilit: commit/rollback'da otomatik bırakılır; hata
        # durumunda kilitli bağlantı havuza dönmez.
        cur.execute("SELECT pg_advisory_xact_lock(%s)", (LOCK_KEY,))
        cur.execute("SELECT to_regclass('public.grid_cells')")
        satir = cur.fetchone()
        assert satir is not None
        varsa = satir[0] is not None
        if varsa:
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
            _migrations(cur)
            return False
        sql = (ROOT / "sql" / "init.sql").read_text(encoding="utf-8")
        cur.execute(sql)
        _migrations(cur)
        return True


if __name__ == "__main__":
    print({"yeni_sema": ensure_schema()})
