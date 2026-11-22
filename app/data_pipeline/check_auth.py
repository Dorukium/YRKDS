"""V5 FAZ 1 — `make check-auth`: tüm veri kimliklerinin tek ekranda durumu.

Hiçbir kimlik uydurulmaz; eksik olan "yok" olarak görünür ve ilgili görevin
merdiveninin hangi basamağına geçileceği belirtilir (U9/U12).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def check() -> dict[str, Any]:
    dotenv = Path(".env")
    icerik = dotenv.read_text(encoding="utf-8") if dotenv.exists() else ""

    def anahtar_var(ad: str) -> bool:
        return any(
            satir.startswith(f"{ad}=") and len(satir.split("=", 1)[1].strip()) > 0
            for satir in icerik.splitlines()
        )

    nasa = anahtar_var("EARTHDATA_USERNAME") and anahtar_var("EARTHDATA_PASSWORD")
    gee = (Path.home() / ".config" / "earthengine" / "credentials").is_file()
    zenodo = anahtar_var("ZENODO_TOKEN")

    return {
        "nasa_earthdata": {
            "durum": "var" if nasa else "yok",
            "kullanılabilir_görev": "A1 InSAR (tamamlandı) / A2 L2 Sentinel-1",
        },
        "google_earth_engine": {
            "durum": "var" if gee else "yok",
            "komut": "uv run earthengine authenticate",
            "kullanılabilir_görev": "A2 L1 GFD MODIS / L2 Sentinel-1 GRD",
        },
        "zenodo": {
            "durum": "var" if zenodo else "yok",
            "komut": "https://zenodo.org/account/settings/applications/tokens/new/",
            "kullanılabilir_görev": "DOI yayını (make publish)",
        },
        "tdth": {
            "durum": "deaktif",
            "karar": "ADR-0004 kalıcı açık — yeni deneme yok, GEM+USGS Araştırma rozeti",
        },
        "genel": "hazır" if (nasa and gee and zenodo) else "eksik kimlik var",
        "not": "HAZIR değilse ilgili görevin merdivenini bir sonraki basamağa kaydır.",
    }


if __name__ == "__main__":
    print(json.dumps(check(), ensure_ascii=False, indent=2))
