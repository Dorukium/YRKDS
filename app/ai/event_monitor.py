"""Deprem/taşkın olay izleme iskeleti.

Canlı AFAD API'si erişilemediğinde veri uydurulmaz; mevcut kayıtlar
korunur ve durum 'kaynak erişilemedi' olarak raporlanır.
"""
from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from typing import Any

import requests

AFAD_API = "https://deprem.afad.gov.tr/apiv2/event/filter"
UA = {"User-Agent": "YRKDS/0.1 (TUBITAK 2204-A)"}


def son_depremler(saat: int = 24) -> dict[str, Any]:
    bitis = datetime.now(UTC)
    baslangic = bitis - timedelta(hours=saat)
    try:
        r = requests.get(
            AFAD_API,
            params={
                "start": baslangic.strftime("%Y-%m-%d %H:%M:%S"),
                "end": bitis.strftime("%Y-%m-%d %H:%M:%S"),
                "orderby": "date",
            },
            headers=UA,
            timeout=20,
        )
        r.raise_for_status()
        olaylar = r.json()
        return {"durum": "ok", "sayi": len(olaylar), "olaylar": olaylar[:50]}
    except Exception as exc:
        return {"durum": "kaynak_erisiilemedi", "hata": str(exc), "sayi": 0, "olaylar": []}


def durum_raporu() -> str:
    return json.dumps(son_depremler(), ensure_ascii=False, default=str)


if __name__ == "__main__":
    print(durum_raporu())
