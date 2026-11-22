"""COMET-LiCSAR InSAR deformasyon hizi.

Kimlik bilgisi/frame isleme zinciri (LiCSBAS) bu ortamda yoksa insar_hiz NULL
birakilir. Mikrobolegeleme/sondaj verisinden sahte deformasyon hizi uretilmez.
"""
from __future__ import annotations

import json
import os

from app.config import PROCESSED_DIR, RAW_DIR


def indir() -> dict[str, object]:
    durum: dict[str, object] = {
        "kaynak": "COMET LiCSAR portal + LiCSBAS",
        "insar_velocity": "yok",
        "not": "COMET kimlik bilgisi ve LiCSBAS isleme zinciri olmadigi icin "
        "InSAR hizi uretilmedi. S alt puani NULL kalir, guven skoru dusurulur.",
    }
    if os.getenv("COMET_USER") and os.getenv("COMET_PASSWORD"):
        durum["not"] = (
            "COMET kimlik bilgisi mevcut fakat frame secimi/interferogram "
            "isleme otomatiklestirilmedi; manuel LiCSBAS kosusu gerekir."
        )
    (PROCESSED_DIR / "insar_durum.json").write_text(json.dumps(durum, indent=2), encoding="utf-8")
    (RAW_DIR / "insar_kaynak.json").write_text(json.dumps(durum, indent=2), encoding="utf-8")
    return durum


if __name__ == "__main__":
    indir()
