"""GET /api/layers/{ad} — katman verileri GeoJSON olarak."""
from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.db import get_conn

router = APIRouter()

KATMANLAR = {
    "grid": "risk ızgarası (örneklenmiş)",
    "taskin": "taşkın / akarsu katmanı",
    "bina": "OSM bina ayak izleri",
    "su_yollari": "OSM su yolları",
    "deprem": "deprem olayları",
    "afete_maruz": "afete maruz bölge (yükseklik proxy)",
}


@router.get("/api/layers/{ad}")
def layer(ad: str) -> JSONResponse:
    if ad not in KATMANLAR:
        raise HTTPException(404, f"Bilinmeyen katman: {ad}")

    with get_conn() as conn, conn.cursor() as cur:
        if ad == "grid":
            # Tum 800k hucreyi gondermek yerine deterministik ornekleme
            cur.execute(
                """SELECT json_build_object('type','FeatureCollection','features',
                              json_agg(json_build_object(
                                'type','Feature',
                                'geometry', ST_AsGeoJSON(geom)::json,
                                'properties', json_build_object(
                                   'ilce',ilce,'egim',dem_egim,'twi',dem_twi,
                                   'vs30',vs30,'kum',soil_sand_pct,
                                   'tamlik',veri_tamligi_pct))) )
                       FROM (SELECT * FROM grid_cells WHERE id %% 40 = 0) s""".replace("%%", "%")
            )
        elif ad == "taskin":
            cur.execute(
                """SELECT json_build_object('type','FeatureCollection','features',
                              json_agg(json_build_object('type','Feature',
                                'geometry', ST_AsGeoJSON(geom)::json,
                                'properties', json_build_object('ilce',ilce,
                                  'akarsu_m',akarsu_mesafe_m,'twi',dem_twi))) )
                       FROM (SELECT * FROM grid_cells WHERE akarsu_mesafe_m < 500
                             AND id %% 20 = 0) s""".replace("%%", "%")
            )
        elif ad == "afete_maruz":
            cur.execute(
                """SELECT json_build_object('type','FeatureCollection','features',
                              json_agg(json_build_object('type','Feature',
                                'geometry', ST_AsGeoJSON(geom)::json,
                                'properties', json_build_object('ilce',ilce))) )
                       FROM grid_cells WHERE afete_maruz_bolge = TRUE"""
            )
        elif ad == "deprem":
            cur.execute(
                """SELECT json_build_object('type','FeatureCollection','features',
                              json_agg(json_build_object('type','Feature',
                                'geometry', ST_AsGeoJSON(geom)::json,
                                'properties', json_build_object('etki',etki,'tarih',tarih))) )
                       FROM events WHERE olay_turu='deprem' AND geom IS NOT NULL"""
            )
        else:
            # bina / su_yollari: dosyadan dogrudan okunur (PostGIS'e yuklenmedi)
            from pathlib import Path

            import geopandas as gpd

            dosya = Path("data/processed") / f"osm_{ad}.gpkg"
            if not dosya.exists():
                raise HTTPException(404, f"{ad} verisi indirilmemiş")
            gdf = gpd.read_file(dosya)
            if ad == "bina":
                gdf = gdf.iloc[::20]  # okunabilirlik icin ornekle
            return JSONResponse(json.loads(gdf.to_json()))

        satir = cur.fetchone()
    veri = satir[0] if satir and satir[0] else {"type": "FeatureCollection", "features": []}
    return JSONResponse(veri)
