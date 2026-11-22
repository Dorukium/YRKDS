"""Spesifikasyon 2.1 / 2.4 icin deterministik birim testleri."""
from __future__ import annotations

import pytest

from app.core.engine import analiz_et
from app.core.scoring import (
    f_puani,
    h_puani,
    l_puani,
    s_puani,
    toplam_skor,
    zb_puani,
)
from app.models.schemas import SkorInput


def test_zb_esikleri_ve_fay_bonusu():
    assert zb_puani(SkorInput(vs30=800)) == 0.0
    assert zb_puani(SkorInput(vs30=500)) == 0.3
    assert zb_puani(SkorInput(vs30=250)) == 0.7
    assert zb_puani(SkorInput(vs30=150)) == 1.0
    assert zb_puani(SkorInput(vs30=800, fay_mesafe_km=3)) == 0.15
    assert zb_puani(SkorInput(vs30=800, fay_mesafe_km=10)) == 0.10
    assert zb_puani(SkorInput(vs30=800, fay_mesafe_km=30)) == 0.05
    assert zb_puani(SkorInput(vs30=800, fay_mesafe_km=40)) == 0.0
    assert zb_puani(SkorInput(vs30=100, fay_mesafe_km=3)) == 1.0  # clamp


def test_siniftan_vs30_turetme_turetilmis_etiketli():
    from app.core.scoring import vs30_etkin

    assert vs30_etkin(SkorInput(zemin_sinifi="ZD"))[1] == "turetilmis"
    assert vs30_etkin(SkorInput(zemin_sinifi="ZD-ZE"))[0] == 110.0
    assert vs30_etkin(SkorInput())[0] is None


def test_l_sivilasma_kurallari():
    assert l_puani(SkorInput(yass_m=2, kum_orani=70)) == 1.0
    assert l_puani(SkorInput(yass_m=4, kum_orani=50)) == 0.7
    assert l_puani(SkorInput(yass_m=8, kum_orani=10)) == 0.3
    assert l_puani(SkorInput(yass_m=20, kum_orani=10)) == 0.0
    assert l_puani(SkorInput(kum_orani=70)) is None  # YASS yok -> 0 varsayilmaz


def test_s_oturma_ve_eklemeler():
    assert s_puani(SkorInput(insar_hiz=12)) == 1.0
    assert s_puani(SkorInput(insar_hiz=7)) == 0.6
    assert s_puani(SkorInput(insar_hiz=3)) == 0.3
    assert s_puani(SkorInput(insar_hiz=0.5)) == 0.0
    assert s_puani(SkorInput(insar_hiz=3, karst=True, turba=True)) == 0.7
    assert s_puani(SkorInput(insar_hiz=12, karst=True, yuksek_bina_yuku=True)) == 1.0
    assert s_puani(SkorInput(karst=True)) is None


def test_h_heyelan_override_ve_kaya_dusmesi():
    assert h_puani(SkorInput(egim=35)) == 1.0
    assert h_puani(SkorInput(egim=20)) == 0.6
    assert h_puani(SkorInput(egim=10)) == 0.2
    assert h_puani(SkorInput(egim=2, kaya_dusmesi=True)) == 0.2
    assert h_puani(SkorInput(egim=2, heyelan_envanter=True)) == 1.0
    assert h_puani(SkorInput(kaya_dusmesi=True)) is None


def test_f_taskin_kurallari():
    assert f_puani(SkorInput(taskin_100y=True)) == 1.0
    assert f_puani(SkorInput(taskin_500y=True)) == 0.6
    assert f_puani(SkorInput(akarsu_mesafe_m=100, twi=9)) == 0.7
    assert f_puani(SkorInput(taskin_500y=True, gecmis_taskin_sayisi=3)) == 0.75
    assert f_puani(SkorInput()) is None


def test_toplam_skor_agirlik_normalizasyonu():
    # Yalnizca ZB=1, L=0 -> 100*(0.25*1 + 0.20*0)/(0.45) = 55.6
    assert toplam_skor({"ZB": 1.0, "L": 0.0}) == 55.6
    assert toplam_skor({}) is None


def test_kararsiz_kurali():
    r = analiz_et(SkorInput(egim=2), parsel_id="T-KARARSIZ")
    assert r.bant == "KARARSIZ"
    assert r.skor is None
    assert "sondaj/etüt" in r.karar
    assert r.guven_skoru < 0.4


def test_tam_veri_sayisal_skor_ve_kanit():
    r = analiz_et(
        SkorInput(
            vs30=250,
            fay_mesafe_km=40,
            yass_m=2,
            kum_orani=70,
            insar_hiz=7,
            karst=True,
            egim=20,
            taskin_100y=True,
            gecmis_taskin_sayisi=3,
            jeoloji="Alüvyon",
            pga_g=0.4,
            fay_sakinim_bandi=False,
            afete_maruz_bolge=False,
            taskin_yapi_yasagi=False,
            falez_cekme_mesafesi=False,
        ),
        parsel_id="T-TAM",
    )
    assert r.skor is not None and 0 <= r.skor <= 100
    assert r.bant in {"Düşük", "Düşük-Orta", "Orta-Yüksek", "Yüksek", "Kritik"}
    assert r.veto is False
    assert any(k.katman == "DEM" for k in r.kanit)
    assert any(k.katman == "InSAR" and k.guven == "eksik" for k in r.kanit) is False


def test_kismi_skor_uygun_karari_vermez_ve_guveni_dusurur():
    """InSAR yokken S bileşeni eksik -> kısmi skor, düşük güven, koşullu karar."""
    r = analiz_et(
        SkorInput(
            vs30=760, yass_m=20, kum_orani=10, egim=2, twi=2, gecmis_taskin_sayisi=0,
            fay_mesafe_km=85, pga_g=0.2, karst=False, insar_hiz=None,
            fay_sakinim_bandi=False, afete_maruz_bolge=False,
            taskin_yapi_yasagi=False, falez_cekme_mesafesi=False,
        ),
        "T-KISMI",
    )
    assert r.skor_kapsami["tur"] == "kısmi"
    assert "S" in r.skor_kapsami["eksik"]
    assert r.skor is not None
    assert not r.karar.startswith("Uygun")
    assert r.guven_skoru < r.veri_tamligi * 0.6
    assert any("Kısmi skor" in u for u in r.uyarilar)


def test_dogrulanmamis_yasal_kisit_uygun_karari_engeller():
    r = analiz_et(
        SkorInput(vs30=760, yass_m=20, kum_orani=10, egim=2, twi=2, insar_hiz=0,
                  gecmis_taskin_sayisi=0, fay_mesafe_km=85, pga_g=0.2),
        "T-YASAL",
    )
    assert r.yasal_kisit_durumu == "dogrulanamadi"
    assert not r.karar.startswith("Uygun")
    assert any("yasal kısıt" in u for u in r.uyarilar)


@pytest.mark.parametrize("karst", [True, False])
def test_kanit_ve_uyari_tutarliligi(karst):
    r = analiz_et(SkorInput(vs30=500, karst=karst, zemin_sinifi="ZC"), "T-1")
    assert isinstance(r.uyarilar, list)
    assert r.katman_durumu
