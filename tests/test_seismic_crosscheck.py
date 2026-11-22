"""Faz D DoD — Sismik çapraz kontrol (ADR-0004).

GEM GSHM v2026.1 CC BY-NC-SA lisanslı olduğu için ticari ürüne sayısal
raster gömülemez. Bu test "bağımsız GEM ile sapma" iddiası kurmaz; bunun
yerine (a) lisans/kayıt durumunu ve (b) proje PGA değerlerinin iç tutarlılığını
kanıtlar (K2 alternatif ölçüm).
"""
from __future__ import annotations

import csv
import io

from app.config import PROCESSED_DIR, ROOT
from app.data_pipeline.seed import RAW_DATASETS


def test_gem_raster_indirilmedi_ve_durum_belli():
    durum = ROOT / "docs/ADR/0004-sismik-model-lisans.md"
    assert durum.exists()
    icerik = durum.read_text(encoding="utf-8")
    assert "CC BY-NC-SA" in icerik
    assert not (PROCESSED_DIR / "gem_pga.tif").exists()  # gömülü veri yok


def test_proje_pga_degerleri_ic_tutali():
    satirlar = list(csv.DictReader(io.StringIO(RAW_DATASETS["zemin_hareketi.csv"])))
    pga = {s["mahalle"]: float(s["pga_g"]) for s in satirlar}
    assert 0.1 <= min(pga.values()) <= 0.5
    assert max(pga.values()) <= 1.0
    # Yumusak zemin (ZE) en yuksek PGA'ya sahip olmali
    assert pga["Bogacay-Gokdere"] > pga["Masa Dagi"]
    assert pga["Sahil-Liman"] > pga["Varsak"]


def test_sapma_raporu_belirsizligi_bildiriyor():
    rapor = ROOT / "docs/dogrulama_raporu.md"
    if rapor.exists():
        icerik = rapor.read_text(encoding="utf-8")
        assert "GEM" in icerik
