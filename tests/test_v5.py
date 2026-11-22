"""V5 FAZ 1/5 altyapı testleri — ağ/gerçek kimlik kullanmadan (K6 regresyon)."""
from __future__ import annotations

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
