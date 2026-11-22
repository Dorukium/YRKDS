"""Faz F: metrikler, Redis hız sınırı, olay izleme ve zamanlayıcı."""
from __future__ import annotations

from types import SimpleNamespace

from fastapi.testclient import TestClient

from app import security
from app.main import app


def test_metrics_ve_durum_uclari():
    with TestClient(app) as c:
        m = c.get("/metrics")
        assert m.status_code == 200 and "yrkds_requests_total" in m.text
        assert c.get("/healthz").json()["durum"] == "ok"
        assert c.get("/readyz").json()["durum"] == "ready"


def test_redis_hiz_siniri_dali(monkeypatch):
    class FakeRedis:
        def __init__(self):
            self.sayi = 0

        def incr(self, key):
            self.sayi += 1
            return self.sayi

        def expire(self, key, s):
            return True

    fake = FakeRedis()
    monkeypatch.setattr(security, "_redis_client", fake)
    monkeypatch.setattr(security, "RATE_LIMIT", 1)
    with TestClient(app) as c:
        assert c.get("/api/saglik").status_code == 200
        r = c.post("/api/analyze", json={"geojson": {"type": "Point"}})
        assert r.status_code in (401, 429, 422)
    monkeypatch.setattr(security, "_redis_client", None)
    monkeypatch.setattr(security, "RATE_LIMIT", 100000)


def test_redis_hataliyken_yerel_sayaca_duser(monkeypatch):
    class Bozuk:
        def incr(self, key):
            raise OSError("redis down")

    monkeypatch.setattr(security, "_redis_client", Bozuk())
    monkeypatch.setattr(security, "RATE_LIMIT", 100000)
    with TestClient(app) as c:
        assert c.get("/api/saglik").status_code == 200
    monkeypatch.setattr(security, "_redis_client", None)


def test_event_monitor_ve_zamanlayici(monkeypatch):
    from app.ai import event_monitor, scheduler

    monkeypatch.setattr(
        event_monitor.requests, "get",
        lambda *a, **k: SimpleNamespace(
            raise_for_status=lambda: None, json=lambda: [{"id": 1}]
        ),
    )
    d = event_monitor.son_depremler(1)
    assert d["durum"] == "ok" and d["sayi"] == 1
    monkeypatch.setattr(
        event_monitor.requests, "get",
        lambda *a, **k: (_ for _ in ()).throw(OSError("no afad")),
    )
    assert event_monitor.son_depremler(1)["durum"] == "kaynak_erisiilemedi"

    monkeypatch.setenv("YRKDS_MONITOR", "1")
    s = scheduler.baslat()
    assert s is not None
    scheduler.durdur()
    monkeypatch.setenv("YRKDS_MONITOR", "0")


def test_duyarlilik_ve_guven_dili():
    from app.core.sensitivity import guven_ifadesi, skor_araligi

    assert guven_ifadesi(0.8) == "yüksek güven"
    assert guven_ifadesi(0.5) == "orta güven"
    assert "yetersiz" in guven_ifadesi(0.2)
    assert skor_araligi({})["n"] == 0
    aralik = skor_araligi({"ZB": 0.8, "L": 0.5, "S": None, "H": 0.2, "F": 0.9}, n=10)
    assert aralik["p5"] is not None and aralik["p95"] >= aralik["p5"]
