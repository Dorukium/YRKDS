"""V5 A7 — JRC CEMS-GLOFAS v2.1 taşkın tehlike raster'i ve dürüst çakışma testi.

Kaynak: ee.ImageCollection('JRC/CEMS_GLOFAS/FloodHazard/v2_1')
Lisans: "available without restriction on use or distribution" → Otorite rozeti.
DoD: 2009 "Ağır" noktalarıyla ≥%60 çakışma. Çakışma yoksa sayıyı uydurmaz,
ADR-0007 açık kalır (K3/U12).
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
from datetime import date
from pathlib import Path
from typing import Any

import rasterio

from app.config import PROCESSED_DIR, RAW_DIR
from app.data_pipeline.seed import DOGRULAMA_ETIKETLERI

COLLECTION = "JRC/CEMS_GLOFAS/FloodHazard/v2_1"
AOI = (30.58, 36.82, 30.86, 37.00)
GEE_PROJECT = "rosy-fiber-478123-i1"
LISANS = "JRC CEMS-GLOFAS v2.1 — use/distribution without restriction"
KATALOG = "https://developers.google.com/earth-engine/datasets/catalog/JRC_CEMS_GLOFAS_FloodHazard_v2_1"


def agir_noktalar() -> list[dict[str, Any]]:
    satirlar = list(csv.DictReader(io.StringIO(DOGRULAMA_ETIKETLERI)))
    return [
        {"id": s["id"], "lat": float(s["lat"]), "lon": float(s["lon"]),
         "derinlik": float(s["su_derinligi_m"])}
        for s in satirlar if s["hasar"] == "Agir"
    ]


def indir(rp: int = 100) -> Path:
    """GEE'den AOI kırpılmış RP{rp} tehlike maskesini GeoTIFF olarak indirir."""
    import ee
    import requests

    ee.Initialize(project=GEE_PROJECT)
    aoi = ee.Geometry.Rectangle(list(AOI))
    im = (ee.ImageCollection(COLLECTION).mosaic().clip(aoi)
          .select(f"RP{rp}_depth_category").gt(0).toUint8().rename("flood"))
    url = im.getDownloadURL({
        "name": f"jrc_rp{rp}", "scale": 93, "region": aoi,
        "format": "GEOTIFF", "fileFormat": "GEOTIFF",
    })
    r = requests.get(url, timeout=240)
    r.raise_for_status()
    hedef = PROCESSED_DIR / f"jrc_flood_rp{rp}.tif"
    hedef.write_bytes(r.content)
    return hedef


def _ornekle(dosya: Path, noktalar: list[dict[str, Any]]) -> list[dict[str, Any]]:
    with rasterio.open(dosya) as ds:
        bant = ds.read(1)
        t = ds.transform
        sonuc = []
        for p in noktalar:
            col = int((p["lon"] - t.c) / t.a)
            row = int((p["lat"] - t.f) / t.e)
            deger = int(bant[row, col]) if (0 <= row < bant.shape[0] and 0 <= col < bant.shape[1]) else 0
            sonuc.append({**p, "jrc_rp100": deger})
    return sonuc


def overlap_raporu() -> dict[str, Any]:
    """2009 Ağır noktalarının JRC RP100 alanı içindeki oranını dürüst raporlar."""
    noktalar = agir_noktalar()
    dosya = PROCESSED_DIR / "jrc_flood_rp100.tif"
    if not dosya.exists():
        return {"durum": "raster_yok", "not": "make data-jrc ile indir;"}
    ornekl = _ornekle(dosya, noktalar)
    kapsanan = [p for p in ornekl if p["jrc_rp100"] > 0]
    oran = len(kapsanan) / len(ornekl) if ornekl else 0.0
    return {
        "durum": "ok",
        "kaynak": COLLECTION,
        "lisans": LISANS,
        "yetkinlik": "Otorite",
        "erisim_tarihi": date.today().isoformat(),
        "sha256": hashlib.sha256(dosya.read_bytes()).hexdigest(),
        "hedef": "2009-12-16 Boğaçay 'Ağır' noktaları (kalibrasyon — K4)",
        "nokta_sayisi": len(ornekl),
        "kapsanan": len(kapsanan),
        "cakisma_orani": round(oran, 4),
        "dod": oran >= 0.60,
        "not": ("DoD sağlandı" if oran >= 0.60 else
                "JRC küresel nehir modeli yerel plüvyal taşkını temsil etmiyor; "
                "≥%60 çakışma sağlanamadı. ADR-0007 açık kalır; sayı uydurulmaz."),
        "noktalar": ornekl,
    }


def calistir() -> dict[str, Any]:
    r = overlap_raporu()
    (PROCESSED_DIR / "jrc_overlap_report.json").write_text(
        json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    manifest = RAW_DIR / "enrichment_manifest.json"
    kayitlar = json.loads(manifest.read_text(encoding="utf-8")) if manifest.exists() else []
    if r["durum"] == "ok" and not any(k.get("id") == "JRC_GLOFAS" for k in kayitlar):
        kayitlar.append({
            "id": "JRC_GLOFAS", "url": KATALOG,
            "erisim_tarihi": r["erisim_tarihi"], "lisans": LISANS,
            "sha256": r["sha256"], "yetkinlik": "Otorite",
            "not": f"RP100/RP500 93m; 2009 Ağır çakışma %{r['cakisma_orani']*100:.1f}",
        })
        manifest.write_text(json.dumps(kayitlar, ensure_ascii=False, indent=2), encoding="utf-8")
    return r


if __name__ == "__main__":
    print(json.dumps(calistir(), ensure_ascii=False, indent=2))
