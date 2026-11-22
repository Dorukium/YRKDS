"""OSM bina ayak izi ve su yollari.

HDX 'hotosm_tur_buildings' paketi ~650 MB (tum ulke), bu calisma siniri icin
elverissizdir. Ayni OSM verisine Overpass API ile bbox bazli erisilir ve kaynak
etiketi "OpenStreetMap (Overpass bbox)" olarak acikca yazilir.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import geopandas as gpd
import requests
from shapely.geometry import LineString, Point, Polygon

from app.config import GRID_BBOX, PROCESSED_DIR, RAW_DIR

OVERPASS = "https://overpass-api.de/api/interpreter"
UA = {"User-Agent": "YRKDS/0.1 (TUBITAK 2204-A; open-data research)"}


def _sorgula(sorgu: str) -> dict[str, Any]:
    for deneme in range(3):
        try:
            r = requests.post(OVERPASS, data={"data": sorgu}, headers=UA, timeout=180)
            r.raise_for_status()
            return dict(r.json())
        except Exception as exc:
            print(f"Overpass deneme {deneme + 1} basarisiz: {exc}")
            time.sleep(2 * (deneme + 1))
    raise RuntimeError("Overpass API yanit vermedi")


def _bbox() -> str:
    min_lon, min_lat, max_lon, max_lat = GRID_BBOX
    return f"{min_lat},{min_lon},{max_lat},{max_lon}"


def _geometry(el: dict[str, Any]) -> Any:
    g = el.get("geometry")
    if g:
        coords = [(p["lon"], p["lat"]) for p in g if "lon" in p and "lat" in p]
        if len(coords) >= 4:
            return Polygon(coords)
        if len(coords) >= 2:
            return LineString(coords)
    if "center" in el:
        return Point(el["center"]["lon"], el["center"]["lat"])
    return None


def indir() -> dict[str, Any]:
    b = _bbox()
    ciktilar: dict[str, Path] = {}
    tanimlar = {
        "bina": f'[out:json][timeout:180];(way["building"]({b});relation["building"]({b}););out geom;',
        "su_yollari": f'[out:json][timeout:180];(way["waterway"]({b});relation["waterway"]({b}););out geom;',
    }
    for ad, sorgu in tanimlar.items():
        try:
            doc = _sorgula(sorgu)
            satirlar = []
            for el in doc.get("elements", []):
                g = _geometry(el)
                if g is not None:
                    satirlar.append((el["id"], g))
            gdf = gpd.GeoDataFrame(
                satirlar, columns=["osm_id", "geometry"], geometry="geometry", crs="EPSG:4326"
            )
            hedef = PROCESSED_DIR / f"osm_{ad}.gpkg"
            gdf.to_file(hedef, driver="GPKG", layer=ad)
            ciktilar[ad] = hedef
            print(f"OSM {ad}: {len(gdf)} geometri -> {hedef}")
        except Exception as exc:
            # Veri yoksa SQL'de NULL birakilir; sahte bina sayisi uretilmez.
            print(f"UYARI: OSM {ad} indirilemedi ({exc}). Katman 'veri yok' isaretlenecek.")
            ciktilar[ad] = Path("")

    meta = {
        "kaynak": "OpenStreetMap via Overpass API (bbox)",
        "hdx_paket": "hotosm_tur_buildings / hotosm_tur_waterways (ulke geneli ~650 MB)",
        "not": "Calisma siniri icin bbox bazli Overpass kullanildi.",
        "durum": {k: ("var" if str(v) else "yok") for k, v in ciktilar.items()},
    }
    (RAW_DIR / "osm_kaynak.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return ciktilar


if __name__ == "__main__":
    indir()
