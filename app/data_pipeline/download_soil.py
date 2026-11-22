"""SoilGrids v2 REST ornekleri.

1.5M hucreye tek tek REST istegi atilamayacagi icin ~1 km aralikli duzenli
orneklemeler alinir, 25 m grid'e bilineer enterpolasyon process_grid.py'de
yapilir. Kanit kaydi: "SoilGrids v2 REST + bilineer enterpolasyon" (turetilmis).
"""
from __future__ import annotations

import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import requests

from app.config import GRID_BBOX, PROCESSED_DIR, RAW_DIR

URL = "https://rest.isric.org/soilgrids/v2.0/properties/query"
PROPLER = ("clay", "silt", "sand", "phh2o", "soc", "bdod")
# ISRIC REST bu ortamda ~18 sn/istek. Uretim kalitesi icin ~1.1 km aralikli
# 551 nokta cekilir (16 paralel isci). Acil test icin 0.02'ye dusurulebilir.
ORNEK_ADIMI = 0.01  # derece (~1.1 km)
UA = {"User-Agent": "YRKDS/0.1 (TUBITAK 2204-A; open-data research)"}


def _tek_nokta(lon: float, lat: float) -> dict[str, float | None]:
    params: list[tuple[str, str | float]] = [
        ("lon", lon), ("lat", lat), ("depth", "0-5cm"), ("value", "mean")
    ]
    params += [("property", p) for p in PROPLER]
    for deneme in range(3):
        try:
            r = requests.get(URL, params=params, headers=UA, timeout=30)
            r.raise_for_status()
            doc = r.json()
            sonuc: dict[str, float | None] = {}
            for layer in doc["properties"]["layers"]:
                ham = layer["depths"][0]["values"].get("mean")
                faktor = layer.get("unit_measure", {}).get("d_factor", 1) or 1
                sonuc[layer["name"]] = None if ham is None else float(ham) / float(faktor)
            return sonuc
        except Exception:
            time.sleep(0.4 * (deneme + 1))
    return {p: None for p in PROPLER}


def indir() -> Path:
    min_lon, min_lat, max_lon, max_lat = GRID_BBOX
    lons = np.arange(min_lon, max_lon + ORNEK_ADIMI / 2, ORNEK_ADIMI)
    lats = np.arange(min_lat, max_lat + ORNEK_ADIMI / 2, ORNEK_ADIMI)
    noktalar = [(float(lo), float(la)) for la in lats for lo in lons]

    degerler = np.full((len(noktalar), len(PROPLER)), np.nan, dtype=np.float32)
    with ThreadPoolExecutor(max_workers=16) as havuz:
        gorevler = {havuz.submit(_tek_nokta, lo, la): i for i, (lo, la) in enumerate(noktalar)}
        for gorev in as_completed(gorevler):
            i = gorevler[gorev]
            sonuc = gorev.result()
            for j, p in enumerate(PROPLER):
                degerler[i, j] = sonuc.get(p) if sonuc.get(p) is not None else np.nan

    hedef = PROCESSED_DIR / "soil_samples.npz"
    np.savez_compressed(
        hedef,
        lons=np.array([p[0] for p in noktalar]),
        lats=np.array([p[1] for p in noktalar]),
        values=degerler,
        props=np.array(PROPLER),
        step=ORNEK_ADIMI,
        shape=(len(lons), len(lats)),
    )
    meta = {
        "kaynak": "SoilGrids v2 REST (ISRIC), depth 0-5cm, mean",
        "url": URL,
        "ornek_sayisi": len(noktalar),
        "gecerli_oran": round(float(np.mean(~np.isnan(degerler))), 3),
        "uyari": "Bazi noktalarda SoilGrids null dondurdu; bu hucreler enterpolasyonda dislanir.",
    }
    (RAW_DIR / "soil_kaynak.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"SoilGrids: {len(noktalar)} nokta, gecerli oran {meta['gecerli_oran']} -> {hedef}")
    return hedef


if __name__ == "__main__":
    indir()
