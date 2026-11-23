"""V5 FAZ 1/5 altyapı testleri — ağ/gerçek kimlik kullanmadan (K6 regresyon)."""
from __future__ import annotations

import json
from types import SimpleNamespace

import pytest


def test_check_auth_durumlari(monkeypatch, tmp_path):
    from app.data_pipeline import check_auth

    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text(
        "EARTHDATA_USERNAME=u\nEARTHDATA_PASSWORD=p\n", encoding="utf-8"
    )
    r = check_auth.check()
    assert r["nasa_earthdata"]["durum"] == "var"
    assert r["zenodo"]["durum"] == "yok"
    assert r["tdth"]["durum"] == "deaktif"
    assert r["genel"] == "eksik kimlik var"


def test_check_auth_tum_kimlikler_var(monkeypatch, tmp_path):
    from pathlib import Path

    from app.data_pipeline import check_auth

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    (tmp_path / ".config" / "earthengine").mkdir(parents=True)
    (tmp_path / ".config" / "earthengine" / "credentials").write_text("{}", encoding="utf-8")
    (tmp_path / ".env").write_text(
        "EARTHDATA_USERNAME=u\nEARTHDATA_PASSWORD=p\nZENODO_TOKEN=tok\nBOŞ=\n",
        encoding="utf-8",
    )
    r = check_auth.check()
    assert r["zenodo"]["durum"] == "var"
    assert r["genel"] == "hazır"


def test_gee_kimlik_durumu_ve_yok_yolu(monkeypatch, tmp_path):
    from app.data_pipeline import gee_auth

    monkeypatch.setattr(gee_auth, "CRED_PATH", tmp_path / "yok")
    r = gee_auth.kimlik_durumu()
    assert r["kimlik"] == "yok"
    d = gee_auth.dogrula()
    assert d["baglanti"] == "kimlik_yok"
    with pytest.raises(FileNotFoundError):
        gee_auth.initialize()


def test_gee_initialize_ve_dogrula_taklit(monkeypatch, tmp_path):
    from app.data_pipeline import gee_auth

    cred = tmp_path / "credentials"
    cred.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(gee_auth, "CRED_PATH", cred)
    monkeypatch.setenv("GEE_PROJECT", "yrkds-test")

    fake_ee = SimpleNamespace(
        Initialize=lambda **kw: None,
        data=SimpleNamespace(getAlgorithms=lambda: [1, 2, 3]),
    )
    import sys

    monkeypatch.setitem(sys.modules, "ee", fake_ee)
    assert gee_auth.initialize() is fake_ee
    d = gee_auth.dogrula()
    assert d["baglanti"] == "ok" and d["algoritma_sayisi"] == 3


def test_gee_dogrula_hata_yolu(monkeypatch, tmp_path):
    from app.data_pipeline import gee_auth

    cred = tmp_path / "credentials"
    cred.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(gee_auth, "CRED_PATH", cred)
    monkeypatch.delenv("GEE_PROJECT", raising=False)

    def hata(**kw):
        raise RuntimeError("baglanti yok")

    import sys

    monkeypatch.setitem(
        sys.modules, "ee",
        SimpleNamespace(Initialize=hata, data=SimpleNamespace(getAlgorithms=list)),
    )
    d = gee_auth.dogrula()
    assert d["baglanti"] == "hata" and d["hata"] == "RuntimeError"


def test_gee_flood_tarih_ve_baglanti(monkeypatch):
    from app.data_pipeline import gee_flood

    assert gee_flood._tarih(0) == "1970-01-01"

    from app.data_pipeline import gee_auth

    monkeypatch.setattr(gee_auth, "initialize", lambda: "ee-modul")
    assert gee_flood.initializeee() == "ee-modul"


def test_gee_flood_aoi_olaylari_taklit():
    from app.data_pipeline.gee_flood import aoi_olaylari

    class FakeEE:
        def FeatureCollection(self, ad):
            return self

        @property
        def Geometry(self):
            return SimpleNamespace(Rectangle=lambda koord: object())

        def filterBounds(self, box):
            return self

        def getInfo(self):
            return {"features": [{
                "properties": {
                    "id": "2175",
                    "system:time_start": 1044345600000,
                    "system:time_end": 1049289600000,
                    "dfo_country": "Turkey",
                    "system:asset_size": 123,
                }
            }]}

    r = aoi_olaylari(FakeEE())
    assert r[0]["id"] == "2175" and r[0]["baslangic"].startswith("2003-02")


def test_gee_flood_etiket_yok_durumu():
    from app.data_pipeline.gee_flood import dogrulama_etiketleri

    olaylar = [
        {"id": "2175", "baslangic": "2003-02-04", "bitis": "2003-03-12"},
        {"id": "2433", "baslangic": "2004-01-24", "bitis": "2004-02-14"},
    ]
    r = dogrulama_etiketleri(olaylar)
    assert r["durum"] == "etiket_yok"
    assert r["aoi_olay_sayisi"] == 2 and r["eslesen_olay_sayisi"] == 0


