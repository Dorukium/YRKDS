"""Spesifikasyon 2.1 ve 2.4'un tek referans uygulamasi.

Kural:
  * Her alt puan 0-1 araliginda.
  * Bir alt puanin birincil girdisi yoksa None dondurulur; 0 varsayilmaz.
  * Toplam skor, mevcut alt puanlarin agirliklari yeniden normalize edilerek
    hesaplanir; hangi alt puanin eksik oldugu ciktiya acikca yazilir.
  * Bu dosya Rust motoru icin de referanstir (parity testi zorunludur).
"""
from __future__ import annotations

import re

from app.config import AGIRLIKLAR, KARAR_BANTLARI
from app.models.schemas import SkorInput

# TBDY2018 zemin sinifi -> temsil Vs30 (m/s). Araliklerin ortasi veya
# birlesik siniflar icin muhafazakar (dusuk) uc alinir. Kaynak: TBDY2018.
VS30_FROM_CLASS: dict[str, float] = {
    "ZA": 800.0,
    "ZB": 560.0,
    "ZC": 270.0,
    "ZD": 135.0,
    "ZE": 90.0,
    "ZC-ZD": 200.0,
    "ZD-ZE": 110.0,
    "ZB-ZC": 400.0,
}


def _clamp(v: float) -> float:
    return max(0.0, min(1.0, v))


def vs30_etkin(girdi: SkorInput) -> tuple[float | None, str]:
    """Vs30 dogrudan varsa kullan; yoksa siniftan turet (kaynak etiketli)."""
    if girdi.vs30 is not None:
        return girdi.vs30, "dogrudan"
    sinif = (girdi.zemin_sinifi or "").strip().upper()
    if sinif in VS30_FROM_CLASS:
        return VS30_FROM_CLASS[sinif], "turetilmis"
    # "ZD-ZE" gibi birlesik siniflarin bosluklu yazimi
    sinif_normal = re.sub(r"\s+", "-", sinif)
    if sinif_normal in VS30_FROM_CLASS:
        return VS30_FROM_CLASS[sinif_normal], "turetilmis"
    return None, "eksik"


def zb_puani(girdi: SkorInput) -> float | None:
    vs30, _ = vs30_etkin(girdi)
    if vs30 is None:
        return None
    if vs30 >= 760:
        puan = 0.0
    elif vs30 >= 360:
        puan = 0.3
    elif vs30 >= 180:
        puan = 0.7
    else:
        puan = 1.0

    if girdi.fay_mesafe_km is not None:
        d = girdi.fay_mesafe_km
        puan += 0.15 if d < 5 else 0.10 if d < 15 else 0.05 if d < 35 else 0.0
    return _clamp(puan)


def l_puani(girdi: SkorInput) -> float | None:
    yass, kum = girdi.yass_m, girdi.kum_orani
    if yass is None:
        # Kum orani yuksekse ve jeoloji lagun/aluvyon ise en dusuk goreli
        # deger 0.3 uygulanabilir; ancak YASS bilinmeden kesinlik iddia
        # edilemez -> None.
        return None
    if kum is None:
        # Sadece YASS < 10 m kurali uygulanabilir (zayif kanit).
        return 0.3 if yass < 10 else 0.0
    if yass < 3 and kum > 60:
        return 1.0
    if yass < 5 and kum > 40:
        return 0.7
    if yass < 10:
        return 0.3
    return 0.0


def s_puani(girdi: SkorInput) -> float | None:
    if girdi.insar_hiz is None:
        # InSAR yoksa taban puan yok; turba/karst eklemeleri tek basina
        # oturma hizini belirlemez. Eksik olarak isaretle.
        return None
    h = girdi.insar_hiz
    puan = 1.0 if h > 10 else 0.6 if h > 5 else 0.3 if h > 1 else 0.0
    if girdi.karst:
        puan += 0.2
    if girdi.turba or girdi.organik:
        puan += 0.2
    if girdi.yuksek_bina_yuku and girdi.karst:
        puan += 0.2
    return _clamp(puan)


def h_puani(girdi: SkorInput) -> float | None:
    if girdi.heyelan_envanter is True:
        return 1.0  # override
    if girdi.egim is None:
        return None
    egim = girdi.egim
    puan = 1.0 if egim > 30 else 0.6 if egim > 15 else 0.2 if egim > 5 else 0.0
    if girdi.kaya_dusmesi:
        puan += 0.2
    return _clamp(puan)


def f_puani(girdi: SkorInput) -> float | None:
    if girdi.taskin_100y is True:
        puan = 1.0
    elif girdi.taskin_500y is True:
        puan = 0.6
    elif (
        girdi.akarsu_mesafe_m is not None
        and girdi.akarsu_mesafe_m < 200
        and girdi.twi is not None
        and girdi.twi > 8
    ):
        puan = 0.7
    elif girdi.twi is not None:
        # Spesifikasyon 2.4 F girdileri HAND ve gecmis taskin sayisini da
        # icerir. SYGm haritasi olmadigi icin bunlarla topografik duyarlilik
        # kurali genisletildi: TWI>8 yada (TWI>6 ve HAND<5m) yada
        # (TWI>6 ve bolgede 2+ kayitli taskin). Esikler 2009 olayinin
        # gozlenen yaygin yuzey akisi ile uyumlu secildi; docs/algoritma.md
        # bu kalibrasyonu acikca belgeler.
        gecmis = girdi.gecmis_taskin_sayisi or 0
        if girdi.twi > 8 or (
            girdi.twi > 6
            and ((girdi.hand_m is not None and girdi.hand_m < 5) or gecmis >= 2)
        ):
            puan = 0.7
        elif girdi.twi > 5:
            puan = 0.4
        else:
            puan = 0.1
    else:
        return None
    if girdi.gecmis_taskin_sayisi is not None and girdi.gecmis_taskin_sayisi >= 3:
        puan += 0.15
    return _clamp(puan)


HESAPLAYICILAR = {
    "ZB": zb_puani,
    "L": l_puani,
    "S": s_puani,
    "H": h_puani,
    "F": f_puani,
}


def alt_puanlar(girdi: SkorInput) -> dict[str, float | None]:
    return {k: fn(girdi) for k, fn in HESAPLAYICILAR.items()}


def toplam_skor(alt: dict[str, float | None]) -> float | None:
    """Mevcut alt puanlarin agirliklarini yeniden normalize et."""
    mevcut = {k: v for k, v in alt.items() if v is not None}
    if not mevcut:
        return None
    toplam_agirlik = sum(AGIRLIKLAR[k] for k in mevcut)
    if toplam_agirlik <= 0:
        return None
    return round(
        100.0 * sum(AGIRLIKLAR[k] * v for k, v in mevcut.items()) / toplam_agirlik,
        1,
    )


def karar_bandi(skor: float) -> tuple[str, str]:
    for ust, bant, karar in KARAR_BANTLARI:
        if skor <= ust:
            return bant, karar
    return "Kritik", "Uygun Değil"
