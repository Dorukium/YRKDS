"""Ağırlık duyarlılığı: deterministik ±%10 pertürbasyon, 200 koşu.

Vektörleştirildi: Python döngüsü yerine tek numpy matris çarpımı (yük testi
p95 hedefi için). Tohum sabit (42) -> aynı girdi için aynı aralık.
"""
from __future__ import annotations

import numpy as np

from app.config import AGIRLIKLAR

N_KOSU = 200
TOHUM = 42
_KODLAR = list(AGIRLIKLAR)
_TEMEL = np.array([AGIRLIKLAR[k] for k in _KODLAR], dtype=np.float64)
_RNG = np.random.default_rng(TOHUM)
_PERTURBASYON = 1.0 + _RNG.uniform(-0.10, 0.10, size=(N_KOSU, len(_KODLAR)))


def guven_ifadesi(guven: float) -> str:
    if guven >= 0.7:
        return "yüksek güven"
    if guven >= 0.4:
        return "orta güven"
    return "düşük güven — karar için yetersiz"


def skor_araligi(alt: dict[str, float | None], n: int = N_KOSU) -> dict[str, object]:
    degerler = np.array([alt.get(k) if alt.get(k) is not None else np.nan for k in _KODLAR])
    gecerli = np.isfinite(degerler)
    if not gecerli.any():
        return {"p5": None, "p95": None, "n": 0}
    agirliklar = _PERTURBASYON[:n] * _TEMEL
    pay = (agirliklar[:, gecerli] * degerler[gecerli]).sum(axis=1)
    payda = agirliklar[:, gecerli].sum(axis=1)
    skorlar = 100.0 * pay / payda
    return {
        "p5": round(float(np.percentile(skorlar, 5)), 1),
        "p95": round(float(np.percentile(skorlar, 95)), 1),
        "n": int(n),
    }
