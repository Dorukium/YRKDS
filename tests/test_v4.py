"""V4 A1/A8 modülleri için ağ/DB bağımlılığı olmadan kapsam testleri."""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
from fastapi.testclient import TestClient

from app.main import app


def test_a1_tarih_ayristirma():
    from app.data_pipeline.download_insar import _tarihler

    p = Path("S1-GUNW-A-R-160-tops-20240121_20240109-155057-00030E_00036N-PP-4589-v3_0_1.nc")
    ikinci, birinci = _tarihler(p)
    assert ikinci.date().isoformat() == "2024-01-21"
    assert birinci.date().isoformat() == "2024-01-09"
    assert (ikinci - birinci).days == 12


def test_a1_granul_hiz_ve_yigin(monkeypatch, tmp_path):
    from app.data_pipeline import download_insar as insar

    class FakeDs:
        def __init__(self):
            faz = np.linspace(-1, 1, 40, dtype=np.float32).reshape(5, 8)
            coh = np.full((5, 8), 0.8, dtype=np.float32)
            lon = np.linspace(30.60, 30.84, 8)
            lat = np.linspace(36.98, 36.84, 5)
            self.icerik = {
                "unwrappedPhase": SimpleNamespace(values=faz),
                "coherence": SimpleNamespace(values=coh),
                "longitude": SimpleNamespace(values=lon),
                "latitude": SimpleNamespace(values=lat),
            }

        def __getitem__(self, key):
            return self.icerik[key]

        def close(self):
            return None

    import xarray as xr
    monkeypatch.setattr(xr, "open_dataset", lambda *a, **k: FakeDs())
    monkeypatch.setattr(insar, "PROCESSED_DIR", tmp_path)
    monkeypatch.setattr(insar, "MIN_GRANULES", 2)
    dosyalar = [
        Path(f"S1-GUNW-A-R-160-tops-20240121_20240109-155057-00030E_00036N-PP-4589-v3_0_1_{i}.nc")
        for i in range(3)
    ]
    sonuc = insar.hiz_haritasi_olustur(dosyalar)
    assert sonuc["durum"] == "ok"
    assert sonuc["kapsam_pct"] >= 95
    assert (tmp_path / "insar_aria_velocity_25m.tif").exists()
    assert (tmp_path / "insar_aria_validity.tif").exists()


def test_a1_bozuk_granul_toleransi():
    from app.data_pipeline.download_insar import _gundeki_hiz

    assert _gundeki_hiz(Path("yok.nc")) is None


def test_a1_yetersiz_gozlem():
    from app.data_pipeline.download_insar import hiz_haritasi_olustur

    assert hiz_haritasi_olustur([])["durum"] == "veri_yok"


def test_a1_eula_akisi_taklit(monkeypatch):
    from app.data_pipeline import download_insar as insar

    class FakeSession:
        def __init__(self):
            self.calls = []

        def get(self, url, timeout=None):
            self.calls.append(url)
            if "unaccepted" in url:
                html = '<form><input name="authenticity_token" value="t"/></form>'
            else:
                html = '<input name="authenticity_token" value="t"/><input name="redirect_uri" value="u"/>'
            return SimpleNamespace(text=html, status_code=200)

        def post(self, url, data=None, allow_redirects=None, timeout=None):
            self.calls.append(url)
            return SimpleNamespace(status_code=200, text="ok")

    monkeypatch.setenv("EARTHDATA_USERNAME", "test")
    monkeypatch.setenv("EARTHDATA_PASSWORD", "test")
    import requests

    monkeypatch.setattr(requests, "Session", FakeSession)
    insar._ensure_asf_eula()  # hata fırlatmamalı


def test_a8_parsel_api_taklit(monkeypatch, tmp_path):
    from app.api import routes_parcel

    monkeypatch.setattr(routes_parcel, "_redis", None)
    monkeypatch.setattr(routes_parcel, "_bellek", {})
    monkeypatch.setattr(routes_parcel, "RAW_DIR", tmp_path)
    feature = {
        "type": "Feature",
        "geometry": {"type": "Polygon", "coordinates": [[[30.7, 36.9], [30.701, 36.9],
                     [30.701, 36.901], [30.7, 36.9]]]},
        "properties": {"mahalleAd": "Test", "adaNo": "1", "parselNo": "2"},
    }
    monkeypatch.setattr(
        routes_parcel.requests, "get",
        lambda *a, **k: SimpleNamespace(raise_for_status=lambda: None, json=lambda: feature),
    )
    with TestClient(app, follow_redirects=False) as c:
        r = c.get("/api/parcel-search?lat=36.9050&lon=30.7050")
        assert r.status_code == 200
        assert r.json()["properties"]["yetkinlik"] == "Otorite"
        r2 = c.get("/api/parcel-search?lat=36.9050&lon=30.7050")
        assert r2.json()["cache"] == "HIT"
        assert c.get("/api/parcel-search?lat=40.98&lon=28.72").status_code == 400
    assert (tmp_path / "tkgm_manifest.json").exists()


def test_a6_tdth_dogrulama_hatalari(monkeypatch, tmp_path):
    import pytest

    from app.data_pipeline import load_tdth

    monkeypatch.setattr(load_tdth, "RAW_DIR", tmp_path)
    eksik = tmp_path / "tdth_grid.csv"
    pd.DataFrame({"lon": [30.7], "lat": [36.9]}).to_csv(eksik, index=False)
    monkeypatch.setattr(load_tdth, "DOSYA", eksik)
    with pytest.raises(ValueError):
        load_tdth.yukle()

    pd.DataFrame({
        "lon": [30.7] * 10, "lat": [36.9] * 10, "pga_g": [0.3] * 10,
        "ss_g": [0.7] * 10, "s1_g": [0.3] * 10, "pgv_cm_s": [25.0] * 10,
    }).to_csv(eksik, index=False)
    with pytest.raises(ValueError):
        load_tdth.yukle()

    pd.DataFrame({
        "lon": [30.7] * 200, "lat": [36.9] * 200, "pga_g": [1.9] * 200,
        "ss_g": [0.7] * 200, "s1_g": [0.3] * 200, "pgv_cm_s": [25.0] * 200,
    }).to_csv(eksik, index=False)
    with pytest.raises(ValueError):
        load_tdth.yukle()


