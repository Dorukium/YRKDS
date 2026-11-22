"""VETO ust kurali testleri: skoru ezer, eksik katman sessizce False degildir."""
from __future__ import annotations

from app.core.engine import analiz_et
from app.core.veto_rules import veto_kontrol
from app.models.schemas import SkorInput

TAM = dict(
    vs30=760,
    yass_m=20,
    kum_orani=10,
    insar_hiz=0,
    egim=2,
    twi=3,
    fay_mesafe_km=100,
    jeoloji="Traverten",
    pga_g=0.2,
)


def test_vetolar_skoru_ezer():
    girdi = SkorInput(
        **TAM,
        fay_sakinim_bandi=False,
        afete_maruz_bolge=False,
        taskin_yapi_yasagi=False,
        falez_cekme_mesafesi=False,
    )
    normal = analiz_et(girdi, "T-NORMAL")
    veto = analiz_et(girdi.model_copy(update={"afete_maruz_bolge": True}), "T-VETO")
    assert normal.veto is False
    assert veto.veto is True
    assert veto.karar == "Uygun Değil (Yasal Kısıt)"
    assert "Hisarçandır" in veto.veto_neden
    assert veto.skor == normal.skor  # skor ekranda gorunse de karar ezildi


def test_eksik_veto_katmani_uyari_ve_guven_dususu():
    girdi = SkorInput(**TAM)
    v, neden, uyari = veto_kontrol(girdi)
    assert v is False and neden is None
    assert len(uyari) == 4  # hicbiri dogrulanmadi
    r = analiz_et(girdi, "T-EKSIK-VETO")
    assert len(r.uyarilar) >= 4
    assert r.guven_skoru < r.veri_tamligi


def test_avc1999_kaydi_reddedilir():
    """AVC-1999 Istanbul verisi Antalya modeline asla karismaz."""
    from app.data_pipeline.seed import yuklenen_kayitlar

    kayitlar = yuklenen_kayitlar()
    assert all(not str(k.get("id", "")).startswith("AVC-") for k in kayitlar)
    assert any(str(k.get("id", "")).startswith("ANT-2009") for k in kayitlar)
