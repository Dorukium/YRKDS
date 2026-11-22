"""Veritabanı bağlantı havuzu (yük testi gereksinimi: p95 < 300 ms)."""
from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

import psycopg
from psycopg_pool import ConnectionPool

from app.config import DATABASE_URL

_pool: ConnectionPool | None = None


def _dsn() -> str:
    # SQLAlchemy formatindaki "+psycopg" suffixini psycopg3 anlamaz.
    return DATABASE_URL.replace("postgresql+psycopg://", "postgresql://")


def _get_pool() -> ConnectionPool:
    global _pool
    if _pool is None:
        # 4 uvicorn worker × 8 = 32 bağlantı; Postgres varsayılan 100 limiti altında kalır.
        _pool = ConnectionPool(_dsn(), min_size=2, max_size=8, open=True)
    return _pool


@contextmanager
def get_conn() -> Iterator[psycopg.Connection]:
    with _get_pool().connection() as conn:
        yield conn