def test_gee_flood_eslesen_olay_var():
    from app.data_pipeline.gee_flood import dogrulama_etiketleri

    olaylar = [{"id": "X", "baslangic": "2003-12-01", "bitis": "2003-12-15"}]
    r = dogrulama_etiketleri(olaylar)
    assert r["durum"] == "etiket_var" and r["eslesen_olay_sayisi"] == 1


def test_gee_flood_calistir_taklit(monkeypatch, tmp_path):
    from app.data_pipeline import gee_flood

    monkeypatch.setattr(gee_flood, "LABELS", tmp_path)
    monkeypatch.setattr(gee_flood, "initializeee", lambda: object())
    monkeypatch.setattr(
        gee_flood, "aoi_olaylari",
        lambda ee: [{"id": "1", "baslangic": "2003-02-01", "bitis": "2003-03-01"}],
    )
    r = gee_flood.calistir()
    assert r["durum"] == "etiket_yok"
    assert (tmp_path / "gfd_antalya_events.json").exists()
    assert (tmp_path / "gfd_validation_labels.json").exists()


def test_jrc_agir_noktalar():
    from app.data_pipeline.jrc_flood import agir_noktalar

    n = agir_noktalar()
    assert len(n) == 6
    assert all(p["derinlik"] >= 1.0 for p in n)
    assert n[0]["id"] == "ANT-2009-001"


def test_jrc_overlap_durust_rapor(monkeypatch, tmp_path):
    import numpy as np
    import rasterio
    from rasterio.transform import from_origin

    from app.data_pipeline import jrc_flood

    tif = tmp_path / "jrc_flood_rp100.tif"
    with rasterio.open(tif, "w", driver="GTiff", height=10, width=10, count=1,
                       dtype="uint8", crs="EPSG:4326",
                       transform=from_origin(30.58, 37.00, 0.03, 0.02)) as ds:
        a = np.zeros((10, 10), dtype=np.uint8)
        a[4, 4] = 1
        ds.write(a, 1)
    monkeypatch.setattr(jrc_flood, "PROCESSED_DIR", tmp_path)
    r = jrc_flood.overlap_raporu()
    assert r["durum"] == "ok" and r["nokta_sayisi"] == 6
    assert r["yetkinlik"] == "Otorite" and r["dod"] is False
    assert "uydurulmaz" in r["not"]

    tif.unlink()
    assert jrc_flood.overlap_raporu()["durum"] == "raster_yok"


def test_jrc_calistir_manifest(monkeypatch, tmp_path):
    import numpy as np
    import rasterio
    from rasterio.transform import from_origin

    from app.data_pipeline import jrc_flood

    with rasterio.open(tmp_path / "jrc_flood_rp100.tif", "w", driver="GTiff",
                       height=5, width=5, count=1, dtype="uint8", crs="EPSG:4326",
                       transform=from_origin(30.58, 37.00, 0.06, 0.04)) as ds:
        ds.write(np.ones((5, 5), dtype=np.uint8), 1)
    monkeypatch.setattr(jrc_flood, "PROCESSED_DIR", tmp_path)
    monkeypatch.setattr(jrc_flood, "RAW_DIR", tmp_path)
    r = jrc_flood.calistir()
    assert (tmp_path / "jrc_overlap_report.json").exists()
    if r["durum"] == "ok":
        m = json.loads((tmp_path / "enrichment_manifest.json").read_text())
        assert any(k.get("id") == "JRC_GLOFAS" for k in m)


def test_publish_citation_ve_token_yok(monkeypatch, tmp_path):
    from app.data_pipeline import publish

    monkeypatch.setattr(publish, "ROOT", tmp_path)
    monkeypatch.delenv("ZENODO_TOKEN", raising=False)
    r = publish.publish()
    assert r["durum"] == "kimlik_yok"
    assert (tmp_path / "CITATION.cff").exists()
    icerik = (tmp_path / "CITATION.cff").read_text(encoding="utf-8")
    assert "PENDING" in icerik and "10.5281/zenodo.XXXX" not in icerik
    assert publish.citation_yaz("10.5281/zenodo.123").exists()
    assert (tmp_path / "CITATION.cff").read_text(encoding="utf-8").find("10.5281/zenodo.123") > 0


