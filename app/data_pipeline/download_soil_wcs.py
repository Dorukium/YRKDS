"""D4 — SoilGrids v2 WCS GetCoverage, 250 m, tam kapsam (IDW kaldırıldı).

Yetkinlik rozeti: "SoilGrids v2 WCS — Otorite (250 m)".
"""
from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime

import requests

from app.config import GRID_BBOX, PROCESSED_DIR, RAW_DIR

WCS = "https://maps.isric.org/mapserv"
PROPLER = {
    "clay": ("clay.map", "clay_0-5cm_mean"),
    "silt": ("silt.map", "silt_0-5cm_mean"),
    "sand": ("sand.map", "sand_0-5cm_mean"),
    "soc": ("soc.map", "soc_0-5cm_mean"),
    "phh2o": ("phh2o.map", "phh2o_0-5cm_mean"),
}
CRS = "http://www.opengis.net/def/crs/EPSG/0/4326"


def indir() -> dict[str, object]:
    min_lon, min_lat, max_lon, max_lat = GRID_BBOX
    kayitlar: list[dict[str, object]] = []
    for ad, (map_dosyasi, coverage) in PROPLER.items():
        params = {
            "map": f"/map/{map_dosyasi}",
            "SERVICE": "WCS", "VERSION": "2.0.1", "REQUEST": "GetCoverage",
            "COVERAGEID": coverage, "FORMAT": "image/tiff",
            "SUBSET": [f"X({min_lon},{max_lon})", f"Y({min_lat},{max_lat})"],
            "SUBSETTINGCRS": CRS, "OUTPUTCRS": CRS,
        }
        r = requests.get(WCS, params=params, timeout=180)
        r.raise_for_status()
        if not r.content.startswith(b"II") and not r.content.startswith(b"MM"):
            raise RuntimeError(f"{ad}: WCS GeoTIFF dönmedi ({r.content[:80]!r})")
        hedef = PROCESSED_DIR / f"soil_wcs_{ad}.tif"
        hedef.write_bytes(r.content)
        kayitlar.append({
            "ozellik": ad, "coverage": coverage, "url": r.url,
            "erisim_tarihi": datetime.now(UTC).date().isoformat(),
            "sha256": hashlib.sha256(r.content).hexdigest(),
            "bayt": len(r.content),
            "cozunurluk": "250 m (WCS)",
            "yetkinlik": "Otorite",
            "lisans": "CC BY 4.0 (ISRIC)",
            "rozet": "Otorite",
        })
    (RAW_DIR / "soil_wcs_manifest.json").write_text(
        json.dumps(kayitlar, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return {"katman_sayisi": len(kayitlar), "kayitlar": kayitlar}


if __name__ == "__main__":
    r = indir()
    print(r["katman_sayisi"], "WCS katmani indirildi")
