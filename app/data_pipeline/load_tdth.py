"""A6 — insan adımıyla gelen `data/raw/tdth_grid.csv`'yi Otorite katmana yükler.

Dosya yoksa hata verir; asla sentetik değer üretmez (K3).
"""
from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime

import pandas as pd

from app.config import RAW_DIR
from app.db import get_conn

DOSYA = RAW_DIR / "tdth_grid.csv"
BASLIKLAR = {"lon", "lat", "pga_g", "ss_g", "s1_g", "pgv_cm_s"}


def yukle() -> dict[str, object]:
    if not DOSYA.exists():
        return {"durum": "veri_yok", "not": "docs/sop_tdth.md — insan adımı bekleniyor"}
    df = pd.read_csv(DOSYA)
    eksik = BASLIKLAR - set(df.columns)
    if eksik:
        raise ValueError(f"Eksik kolonlar: {sorted(eksik)}")
    if not (150 <= len(df) <= 400):
        raise ValueError(f"Beklenen 200–260 nokta, bulunan {len(df)}")
    if df["pga_g"].min() < 0.1 or df["pga_g"].max() > 0.8:
        raise ValueError("PGA aralığı beklenen 0.1–0.8 g dışında")

    sha = hashlib.sha256(DOSYA.read_bytes()).hexdigest()
    with get_conn() as conn, conn.cursor() as cur:
        # Geçici nokta tablosu
        cur.execute("CREATE TEMP TABLE tdth_points (lon float, lat float, pga float, ss float, s1 float, pgv float)")
        for satir in df.itertuples(index=False):
            cur.execute("INSERT INTO tdth_points VALUES (%s,%s,%s,%s,%s,%s)",
                        (float(satir.lon), float(satir.lat), float(satir.pga_g),
                         float(satir.ss_g), float(satir.s1_g), float(satir.pgv_cm_s)))
        cur.execute(
            """UPDATE grid_cells g SET pga_g = t.pga, ss_g = t.ss, s1_g = t.s1
               FROM (SELECT DISTINCT ON (g2.id) g2.id, p.pga, p.ss, p.s1
                     FROM grid_cells g2
                     CROSS JOIN LATERAL (
                       SELECT pga, ss, s1 FROM tdth_points p
                       ORDER BY ST_Distance(g2.geom::geography,
                                ST_SetSRID(ST_MakePoint(p.lon,p.lat),4326)::geography)
                       LIMIT 1) p) t
               WHERE g.id = t.id"""
        )
        cur.execute("SELECT COUNT(*) FROM grid_cells WHERE pga_g IS NOT NULL")
        satir = cur.fetchone()
        assert satir is not None
        dolu = satir[0]

    rapor = {"durum": "ok", "nokta": len(df), "dolu_hucre": dolu,
             "sha256": sha, "tarih": datetime.now(UTC).date().isoformat(),
             "yetkinlik": "Otorite"}
    (RAW_DIR / "tdth_manifest.json").write_text(
        json.dumps(rapor, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return rapor


if __name__ == "__main__":
    print(json.dumps(yukle(), ensure_ascii=False))
