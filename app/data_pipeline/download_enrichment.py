"""Ek açık veri entegrasyonları (ek plan Bölüm 6).

Her kaynak için URL + erişim tarihi + SHA256 manifest'e yazılır. Çapraz
kontroller birincil kaynağın yerine geçmez; sapma >%20 ise ADR (K2/K5).
"""
from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Any

import requests

from app.config import GRID_BBOX, PROCESSED_DIR, RAW_DIR

UA = {"User-Agent": "YRKDS/0.2 (TUBITAK 2204-A; open-data research)"}
ERISIM = datetime.now(UTC).date().isoformat()
KAYITLAR: list[dict[str, Any]] = []


def _kayit(veri: bytes | None, ad: str, url: str, lisans: str, not_: str) -> dict[str, Any]:
    k: dict[str, Any] = {
        "id": ad,
        "url": url,
        "erisim_tarihi": ERISIM,
        "lisans": lisans,
        "sha256": hashlib.sha256(veri).hexdigest() if veri else None,
        "not": not_,
    }
    KAYITLAR.append(k)
    return k


def koeri_katalogu() -> dict[str, Any]:
    url = "http://www.koeri.boun.edu.tr/scripts/lst6.asp"
    r = requests.get(url, headers=UA, timeout=30)
    r.raise_for_status()
    veri = r.content
    (RAW_DIR / "koeri_katalog.txt").write_bytes(veri)
    metin = veri.decode("cp1254", errors="replace")
    satirlar = [s for s in metin.splitlines() if len(s.split()) >= 7][:200]
    (PROCESSED_DIR / "koeri_katalog.json").write_text(
        json.dumps({"kayit_sayisi": len(satirlar), "ornekler": satirlar[:20]}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return _kayit(veri, "KOERI_KATALOG", url, "kamuya açık metin",
                  f"{len(satirlar)} olay satırı; AFAD kataloğu ile çapraz kontrol için kullanılır.")


def pc_stac(ad: str, collection: str, lisans: str) -> dict[str, Any]:
    temel = "https://planetarycomputer.microsoft.com/api/stac/v1"
    r = requests.get(f"{temel}/collections/{collection}", headers=UA, timeout=30)
    r.raise_for_status()
    meta = r.json()
    min_lon, min_lat, max_lon, max_lat = GRID_BBOX
    params: dict[str, str | int] = {
        "collections": collection,
        "bbox": f"{min_lon},{min_lat},{max_lon},{max_lat}",
        "limit": 5,
    }
    arama = requests.get(
        f"{temel}/search",
        params=params,
        headers=UA, timeout=30,
    )
    sonuc: dict[str, Any] = {"collection": collection, "title": meta.get("title"),
                             "license": meta.get("license"), "item_sayisi": 0, "itemler": []}
    if arama.ok:
        j = arama.json()
        sonuc["item_sayisi"] = len(j.get("features", []))
        sonuc["itemler"] = [{"id": f.get("id"), " tarih": (f.get("properties") or {}).get("datetime")}
                            for f in j.get("features", [])]
    (PROCESSED_DIR / f"{ad}.json").write_text(json.dumps(sonuc, ensure_ascii=False, indent=2), encoding="utf-8")
    return _kayit(json.dumps(meta).encode(), ad, f"{temel}/collections/{collection}", lisans,
                  f"{sonuc['item_sayisi']} STAC item'i çalışma alanında; otorite katman yerine geçmez.")


def usgs_vs30() -> dict[str, Any]:
    url = "https://earthquake.usgs.gov/arcgis/rest/services/eq/vs30_mosaic/MapServer"
    r = requests.get(url, params={"f": "json"}, headers=UA, timeout=30)
    r.raise_for_status()
    meta = r.json()
    (PROCESSED_DIR / "usgs_vs30_servis.json").write_text(
        json.dumps({"servis": meta.get("serviceDescription"), "katmanlar": meta.get("layers")}, indent=2),
        encoding="utf-8",
    )
    return _kayit(json.dumps(meta).encode(), "USGS_VS30", url + "?f=json",
                  "USGS public domain",
                  "Servis metadatası indirildi; nokta sorgu API'si bu ortamda 400 döndü "
                  "(ADR-0005). Vs30 vekili olarak kullanılmaz.")


def calistir() -> list[dict[str, Any]]:
    KAYITLAR.clear()
    for fn in (koeri_katalogu, usgs_vs30,
               lambda: pc_stac("esa_worldcover", "esa-worldcover", "CC-BY-4.0"),
               lambda: pc_stac("ms_buildings", "ms-buildings", "ODbL-1.0")):
        try:
            fn()
        except Exception as exc:
            _kayit(None, fn.__name__, "?", "?", f"Erişilemedi: {exc}")
    (RAW_DIR / "enrichment_manifest.json").write_text(
        json.dumps(KAYITLAR, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return KAYITLAR


if __name__ == "__main__":
    for k in calistir():
        print(k["id"], k["sha256"] is not None)
