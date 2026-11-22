"""Veri tamlığı ve güven skoru.

Spesifikasyon 2.3: tamlık %40 altindaysa sayisal skor gosterilmez.
Guven skoru, eksik yasal VETO katmanlarinda ek olarak dusurulur; boylece
"kesin gibi gorunen ama dogrulanmamis" ciktilarin onune gecilir.
"""
from __future__ import annotations

from app.config import KARARSIZ_ESIK, KATMAN_AGIRLIKLARI
from app.models.schemas import SkorInput

# Katman -> girdi alanlari. Tum alanlar None ise katman yok sayilir.
KATMAN_ALANLARI: dict[str, tuple[str, ...]] = {
    "dem": ("egim", "twi"),
    "soil": ("kum_orani", "organik"),
    "jeoloji": ("jeoloji", "karst"),
    "mikrobölge_vs30": ("vs30", "zemin_sinifi"),
    "zemin_hareketi": ("pga_g",),
    "fay": ("fay_mesafe_km",),
    "insar": ("insar_hiz",),
    "taskin": ("taskin_100y", "taskin_500y", "akarsu_mesafe_m", "gecmis_taskin_sayisi"),
    "sondaj": ("yass_m",),
    "bina": ("yuksek_bina_yuku",),
}
VETO_ALANLARI = (
    "fay_sakinim_bandi",
    "afete_maruz_bolge",
    "taskin_yapi_yasagi",
    "falez_cekme_mesafesi",
)


def katman_durumu(girdi: SkorInput) -> dict[str, str]:
    durum: dict[str, str] = {}
    for katman, alanlar in KATMAN_ALANLARI.items():
        if any(getattr(girdi, a) is not None for a in alanlar):
            durum[katman] = "var"
        else:
            durum[katman] = "yok"
    for alan in VETO_ALANLARI:
        if getattr(girdi, alan) is None:
            durum[f"veto:{alan}"] = "doğrulanamadı"
        else:
            durum[f"veto:{alan}"] = "var"
    return durum


def veri_tamligi(durum: dict[str, str]) -> float:
    toplam = sum(KATMAN_AGIRLIKLARI.values())
    mevcut = sum(w for k, w in KATMAN_AGIRLIKLARI.items() if durum.get(k) == "var")
    return round(mevcut / toplam, 3) if toplam else 0.0


def guven_skoru(tamlik: float, durum: dict[str, str]) -> float:
    guven = tamlik
    dogrulanmayan = sum(1 for k, v in durum.items() if k.startswith("veto:") and v != "var")
    if dogrulanmayan:
        guven *= 0.85
    if durum.get("sondaj") != "var":
        guven *= 0.90
    # A1: radar gölgesi boşlukları en yakın komşu ile doldurulduysa proxy cezası
    if durum.get("insar_proxy") == "var":
        guven *= 0.90
    return round(min(1.0, max(0.0, guven)), 3)


def kararsiz_mi(tamlik: float) -> bool:
    return tamlik < KARARSIZ_ESIK


def tamlık_aciklama(durum: dict[str, str], tamlik: float) -> str:
    var = [k for k, v in durum.items() if v == "var" and not k.startswith("veto:")]
    yok = [k for k, v in durum.items() if v == "yok"]
    return (
        f"Tamlık %{tamlik * 100:.0f}. Mevcut: {', '.join(var) or 'yok'}. "
        f"Eksik: {', '.join(yok) or 'yok'}."
    )
