"""ERA5-Land yeniden analiz (CDS). Anahtar yoksa katman 'veri yok' kalir.

Mevcut iklim normalleri ve CMIP6 projeksiyonlari zaten proje veri setindedir;
bunlar kopyalanir, ERA5-Land gelmezse trend analizi "veri yetersiz" der.
"""
from __future__ import annotations

import json
import shutil

from app.config import CDSAPI_KEY, PROCESSED_DIR, RAW_DIR


def indir() -> dict[str, object]:
    for dosya in ("iklim_normalleri.csv", "istasyon_mikroklima.csv", "iklim_projeksiyonlari.csv"):
        shutil.copyfile(RAW_DIR / dosya, PROCESSED_DIR / dosya)

    durum: dict[str, object] = {
        "kaynak": "MGM Antalya 1991-2020 + CMIP6 (proje veri seti)",
        "era5_land": "yok",
        "not": "CDS API anahtari saglanmadigi icin ERA5-Land indirilmedi; "
        "iklim trendi icin yeterli veri yok olarak isaretlenir.",
    }
    if CDSAPI_KEY:
        try:
            import cdsapi

            c = cdsapi.Client()
            c.retrieve(
                "reanalysis-era5-land",
                {
                    "variable": ["total_precipitation", "2m_temperature"],
                    "year": ["2000", "2024"],
                    "month": [f"{m:02d}" for m in range(1, 13)],
                    "day": [f"{d:02d}" for d in range(1, 32)],
                    "area": [37.1, 30.5, 36.7, 30.9],
                    "format": "netcdf",
                },
                str(PROCESSED_DIR / "era5_land.nc"),
            )
            durum["era5_land"] = "var"
            durum["not"] = "ERA5-Land CDS uzerinden indirildi."
        except Exception as exc:
            durum["not"] = f"ERA5-Land indirilemedi: {exc}"

    (RAW_DIR / "iklim_kaynak.json").write_text(json.dumps(durum, indent=2), encoding="utf-8")
    return durum


if __name__ == "__main__":
    indir()