def test_a1_arama_ve_indirme_taklit(monkeypatch, tmp_path):
    import earthaccess

    from app.data_pipeline import download_insar as insar

    monkeypatch.setattr(insar, "_login", lambda: None)
    monkeypatch.setattr(insar, "_ensure_asf_eula", lambda: None)
    monkeypatch.setattr(
        earthaccess, "search_data",
        lambda **kwargs: [object()] * 3,
    )
    assert len(insar.arama(3)) == 3
    monkeypatch.setattr(earthaccess, "download", lambda granuller, hedef: [str(tmp_path / "a.nc")])
    monkeypatch.setattr(insar, "RAW_DIR", tmp_path)
    assert len(insar.indir([object()])) == 1


def test_a1_calistir_ve_hata_yollari(monkeypatch, tmp_path):
    from app.data_pipeline import download_insar as insar

    monkeypatch.setattr(insar, "PROCESSED_DIR", tmp_path)
    monkeypatch.setattr(insar, "RAW_DIR", tmp_path)
    monkeypatch.setattr(insar, "arama", lambda limit=12: [object()] * 3)
    monkeypatch.setattr(insar, "indir", lambda g: [tmp_path / "a.nc"])
    (tmp_path / "a.nc").write_bytes(b"1234")
    monkeypatch.setattr(
        insar, "hiz_haritasi_olustur",
        lambda dosyalar: {"durum": "ok", "kapsam_pct": 100.0, "gozlem": 3},
    )
    rapor = insar.calistir(3)
    assert rapor["durum"] == "ok" and rapor["granul_sayisi"] == 3
    assert (tmp_path / "insar_aria.json").exists()
    monkeypatch.setattr(insar, "arama", lambda limit=12: [])
    monkeypatch.setattr(insar, "indir", lambda g: [])
    monkeypatch.setattr(insar, "hiz_haritasi_olustur", lambda d: {"durum": "veri_yok"})
    assert insar.calistir(0)["durum"] == "veri_yok"


def test_a8_redis_cache_yolu(monkeypatch, tmp_path):

    from app.api import routes_parcel

    class FakeRedis:
        def __init__(self):
            self.data = None

        def get(self, key):
            return self.data

        def setex(self, key, ttl, value):
            self.data = value

    monkeypatch.setattr(routes_parcel, "_redis", FakeRedis())
    monkeypatch.setattr(routes_parcel, "RAW_DIR", tmp_path)
    feature = {"type": "Feature", "geometry": {"type": "Polygon", "coordinates": []},
               "properties": {"mahalleAd": "X"}}
    monkeypatch.setattr(
        routes_parcel.requests, "get",
        lambda *a, **k: SimpleNamespace(raise_for_status=lambda: None, json=lambda: feature),
    )
    with TestClient(app, follow_redirects=False) as c:
        assert c.get("/api/parcel-search?lat=36.92&lon=30.72").json()["cache"] == "MISS"
        assert c.get("/api/parcel-search?lat=36.92&lon=30.72").json()["cache"] == "HIT"


def test_a8_hata_yollari(monkeypatch, tmp_path):
    from app.api import routes_parcel

    monkeypatch.setattr(routes_parcel, "_redis", None)
    monkeypatch.setattr(routes_parcel, "_bellek", {})
    monkeypatch.setattr(routes_parcel, "RAW_DIR", tmp_path)

    def bos(*a, **k):
        return SimpleNamespace(raise_for_status=lambda: None,
                               json=lambda: {"type": "FeatureCollection", "geometry": None})

    monkeypatch.setattr(routes_parcel.requests, "get", bos)
    with TestClient(app, follow_redirects=False) as c:
        assert c.get("/api/parcel-search?lat=36.90&lon=30.70").status_code == 404

    def hata(*a, **k):
        raise OSError("servis yok")

    monkeypatch.setattr(routes_parcel.requests, "get", hata)
    with TestClient(app, follow_redirects=False) as c:
        assert c.get("/api/parcel-search?lat=36.91&lon=30.71").status_code == 502


def test_a6_tdth_yukleyici(monkeypatch, tmp_path):
    from app.data_pipeline import load_tdth

    monkeypatch.setattr(load_tdth, "DOSYA", tmp_path / "yok.csv")
    assert load_tdth.yukle()["durum"] == "veri_yok"

    monkeypatch.setattr(load_tdth, "DOSYA", tmp_path / "tdth_grid.csv")
    monkeypatch.setattr(load_tdth, "RAW_DIR", tmp_path)

    class FakeCursor:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def execute(self, sql, params=None):
            self.son = (100,)

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

    monkeypatch.setattr(load_tdth, "get_conn", lambda: Ctx())
    df = pd.DataFrame({
        "lon": [30.7] * 200, "lat": [36.9] * 200, "pga_g": [0.3] * 200,
        "ss_g": [0.7] * 200, "s1_g": [0.3] * 200, "pgv_cm_s": [25.0] * 200,
    })
    df.to_csv(load_tdth.DOSYA, index=False)
    r = load_tdth.yukle()
    assert r["durum"] == "ok" and r["nokta"] == 200
    assert (tmp_path / "tdth_manifest.json").exists()
