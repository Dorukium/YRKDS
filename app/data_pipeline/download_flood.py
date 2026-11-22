"""SYGM tasin tehlike haritasi (WMS) denemesi.

Erisilemezse katman NULL birakilir; F puanı DEM/TWI + OSM akarsu mesafesi +
gecmis olay sayisiyla hesaplanir ve kanit kaydi "SYGM haritasi: veri yok" der.
"""
from __future__ import annotations

import json

import requests

from app.config import PROCESSED_DIR, RAW_DIR

WMS_URL = "https://usbs.tarimorman.gov.tr/geoserver/wms"
UA = {"User-Agent": "YRKDS/0.1 (TUBITAK 2204-A; open-data research)"}


def indir() -> dict[str, object]:
    durum: dict[str, object] = {
        "kaynak": "SYGM WMS / TYPlan PDF",
        "wms_erisiildi": False,
        "tasin_bolge_katmani": "yok",
        "not": "SYGM WMS erisilemedi; 100/500 yillik tasin bolgesi bilinmiyor (NULL).",
    }
    try:
        r = requests.get(
            WMS_URL,
            params={"service": "WMS", "request": "GetCapabilities"},
            headers=UA,
            timeout=25,
        )
        if r.ok and "WMS_Capabilities" in r.text:
            durum["wms_erisiildi"] = True
            durum["not"] = (
                "WMS erisilebilir fakat yetkili tasin tehlike katmani adlari "
                "dogrulanmadan kullanilamaz; manuel katman secimi gerekir."
            )
    except Exception as exc:
        durum["not"] = f"SYGM WMS erisilemedi: {exc}"

    # Gecmis olay sayisi her zaman proje veri setinden turetilir.
    import csv
    import io

    from app.data_pipeline.seed import RAW_DATASETS

    olaylar = list(csv.DictReader(io.StringIO(RAW_DATASETS["taskin_olaylari.csv"])))
    durum["kayitli_olay_sayisi"] = len(olaylar)
    shutil_copy = PROCESSED_DIR / "taskin_olaylari.csv"
    shutil_copy.write_text(RAW_DATASETS["taskin_olaylari.csv"], encoding="utf-8")
    (RAW_DIR / "tasin_kaynak.json").write_text(json.dumps(durum, indent=2), encoding="utf-8")
    return durum


if __name__ == "__main__":
    indir()
