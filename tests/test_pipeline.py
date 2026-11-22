"""Faz F: veri pipeline modüllerinin ağ/DB bağımlılığı olmadan testi."""
from __future__ import annotations

import io
from types import SimpleNamespace

import numpy as np
import pandas as pd
from PIL import Image


def test_db_modelleri_ve_seed_manifest():
    import app.models.db_models  # noqa: F401  -- sinif tanimlari
    from app.data_pipeline import seed

    manifest = seed.dosya_yaz()
    assert manifest.exists()
    kayitlar = seed.yuklenen_kayitlar()
    assert kayitlar and all(not k["_id"].startswith("AVC-") for k in kayitlar)
    assert len(seed.dogrulama_etiketleri()) == 18
    assert len(seed.kontrol_ornekleri()) == 8


def test_yasal_karar_ve_sema():
    from app.data_pipeline.ensure_schema import ensure_schema
    from app.data_pipeline.seed_legal import yukle

    assert ensure_schema() in (True, False)
    assert yukle() == 1


def test_insar_ve_iklim_ve_tasin(monkeypatch, tmp_path):
    from app.config import PROCESSED_DIR, RAW_DIR
    from app.data_pipeline import download_climate, download_flood, download_insar

    monkeypatch.setattr(download_climate, "CDSAPI_KEY", "")
    durum = download_climate.indir()
    assert durum["era5_land"] == "yok"
    monkeypatch.setattr(
        download_flood.requests, "get", lambda *a, **k: (_ for _ in ()).throw(OSError("no wms"))
    )
    f = download_flood.indir()
    assert f["wms_erisiildi"] is False
    i = download_insar.indir()
    assert i["insar_velocity"] == "yok"

    assert (PROCESSED_DIR / "iklim_normalleri.csv").exists()
    assert (RAW_DIR / "tasin_kaynak.json").exists()
    assert (PROCESSED_DIR / "insar_durum.json").exists()


def test_soil_rest_taklit(monkeypatch, tmp_path):
    from app.data_pipeline import download_soil

    monkeypatch.setattr(download_soil, "GRID_BBOX", (30.70, 36.90, 30.71, 36.91))
    monkeypatch.setattr(download_soil, "ORNEK_ADIMI", 0.01)
    monkeypatch.setattr(download_soil, "PROCESSED_DIR", tmp_path)
    monkeypatch.setattr(download_soil, "RAW_DIR", tmp_path)

    def fake_get(url, params=None, headers=None, timeout=None):
        props = {p[1] for p in params if p[0] == "property"}
        return SimpleNamespace(
            raise_for_status=lambda: None,
            json=lambda: {
                "properties": {
                    "layers": [
                        {"name": p, "unit_measure": {"d_factor": 10},
                         "depths": [{"values": {"mean": 300}}]}
                        for p in props
                    ]
                }
            },
        )

    monkeypatch.setattr(download_soil.requests, "get", fake_get)
    out = download_soil.indir()
    assert out.exists()
    z = np.load(out)
    assert z["values"].shape == (4, 6)


def test_dem_taklit(monkeypatch, tmp_path):
    from app.data_pipeline import download_dem

    monkeypatch.setattr(download_dem, "GRID_BBOX", (30.70, 36.90, 30.702, 36.902))
    monkeypatch.setattr(download_dem, "ZOOM", 13)
    monkeypatch.setattr(download_dem, "PROCESSED_DIR", tmp_path)
    monkeypatch.setattr(download_dem, "RAW_DIR", tmp_path)

    img = Image.new("RGB", (256, 256), (128, 0, 0))

    def fake_get(self, url, timeout=None):
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return SimpleNamespace(raise_for_status=lambda: None, content=buf.getvalue())

    monkeypatch.setattr(download_dem.requests.Session, "get", fake_get)
    out = download_dem.indir_terrarium()
    assert out.exists()


def test_osm_taklit(monkeypatch, tmp_path):
    from app.data_pipeline import download_osm

    monkeypatch.setattr(download_osm, "PROCESSED_DIR", tmp_path)
    monkeypatch.setattr(download_osm, "RAW_DIR", tmp_path)

    def fake_post(url, data=None, headers=None, timeout=None):
        return SimpleNamespace(
            raise_for_status=lambda: None,
            json=lambda: {"elements": [
                {"id": 1, "geometry": [
                    {"lon": 30.70, "lat": 36.90}, {"lon": 30.701, "lat": 36.90},
                    {"lon": 30.701, "lat": 36.901}, {"lon": 30.70, "lat": 36.90},
                ]},
                {"id": 2, "center": {"lon": 30.70, "lat": 36.90}},
            ]},
        )

    monkeypatch.setattr(download_osm.requests, "post", fake_post)
    out = download_osm.indir()
    assert all(str(v) for v in out.values())


