"""POST /api/analyze, /api/stats/ilce/{ad}, /api/backtest/2009."""
from __future__ import annotations

import json
from typing import Any, cast

from fastapi import APIRouter, HTTPException, Request

from app.api.grid_lookup import poligondan_girdi
from app.auth import oturum_oku
from app.core.backtest import hesapla as backtest_hesapla
from app.core.engine import analiz_et
from app.core.legal_veto import legal_veto
from app.core.mitigation import sonuc_uret
from app.core.provenance import katalog
from app.db import get_conn
from app.models.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    BacktestResponse,
    MitigateRequest,
    StatsResponse,
)

router = APIRouter()


def _geom_cikar(g: dict[str, Any]) -> dict[str, Any]:
    if g.get("type") == "FeatureCollection":
        features = cast(list[dict[str, Any]], g.get("features", []))
        if len(features) != 1:
            raise HTTPException(422, "FeatureCollection yalnızca tek parsel içermeli")
        return _geom_cikar(features[0])
    if g.get("type") == "Feature":
        return cast(dict[str, Any], g["geometry"])
    if g.get("type") in ("Polygon", "MultiPolygon"):
        return g
    if "geometry" in g:
        return cast(dict[str, Any], g["geometry"])
    raise HTTPException(422, "GeoJSON Polygon / Feature bekleniyor")


@router.post("/api/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest, request: Request) -> AnalyzeResponse:
    geojson = _geom_cikar(req.geojson)
    girdi, meta = poligondan_girdi(geojson)
    sonuc = analiz_et(girdi, req.parsel_id, legal=legal_veto(geojson),
                      senaryo_adi=req.senaryo, ilce=meta.get("ilce"))
    if meta.get("uyari"):
        sonuc.uyarilar.append(meta["uyari"])
    sonuc.katman_durumu["kesisen_hucre_sayisi"] = str(meta["hucre_sayisi"])

    # Sorguyu sakla (PDF rapor bu id ile uretilir)
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """INSERT INTO parcel_queries
                   (geom, parsel_id, skor, bant, karar, zb_puan, l_puan, s_puan,
                    h_puan, f_puan, veto, veto_neden, guven_skoru, sonuc_json, username)
                   VALUES (ST_GeomFromGeoJSON(%s),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                   RETURNING id""",
            (
                json.dumps(geojson), sonuc.parsel_id, sonuc.skor, sonuc.bant,
                sonuc.karar, sonuc.tehlike_kirilimi.get("ZB"),
                sonuc.tehlike_kirilimi.get("L"), sonuc.tehlike_kirilimi.get("S"),
                sonuc.tehlike_kirilimi.get("H"), sonuc.tehlike_kirilimi.get("F"),
                sonuc.veto, sonuc.veto_neden, sonuc.guven_skoru,
                json.dumps(sonuc.model_dump(mode="json"), ensure_ascii=False),
                (oturum_oku(request) or {}).get("u"),
            ),
        )
        satir = cur.fetchone()
        assert satir is not None
        sonuc.parsel_id = f"{satir[0]}:{sonuc.parsel_id}"
        cur.execute(
            "UPDATE parcel_queries SET parsel_id=%s, sonuc_json=%s WHERE id=%s",
            (sonuc.parsel_id, json.dumps(sonuc.model_dump(mode="json"), ensure_ascii=False), satir[0]),
        )
    return sonuc


@router.get("/api/stats/ilce/{ad}", response_model=StatsResponse)
def ilce_stats(ad: str) -> StatsResponse:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT COUNT(*), AVG(dem_egim), AVG(vs30), AVG(fay_mesafe_km),
                          AVG(soil_sand_pct), AVG(yass_m), AVG(veri_tamligi_pct)
                   FROM grid_cells WHERE ilce = %s""",
            (ad,),
        )
        r = cur.fetchone()
    if r is None or r[0] == 0:
        raise HTTPException(404, f"{ad} için grid hücresi yok")
    return StatsResponse(ilce=ad, veri=dict(zip(
        ["hucre_sayisi", "ort_egim", "ort_vs30", "ort_fay_km", "ort_kum_pct",
         "ort_yass_m", "ort_veri_tamligi_pct"], r,
    )))


@router.post("/api/mitigate")
def mitigate(req: MitigateRequest, request: Request) -> dict[str, object]:
    geojson = _geom_cikar(req.geojson)
    girdi, _meta = poligondan_girdi(geojson)
    baz = analiz_et(girdi, legal=legal_veto(geojson), senaryo_adi=req.senaryo)
    sonuc = sonuc_uret(baz.tehlike_kirilimi, req.onlemler)
    sonuc["baz_skor"] = baz.skor
    sonuc["delta"] = (
        round(sonuc["skor"] - baz.skor, 1)
        if sonuc["skor"] is not None and baz.skor is not None else None
    )
    return sonuc


@router.get("/api/catalog")
def api_catalog() -> list[dict[str, object]]:
    """U7: yetkinlik rozeti, kapsam ve güncelleme tarihi ile katman kataloğu."""
    return katalog()


@router.get("/api/backtest/2009", response_model=BacktestResponse)
def backtest_2009() -> BacktestResponse:
    return BacktestResponse(**backtest_hesapla())
