"""FastAPI giriş noktası."""
from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from logging import getLogger
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, Response
from fastapi.staticfiles import StaticFiles

from app.api import (
    routes_analyze,
    routes_auth,
    routes_events,
    routes_layers,
    routes_parcel,
    routes_report,
    routes_tiles,
)
from app.config import FRONTEND_DIR
from app.data_pipeline.ensure_schema import ensure_schema
from app.metrics import GECIKME, ISTEK_SAYISI, metrikleri_uretip
from app.security import ApiAnahtari, GuvenlikBasliklari, HizSiniri

log = getLogger("yrkds")


@asynccontextmanager
async def yasam_dongusu(app: FastAPI) -> AsyncIterator[None]:
    try:
        yeni = ensure_schema()
        log.info("Veritabanı şeması %s", "oluşturuldu" if yeni else "mevcuttu")
        from app.auth import bootstrap_admin

        bootstrap_admin()
    except Exception as exc:
        log.warning("Şema kontrolü başarısız (API yine de açılıyor): %s", exc)
    yield


app = FastAPI(
    title="YRKDS — Antalya Yatırım Riski Karar Destek Sistemi",
    version="5.0.0",
    description="Deterministik, kural tabanlı parsel ön-tarama risk skorlama API'si.",
    lifespan=yasam_dongusu,
)

# CORS: aynı kökenli frontend varsayılan; ek origin'ler env ile eklenir.
import os

_origins = ["http://localhost", "http://localhost:80", "http://127.0.0.1:8000"]
_origins += [o for o in os.getenv("CORS_ORIGINS", "").split(",") if o]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-API-Key"],
)
app.add_middleware(GuvenlikBasliklari)
app.add_middleware(HizSiniri)
app.add_middleware(ApiAnahtari)

app.include_router(routes_auth.router)
app.include_router(routes_analyze.router)
app.include_router(routes_layers.router)
app.include_router(routes_events.router)
app.include_router(routes_parcel.router)
app.include_router(routes_report.router)
app.include_router(routes_tiles.router)


@app.middleware("http")
async def olcum(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    import time

    basla = time.monotonic()
    response: Response = await call_next(request)
    sure = time.monotonic() - basla
    yol = request.url.path.split("/")[1] or "kök"
    ISTEK_SAYISI.labels(request.method, yol, str(response.status_code)).inc()
    GECIKME.labels(request.method, yol).observe(sure)
    return response


@app.get("/api/docs", include_in_schema=False)
def api_docs() -> Response:
    return RedirectResponse("/docs")


@app.get("/metrics")
def metrikler() -> Response:
    govde, tur = metrikleri_uretip()
    return Response(content=govde, media_type=tur)


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"durum": "ok"}


@app.get("/readyz")
def readyz() -> dict[str, str]:
    try:
        from app.db import get_conn

        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT 1")
            assert cur.fetchone() is not None
        return {"durum": "ready"}
    except Exception as exc:
        return {"durum": "not_ready", "hata": str(exc)}


@app.get("/health")
@app.get("/api/saglik")
def saglik() -> dict[str, str]:
    return {"durum": "ok", "urun": "YRKDS", "surum": "0.2.0"}


@app.get("/api/hazirlik")
def hazirlik() -> dict[str, Any]:
    """Veri doluluğu raporu: üretim öncesi doğrulama için."""
    from app.db import get_conn

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT COUNT(*) AS hucre,
                          COUNT(insar_velocity_mm_yr) AS insar,
                          COUNT(pga_g) AS tdth,
                          COUNT(taskin_100y) AS sygm,
                          COUNT(*) FILTER (WHERE afete_maruz_bolge IS NOT NULL) AS yasal_veto
                   FROM grid_cells"""
        )
        r = cur.fetchone()
    assert r is not None
    return dict(zip(["hucre", "insar", "tdth", "sygm", "yasal_veto"], r))


if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
