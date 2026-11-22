"""V2 yükseltme kapıları: D3/D4/D8/D10, F4/F6, afete_maruz regresyonu."""
from __future__ import annotations

import json

import pandas as pd
from fastapi.testclient import TestClient

from app.config import PROCESSED_DIR, RAW_DIR, ROOT
from app.main import app

POLY = {"type": "Polygon", "coordinates": [[[30.64, 36.88], [30.642, 36.88],
                                             [30.642, 36.882], [30.64, 36.882],
                                             [30.64, 36.88]]]}


def test_d4_wcs_indirme_fonksiyonu(monkeypatch, tmp_path):
    from types import SimpleNamespace

    from app.data_pipeline import download_soil_wcs as wcs

    monkeypatch.setattr(wcs, "PROCESSED_DIR", tmp_path)
    monkeypatch.setattr(wcs, "RAW_DIR", tmp_path)

    def fake_get(url, params=None, timeout=None):
        return SimpleNamespace(raise_for_status=lambda: None,
                               content=b"II*\x00" + b"fake-tiff", url=url)

    monkeypatch.setattr(wcs.requests, "get", fake_get)
    r = wcs.indir()
    assert r["katman_sayisi"] == 5
    assert len(list(tmp_path.glob("soil_wcs_*.tif"))) == 5


def test_d3_crosscheck_fonksiyonu(monkeypatch, tmp_path):
    import numpy as np
    import rasterio
    from rasterio.transform import from_origin

    from app.data_pipeline import crosscheck_d3 as d3

    tif = tmp_path / "gem.tif"
    veri = np.full((10, 10), 0.23, dtype=np.float64)
    with rasterio.open(tif, "w", driver="GTiff", height=10, width=10, count=1,
                       dtype="float64", crs="EPSG:4326",
                       transform=from_origin(30.5, 37.1, 0.05, 0.04)) as ds:
        ds.write(veri, 1)
    monkeypatch.setattr(d3, "GEM_TIF", tif)
    monkeypatch.setattr(d3, "PROCESSED_DIR", tmp_path)
    monkeypatch.setattr(d3, "RAW_DIR", tmp_path)
    (tmp_path / "enrichment_manifest.json").write_text("[]", encoding="utf-8")
    r = d3.calistir()
    assert r["durum"] == "tamamlandi" and r["rozet"] == "Araştırma"
    assert (tmp_path / "gem_crosscheck.json").exists()


def test_d4_soilgrids_wcs_tam_kapsam():
    manifest = json.loads((RAW_DIR / "soil_wcs_manifest.json").read_text(encoding="utf-8"))
    assert len(manifest) == 5
    assert all(k["yetkinlik"] == "Otorite" and k["sha256"] for k in manifest)
    df = pd.read_parquet(PROCESSED_DIR / "grid_25m.parquet",
                         columns=["soil_soc", "soil_sand_pct", "kaynak_toprak"])
    assert df.soil_soc.notna().mean() > 0.99
    assert "WCS" in df.kaynak_toprak.iloc[0]


def test_d3_gem_arastirma_ve_adr():
    r = json.loads((PROCESSED_DIR / "gem_crosscheck.json").read_text(encoding="utf-8"))
    assert r["rozet"] == "Araştırma"
    assert any(x["sapma_pct"] and x["sapma_pct"] > 20 for x in r["ilceler"])
    assert (ROOT / "docs/ADR/0008-gem-pga-sapma.md").exists()
    assert (ROOT / "docs/ADR/0010-iklim-senaryo-S.md").exists()


def test_d8_kiyi_zonlari_ve_d1_egms_adr():
    df = pd.read_parquet(PROCESSED_DIR / "grid_25m.parquet", columns=["kiyi_2m", "kiyi_5m"])
    assert df.kiyi_2m.sum() > 0 and df.kiyi_5m.sum() >= df.kiyi_2m.sum()
    assert (ROOT / "docs/ADR/0009-egms-insar.md").exists()


def test_afete_maruz_null_regresyonu():
    """U8: afete_maruz asla True/False proxy olmamalı."""
    df = pd.read_parquet(PROCESSED_DIR / "grid_25m.parquet", columns=["afete_maruz_bolge"])
    assert df.afete_maruz_bolge.isna().all()

    with TestClient(app) as c:
        sonuc = c.post("/api/analyze", json={"geojson": POLY}).json()
    assert sonuc["veto"] is False
    assert sonuc["yasal_kisit_durumu"] == "dogrulanamadi"


def test_d10_katalog_rozetsiz_katman_kirmizi():
    with TestClient(app, follow_redirects=False) as c:
        r = c.get("/api/catalog")
        assert r.status_code == 200
        katmanlar = r.json()
    uygun = {"Otorite", "Proxy", "Tahmin", "Araştırma", "Eksik"}
    assert katmanlar and all(k.get("yetkinlik") in uygun for k in katmanlar)
    assert all("kapsam_pct" in k and "guncelleme" in k for k in katmanlar)
    assert any(k["id"] == "pga_gem" and k["yetkinlik"] == "Araştırma" for k in katmanlar)


def test_u7_kanit_rozeti_ve_f4_senaryo():
    with TestClient(app, follow_redirects=False) as c:
        bugun = c.post("/api/analyze", json={"geojson": POLY, "senaryo": "bugun"}).json()
        ssp = c.post("/api/analyze", json={"geojson": POLY, "senaryo": "ssp585_2050"}).json()
    uygun = {"Otorite", "Proxy", "Tahmin", "Araştırma", "Eksik"}
    assert all(k["yetkinlik"] in uygun for k in bugun["kanit"])
    assert bugun["senaryo"]["ad"] == "Bugün"
    assert ssp["senaryo"]["rozet"] == "Tahmin"
    assert ssp["skor"] > bugun["skor"]
    assert any("S bileşeni için güvenilir iklim çarpanı yok" in u for u in ssp["uyarilar"])


def test_f6_tile_ve_nokta_api():
    with TestClient(app, follow_redirects=False) as c:
        tile = c.get("/tiles/11/1200/770.png")
        assert tile.status_code == 200 and tile.content[:4] == b"\x89PNG"
        hucre = c.get("/api/cell?lon=30.7&lat=36.9")
        assert hucre.status_code == 200
        assert "twi" in hucre.json() and "kiyi_2m" in hucre.json()
