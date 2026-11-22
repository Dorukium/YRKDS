"""GeoJSON poligonunu temsil eden SkorInput uretir (zonal özet).

Poligonla kesisen grid hucrelerinin sayisal ortalamasi ve boolean "herhangi"
(OR) degerleri kullanilir. Kaynak veri yoksa None kalir; 0 varsayilmaz.
"""
from __future__ import annotations

import json
from typing import Any

from app.db import get_conn
from app.models.schemas import SkorInput

SAYISAL = [
    "dem_egim", "dem_twi", "dem_hand", "soil_sand_pct", "soil_clay_pct",
    "soil_ph", "insar_velocity_mm_yr", "vs30", "pga_g", "fay_mesafe_km",
    "yass_m", "akarsu_mesafe_m", "gecmis_taskin_sayisi",
]
BOOLEAN = [
    "taskin_100y", "taskin_500y", "taskin_yapi_yasagi", "falez_cekme_mesafesi",
    "fay_sakinim_bandi", "afete_maruz_bolge", "karst_alan",
]


def poligondan_girdi(geojson: dict[str, Any]) -> tuple[SkorInput, dict[str, Any]]:
    geom_json = json.dumps(geojson)
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
                SELECT
                    AVG(dem_egim), AVG(dem_twi), AVG(dem_hand),
                    AVG(soil_sand_pct), AVG(soil_clay_pct), AVG(soil_ph),
                    AVG(insar_velocity_mm_yr), AVG(vs30), AVG(pga_g),
                    AVG(fay_mesafe_km), AVG(yass_m), AVG(akarsu_mesafe_m),
                    AVG(gecmis_taskin_sayisi),
                    BOOL_OR(taskin_100y), BOOL_OR(taskin_500y),
                    BOOL_OR(taskin_yapi_yasagi), BOOL_OR(falez_cekme_mesafesi),
                    BOOL_OR(fay_sakinim_bandi), BOOL_OR(afete_maruz_bolge),
                    BOOL_OR(karst_alan),
                    MODE() WITHIN GROUP (ORDER BY zemin_sinifi) AS sinif,
                    MODE() WITHIN GROUP (ORDER BY ilce) AS ilce,
                    COUNT(*) AS hucre_sayisi
                FROM grid_cells
                WHERE ST_Intersects(geom, ST_GeomFromGeoJSON(%s))
                """,
            (geom_json,),
        )
        satir = cur.fetchone()

    if satir is None or satir[-1] == 0:
        return SkorInput(), {"hucre_sayisi": 0, "uyari": "Parsel çalışma alanı dışında"}

    veri = dict(zip(SAYISAL + BOOLEAN + ["zemin_sinifi", "ilce", "hucre_sayisi"], satir))
    # Sıvılaşma için kum oranı: SoilGrids kum yüzdesi (zaten yüzde biriminde)
    girdi = SkorInput(
        egim=veri["dem_egim"],
        twi=veri["dem_twi"],
        hand_m=veri["dem_hand"],
        yass_m=veri["yass_m"],
        kum_orani=veri["soil_sand_pct"],
        insar_hiz=veri["insar_velocity_mm_yr"],
        karst=veri["karst_alan"],
        heyelan_envanter=None,  # heyelan envanteri katmanı yok -> bilinmiyor
        kaya_dusmesi=None,
        taskin_100y=veri["taskin_100y"],
        taskin_500y=veri["taskin_500y"],
        akarsu_mesafe_m=veri["akarsu_mesafe_m"],
        gecmis_taskin_sayisi=int(veri["gecmis_taskin_sayisi"])
        if veri["gecmis_taskin_sayisi"] is not None else None,
        fay_mesafe_km=veri["fay_mesafe_km"],
        pga_g=veri["pga_g"],
        vs30=veri["vs30"],
        zemin_sinifi=veri["zemin_sinifi"],
        turba=None,
        organik=None,
        yuksek_bina_yuku=None,
        fay_sakinim_bandi=veri["fay_sakinim_bandi"],
        afete_maruz_bolge=veri["afete_maruz_bolge"],
        taskin_yapi_yasagi=veri["taskin_yapi_yasagi"],
        falez_cekme_mesafesi=veri["falez_cekme_mesafesi"],
    )
    return girdi, {
        "hucre_sayisi": veri["hucre_sayisi"],
        "ilce": veri["ilce"],
        "uyari": "Heyelan envanteri, InSAR, SYGM taşkın haritası ve turba katmanı "
                 "veri setinde yok; ilgili alanlar bilinmiyor (NULL) olarak bırakıldı.",
    }
