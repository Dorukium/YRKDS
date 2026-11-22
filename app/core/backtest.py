"""2009 seli geriye dönük doğrulama.

ML EĞİTİMİ YOK. Deterministik F (taşkın) alt puanı, 2009 öncesi verilerle
(DEM/TWI, akarsu mesafesi, kayıtlı taşkın sayısı) hesaplanır ve ANT-2009
etiketleriyle karşılaştırılır. Doğrulama mekansal blok tabanlıdır:
her ilçe ayrı bir bloktur (leave-one-district-out), rastgele CV kullanılmaz.
"""
from __future__ import annotations

from math import sqrt
from typing import Any

import pandas as pd

from app.config import PROCESSED_DIR
from app.core.scoring import f_puani
from app.data_pipeline.seed import dogrulama_etiketleri
from app.models.schemas import SkorInput

ESIK = 0.7  # yuksek risk siniri (spesifikasyon: F >= 0.7 -> 0.7 puan)


def _wilson(k: int, n: int, z: float = 1.96) -> list[float]:
    """Oran için Wilson 95% güven aralığı (rastgelelik içermez, deterministik)."""
    if n == 0:
        return [0.0, 0.0]
    p = k / n
    bolen = 1 + z**2 / n
    merkez = (p + z**2 / (2 * n)) / bolen
    yari = z * sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / bolen
    return [round(max(0.0, merkez - yari), 3), round(min(1.0, merkez + yari), 3)]


def _gecerli(deger: Any) -> float | None:
    return float(deger) if deger is not None and pd.notna(deger) else None


def _yuksek_risk(satir: pd.Series) -> bool:
    girdi = SkorInput(
        twi=_gecerli(satir["dem_twi"]),
        hand_m=_gecerli(satir["dem_hand"]),
        akarsu_mesafe_m=_gecerli(satir["akarsu_mesafe_m"]),
        gecmis_taskin_sayisi=int(satir["gecmis_taskin_sayisi"])
        if pd.notna(satir["gecmis_taskin_sayisi"]) else None,
        taskin_100y=None,  # SYGM haritasi yok -> bilinmiyor, 0 varsayilmaz
        taskin_500y=None,
    )
    p = f_puani(girdi)
    return p is not None and p >= ESIK


def _hucreye_en_yakin(grid: pd.DataFrame, lon: float, lat: float) -> pd.Series:
    # Donusum: 1 derece enlem ~111.32 km; 1 derece lon ~111.32*cos(lat) km
    k = 111_320.0 * __import__("math").cos(__import__("math").radians(lat))
    d = ((grid["lon"] - lon) * k) ** 2 + ((grid["lat"] - lat) * 111_320.0) ** 2
    return grid.loc[d.idxmin()]


def hesapla() -> dict[str, Any]:
    grid_path = PROCESSED_DIR / "grid_25m.parquet"
    if not grid_path.exists():
        raise FileNotFoundError("grid_25m.parquet yok; once veri pipeline'ini calistir")
    grid = pd.read_parquet(grid_path, columns=[
        "lon", "lat", "ilce", "dem_twi", "dem_hand", "akarsu_mesafe_m", "gecmis_taskin_sayisi"
    ])

    etiketler = dogrulama_etiketleri()
    # Pozitif: su baskini derinligi >= 0.5 m (kaynak: ANT-2009 etiketi)
    pozitifler = [e for e in etiketler if float(e["su_derinligi_m"]) >= 0.5]
    negatifler = [e for e in etiketler if float(e["su_derinligi_m"]) < 0.5]

    # Negatif kontrol: yuksek ve akarsudan uzak hucreler (DEM'den turetilmis).
    # Bu bir ML egitimi degil, deterministik kontrol orneklemidir.
    guvenli = grid[(grid["dem_twi"] < 4) & (grid["akarsu_mesafe_m"] > 1500)]
    adim = max(1, len(guvenli) // 200)
    kontrol_hucreleri = guvenli.iloc[::adim].head(100)

    tp = fp = fn = tn = 0
    etiket_fp = 0  # yalnizca gerçek ANT etiketlerinden gelen yanlis pozitif
    blok_sonuclari: dict[str, dict[str, float]] = {}
    for ilce in sorted({e["ilce"] for e in etiketler}):
        b_tp = b_fp = b_fn = b_tn = 0
        for e in pozitifler:
            if e["ilce"] != ilce:
                continue
            hucre = _hucreye_en_yakin(grid, float(e["lon"]), float(e["lat"]))
            tahmin = _yuksek_risk(hucre)
            if tahmin:
                tp += 1; b_tp += 1
            else:
                fn += 1; b_fn += 1
        for e in negatifler:
            if e["ilce"] != ilce:
                continue
            hucre = _hucreye_en_yakin(grid, float(e["lon"]), float(e["lat"]))
            tahmin = _yuksek_risk(hucre)
            if tahmin:
                fp += 1; etiket_fp += 1; b_fp += 1
            else:
                tn += 1; b_tn += 1
        recall = b_tp / (b_tp + b_fn) if (b_tp + b_fn) else 0.0
        blok_sonuclari[ilce] = {"recall": round(recall, 3), "tp": b_tp, "fn": b_fn}

    for _, satir in kontrol_hucreleri.iterrows():
        if _yuksek_risk(satir):
            fp += 1
        else:
            tn += 1

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return {
        "metrikler": {
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "f1": round(f1, 3),
            "tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "esik": ESIK,
            "recall_ci95": _wilson(tp, tp + fn),
            "precision_sadece_etiket": round(
                tp / (tp + etiket_fp), 3
            ) if (tp + etiket_fp) else 0.0,
            "dogrulama": "Mekansal blok doğrulama — ilçe bazlı bırakmalı (leave-one-district-out)",
            "not": "Pozitif etiket: su_derinligi_m >= 0.5 ANT-2009 (17 nokta). "
                   "SYGM/InSAR yok; F, TWI + gerçek HAND + akarsu mesafesi + "
                   "gecmis olay ile hesaplandi. Eşikler aynı etiketler üzerinde "
                   "kalibre edildiği için bu BAĞIMSIZ bir doğrulama DEĞİLDİR.",
        },
        "kalibrasyon": {
            "bagimsiz_mi": False,
            "esikler": {"F_yuksek_risk": ESIK, "TWI_guclu": 8.0, "TWI_zayif": 6.0,
                        "HAND_m": 5.0, "gecmis_taskin": 2},
            "aciklama": "Eşikler ANT-2009 etiketlerinin gözlenen örüntüsüne göre "
                        "kalibre edildi. Bağımsız bir validasyon için eşiklerin farklı "
                        "bir olay/şehirde önceden sabitlenmesi gerekir.",
        },
        "yontem": "Mekansal blok doğrulama (leave-one-district-out), rastgele CV yok",
        "kaynak": "ANT-2009 dogrulama etiketleri (18 nokta) + DEM/TWI/HAND + OSM akarsu",
        "bloklar": blok_sonuclari,
        "uyarilar": [
            "Kontrol örneklerinin (BLN) koordinatı veri setinde yok; "
            "negatif kontrol DEM'den türetilen yüksek ve kuru hücrelerdir.",
            "17 pozitif nokta için Wilson %95 güven aralığı geniştir; "
            "recall tek bir sayı olarak yorumlanmamalıdır.",
            "Bu bir doğrulama testidir; model eğitimi yapılmaz.",
        ],
    }
