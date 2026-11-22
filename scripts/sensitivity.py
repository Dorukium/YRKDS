"""C1 — Morris küresel duyarlılık analizi (SALib).

Temsili alt puan vektörü üretim API'sinden alınan gerçek bir sorgudur;
S bileşeni NULL olduğu için ağırlığı perturbasyona rağmen skora etki etmez.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from SALib.analyze import morris
from SALib.sample import morris as morris_sample

from app.config import AGIRLIKLAR, ROOT

ALT = {"ZB": 0.7, "L": 0.7, "S": None, "H": 0.0, "F": 0.85}
KODLAR = list(AGIRLIKLAR)


def skor(agirliklar: np.ndarray) -> float:
    toplam = 0.0
    payda = 0.0
    for kod, w in zip(KODLAR, agirliklar):
        if ALT[kod] is not None:
            toplam += w * ALT[kod]
            payda += w
    return 100.0 * toplam / payda if payda else 0.0


def calistir() -> dict[str, float]:
    problem = {
        "num_vars": 5,
        "names": KODLAR,
        "bounds": [[0.8, 1.2]] * 5,
    }
    X = morris_sample.sample(problem, 2000, num_levels=4, seed=42)
    Y = np.array([skor(x) for x in X])
    sonuc = morris.analyze(problem, X, Y, num_levels=4, seed=42)
    mu = [float(v) for v in sonuc["mu_star"]]
    sigma = [float(v) for v in sonuc["sigma"]]
    toplam = sum(mu) or 1.0
    oran = {k: round(100 * mu[i] / toplam, 1) for i, k in enumerate(KODLAR)}

    # DoD: F ağırlığı +%10 -> skor dağılımı anlamlı kayar
    temel = np.array([1.0] * 5)
    f_art = temel.copy(); f_art[KODLAR.index("F")] = 1.10
    kayma = skor(f_art) - skor(temel)
    assert kayma > 0.5, kayma

    satirlar = "\n".join(
        f"| {k} | {mu[i]:.3f} | {sigma[i]:.3f} | {oran[k]}% |"
        for i, k in enumerate(KODLAR)
    )
    cubuklar = "\n".join(
        f'<rect x="10" y="{i*28+5}" width="{oran[k]*4}" height="18" fill="#0F766E"/>' \
        f'<text x="{oran[k]*4+16}" y="{i*28+19}" font-size="11">{k} %{oran[k]}</text>'
        for i, k in enumerate(KODLAR)
    )
    rapor = f"""# Küresel Duyarlılık Analizi (C1)

Yöntem: SALib Morris, 2000 trajektörü, 4 seviye, ±%20 ağırlık perturbasyonu.
Temsili vektör: ZB 0.7, L 0.7, S NULL, H 0.0, F 0.85 (gerçek API sorgusundan).

| Bileşen | μ* | σ | Pay |
|---|---|---|---|
{satirlar}

F ağırlığını %10 artırmak skoru {kayma:.2f} puan değiştirir (pozitif, anlamlı).

<svg xmlns="http://www.w3.org/2000/svg" width="420" height="150" role="img" aria-label="Duyarlılık çubukları">
{cubuklar}
</svg>

**Yorum:** S bileşeni bu örnekte NULL olduğundan skora etkisi yoktur. Bu,
modelin bir eksikliği değil, veri eksikliğinin dürüst yansımasıdır (K3).
"""
    (ROOT / "docs/duyarlilik.md").write_text(rapor, encoding="utf-8")
    return oran


if __name__ == "__main__":
    print(calistir())
