"""A3 — Resmî Gazete kararları + Nominatim geocode ile yaklaşık VETO geometrisi.

U7: her kayıt `konum_guveni=dusuk (geocode proxy)` ve kaynak URL taşır.
Bu poligonlar resmi sınır DEĞİLDİR; 300 m tamponlu mahalle merkezidir.
"""
from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Any

from app.config import RAW_DIR
from app.db import get_conn

KARARLAR: list[dict[str, Any]] = [
    {
        "karar_no": "2016/9615", "tarih": "2017-01-03", "tur": "6306_riskli_alan",
        "yer": "Kepez / Gülveren Mahallesi", "lat": 36.9049387, "lon": 30.6443809,
        "rg": "RG 03.01.2017/29937",
        "url": "https://www.lexpera.com.tr/mevzuat/arama?p=lZHRSsMwFIZfpcQ7GaPtcMzdRctwtBZpy0RklMOSldAsHUkmzLFn8Rm88Wp3ne9lNuw61EK9ysn5vz9",
    },
    {
        "karar_no": "2014/7041", "tarih": "2014-12-25", "tur": "6306_riskli_alan",
        "yer": "Kepez / Santral (Santral Kentsel Dönüşüm)", "lat": 36.9358467, "lon": 30.6332241,
        "rg": "RG 25.12.2014/29216",
        "url": "https://kurultay.hkmo.org.tr/Files/Declarations/93cd1abe7ec4e18_ek.pdf",
    },
    {
        "karar_no": "11600", "tarih": "2026-08-10", "tur": "afete_maruz_bolge",
        "yer": "Konyaaltı / Hisarçandır, Üçoluk, Gökdere", "lat": 36.7706015, "lon": 30.4681614,
        "rg": "Cumhurbaşkanı Kararı, 7269 sayılı Kanun",
        "url": "https://www.antalyakorfez.com/antalyada-3-mahalle-afet-bolgesi-ilan-edildi-yapilasma-kisitlandi",
    },
]


def yukle() -> int:
    with get_conn() as conn, conn.cursor() as cur:
        for k in KARARLAR:
            aciklama = (
                f"{k['rg']}. Resmî sınır belgeye ekli değil; Nominatim geocode "
                "merkezine 300 m tampon uygulandı. GEOKODE PROXY — resmi VETO sınırı değil."
            )
            cur.execute(
                """INSERT INTO legal_constraints
                   (karar_no, karar_tarihi, tur, ilce, mahalle, geom, kaynak_url,
                    konum_guveni, aciklama)
                   VALUES (%s,%s,%s,%s,%s,
                     ST_Buffer(ST_SetSRID(ST_MakePoint(%s,%s),4326)::geography,300)::geometry,
                     %s,%s,%s)
                   ON CONFLICT (karar_no) DO UPDATE SET
                     geom=EXCLUDED.geom, konum_guveni=EXCLUDED.konum_guveni,
                     aciklama=EXCLUDED.aciklama""",
                (k["karar_no"], k["tarih"], k["tur"], k["yer"].split(" / ")[0],
                 k["yer"], k["lon"], k["lat"], k["url"], "dusuk (geocode proxy)", aciklama),
            )
        cur.execute("SELECT COUNT(*) FROM legal_constraints WHERE geom IS NOT NULL")
        satir = cur.fetchone()
        assert satir is not None
        return int(satir[0])


if __name__ == "__main__":
    n = yukle()
    manifest = RAW_DIR / "legal_geometry_manifest.json"
    kayitlar = [
        {
            "karar_no": k["karar_no"], "url": k["url"],
            "erisim_tarihi": datetime.now(UTC).date().isoformat(),
            "koordinat": [k["lat"], k["lon"]],
            "sha256": hashlib.sha256(json.dumps(k, sort_keys=True).encode()).hexdigest(),
            "rozet": "Tahmin — geocode proxy (300 m tampon)",
        }
        for k in KARARLAR
    ]
    manifest.write_text(json.dumps(kayitlar, ensure_ascii=False, indent=2), encoding="utf-8")
    print("geometri sayisi", n)