def test_publish_guncelle_ve_basarili_yayin(monkeypatch, tmp_path):
    from app.data_pipeline import publish

    monkeypatch.setattr(publish, "ROOT", tmp_path)
    (tmp_path / "CHANGELOG.md").write_text("# changelog", encoding="utf-8")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "sbom.json").write_text("{}", encoding="utf-8")
    readme = tmp_path / "README.md"
    readme.write_text("# YRKDS\n", encoding="utf-8")
    ozet = tmp_path / "docs" / "tubitak_rapor" / "01_ozet.md"
    ozet.parent.mkdir(parents=True)
    ozet.write_text("# Özet\n", encoding="utf-8")

    class Resp:
        def __init__(self, veri=None):
            self.veri = veri or {}

        def raise_for_status(self):
            return None

        def json(self):
            return self.veri

    def post(url, **kw):
        if "publish" in url:
            return Resp({"doi": "10.5281/zenodo.999"})
        return Resp({"id": 42, "links": {"bucket": "http://bucket"}})

    monkeypatch.setattr(publish.requests, "post", post)
    monkeypatch.setattr(publish.requests, "put", lambda *a, **k: Resp())
    monkeypatch.setenv("ZENODO_TOKEN", "test-token")
    r = publish.publish()
    assert r["durum"] == "ok" and r["doi"] == "10.5281/zenodo.999"
    assert "10.5281/zenodo.999" in readme.read_text(encoding="utf-8")
    assert "10.5281/zenodo.999" in ozet.read_text(encoding="utf-8")
    assert "10.5281/zenodo.999" in (tmp_path / "CITATION.cff").read_text(encoding="utf-8")


def test_ensure_schema_advisory_lock(monkeypatch):
    """K6 regresyon: çoklu worker DDL deadlock'u advisory lock ile serileşir."""
    from app.data_pipeline import ensure_schema as es

    cagirilar = []

    class Cur:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def execute(self, sql, params=None):
            cagirilar.append(sql)

        def fetchone(self):
            return (None,)

    class Conn:
        def cursor(self):
            return Cur()

    class Ctx:
        def __enter__(self):
            return Conn()

        def __exit__(self, *a):
            return False

    monkeypatch.setattr(es, "get_conn", lambda: Ctx())
    assert es.ensure_schema() is True
    assert any("pg_advisory_xact_lock" in s for s in cagirilar)
    assert not any("pg_advisory_unlock" in s for s in cagirilar)


def test_modul_main_bloklari(monkeypatch, tmp_path, capsys):
    import runpy

    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text("NASA_EARTHDATA_USER=u\n", encoding="utf-8")
    runpy.run_module("app.data_pipeline.check_auth", run_name="__main__")
    assert "nasa_earthdata" in capsys.readouterr().out
    monkeypatch.setattr(
        "pathlib.Path.home", classmethod(lambda cls: tmp_path)
    )
    runpy.run_module("app.data_pipeline.gee_auth", run_name="__main__")
    assert "baglanti" in capsys.readouterr().out


def test_publish_yardimci_dallari(monkeypatch, tmp_path):
    from app.data_pipeline import publish

    monkeypatch.setattr(publish, "ROOT", tmp_path)
    # Dosya yoksa _guncelle hiçbir şey yapmaz.
    publish._guncelle(tmp_path / "yok.md", "10.5281/zenodo.1")
    # DOI zaten varsa tekrar yazılmaz.
    readme = tmp_path / "README.md"
    readme.write_text("**Zenodo DOI:** [10.5281/zenodo.5](https://doi.org/10.5281/zenodo.5)\n",
                      encoding="utf-8")
    publish._guncelle(readme, "10.5281/zenodo.5")
    assert readme.read_text(encoding="utf-8").count("10.5281/zenodo.5") == 2
    # Eski DOI satırı yenisiyle değiştirilir.
    publish._guncelle(readme, "10.5281/zenodo.6")
    assert "10.5281/zenodo.6" in readme.read_text(encoding="utf-8")
    assert "10.5281/zenodo.5" not in readme.read_text(encoding="utf-8")
    # CITATION.cff yeniden yazılabilir.
    assert publish.citation_yaz("10.5281/zenodo.7").exists()


def test_publish_doi_yok_dali(monkeypatch, tmp_path):
    from app.data_pipeline import publish

    monkeypatch.setattr(publish, "ROOT", tmp_path)
    monkeypatch.setenv("ZENODO_TOKEN", "test-token")

    class Resp:
        def __init__(self, veri):
            self.veri = veri

        def raise_for_status(self):
            return None

        def json(self):
            return self.veri

    monkeypatch.setattr(
        publish.requests, "post",
        lambda *a, **k: Resp({"id": 1, "links": {"bucket": "b"}})
        if "publish" not in a[0] else Resp({}),
    )
    monkeypatch.setattr(publish.requests, "put", lambda *a, **k: Resp({}))
    assert publish.publish()["durum"] == "doi_yok"


def test_publish_dry_run_ve_hata(monkeypatch, tmp_path):
    from app.data_pipeline import publish

    monkeypatch.setattr(publish, "ROOT", tmp_path)
    monkeypatch.setenv("ZENODO_TOKEN", "test-token")

    class Resp:
        def raise_for_status(self):
            return None

        def json(self):
            return {"id": 7, "links": {"bucket": "b"}}

    monkeypatch.setattr(publish.requests, "post", lambda *a, **k: Resp())
    monkeypatch.setattr(publish.requests, "put", lambda *a, **k: Resp())
    assert publish.publish(dry_run=True)["durum"] == "sandbox_taslak"

    def hata(*a, **k):
        raise OSError("servis yok")

    monkeypatch.setattr(publish.requests, "post", hata)
    r = publish.publish()
    assert r["durum"] == "hata" and r["hata"] == "OSError"
