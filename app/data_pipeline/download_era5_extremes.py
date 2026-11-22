"""A5 — ERA5-Land tabanlı günlük yağış serisi (Open-Meteo Archive API).

Kaynak: https://archive-api.open-meteo.com (ERA5 / ERA5-Land türevleri).
Anahtar gerekmez; K5 manifest'i URL + tarih + SHA256 içerir.
1969-01-17 ızgara değeri ile istasyon kaydı (331.5 mm) farkı ADR-0014'te.
"""
from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime

import numpy as np
import requests

from app.config import PROCESSED_DIR, RAW_DIR

API = "https://archive-api.open-meteo.com/v1/archive"
LAT, LON = 36.90, 30.70
OLAY_TARIHI = "1969-01-17"


def indir() -> dict[str, object]:
    seri: list[dict[str, float | str]] = []
    for yil in (1991, 2000, 2003, 2008, 2009, 2020, 2024):
        params: dict[str, str | float] = {
            "latitude": LAT, "longitude": LON,
            "start_date": f"{yil}-01-01", "end_date": f"{yil}-12-31",
            "daily": "precipitation_sum,temperature_2m_max", "timezone": "UTC",
        }
        r = requests.get(API, params=params, timeout=60)
        r.raise_for_status()
        (RAW_DIR / f"era5_openmeteo_{yil}.json").write_bytes(r.content)
        j = r.json()
        gunler = j["daily"]
        for t, p, s in zip(gunler["time"], gunler["precipitation_sum"],
                           gunler["temperature_2m_max"]):
            if p is not None:
                seri.append({"tarih": t, "yagis_mm": float(p), "sicaklik_C": float(s)})

    olay_params: dict[str, str | float] = {
        "latitude": LAT, "longitude": LON,
        "start_date": OLAY_TARIHI, "end_date": OLAY_TARIHI,
        "daily": "precipitation_sum", "timezone": "UTC",
    }
    olay = requests.get(API, params=olay_params, timeout=60)
    olay.raise_for_status()
    olay_j = olay.json()
    olay_mm = float(olay_j["daily"]["precipitation_sum"][0])
    p99 = float(np.percentile([s["yagis_mm"] for s in seri], 99))

    (PROCESSED_DIR / "era5_gunluk.csv").write_text(
        "tarih,yagis_mm,sicaklik_C\n" + "\n".join(
            f"{s['tarih']},{s['yagis_mm']},{s['sicaklik_C']}" for s in seri
        ), encoding="utf-8",
    )
    rapor = {
        "kaynak": API, "rozet": "Proxy — ERA5-Land günlük (araştırma)",
        "erisim_tarihi": datetime.now(UTC).date().isoformat(),
        "koordinat": [LAT, LON],
        "gun_sayisi": len(seri),
        "p99_yagis_mm": round(p99, 1),
        "olay_1969_01_17_yagis_mm": olay_mm,
        "istasyon_acion": 331.5,
        "sha256": hashlib.sha256(json.dumps(olay_j, sort_keys=True).encode()).hexdigest(),
        "uyari": "Izgara hücresi ortalama değeridir; istasyon nokta ölçümüyle karşılaştırılamaz (ADR-0014).",
    }
    (PROCESSED_DIR / "era5_extremes.json").write_text(
        json.dumps(rapor, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    manifest = RAW_DIR / "enrichment_manifest.json"
    kayitlar = json.loads(manifest.read_text(encoding="utf-8")) if manifest.exists() else []
    kayitlar.append({
        "id": "ERA5_OPENMETEO", "url": API, "erisim_tarihi": rapor["erisim_tarihi"],
        "lisans": "CC BY 4.0 (CopernicusERA5 / Open-Meteo)",
        "sha256": rapor["sha256"], "yetkinlik": "Proxy",
        "not": f"{len(seri)} gün; 1969 olay günü {olay_mm} mm (ızgara).",
    })
    manifest.write_text(json.dumps(kayitlar, ensure_ascii=False, indent=2), encoding="utf-8")
    return rapor


if __name__ == "__main__":
    r = indir()
    print(r["gun_sayisi"], "gün, p99", r["p99_yagis_mm"], "1969", r["olay_1969_01_17_yagis_mm"])
