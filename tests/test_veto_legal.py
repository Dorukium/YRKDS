"""Faz B DoD: Resmî Gazete kaynaklı VETO mekanizması.

A3: üç gerçek Resmî Gazete kararının geocode proxy geometrisi VETO üretir.
Proxy olduğu (`konum_guveni=dusuk`) açıkça etiketlidir (ADR-0017).
"""
from __future__ import annotations

import json

from app.config import ROOT
from app.core.legal_veto import legal_veto
from app.db import get_conn

IC = {
    "type": "Polygon",
    "coordinates": [[[30.70, 36.90], [30.702, 36.90], [30.702, 36.902],
                     [30.70, 36.902], [30.70, 36.90]]],
}
DIS = {
    "type": "Polygon",
    "coordinates": [[[30.80, 36.95], [30.802, 36.95], [30.802, 36.952],
                     [30.80, 36.952], [30.80, 36.95]]],
}


def test_gercek_karar_geometrileri_ve_manifest():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT karar_no FROM legal_constraints WHERE geom IS NOT NULL ORDER BY karar_no"
        )
        kararlar = [r[0] for r in cur.fetchall()]
    assert len(kararlar) >= 3
    assert "2016/9615" in kararlar and "11600" in kararlar
    manifest = ROOT / "data/raw/legal_geometry_manifest.json"
    assert manifest.exists()
    kayitlar = json.loads(manifest.read_text(encoding="utf-8"))
    assert all("geocode proxy" in k["rozet"] for k in kayitlar)


def test_geocode_proxy_icinde_veto_disinda_degil():
    # Gülveren merkezi 30.64438, 36.90494 — 300 m tampon içinde
    ic = {"type": "Polygon", "coordinates": [[
        [30.6442, 36.9048], [30.6446, 36.9048], [30.6446, 36.9051],
        [30.6442, 36.9051], [30.6442, 36.9048]]]}
    sonuc = legal_veto(ic)
    assert sonuc["veto"] is True
    assert "2016/9615" in sonuc["neden"]
    dis = legal_veto(IC)
    assert dis["veto"] is False


def test_geometrisi_olan_karar_icinde_veto_disinda_degil():
    import json

    from app.core.legal_veto import legal_veto

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO legal_constraints
                   (karar_no, karar_tarihi, tur, ilce, mahalle, geom, kaynak_url,
                    konum_guveni, aciklama)
                   VALUES ('TEST-1','2020-01-01','6306_riskli_alan','Kepez','Test',
                     ST_GeomFromGeoJSON(%s),'test','yuksek','mekanizma testi')""",
                (json.dumps(IC),),
            )
        ic = legal_veto(IC, conn_in=conn)
        dis = legal_veto(DIS, conn_in=conn)
        assert ic["veto"] is True
        assert "TEST-1" in ic["neden"]
        assert dis["veto"] is False
        conn.rollback()  # test verisi kalıcı değil


def test_karar_11600_manifestte_kayitli():
    import json

    from app.config import ROOT

    manifest = json.loads((ROOT / "data/raw/research_manifest.json").read_text())
    assert any(m.get("id") == "RES-001" and "11600" in m.get("not", "") for m in manifest)
