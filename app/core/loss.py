"""B3 — Beklenen yıllık kayıp görünümü (Tahmin, ±%50).

Katsayılar resmi hasar fonksiyonu değildir; ADR-0020'de uzman varsayımı
olduğu açıkça belirtilir. TL tutarı mertebe göstergesidir.
"""
from __future__ import annotations

import csv
import io
from typing import Any

from app.data_pipeline.seed import RAW_DATASETS

KATSAYILAR = {
    "Düşük": 0.001, "Düşük-Orta": 0.003, "Orta-Yüksek": 0.010,
    "Yüksek": 0.030, "Kritik": 0.060, "KARARSIZ": 0.0,
}
_ILCE_VALUE: dict[str, tuple[float, int]] = {}


def _veriler() -> dict[str, tuple[float, int]]:
    if _ILCE_VALUE:
        return _ILCE_VALUE
    for s in csv.DictReader(io.StringIO(RAW_DATASETS["bina_maruziyeti.csv"])):
        if s["ilce"] == "Toplam":
            continue
        deger = s["yapi_degeri_TL"].replace(" milyar", "")
        _ILCE_VALUE[s["ilce"]] = (float(deger) * 1e9, int(s["toplam_bina"]))
    return _ILCE_VALUE


def beklenen_kayip(bant: str, ilce: str | None) -> dict[str, Any]:
    kayit = _veriler().get(ilce or "")
    if not kayit:
        return {"durum": "veri_yok", "rozet": "Eksik"}
    toplam_deger, bina_sayisi = kayit
    birim = toplam_deger / max(1, bina_sayisi)
    k = KATSAYILAR.get(bant, 0.0)
    merkez = birim * k
    return {
        "durum": "ok",
        "rozet": "Tahmin",
        "birim_bina_degeri_TL": round(birim),
        "merkez_TL_yil": round(merkez),
        "alt_TL_yil": round(merkez * 0.5),
        "ust_TL_yil": round(merkez * 1.5),
        "aralik": "±%50",
        "aciklama": "Bina başına ilçe ortalaması × bant katsayısı; resmi hasar fonksiyonu değil (ADR-0020).",
    }
