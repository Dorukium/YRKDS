"""Faz F: FastAPI uç noktaları ve güvenlik başlıkları (gerçek DB ile)."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app import security
from app.main import app

POLY = {
    "type": "Polygon",
    "coordinates": [[[30.64, 36.88], [30.642, 36.88], [30.642, 36.882],
                     [30.64, 36.882], [30.64, 36.88]]],
}


@pytest.fixture(scope="module")
def client():
    security.RATE_LIMIT = 100000
    with TestClient(app) as c:
        yield c


def test_saglik_ve_hazirlik(client):
    r = client.get("/api/saglik")
    assert r.status_code == 200 and r.json()["urun"] == "YRKDS"
    assert client.get("/health").status_code == 200
    h = client.get("/api/hazirlik").json()
    assert h["hucre"] > 700000


def test_guvenlik_basliklari(client):
    r = client.get("/api/saglik")
    assert r.headers["x-content-type-options"] == "nosniff"
    assert "default-src 'self'" in r.headers["content-security-policy"]


def test_frontend_statik(client):
    assert client.get("/").status_code == 200
    assert client.get("/js/map.js").status_code == 200


def test_analyze_ve_pdf(client):
    r = client.post("/api/analyze", json={"geojson": POLY})
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["skor_kapsami"]["tur"] == "kısmi"
    assert d["yasal_kisit_durumu"] == "dogrulanamadi"
    qid = d["parsel_id"].split(":")[0]
    pdf = client.get(f"/api/report/{qid}.pdf")
    assert pdf.status_code == 200 and pdf.content[:4] == b"%PDF"


def test_analyze_feature_collection_ve_hatali_geometri(client):
    fc = {"type": "FeatureCollection", "features": [{"type": "Feature", "geometry": POLY,
                                                       "properties": {}}]}
    assert client.post("/api/analyze", json={"geojson": fc}).status_code == 200
    assert client.post("/api/analyze", json={"geojson": {"type": "Point"}}).status_code == 422


def test_events_ve_filtre(client):
    assert client.get("/api/events?limit=5").status_code == 200
    assert client.get("/api/events?tur=deprem&limit=3").status_code == 200
    assert client.get("/api/events?bbox=30.6,36.8,30.9,37.0&limit=3").status_code == 200
    assert client.get("/api/events?bbox=bad").status_code == 422


def test_layer_endpointleri(client):
    for ad in ("grid", "taskin", "afete_maruz", "deprem", "bina", "su_yollari"):
        r = client.get(f"/api/layers/{ad}")
        assert r.status_code == 200, (ad, r.text[:120])
    assert client.get("/api/layers/yok").status_code == 404


def test_stats_ve_backtest(client):
    assert client.get("/api/stats/ilce/Kepez").status_code == 200
    assert client.get("/api/stats/ilce/YokIlce").status_code == 404
    b = client.get("/api/backtest/2009").json()
    assert b["metrikler"]["recall"] >= 0.6
    assert b["kalibrasyon"]["bagimsiz_mi"] is False


def test_api_anahtari_zorunlu_oldugunda(monkeypatch, client):
    monkeypatch.setattr(security, "API_KEY", "test-key")
    r = client.post("/api/analyze", json={"geojson": POLY})
    assert r.status_code == 401
    r = client.post("/api/analyze", json={"geojson": POLY}, headers={"X-API-Key": "test-key"})
    assert r.status_code == 200
    monkeypatch.setattr(security, "API_KEY", "")
