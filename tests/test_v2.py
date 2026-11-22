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
    assert sonuc["veto"] is False  # bu poligon üç proxy alanın dışında
    assert sonuc["yasal_kisit_durumu"] in ("dogrulandi", "dogrulanamadi")


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


def test_a8_tkgm_parsel_sorgu():
    with TestClient(app, follow_redirects=False) as c:
        r = c.get("/api/parcel-search?lat=36.9050&lon=30.7050")
        assert r.status_code == 200, r.text[:200]
        f = r.json()
        assert f["type"] == "Feature" and f["geometry"]["type"] == "Polygon"
        assert f["properties"]["yetkinlik"] == "Otorite"
        assert f["properties"]["kaynak"] == "TKGM Parsel Sorgu"
        assert f["cache"] in ("HIT", "MISS")
        assert c.get("/api/parcel-search?lat=40.98&lon=28.72").status_code == 400
    assert (ROOT / "data/raw/tkgm_manifest.json").exists()


def test_d2_d3_d4_altyapi():
    with TestClient(app, follow_redirects=False) as c:
        assert c.get("/locales/tr.json").status_code == 200
        assert c.get("/locales/en.json").status_code == 200
        tr = c.get("/locales/tr.json").json()
        en = c.get("/locales/en.json").json()
        assert set(tr) == set(en)
        assert en["nav.map"] == "Map & Analysis"
    assert (ROOT / "tests/load_500.js").exists()
    assert (ROOT / "monitoring/prometheus.yml").exists()
    assert (ROOT / "monitoring/grafana/dashboards/yrkds.json").exists()
    assert (ROOT / "docs/ADR/0022-i18n-kapsam.md").exists()


def test_v3_yeni_pipeline_fonksiyonlari(monkeypatch, tmp_path):
    from types import SimpleNamespace

    from app.data_pipeline import download_era5_extremes as era5

    monkeypatch.setattr(era5, "PROCESSED_DIR", tmp_path)
    monkeypatch.setattr(era5, "RAW_DIR", tmp_path)

    def fake_get(url, params=None, timeout=None):
        gunler = {
            "time": ["1969-01-17", "1991-06-01"],
            "precipitation_sum": [57.1, 10.0],
            "temperature_2m_max": [12.0, 25.0],
        }
        return SimpleNamespace(
            raise_for_status=lambda: None,
            json=lambda: {"daily": gunler},
            content=b'{"daily":{}}',
        )

    monkeypatch.setattr(era5.requests, "get", fake_get)
    r = era5.indir()
    assert r["gun_sayisi"] > 0 and r["olay_1969_01_17_yagis_mm"] == 57.1

    # Yasal geometri seed (DB yerine taklit imleç)
    from app.data_pipeline import seed_legal_geometry as slg

    class FakeCursor:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def execute(self, sql, params=None):
            self.son = (3,)

        def fetchone(self):
            return self.son

    class FakeConn:
        def cursor(self):
            return FakeCursor()

    class Ctx:
        def __enter__(self):
            return FakeConn()

        def __exit__(self, *a):
            return False

    monkeypatch.setattr(slg, "get_conn", lambda: Ctx())
    monkeypatch.setattr(slg, "RAW_DIR", tmp_path)
    assert slg.yukle() == 3


def test_v3_exposure_stac_taklit(monkeypatch, tmp_path):

    from app.data_pipeline import download_exposure as dex

    monkeypatch.setattr(dex, "PROCESSED_DIR", tmp_path)
    monkeypatch.setattr(dex, "RAW_DIR", tmp_path)

    class FakeAsset:
        href = "https://example.invalid/cog.tif"

    class FakeItem:
        def __init__(self):
            self.id = "test-item"
            self.assets = {"map": FakeAsset()}
            self.datetime = "2021-01-01T00:00:00Z"

    class FakeSearch:
        def items(self):
            return [FakeItem()]

    class FakeClient:
        def search(self, **kwargs):
            return FakeSearch()

    monkeypatch.setattr(dex.pystac_client.Client, "open", lambda *a, **k: FakeClient())

    class FakeDs:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def index(self, lon, lat):
            return 0, 0

        def read(self, *a, **k):
            import numpy as np

            return np.array([[50]], dtype=np.uint8)

    monkeypatch.setattr(dex.rasterio, "open", lambda *a, **k: FakeDs())
    r = dex.calistir()
    assert r["worldcover_okundu"] is True
    assert len(r["worldcover_ornekleri"]) == 18


def test_b4_b5_embed_ve_pwa():
    with TestClient(app, follow_redirects=False) as c:
        assert c.get("/embed.html").status_code == 200
        assert c.get("/sw.js").status_code == 200
        assert c.get("/manifest.webmanifest").status_code == 200
        assert "frame-ancestors" in c.get("/api/saglik").headers.get("content-security-policy", "")


def test_b3_beklenen_kayip_tahmin():
    with TestClient(app, follow_redirects=False) as c:
        r = c.post("/api/analyze", json={"geojson": POLY}).json()
    k = r.get("beklenen_kayip", {})
    assert k["durum"] == "ok" and k["rozet"] == "Tahmin"
    assert k["alt_TL_yil"] <= k["merkez_TL_yil"] <= k["ust_TL_yil"]
    assert k["aralik"] == "±%50"
    assert "ADR-0020" in k["aciklama"]


def test_b2_portfoy_pdf():
    with TestClient(app, follow_redirects=False) as c:
        kimlikler = []
        for _ in range(5):
            r = c.post("/api/analyze", json={"geojson": POLY})
            kimlikler.append(int(r.json()["parsel_id"].split(":")[0]))
        pdf = c.post("/api/portfolio-report", json=kimlikler)
    assert pdf.status_code == 200
    icerik = pdf.content
    assert icerik[:4] == b"%PDF"
    from io import BytesIO

    from pypdf import PdfReader

    sayfa_sayisi = len(PdfReader(BytesIO(icerik)).pages)
    assert sayfa_sayisi >= 10, sayfa_sayisi


def test_b1_what_if_onlem_modulu():
    with TestClient(app, follow_redirects=False) as c:
        baz = c.post("/api/analyze", json={"geojson": POLY}).json()
        r = c.post("/api/mitigate", json={
            "geojson": POLY, "onlemler": ["kazikli_temel", "drenaj"]})
    assert r.status_code == 200
    sonuc = r.json()
    assert sonuc["rozet"] == "Tahmin"
    assert sonuc["baz_skor"] == baz["skor"]
    assert sonuc["skor"] <= baz["skor"]
    assert sonuc["maliyet_seviyesi"] in ("düşük", "orta", "yüksek")
    assert "ADR-0019" in sonuc["aciklama"]
    assert (ROOT / "docs/ADR/0019-onlem-katsayilari.md").exists()


def test_f6_tile_ve_nokta_api():
    with TestClient(app, follow_redirects=False) as c:
        tile = c.get("/tiles/11/1200/770.png")
        assert tile.status_code == 200 and tile.content[:4] == b"\x89PNG"
        hucre = c.get("/api/cell?lon=30.7&lat=36.9")
        assert hucre.status_code == 200
        assert "twi" in hucre.json() and "kiyi_2m" in hucre.json()
