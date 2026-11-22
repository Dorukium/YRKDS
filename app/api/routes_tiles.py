"""F6 — sunucu tarafı risk PNG tile'ları ve hücre nokta API'si.

İstemci tarafındaki 20 bin canvas dairesi kaldırılır; harita bu tile'ları
kullanır. p95 hedefi <120 ms (bellek önbelleği + GiST indeksi).
"""
from __future__ import annotations

import io
import math
from functools import lru_cache

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from PIL import Image, ImageDraw

from app.db import get_conn

router = APIRouter()
RENKLER = ["#440154", "#3b528b", "#21918c", "#5ec962", "#fde725"]


def _sinir(v: float, u: float) -> float:
    return max(0.0, min(1.0, (v or 0) / u))


def _risk(twi: float, egim: float, vs30: float) -> int:
    sinir = _sinir
    r = 0.35 * sinir(twi, 12) + 0.25 * sinir(egim, 30) + 0.25 * (1 - sinir(vs30 or 800, 800))
    return min(4, int(r * 5))


def _bounds(z: int, x: int, y: int) -> tuple[float, float, float, float]:
    n = 2**z
    lon0 = x / n * 360 - 180
    lon1 = (x + 1) / n * 360 - 180
    def lat(yy: int) -> float:
        return math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * yy / n))))

    return lon0, lat(y + 1), lon1, lat(y)


@lru_cache(maxsize=512)
def _tile(z: int, x: int, y: int) -> bytes:
    w, s, e, n = _bounds(z, x, y)
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT ST_X(ST_Centroid(geom)), ST_Y(ST_Centroid(geom)),
                      dem_twi, dem_egim, vs30
               FROM grid_cells
               WHERE geom && ST_MakeEnvelope(%s,%s,%s,%s,4326)
                 AND dem_twi IS NOT NULL""",
            (w, s, e, n),
        )
        satirlar = cur.fetchall()
    img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    c = ImageDraw.Draw(img)
    for lon, lat, twi, egim, vs30 in satirlar:
        px = int((lon - w) / (e - w) * 256)
        py = int((n - lat) / (n - s) * 256)
        renk = RENKLER[_risk(float(twi), float(egim), float(vs30))]
        r, g, b = tuple(int(renk[i:i + 2], 16) for i in (1, 3, 5))
        c.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(r, g, b, 110))
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


@router.get("/tiles/{z}/{x}/{y}.png")
def tile(z: int, x: int, y: int) -> Response:
    if not (0 <= z <= 16) or x < 0 or y < 0:
        raise HTTPException(400, "Geçersiz tile koordinatı")
    return Response(content=_tile(z, x, y), media_type="image/png",
                    headers={"Cache-Control": "public, max-age=3600"})


@router.get("/api/cell")
def cell(lon: float, lat: float) -> dict[str, object]:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT ilce, dem_egim, dem_twi, dem_hand, vs30, soil_sand_pct,
                      pga_gem_arastirma, kiyi_2m, kiyi_5m, veri_tamligi_pct,
                      afete_maruz_bolge
               FROM grid_cells
               ORDER BY geom <-> ST_SetSRID(ST_MakePoint(%s,%s),4326) LIMIT 1""",
            (lon, lat),
        )
        satir = cur.fetchone()
    if not satir:
        raise HTTPException(404, "Hücre bulunamadı")
    return dict(zip(
        ["ilce", "egim", "twi", "hand", "vs30", "kum", "pga_gem_arastirma",
         "kiyi_2m", "kiyi_5m", "tamlik", "afete_maruz"],
        satir,
    ))
