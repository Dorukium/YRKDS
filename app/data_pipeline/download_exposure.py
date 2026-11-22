"""A4 — Planetary Computer: ESA WorldCover 10 m + Microsoft Buildings STAC.

WorldPop 100 m koleksiyonu Planetary Computer'da bulunamadı (ADR-0015);
maruziyet nüfusu TÜİK ilçe verisiyle "Tahmin" rozetli kullanılır.
"""
from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

import planetary_computer
import pystac_client
import rasterio

from app.config import GRID_BBOX, PROCESSED_DIR, RAW_DIR
from app.data_pipeline.seed import dogrulama_etiketleri

STAC = "https://planetarycomputer.microsoft.com/api/stac/v1"
BBOX = list(GRID_BBOX)


def calistir() -> dict[str, Any]:
    client = pystac_client.Client.open(STAC, modifier=planetary_computer.sign_inplace)
    sonuc: dict[str, Any] = {
        "erisim_tarihi": datetime.now(UTC).date().isoformat(),
        "kaynak": STAC, "koleksiyonlar": {}, "worldcover_ornekleri": [],
        "not": "MS Buildings GeoParquet uzak abfs; operasyonel geometri OSM'den. WorldPop yok (ADR-0015).",
    }
    for ad in ("esa-worldcover", "ms-buildings"):
        items = list(client.search(collections=[ad], bbox=BBOX, max_items=2).items())
        sonuc["koleksiyonlar"][ad] = [
            {"id": i.id, "varliklar": list(i.assets.keys()),
             "tarih": str(getattr(i, "datetime", ""))[:19]} for i in items
        ]

    wc = None
    for ad in ("esa-worldcover",):
        items = list(client.search(collections=[ad], bbox=BBOX, max_items=1).items())
        if items:
            href = items[0].assets["map"].href
            try:
                with rasterio.open(href) as ds:
                    for e in dogrulama_etiketleri()[:18]:
                        r, c = ds.index(float(e["lon"]), float(e["lat"]))
                        v = ds.read(1, window=((r, r + 1), (c, c + 1)))[0, 0]
                        sonuc["worldcover_ornekleri"].append({
                            "id": e["id"], "sinif": int(v),
                        })
                wc = True
            except Exception as exc:
                sonuc["worldcover_hata"] = str(exc)[:200]
    sonuc["worldcover_okundu"] = bool(wc)

    (PROCESSED_DIR / "exposure_stac.json").write_text(
        json.dumps(sonuc, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    manifest = RAW_DIR / "enrichment_manifest.json"
    kayitlar = json.loads(manifest.read_text(encoding="utf-8")) if manifest.exists() else []
    kayitlar.append({
        "id": "PC_EXPOSURE", "url": STAC,
        "erisim_tarihi": sonuc["erisim_tarihi"],
        "lisans": "ESA WorldCover CC BY 4.0 / MS Buildings ODbL",
        "sha256": None, "yetkinlik": "Otorite",
        "not": f"STAC item'leri: {list(sonuc['koleksiyonlar'].keys())}; COG okuma: {bool(wc)}",
    })
    manifest.write_text(json.dumps(kayitlar, ensure_ascii=False, indent=2), encoding="utf-8")
    return sonuc


if __name__ == "__main__":
    r = calistir()
    print("STAC okundu", r["worldcover_okundu"], len(r["worldcover_ornekleri"]))
