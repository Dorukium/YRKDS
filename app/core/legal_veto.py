"""Yasal VETO motoru — legal_constraints tablosundan okur.

K3: geometrisi olmayan karar "doğrulanamadı" sayılır, VETO üretmez.
D9: geometrisi olan kayıtlı alanlara 300 m "önlem bölgesi" danışmanlık
uyarısıdır, VETO değildir.
"""
from __future__ import annotations

import json
from typing import Any

from app.db import get_conn

_SORGU = """SELECT karar_no, karar_tarihi, tur, kaynak_url
            FROM legal_constraints
            WHERE geom IS NOT NULL
              AND ST_Intersects(geom, ST_GeomFromGeoJSON(%s))"""
_ONLEM = """SELECT EXISTS (SELECT 1 FROM legal_constraints
             WHERE geom IS NOT NULL
               AND ST_DWithin(geom, ST_GeomFromGeoJSON(%s), 300))"""


def _sonuc(satirlar: list[Any], bilinmeyen: int, hata: str | None) -> dict[str, Any]:
    if hata:
        return {"veto": False, "neden": None, "durum": "dogrulanamadi",
                "uyari": f"Yasal kısıt tablosu sorgulanamadı: {hata}",
                "kararlar": [], "onlem_bolgesi": False}
    if satirlar:
        ilk = satirlar[0]
        return {
            "veto": True,
            "neden": f"Uygun Değil (Yasal Kısıt): {ilk[2]}, karar {ilk[0]} ({ilk[1]})",
            "durum": "dogrulandi", "uyari": None,
            "kararlar": [
                {"karar_no": s[0], "tarih": str(s[1]), "tur": s[2], "kaynak": s[3]}
                for s in satirlar
            ],
            "onlem_bolgesi": False,
        }
    return {
        "veto": False, "neden": None,
        "durum": "dogrulanamadi" if bilinmeyen else "dogrulandi",
        "uyari": (
            f"{bilinmeyen} yasal kararın jeoreferanslı sınırı olmadığı için "
            "yasal kısıt doğrulanamadı; resmi imar kontrolü gerekir."
        ) if bilinmeyen else None,
        "kararlar": [], "onlem_bolgesi": False,
    }


def legal_veto(geojson: dict[str, Any], conn_in: Any = None) -> dict[str, Any]:
    """GeoJSON poligon için yasal kısıt durumunu döndürür."""
    try:
        if conn_in is not None:
            with conn_in.cursor() as cur:
                cur.execute(_SORGU, (json.dumps(geojson),))
                satirlar = cur.fetchall()
                cur.execute("SELECT COUNT(*) FROM legal_constraints WHERE geom IS NULL")
                satir = cur.fetchone()
                assert satir is not None
                bilinmeyen = satir[0]
                cur.execute(_ONLEM, (json.dumps(geojson),))
                onlem = cur.fetchone()[0]
            sonuc = _sonuc(satirlar, bilinmeyen, None)
            sonuc["onlem_bolgesi"] = bool(onlem)
            return sonuc
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(_SORGU, (json.dumps(geojson),))
            satirlar = cur.fetchall()
            cur.execute("SELECT COUNT(*) FROM legal_constraints WHERE geom IS NULL")
            satir = cur.fetchone()
            assert satir is not None
            bilinmeyen = satir[0]
            cur.execute(_ONLEM, (json.dumps(geojson),))
            onlem_satir = cur.fetchone()
            assert onlem_satir is not None
            onlem = onlem_satir[0]
        sonuc = _sonuc(satirlar, bilinmeyen, None)
        sonuc["onlem_bolgesi"] = bool(onlem)
        return sonuc
    except Exception as exc:
        return _sonuc([], 0, str(exc))
