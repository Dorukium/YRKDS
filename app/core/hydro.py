"""Hidrolojik türevler — deterministik, test edilebilir, kaynaklı.

Uygulanan yöntemler:
  1. Priority-flood depresyon doldurma (Barnes, Lehman & Mulla, 2014) —
     CAP=None, tüm drenaj havzaları deniz seviyesine bağlanır.
  2. D8 akış yönü ve akış birikimi (O'Callaghan & Mark, 1984).
  3. Topografik Islaklık İndeksi TWI = ln(a / tan β) (Beven & Kirkby, 1979).
  4. HAND — her hücrenin akış yoluyla ulaştığı en yakın kanal hücresinin
     yüksekliğine göre yüksekliği (Rennó et al., 2008).

Önceki sürümde HAND "yerel 11x11 minimum yükseklik farkı"ydı; bu gerçek
HAND değildir ve bu modülle değiştirildi. Kanal eşiği (flow accumulation)
açıkça parametredir ve dokümante edilir.
"""
from __future__ import annotations

from heapq import heappop, heappush

import numpy as np

_KOMSULAR: tuple[tuple[int, int, float], ...] = (
    (-1, 0, 1.0), (1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0),
    (-1, -1, 2**0.5), (-1, 1, 2**0.5), (1, -1, 2**0.5), (1, 1, 2**0.5),
)


def havza_doldur(dem: np.ndarray) -> np.ndarray:
    """Priority-flood ile tüm kapalı çukurları taşırarak doldur.

    Dış sınır hücreleri tohumdur. Her hücre, kendisine ulaşan en düşük
    taşma seviyesine yükseltilir; böylece her noktanın okyanusa giden bir
    iniş yolu kalır.
    """
    h, w = dem.shape
    z = np.asarray(dem, dtype=np.float64)
    if not np.isfinite(z).all():
        raise ValueError("DEM NaN/inf içeriyor; hydro çağrılmadan önce doldurulmalı")
    vis = np.zeros((h, w), dtype=bool)
    filled = z.copy()
    heap: list[tuple[float, int, int]] = []
    for x in range(w):
        for y in (0, h - 1):
            heappush(heap, (float(z[y, x]), y, x))
    for y in range(1, h - 1):
        for x in (0, w - 1):
            heappush(heap, (float(z[y, x]), y, x))

    while heap:
        seviye, y, x = heappop(heap)
        if vis[y, x]:
            continue
        vis[y, x] = True
        filled[y, x] = seviye
        for dy, dx, _ in _KOMSULAR:
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and not vis[ny, nx]:
                heappush(heap, (max(seviye, float(z[ny, nx])), ny, nx))
    return filled


def d8_akis_ve_kanal(filled: np.ndarray, hucre_x_m: float, hucre_y_m: float,
                     kanal_esigi: int = 100) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """D8 akış birikimi,下游 indeks ve kanal maskesi.

    kanal_esigi: bir hücre kanal sayılmak için gereken yukarı akış hücre
    sayısı. 25 m grid'de 100 hücre ≈ 0.0625 km² drenaj alanıdır.
    """
    h, w = filled.shape
    duz = np.asarray(filled, dtype=np.float64).ravel()
    n = duz.size
    sirali = np.argsort(-duz, kind="stable")  # yuksekten asagiya
    akis = np.ones(n, dtype=np.float32)
    asagi = np.full(n, -1, dtype=np.int32)
    mesafeler = (
        (hucre_y_m, hucre_y_m, hucre_y_m * 2**0.5, hucre_y_m * 2**0.5),
        (hucre_x_m, hucre_x_m, hucre_x_m * 2**0.5, hucre_x_m * 2**0.5),
    )
    dy_list = (-1, 1, 0, 0, -1, -1, 1, 1)
    dx_list = (0, 0, -1, 1, -1, 1, -1, 1)
    dist_list = (
        mesafeler[0][0], mesafeler[0][1], mesafeler[1][0], mesafeler[1][1],
        mesafeler[0][2], mesafeler[0][3], mesafeler[1][2], mesafeler[1][3],
    )
    for idx in sirali:
        i = int(idx)
        y, x = divmod(i, w)
        en_iyi = -1
        en_dik = 0.0
        for dy, dx, mesafe in zip(dy_list, dx_list, dist_list):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w:
                j = ny * w + nx
                dusus = duz[i] - duz[j]
                if dusus > 0:
                    egim = dusus / mesafe
                    if egim > en_dik:
                        en_dik = egim
                        en_iyi = j
        if en_iyi >= 0:
            asagi[i] = en_iyi
            akis[en_iyi] += akis[i]
    kanal = (akis >= kanal_esigi).reshape(h, w)
    return akis.reshape(h, w), asagi, kanal


def turevler(dem: np.ndarray, hucre_x_m: float, hucre_y_m: float,
             kanal_esigi: int = 100) -> dict[str, np.ndarray]:
    """Tek çağrıda doldurulmuş DEM, eğim, TWI ve HAND üretir."""
    doldurulmus = havza_doldur(dem)
    akis, asagi, kanal = d8_akis_ve_kanal(doldurulmus, hucre_x_m, hucre_y_m, kanal_esigi)
    dy, dx = np.gradient(doldurulmus, hucre_y_m, hucre_x_m)
    beta = np.arctan(np.hypot(dy, dx))
    tan_beta = np.maximum(np.tan(beta).ravel(), 1e-4)
    # a = biriken hucre sayisi * hucre alani / hucre genisligi  [m]
    alan = akis.ravel() * (hucre_x_m * hucre_y_m) / hucre_x_m
    twi = np.log(np.maximum(alan, 1.0) / tan_beta)
    twi = np.clip(np.nan_to_num(twi, nan=0.0, posinf=25.0), 0, 25).reshape(dem.shape)

    hand = np.zeros(dem.size, dtype=np.float32)
    sirali = np.argsort(-doldurulmus.ravel(), kind="stable")
    for idx in sirali[::-1]:  # asagi->yukari: asagi akis once hesaplandi
        i = int(idx)
        j = int(asagi[i])
        if kanal.ravel()[i] or j < 0:
            hand[i] = 0.0
        else:
            hand[i] = hand[j] + (doldurulmus.ravel()[i] - doldurulmus.ravel()[j])
    return {
        "doldurulmus": doldurulmus,
        "egim": np.degrees(beta).astype(np.float32),
        "twi": twi.astype(np.float32),
        "hand": hand.reshape(dem.shape),
        "akis": akis,
        "kanal": kanal,
    }
