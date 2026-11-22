"""V5 A2 — GEE Global Flood Database (MODIS) sorgusu ve dürüst etiket raporu.

GEE kimliği ~/.config/earthengine/credentials, proje .env GEE_PROJECT.
GFD v1'de Antalya AOI'sini kesen olayları bulur; 2003-12-10 ve 2008-01-27
doğrulama olaylarıyla tarih eşleşmesi arar. Eşleşme yoksa etiket ÜRETMEZ
(K3); sonucu manifest + GeoJSON olarak yazar.
"""
from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

from dotenv import load_dotenv

from app.config import RAW_DIR, ROOT

load_dotenv(ROOT / ".env")
COLLECTION = "GLOBAL_FLOOD_DB/MODIS_EVENTS/V1"
AOI = (30.58, 36.82, 30.86, 37.00)  # çalışma ızgarası (GRID_BBOX)
DOGRULAMA = ("2003-12-10", "2008-01-27")
LABELS = RAW_DIR / "labels"


def initializeee() -> Any:
    """Kimliği ve projeyi doğrulayıp ee modülünü döndürür."""
    from app.data_pipeline.gee_auth import initialize

    return initialize()


def _tarih(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000, tz=UTC).date().isoformat()


def aoi_olaylari(ee: Any) -> list[dict[str, Any]]:
    """AOI'yi footprint ile kesen GFD olaylarını özetler (polygon dışa aktarmaz)."""
    gfd = ee.FeatureCollection(COLLECTION)
    box = ee.Geometry.Rectangle(list(AOI))
    secilen = gfd.filterBounds(box).getInfo()["features"]
    olaylar = []
    for f in secilen:
        p = f["properties"]
        bas, bit = _tarih(int(p["system:time_start"])), _tarih(int(p["system:time_end"]))
        olaylar.append({
            "id": str(p.get("id")),
            "baslangic": bas,
            "bitis": bit,
            "ulke": p.get("dfo_country"),
            "asset_boyutu": p.get("system:asset_size"),
            "footprint": p.get("system:footprint"),
        })
    return olaylar


def dogrulama_etiketleri(olaylar: list[dict[str, Any]]) -> dict[str, Any]:
    """2003/2008 olayları için tarih eşleşen GFD etiketlerini üretir veya yok der."""
    eslesen = [o for o in olaylar if any(d >= o["baslangic"] and d <= o["bitis"]
                                         for d in DOGRULAMA)]
    return {
        "kaynak": COLLECTION,
        "aoi": list(AOI),
        "aoi_olay_sayisi": len(olaylar),
        "hedef_tarihler": list(DOGRULAMA),
        "eslesen_olay_sayisi": len(eslesen),
        "eslesen": eslesen,
        "durum": "etiket_var" if eslesen else "etiket_yok",
        "not": ("Eşleşen olay yok; uydurma etiket üretilmedi (K3)."
                if not eslesen else "Gerçek GFD poligonu etiket olarak kullanılabilir."),
    }


def calistir() -> dict[str, Any]:
    ee = initializeee()
    olaylar = aoi_olaylari(ee)
    sonuc = dogrulama_etiketleri(olaylar)
    LABELS.mkdir(parents=True, exist_ok=True)
    (LABELS / "gfd_antalya_events.json").write_text(
        json.dumps({"olaylar": olaylar}, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (LABELS / "gfd_validation_labels.json").write_text(
        json.dumps(sonuc, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return sonuc


if __name__ == "__main__":
    print(json.dumps(calistir(), ensure_ascii=False, indent=2))
