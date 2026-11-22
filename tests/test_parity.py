"""Python ve Rust skor motorlarinin birebir ayni sonucu urettigini kanitlar.

Rastgele uretilmis girdi kullanilmaz: spesifikasyon 2.4'teki esiklerin
her birini exercise eden sabit vektorler kullanilir.
"""
from __future__ import annotations

import pytest

from app.core.scoring import alt_puanlar, karar_bandi, toplam_skor
from app.models.schemas import SkorInput

skor_motoru = pytest.importorskip("skor_motoru", reason="Rust motoru build edilmemis")

VAKTORLER = [
    SkorInput(),
    SkorInput(vs30=800, fay_mesafe_km=3, egim=2, twi=3, yass_m=20, kum_orani=10,
              insar_hiz=0.5, gecmis_taskin_sayisi=0),
    SkorInput(vs30=500, egim=10, twi=6, yass_m=4, kum_orani=50, insar_hiz=3),
    SkorInput(vs30=250, egim=20, twi=9, yass_m=2, kum_orani=70, insar_hiz=7,
              karst=True, gecmis_taskin_sayisi=3),
    SkorInput(zemin_sinifi="ZD-ZE", egim=35, taskin_100y=True, turba=True,
              yuksek_bina_yuku=True, fay_mesafe_km=30),
    SkorInput(heyelan_envanter=True, insar_hiz=12, taskin_500y=True,
              kaya_dusmesi=True, falez_cekme_mesafesi=True),
    SkorInput(vs30=180, yass_m=8, insar_hiz=5.1, egim=15.1, twi=5.1,
              fay_mesafe_km=14.9, gecmis_taskin_sayisi=2),
    SkorInput(vs30=300, twi=7.0, hand_m=3.0, gecmis_taskin_sayisi=1, egim=2),
    SkorInput(vs30=300, twi=6.5, hand_m=30.0, gecmis_taskin_sayisi=2, egim=2),
]


RUST_ALANLARI = {
    "vs30", "zemin_sinifi", "yass_m", "kum_orani", "insar_hiz", "karst",
    "egim", "kaya_dusmesi", "heyelan_envanter", "taskin_100y", "taskin_500y",
    "akarsu_mesafe_m", "twi", "hand_m", "gecmis_taskin_sayisi", "fay_mesafe_km", "pga_g",
    "turba", "organik", "yuksek_bina_yuku", "fay_sakinim_bandi",
    "afete_maruz_bolge", "taskin_yapi_yasagi", "falez_cekme_mesafesi",
}


def _rust(girdi: SkorInput):
    kwargs = {k: v for k, v in girdi.model_dump().items() if k in RUST_ALANLARI}
    return skor_motoru.skor_hesapla(skor_motoru.SkorInput(**kwargs))


@pytest.mark.parametrize("girdi", VAKTORLER, ids=range(len(VAKTORLER)))
def test_python_rust_paritesi(girdi):
    py_alt = alt_puanlar(girdi)
    py_skor = toplam_skor(py_alt)
    py_bant = karar_bandi(py_skor)[0] if py_skor is not None else "KARARSIZ"

    r_skor, r_bant, _r_veto, r_alt = _rust(girdi)
    rust_alt = dict(r_alt)

    assert py_skor == pytest.approx(r_skor, abs=0.05), (py_skor, r_skor)
    assert py_bant == r_bant
    for kod in ("ZB", "L", "S", "H", "F"):
        py_v, r_v = py_alt[kod], rust_alt[kod]
        if py_v is None or r_v is None:
            assert py_v is None and r_v is None, kod
        else:
            assert py_v == pytest.approx(r_v, abs=1e-9), kod
