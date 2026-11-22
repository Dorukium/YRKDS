"""GET /api/events?bbox=&tur= — olay listesi."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from app.db import get_conn

router = APIRouter()


@router.get("/api/events")
def events(
    bbox: str | None = None, tur: str | None = None, limit: int = 500
) -> list[dict[str, Any]]:
    kosullar: list[str] = []
    parametreler: list[Any] = []
    if tur:
        kosullar.append("olay_turu = %s")
        parametreler.append(tur)
    if bbox:
        try:
            parcalar = [float(v) for v in bbox.split(",")]
            if len(parcalar) != 4:
                raise ValueError
        except ValueError as exc:
            raise HTTPException(422, "bbox: min_lon,min_lat,max_lon,max_lat bekleniyor") from exc
        kosullar.append("geom && ST_MakeEnvelope(%s,%s,%s,%s,4326)")
        parametreler += parcalar
    where = " AND ".join(kosullar) if kosullar else "TRUE"
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            f"""SELECT id, olay_turu, to_char(tarih,'YYYY-MM-DD'), ilce, mahalle,
                           lat, lon, buyukluk, etki, kaynak_url, konum_guveni,
                           dogrulama_etiketi
                    FROM events WHERE {where} ORDER BY tarih NULLS LAST LIMIT %s""",
            tuple(parametreler + [limit]),
        )
        satirlar = cur.fetchall()
    return [
        dict(zip(
            ["id", "olay_turu", "tarih", "ilce", "mahalle", "lat", "lon", "buyukluk",
             "etki", "kaynak_url", "konum_guveni", "dogrulama_etiketi"], s,
        ))
        for s in satirlar
    ]
