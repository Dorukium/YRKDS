"""2009 seli geriye dönük doğrulama testi.

Başarı kriteri: Recall >= 0.70 (gerçek etkilenenlerin %70'ini yakalama).
Rastgele CV yok; ilçe bloklarıyla leave-one-district-out yapılır.
"""
from __future__ import annotations

import pytest

from app.core.backtest import hesapla


@pytest.fixture(scope="module")
def sonuc():
    return hesapla()


def test_recall_esigi(sonuc):
    recall = sonuc["metrikler"]["recall"]
    assert recall >= 0.70, (
        f"Recall {recall} < 0.70. Metrikler: {sonuc['metrikler']} "
        f"Bloklar: {sonuc['bloklar']}"
    )


def test_metrikler_aralikta(sonuc):
    m = sonuc["metrikler"]
    for anahtar in ("precision", "recall", "f1"):
        assert 0.0 <= m[anahtar] <= 1.0
    assert m["tp"] + m["fn"] == 17  # su_derinligi >= 0.5 olan ANT-2009 etiketleri


def test_bagimsizlik_ve_guvensizlik_acikca_bildirilir(sonuc):
    assert sonuc["kalibrasyon"]["bagimsiz_mi"] is False
    assert len(sonuc["metrikler"]["recall_ci95"]) == 2
    assert sonuc["metrikler"]["recall_ci95"][0] < sonuc["metrikler"]["recall"]
    assert sonuc["metrikler"]["precision_sadece_etiket"] is not None
    assert "kalibre" in sonuc["kalibrasyon"]["aciklama"].lower()
    assert "doğrulama" in sonuc["metrikler"]["not"].lower()
    assert "kalibre" in sonuc["metrikler"]["not"].lower()


def test_mekansal_blok_dogrulama_kullanildi(sonuc):
    assert "leave-one-district-out" in sonuc["yontem"]
    assert "rastgele CV" in sonuc["yontem"]
    assert set(sonuc["bloklar"]) >= {"Kepez", "Muratpasa", "Konyaalti"}