def test_process_grid_kucuk_alanda(monkeypatch, tmp_path):
    from app.data_pipeline import process_grid

    monkeypatch.setattr(process_grid, "PROCESSED_DIR", tmp_path)
    monkeypatch.setattr(process_grid, "GRID_BBOX", (30.70, 36.90, 30.704, 36.903))
    monkeypatch.setattr(process_grid, "GRID_RESOLUTION_M", 25.0)
    w, h, *_ = process_grid._grid_spec()

    dem = np.linspace(100, 80, w * h, dtype=np.float32).reshape(h, w)
    monkeypatch.setattr(process_grid, "_dem_25m", lambda: (dem, object()))
    toprak = {p: np.full((h, w), v, dtype=np.float32) for p, v in
              (("sand", 30.0), ("clay", 25.0), ("silt", 20.0), ("phh2o", 7.2), ("soc", 5.0))}
    monkeypatch.setattr(process_grid, "_toprak_enterpolasyonu", lambda: toprak)
    (tmp_path / "soil_samples.npz").write_bytes(b"")
    (tmp_path / "dem_raw.tif").write_bytes(b"")

    out = process_grid.olustur()
    df = pd.read_parquet(out)
    assert len(df) == w * h
    assert df.afete_maruz_bolge.isna().all()

    # Yardımcı fonksiyonlar: enterpolasyon, chamfer mesafe, ilçe centroid
    lons = np.array([30.70, 30.71])
    lats = np.array([36.90, 36.91])
    vals = np.full((4, 6), 25.0, dtype=np.float32)
    np.savez_compressed(
        tmp_path / "soil_samples2.npz", lons=lons, lats=lats, values=vals,
        props=np.array(["sand"]), step=0.01, shape=(2, 2),
    )
    monkeypatch.setattr(process_grid, "PROCESSED_DIR", tmp_path)
    (tmp_path / "soil_samples.npz").write_bytes((tmp_path / "soil_samples2.npz").read_bytes())
    toprak = process_grid._toprak_enterpolasyonu()
    assert "sand" in toprak and np.isfinite(toprak["sand"]).all()

    mesafe = process_grid._chamfer(np.array([[False, False], [True, False]]), 25.0)
    assert mesafe[1, 1] > 0 and mesafe[1, 0] == 0
    merkezler = process_grid._ilce_centroidlari()
    assert "Kepez" in merkezler


def test_load_postgis_taklit(monkeypatch, tmp_path):
    from app.data_pipeline import load_postgis

    class FakeCopy:
        def __init__(self):
            self.satir = 0

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def write_row(self, row):
            self.satir += 1

    class FakeCursor:
        def __init__(self):
            self.copy_obj = FakeCopy()
            self.executed = []

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def execute(self, sql, params=None):
            self.executed.append(sql)

        def fetchone(self):
            return (7,)

        def executemany(self, sql, seq):
            self.executed.append((sql, len(seq)))

        def copy(self, sql):
            return self.copy_obj

    class FakeConn:
        def cursor(self):
            return FakeCursor()

    df = pd.DataFrame({k: [1.0] for k in load_postgis.GRID_KOLONLARI})
    df["lon"], df["lat"] = [30.7], [36.9]
    parquet = tmp_path / "kucuk.parquet"
    df.to_parquet(parquet, index=False)
    df.to_parquet(tmp_path / "grid_25m.parquet", index=False)

    conn = FakeConn()
    assert load_postgis._grid_yukle(conn, parquet) == 7
    assert load_postgis._olay_yukle(conn) > 0

    monkeypatch.setattr(load_postgis, "PROCESSED_DIR", tmp_path)
    monkeypatch.setattr(load_postgis, "get_conn", lambda: _Ctx(conn))
    monkeypatch.setattr(load_postgis, "dosya_yaz", lambda: parquet)
    sonuc = load_postgis.yukle()
    assert sonuc["grid_cells"] == 7


class _Ctx:
    def __init__(self, conn):
        self.conn = conn

    def __enter__(self):
        return self.conn

    def __exit__(self, *a):
        return False


def test_dem_25m_yeniden_ornekleme(monkeypatch, tmp_path):
    from app.data_pipeline import process_grid

    class FakeSrc:
        transform = None
        crs = "EPSG:4326"

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    monkeypatch.setattr(process_grid, "PROCESSED_DIR", tmp_path)
    monkeypatch.setattr(process_grid.rasterio, "open", lambda *a, **k: FakeSrc())
    monkeypatch.setattr(process_grid.rasterio, "band", lambda s, i: s)
    monkeypatch.setattr(
        process_grid, "reproject",
        lambda source, destination, **kw: destination.__setitem__(slice(None), 100.0),
    )
    dem, _ = process_grid._dem_25m()
    assert np.isfinite(dem).all() and float(dem.mean()) > 90


def test_ek_yollar(monkeypatch, tmp_path):
    # Copernicus kimligi var ama erisim yok -> Terrarium yedegi
    from app import config as app_config
    from app.data_pipeline import download_dem, download_osm, ensure_schema

    monkeypatch.setattr(app_config, "COPERNICUS_CLIENT_ID", "test")
    monkeypatch.setattr(download_dem, "GRID_BBOX", (30.70, 36.90, 30.702, 36.902))
    monkeypatch.setattr(download_dem, "PROCESSED_DIR", tmp_path)
    monkeypatch.setattr(download_dem, "RAW_DIR", tmp_path)

    def fake_get(self, url, timeout=None):
        buf = io.BytesIO()
        Image.new("RGB", (256, 256), (128, 0, 0)).save(buf, format="PNG")
        return SimpleNamespace(raise_for_status=lambda: None, content=buf.getvalue())

    monkeypatch.setattr(download_dem.requests.Session, "get", fake_get)
    assert download_dem.indir().exists()

    # Overpass erisilemezse katman "yok" isaretlenir
    def fake_post(*a, **k):
        raise OSError("no overpass")

    monkeypatch.setattr(download_osm.requests, "post", fake_post)
    monkeypatch.setattr(download_osm, "PROCESSED_DIR", tmp_path)
    monkeypatch.setattr(download_osm, "RAW_DIR", tmp_path)
    assert download_osm.indir()["bina"] == __import__("pathlib").Path("")

    # Boş veritabanı yolu
    class FreshCursor:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def execute(self, sql, params=None):
            return None

        def fetchone(self):
            return (None,)

    class FreshConn:
        def cursor(self):
            return FreshCursor()

    monkeypatch.setattr(ensure_schema, "get_conn", lambda: _Ctx(FreshConn()))
    assert ensure_schema.ensure_schema() is True
