"""Ek plan: en az 4 kaynağın manifest'li entegrasyonu (K5)."""
from __future__ import annotations

import json

from app.config import PROCESSED_DIR, RAW_DIR


def test_enrichment_manifest_dort_kaynak():
    p = RAW_DIR / "enrichment_manifest.json"
    assert p.exists()
    kayitlar = json.loads(p.read_text(encoding="utf-8"))
    assert len(kayitlar) >= 4
    for k in kayitlar:
        assert "url" in k and "erisim_tarihi" in k and "lisans" in k
        assert "sha256" in k
    assert any(k["id"] == "KOERI_KATALOG" and k["sha256"] for k in kayitlar)
    assert any(k["id"] == "esa_worldcover" and "CC-BY" in k["lisans"] for k in kayitlar)
    assert any(k["id"] == "ms_buildings" and "ODbL" in k["lisans"] for k in kayitlar)


def test_enrichment_fonksiyonlari_taklit(monkeypatch, tmp_path):
    from types import SimpleNamespace

    from app.data_pipeline import download_enrichment as de

    monkeypatch.setattr(de, "RAW_DIR", tmp_path)
    monkeypatch.setattr(de, "PROCESSED_DIR", tmp_path)

    def fake_get(url, params=None, headers=None, timeout=None):
        if "koeri" in url:
            return SimpleNamespace(raise_for_status=lambda: None, content=b"2026 01 01 36.9 30.7 4.0 test")
        if "worldcover" in url or "ms-buildings" in url or "/search" in url:
            if "/search" in url:
                return SimpleNamespace(ok=True, json=lambda: {"features": [{"id": "x", "properties": {"datetime": "2026-01-01"}}]})
            return SimpleNamespace(raise_for_status=lambda: None,
                                   json=lambda: {"title": "t", "license": "CC-BY-4.0"})
        return SimpleNamespace(raise_for_status=lambda: None, json=lambda: {"serviceDescription": "Vs30", "layers": []})

    monkeypatch.setattr(de.requests, "get", fake_get)
    kayitlar = de.calistir()
    assert len(kayitlar) == 4
    assert all(k["sha256"] for k in kayitlar)


def test_stac_ciktilari_ve_adr():
    assert (PROCESSED_DIR / "esa_worldcover.json").exists()
    assert (PROCESSED_DIR / "ms_buildings.json").exists()
    from app.config import ROOT

    for adr in ("0005-usgs-vs30-sorgu.md", "0006-nasa-landslide.md", "0007-jrc-flood.md"):
        assert (ROOT / "docs/ADR" / adr).exists()
    rapor = ROOT / "docs/capraz_kontrol.md"
    assert rapor.exists() and "USGS" in rapor.read_text(encoding="utf-8")
