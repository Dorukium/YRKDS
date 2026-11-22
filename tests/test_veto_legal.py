"""Faz B DoD: Resmî Gazete kaynaklı VETO mekanizması.

Gerçek kararın (11600) jeoreferanslı sınırı yok -> VETO tetiklenmez ve
'dogrulanamadı' döner (K3). Mekanizma, geçici bir geometri ile ayrıca test
edilir; test sonunda transaction rollback yapılır, veri kalıcı değişmez.
"""
from __future__ import annotations

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


def test_gercek_karar_geometrisiz_veto_tetiklemez():
    sonuc = legal_veto(IC)
    assert sonuc["veto"] is False
    assert sonuc["durum"] == "dogrulanamadi"
    assert sonuc["uyari"] is not None


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
