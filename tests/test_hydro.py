"""Hidrolojik türevlerin fiziksel doğruluk testleri."""
from __future__ import annotations

import numpy as np

from app.core.hydro import d8_akis_ve_kanal, havza_doldur, turevler


def test_havza_doldur_kapali_cukuru_tasirir():
    dem = np.ones((5, 5), dtype=np.float32) * 10
    dem[2, 2] = 0  # derin çukur, çıkış yok
    filled = havza_doldur(dem)
    assert filled[2, 2] >= 10.0  # taşma seviyesine yükseldi
    assert np.all(filled >= dem)


def test_d8_birikim_tek_cikista_toplam_hucre_sayisina_ulasma():
    # Soldan saga, yukaridan asagiya azalan duzlem: tum akis sag-alt koseye gelir
    dem = np.zeros((4, 4), dtype=np.float32)
    for y in range(4):
        for x in range(4):
            dem[y, x] = 100 - (x + y)  # sag-alt en dusuk
    akis, _, kanal = d8_akis_ve_kanal(dem, 25.0, 25.0, kanal_esigi=16)
    assert int(akis.max()) == 16
    assert bool(akis[3, 3] == 16)
    assert bool(kanal[3, 3])


def test_hand_kanalda_sifir_yuksekte_pozitif():
    dem = np.zeros((5, 5), dtype=np.float32)
    for y in range(5):
        for x in range(5):
            dem[y, x] = 50.0 - x  # en sag sutun kanal
    t = turevler(dem, 25.0, 25.0, kanal_esigi=3)
    assert float(t["hand"][0, 4]) == 0.0
    assert float(t["hand"][0, 0]) > 0.0
    assert np.all(t["hand"] >= 0)
    assert np.all(np.isfinite(t["twi"]))


def test_gercek_gridde_turevler_sonlu_ve_aralikta():
    import pandas as pd

    from app.config import PROCESSED_DIR

    p = PROCESSED_DIR / "grid_25m.parquet"
    if not p.exists():
        return
    df = pd.read_parquet(p, columns=["dem_egim", "dem_twi", "dem_hand", "dem_elevasyon"])
    assert df.dem_elevasyon.notna().mean() > 0.99  # DEM boslugu kalmadi
    assert np.isfinite(df.dem_twi).all()
    assert (df.dem_hand >= 0).all()
