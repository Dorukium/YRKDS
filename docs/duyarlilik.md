# Küresel Duyarlılık Analizi (C1)

Yöntem: SALib Morris, 2000 trajektörü, 4 seviye, ±%20 ağırlık perturbasyonu.
Temsili vektör: ZB 0.7, L 0.7, S NULL, H 0.0, F 0.85 (gerçek API sorgusundan).

| Bileşen | μ* | σ | Pay |
|---|---|---|---|
| ZB | 1.384 | 0.260 | 12.2% |
| L | 1.379 | 0.256 | 12.2% |
| S | 0.000 | 0.000 | 0.0% |
| H | 5.645 | 0.311 | 49.9% |
| F | 2.900 | 0.272 | 25.6% |

F ağırlığını %10 artırmak skoru 0.70 puan değiştirir (pozitif, anlamlı).

<svg xmlns="http://www.w3.org/2000/svg" width="420" height="150" role="img" aria-label="Duyarlılık çubukları">
<rect x="10" y="5" width="48.8" height="18" fill="#0F766E"/><text x="64.8" y="19" font-size="11">ZB %12.2</text>
<rect x="10" y="33" width="48.8" height="18" fill="#0F766E"/><text x="64.8" y="47" font-size="11">L %12.2</text>
<rect x="10" y="61" width="0.0" height="18" fill="#0F766E"/><text x="16.0" y="75" font-size="11">S %0.0</text>
<rect x="10" y="89" width="199.6" height="18" fill="#0F766E"/><text x="215.6" y="103" font-size="11">H %49.9</text>
<rect x="10" y="117" width="102.4" height="18" fill="#0F766E"/><text x="118.4" y="131" font-size="11">F %25.6</text>
</svg>

**Yorum:** S bileşeni bu örnekte NULL olduğundan skora etkisi yoktur. Bu,
modelin bir eksikliği değil, veri eksikliğinin dürüst yansımasıdır (K3).
