"""Spesifikasyon 2.3 ust kurallari.

Onemli: bir yasal katmanin verisi yoksa VETO yok demek degildir. Bu durumda
uyari uretilir ve guven skoru dusurulur; sessizce False donulmez.
"""
from __future__ import annotations

from app.models.schemas import SkorInput

VETO_KURALLARI: tuple[tuple[str, str], ...] = (
    ("fay_sakinim_bandi", "Fay sakınım bandı"),
    ("afete_maruz_bolge", "Afete maruz bölge (ör. Hisarçandır 1965)"),
    ("taskin_yapi_yasagi", "Taşkın yapı yasağı alanı"),
    ("falez_cekme_mesafesi", "Falez çekme mesafesi"),
)


def veto_kontrol(girdi: SkorInput) -> tuple[bool, str | None, list[str]]:
    nedenler: list[str] = []
    uyari: list[str] = []
    for alan, etiket in VETO_KURALLARI:
        deger = getattr(girdi, alan)
        if deger is True:
            nedenler.append(etiket)
        elif deger is None:
            uyari.append(f"{etiket} katmanı doğrulanamadı; yasal kısıt dışlanamaz.")
    if nedenler:
        return True, "Uygun Değil (Yasal Kısıt): " + "; ".join(nedenler), uyari
    return False, None, uyari
