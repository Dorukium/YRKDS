"""B1 — What-If önlem modülü (deterministik, Tahmin rozetli).

Katsayılar resmi birim fiyat表里 yoktur; göreli azaltma varsayımları
uzman mantığıyla sabitlenmiş ve ADR-0019'da açıklanmıştır. Kesin maliyet
iddiası yapılmaz; yalnızca ordinal seviye (düşük/orta/yüksek) üretilir.
"""
from __future__ import annotations

from typing import Any

from app.core.scoring import karar_bandi, toplam_skor

ONLEMLER: dict[str, dict[str, Any]] = {
    "kazikli_temel": {"etki": {"S": 0.50, "L": 0.60}, "maliyet": 3,
                      "ad": "Kazıklı temel"},
    "zemin_iyilestirme": {"etki": {"S": 0.60, "L": 0.50}, "maliyet": 3,
                          "ad": "Zemin iyileştirme"},
    "drenaj": {"etki": {"F": 0.60}, "maliyet": 1, "ad": "Yüzey drenajı"},
    "radye": {"etki": {"S": 0.70}, "maliyet": 2, "ad": "Radye temel"},
}
SEVIYELER = {0: "yok", 1: "düşük", 2: "orta", 3: "yüksek"}


def onem_uygula(alt: dict[str, float | None], onlemler: list[str]) -> tuple[dict[str, float | None], str]:
    yeni = dict(alt)
    puan = 0
    for ad in onlemler:
        o = ONLEMLER.get(ad)
        if not o:
            continue
        for kod, carp in o["etki"].items():
            if yeni.get(kod) is not None:
                yeni[kod] = round(min(1.0, float(yeni[kod] or 0.0) * float(carp)), 3)
        puan += int(o["maliyet"])
    seviye = SEVIYELER[min(3, puan)]
    return yeni, seviye


def sonuc_uret(alt: dict[str, float | None], onlemler: list[str]) -> dict[str, Any]:
    yeni, seviye = onem_uygula(alt, onlemler)
    skor = toplam_skor(yeni)
    bant, karar = karar_bandi(skor) if skor is not None else ("KARARSIZ", "Veri yetersiz")
    return {
        "skor": skor,
        "bant": bant,
        "karar": karar,
        "tehlike_kirilimi": yeni,
        "maliyet_seviyesi": seviye,
        "rozet": "Tahmin",
        "aciklama": (
            "Azaltma katsayıları ve maliyet seviyesi uzman varsayımıdır "
            "(ADR-0019); resmi birim fiyat veya detaylı etüt yerine geçmez."
        ),
    }
