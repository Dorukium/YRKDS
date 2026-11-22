"""A8 — TKGM Parsel Sorgu entegrasyonu (kamuya açık, anahtarsız).

Kaynak: https://cbsapi.tkgm.gov.tr/megsiswebapi.v3.1/api/parsel/{lat}/{lon}/
24 saat Redis önbellek; yetkinlik rozeti "Otorite", atıf "TKGM Parsel Sorgu".
"""
from __future__ import annotations

import base64
import json
import logging
import os
from typing import Any

import requests
from fastapi import APIRouter, HTTPException

from app.config import RAW_DIR

router = APIRouter()
BASE = "https://cbsapi.tkgm.gov.tr/megsiswebapi.v3.1/api"
HEADERS = {
    "User-Agent": "YRKDS/4.0 (TUBITAK 2204-A; open-data research)",
    "Referer": "https://parselsorgu.tkgm.gov.tr/",
    "Origin": "https://parselsorgu.tkgm.gov.tr",
}
REDIS_URL = os.getenv("REDIS_URL", "")
_redis = None
if REDIS_URL:
    try:
        import redis

        _redis = redis.Redis.from_url(REDIS_URL, socket_timeout=1)
    except Exception:
        _redis = None
_bellek: dict[str, tuple[float, dict[str, Any]]] = {}


def _manifest() -> None:
    dosya = RAW_DIR / "tkgm_manifest.json"
    if dosya.exists():
        return
    dosya.write_text(json.dumps([{
        "id": "TKGM_PARSEL",
        "url": BASE + "/parsel/{lat}/{lon}/",
        "erisim_tarihi": "2026-11-22",
        "lisans": "TKGM kamuya açık parsel sorgu",
        "sha256": None,
        "yetkinlik": "Otorite",
        "not": "Koordinat başına sorgu; yanıt anlıkGeoJSON. Dosya SHA256 yok (API yanıtı).",
    }], ensure_ascii=False, indent=2), encoding="utf-8")


@router.get("/api/parcel-search")
def parcel_search(lat: float, lon: float) -> dict[str, Any]:
    if not (35.5 <= lat <= 37.5 and 29.5 <= lon <= 31.5):
        raise HTTPException(400, "Koordinat Antalya çalışma alanı dışında")
    anahtar = f"yrkds:parsel:v4:{lat:.6f}:{lon:.6f}"
    if _redis is not None:
        try:
            cached = _redis.get(anahtar)
            if cached:
                sonuc: dict[str, Any] = json.loads(base64.b64decode(cached))
                sonuc["cache"] = "HIT"
                return sonuc
        except Exception as exc:
            logging.getLogger("yrkds.parcel").warning("TKGM önbellek hatası: %s", exc)
    else:
        import time

        kayit = _bellek.get(anahtar)
        if kayit and time.time() - kayit[0] < 86400:
            sonuc = dict(kayit[1])
            sonuc["cache"] = "HIT"
            return sonuc

    try:
        r = requests.get(f"{BASE}/parsel/{lat:.6f}/{lon:.6f}/", headers=HEADERS, timeout=30)
        r.raise_for_status()
        geo = r.json()
    except Exception as exc:
        raise HTTPException(502, f"TKGM sorgusu başarısız: {exc}") from exc
    if geo.get("type") != "Feature" or not geo.get("geometry"):
        raise HTTPException(404, "Bu koordinatta parsel bulunamadı")

    props = dict(geo.get("properties") or {})
    sonuc = {
        "type": "Feature",
        "geometry": geo["geometry"],
        "properties": {
            **props,
            "yetkinlik": "Otorite",
            "kaynak": "TKGM Parsel Sorgu",
            "kaynak_url": "https://parselsorgu.tkgm.gov.tr/",
            "erisim_tarihi": "2026-11-22",
        },
        "cache": "MISS",
    }
    if _redis is not None:
        try:
            _redis.setex(anahtar, 86400, base64.b64encode(json.dumps(sonuc).encode()))
        except Exception as exc:
            logging.getLogger("yrkds.parcel").warning("TKGM önbellek hatası: %s", exc)
    else:
        import time

        _bellek[anahtar] = (time.time(), sonuc)
    _manifest()
    return sonuc
