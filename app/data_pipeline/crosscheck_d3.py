"""D3 — GEM/OpenQuake PGA (araştırma etiketi) çapraz kontrol.

Kullanıcı kararı (2026-11-22): kamuya açık AFAD ArcGIS/WMS erişilemediği için
GEM sonucu **araştırma** rozetiyle kullanılır; resmi TDTH yerine geçmez.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
from datetime import UTC, datetime

import numpy as np
import rasterio

from app.config import PROCESSED_DIR, RAW_DIR
from app.data_pipeline.seed import RAW_DATASETS

GEM_TIF = PROCESSED_DIR / "gem_pga_475_rock.tif"
KAYNAK_URL = "https://cloud.openquake.org/s/6SnFk2f92JEr76H/download"


def _ilce_merkezleri() -> dict[str, tuple[float, float]]:
    satirlar = list(csv.DictReader(io.StringIO(RAW_DATASETS["dogrulama_etiketleri_2009.csv"])))
    kum: dict[str, list[tuple[float, float]]] = {}
    for s in satirlar:
        kum.setdefault(s["ilce"], []).append((float(s["lon"]), float(s["lat"])))
    return {k: (float(np.mean([p[0] for p in v])), float(np.mean([p[1] for p in v])))
            for k, v in kum.items()}


def calistir() -> dict[str, object]:
    if not GEM_TIF.exists():
        return {"durum": "veri_yok", "rozet": "Eksik", "not": "GEM raster indirilmedi"}
    satirlar = list(csv.DictReader(io.StringIO(RAW_DATASETS["zemin_hareketi.csv"])))
    proje: dict[str, float] = {}
    for s in satirlar:
        ilce = "Kepez" if s["ilce"] == "Kepez" else (
            "Muratpasa" if s["ilce"] == "Muratpasa" else "Konyaalti")
        proje.setdefault(ilce, float(s["pga_g"]))
    merkezler = _ilce_merkezleri()
    sonuclar: list[dict[str, object]] = []
    with rasterio.open(GEM_TIF) as ds:
        for ilce, (lon, lat) in merkezler.items():
            r, c = ds.index(lon, lat)
            gem = float(ds.read(1)[r, c])
            yerel = proje.get(ilce)
            sapma = None if yerel is None else round(abs(gem - yerel) / gem * 100, 1)
            sonuclar.append({
                "ilce": ilce, "gem_pga_g": round(gem, 4), "proje_pga_g": yerel,
                "sapma_pct": sapma,
                "not": "GEM Vs30=800 kaya; proje değeri zemin sınıfına göre düzeltilmiş",
            })
    sha = hashlib.sha256(GEM_TIF.read_bytes()).hexdigest()
    rapor: dict[str, object] = {
        "durum": "tamamlandi",
        "rozet": "Araştırma",
        "kaynak": KAYNAK_URL,
        "erisim_tarihi": datetime.now(UTC).date().isoformat(),
        "sha256": sha,
        "urun": "GEM GSHM v2023.1 PGA 475 yıl, Vs30=800 kaya",
        "ilceler": sonuclar,
        "uyari": "Resmi TDTH verisi değildir; sapma >%20 olan ilçeler için ADR-0008 yazıldı.",
    }
    (PROCESSED_DIR / "gem_crosscheck.json").write_text(
        json.dumps(rapor, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    manifest = RAW_DIR / "enrichment_manifest.json"
    kayitlar = json.loads(manifest.read_text(encoding="utf-8")) if manifest.exists() else []
    kayitlar.append({
        "id": "GEM_PGA_ARASTIRMA", "url": KAYNAK_URL,
        "erisim_tarihi": rapor["erisim_tarihi"], "lisans": "CC BY-NC-SA 4.0",
        "sha256": sha, "yetkinlik": "Araştırma", "not": str(rapor["uyari"]),
    })
    manifest.write_text(json.dumps(kayitlar, ensure_ascii=False, indent=2), encoding="utf-8")
    return rapor


if __name__ == "__main__":
    r = calistir()
    print(r["durum"], r["rozet"], str(r.get("ilceler", ""))[:20])
