"""Faz C DoD — Doğrulama ayrılığı (K4).

GERÇEK DURUM: 2003 Boğaçay ve 2008 Kundu olayları için mahalle düzeyi
etiket bulunamadı (Faz A / ADR-0003). Bu test "bağımsız doğrulama geçti"
demek için değil, eksikliği kanıtlamak ve mekansal hold-out mekanizmasını
doğrulamak içindir. Eşik kaydırması YOK.
"""
from __future__ import annotations

from app.config import ROOT
from app.core.backtest import hesapla


def test_olay_bazli_bagimsiz_veri_yok_ve_durust_raporlu():
    r = hesapla()
    assert r["kalibrasyon"]["bagimsiz_mi"] is False
    assert "kalibre" in r["kalibrasyon"]["aciklama"].lower()
    adr = ROOT / "docs/ADR/0018-bagimsiz-olay-etiketi.md"
    assert adr.exists()
    icerik = adr.read_text(encoding="utf-8")
    assert "2003" in icerik and "2008" in icerik
    assert "GLOBAL_FLOOD_DB" in icerik and "COPERNICUS/S1_GRD" in icerik
    # K2 alternatif ölçüm: mekansal blok recall + CI raporlanır
    assert len(r["metrikler"]["recall_ci95"]) == 2
    assert any(v["recall"] >= 0.60 for v in r["bloklar"].values())


def test_mekansal_holdout_mechanizmasi_calisiyor():
    """İlçe blokları ayrık tutuluyor; en az bir blokta Recall >= 0.60."""
    r = hesapla()
    bloklar = r["bloklar"]
    assert len(bloklar) >= 4
    assert all("recall" in v for v in bloklar.values())
    assert any(v["recall"] >= 0.60 for v in bloklar.values())
    assert "leave-one-district-out" in r["yontem"]


def test_a2_gfd_taramasi_kaniti():
    """V5: GFD veritabanı tarandı; AOI'de olay yok, Recall hesaplanmadı."""
    import json

    dosya = ROOT / "data/labels/gfd_2003_2008_manifest.json"
    assert dosya.exists()
    m = json.loads(dosya.read_text(encoding="utf-8"))
    assert len(m["denemeler"]) >= 3
    assert m["k4_dogrulama_ayriligi"]["dogrulama"]["etiket_sayisi"] == 0
    assert m["k4_dogrulama_ayriligi"]["kalibrasyon"]["nokta"] == 18
    gfd = m["denemeler"][1]["bulgu"]
    assert gfd["toplam_olay"] == 913
    assert gfd["antalya_aoi_28_34E_35_38N_olay_sayisi"] == 0


def test_dogrulama_tarihleri_manifestte_yok():
    """2003/2008 için etiket dosyası olmadığını kanıtla (uydurma etiket yok)."""
    raw = ROOT / "data/raw"
    dosyalar = [p.name for p in raw.glob("*.csv")]
    assert not any("2003" in d or "2008" in d for d in dosyalar)
    assert any("2009" in d for d in dosyalar)
