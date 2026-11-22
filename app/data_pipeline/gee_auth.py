"""V5 — Google Earth Engine kimlik doğrulama yardımcısı.

`earthengine authenticate` komutu bir kez tarayıcıda onaylandıktan sonra
kimlik ~/.config/earthengine/credentials altına yazılır. Bu modül dosyayı
okur, ee.Initialize() yapar ve durumu dürüst raporlar (K3: uydurma yok).

Kullanıcı tarayıcı onayını vermediyse "kimlik_yok" döner; A2 merdiveni
L2/L3'e geçer veya ADR'li bırakılır (U12).
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

CRED_PATH = Path.home() / ".config" / "earthengine" / "credentials"
DOCS = "https://developers.google.com/earth-engine/guides/auth"


def kimlik_durumu() -> dict[str, Any]:
    """Kimlik dosyasının varlığını ve kaynaklarını raporlar (ağ kullanmaz)."""
    mevcut = CRED_PATH.is_file()
    return {
        "kimlik": "var" if mevcut else "yok",
        "dosya": str(CRED_PATH),
        "service_account": "var" if os.getenv("GEE_SERVICE_ACCOUNT") else "yok",
        "proje": os.getenv("GEE_PROJECT") or "yok",
        "kurulum_komutu": "uv run earthengine authenticate",
        "dokuman": DOCS,
    }


def initialize() -> Any:
    """ee.Initialize() yapar; kimlik yoksa FileNotFoundError fırlatır.

    Döndürülen `ee` modülü, A2 merdivenindeki GFD/S1 sorguları için kullanılır.
    """
    import ee  # earthengine-api

    if not CRED_PATH.is_file() and not os.getenv("GEE_SERVICE_ACCOUNT"):
        raise FileNotFoundError(f"GEE kimliği bulunamadı: {CRED_PATH}")
    if os.getenv("GEE_PROJECT"):
        ee.Initialize(project=os.environ["GEE_PROJECT"])
    else:
        ee.Initialize()
    return ee


def dogrula() -> dict[str, Any]:
    """Canlı bağlantıyı dener; başarısızlıkta nedeni dürüst döndürür."""
    durum = kimlik_durumu()
    if durum["kimlik"] == "yok" and durum["service_account"] == "yok":
        durum["baglanti"] = "kimlik_yok"
        durum["not"] = "earthengine authenticate tamamlanmadı; A2 L2/L3'e geçilir."
        return durum
    try:
        ee = initialize()
        bilgi = ee.data.getAlgorithms()  # hafif canlı çağrı
        durum["baglanti"] = "ok" if bilgi else "veri_yok"
        durum["algoritma_sayisi"] = len(bilgi) if bilgi else 0
    except Exception as exc:
        durum["baglanti"] = "hata"
        durum["hata"] = type(exc).__name__
        durum["not"] = str(exc)[:200]
    return durum


if __name__ == "__main__":
    import json

    print(json.dumps(dogrula(), ensure_ascii=False, indent=2))
