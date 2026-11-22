"""25 m grid ve olay kayitlarini PostGIS'e yukler (tekrarlanabilir)."""
from __future__ import annotations

import csv
import io
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd
import psycopg

from app.config import PROCESSED_DIR
from app.data_pipeline.seed import RAW_DATASETS, dosya_yaz
from app.db import get_conn

GRID_KOLONLARI: list[str] = [
    "ilce", "geom", "dem_elevasyon", "dem_egim", "dem_twi", "dem_hand",
    "soil_clay_pct", "soil_silt_pct", "soil_sand_pct", "soil_ph", "soil_soc",
    "insar_velocity_mm_yr", "vs30", "zemin_sinifi", "pga_g", "pga_gem_arastirma",
    "kiyi_2m", "kiyi_5m", "fay_mesafe_km",
    "yass_m", "akarsu_mesafe_m", "taskin_100y", "taskin_500y",
    "taskin_yapi_yasagi", "falez_cekme_mesafesi", "fay_sakinim_bandi",
    "afete_maruz_bolge", "karst_alan", "gecmis_taskin_sayisi",
    "veri_tamligi_pct", "kaynak_dem", "kaynak_toprak",
]


def _tarih(s: str) -> date | None:
    s = s.strip()
    if len(s) == 4 and s.isdigit():
        return date(int(s), 1, 1)
    try:
        return date.fromisoformat(s)
    except ValueError:
        return None


def _grid_yukle(conn: psycopg.Connection, parquet: Path) -> int:
    df = pd.read_parquet(parquet)
    lon = df["lon"].to_numpy()
    lat = df["lat"].to_numpy()
    # Hucre genisligi: komşu merkezler arasindaki mesafenin yariSI
    dx = float(abs(lon[1] - lon[0]) / 2) if len(lon) > 1 else 0.0001
    dy = float(abs(lat[len(lon)] - lat[0]) / 2) if len(lat) > len(lon) else dx
    # Bilinen 25 m cozunurlukten sabit derece adimi (enlem 111.32 km)
    import numpy as np

    dx = float(25 / (111_320 * np.cos(np.radians(float(np.mean(lat)))))) / 2
    dy = float(25 / 111_320) / 2

    x0, x1 = lon - dx, lon + dx
    y0, y1 = lat - dy, lat + dy
    wkt = (
        "POLYGON((" + pd.Series(x0).astype(str) + " " + pd.Series(y0).astype(str) + ","
        + pd.Series(x1).astype(str) + " " + pd.Series(y0).astype(str) + ","
        + pd.Series(x1).astype(str) + " " + pd.Series(y1).astype(str) + ","
        + pd.Series(x0).astype(str) + " " + pd.Series(y1).astype(str) + ","
        + pd.Series(x0).astype(str) + " " + pd.Series(y0).astype(str) + "))"
    )
    df["geom"] = wkt
    df["taskin_100y"] = df["taskin_100y"].map(lambda v: None if pd.isna(v) else bool(v))
    df["taskin_500y"] = df["taskin_500y"].map(lambda v: None if pd.isna(v) else bool(v))
    df["taskin_yapi_yasagi"] = df["taskin_yapi_yasagi"].map(lambda v: None if pd.isna(v) else bool(v))
    df["falez_cekme_mesafesi"] = df["falez_cekme_mesafesi"].map(lambda v: None if pd.isna(v) else bool(v))
    df["kaynak_dem"] = df["kaynak_dem"].fillna("AWS Terrarium (SRTM-derived)")
    df["kaynak_toprak"] = df["kaynak_toprak"].fillna("SoilGrids v2 + bilineer enterpolasyon")

    with conn.cursor() as cur:
        cur.execute("TRUNCATE grid_cells RESTART IDENTITY")
    kolonlar = ", ".join(GRID_KOLONLARI)
    with conn.cursor() as cur, cur.copy(f"COPY grid_cells ({kolonlar}) FROM STDIN") as cp:
        for satir in df[GRID_KOLONLARI].itertuples(index=False, name=None):
            cp.write_row(tuple(None if pd.isna(v) else v for v in satir))
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM grid_cells")
        satir = cur.fetchone()
        assert satir is not None
        return int(satir[0])


def _olay_yukle(conn: psycopg.Connection) -> int:
    satirlar: list[tuple[Any, ...]] = []

    for s in csv.DictReader(io.StringIO(RAW_DATASETS["deprem_katalogu.csv"])):
        buyukluk = None
        try:
            buyukluk = float(s["mw"])
        except ValueError:
            pass
        satirlar.append((
            "deprem", _tarih(s["tarih"]), None, s["yer"], None, None, buyukluk,
            (s["antalya_etkisi"] + " | " + s["not"])[:500],
            "AFAD / KOERI / USGS (proje veri seti)", None, False, None,
        ))

    for s in csv.DictReader(io.StringIO(RAW_DATASETS["taskin_olaylari.csv"])):
        satirlar.append((
            "taskin", _tarih(s["tarih"]), s["ilce"], None, None, None, None,
            (s["olay"] + " | " + s["yagis"] + " | " + s["etki"])[:500],
            "DSI / MGM (proje veri seti)", None, False, None,
        ))

    for s in csv.DictReader(io.StringIO(RAW_DATASETS["dogrulama_etiketleri_2009.csv"])):
        if s["id"].startswith("AVC-"):
            continue  # Istanbul Avcilar -- KULLANILMAZ
        satirlar.append((
            "tasin_etiketi", date(2009, 12, 16), s["ilce"], s["mahalle"],
            float(s["lat"]), float(s["lon"]), float(s["su_derinligi_m"]),
            f"2009 seli hasar: {s['hasar']} (dogru kaynak: ANT-2009 dogrulama etiketi)",
            "ANT-2009 dogrulama etiketi (proje veri seti)", None, True,
            f"POINT({s['lon']} {s['lat']})",
        ))

    for s in csv.DictReader(io.StringIO(RAW_DATASETS["kontrol_ornekleri.csv"])):
        if s["id"].startswith("AVC-"):
            continue
        satirlar.append((
            "hasarsiz_kontrol", None, s["ilce"], s["mahalle"], None, None, None,
            f"Kontrol ornegi {s['id']}; konum guveni {s['konum_guveni']}. "
            "Koordinat veri setinde bulunmadigi icin haritada gosterilmez.",
            "BLN kontrol ornekleri (proje veri seti)", float(s["konum_guveni"]), False, None,
        ))

    with conn.cursor() as cur:
        cur.execute("TRUNCATE events RESTART IDENTITY")
        cur.executemany(
            """INSERT INTO events
               (olay_turu, tarih, ilce, mahalle, lat, lon, buyukluk, etki,
                kaynak_url, konum_guveni, dogrulama_etiketi, geom)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                       CASE WHEN %s::text IS NULL THEN NULL ELSE ST_GeomFromText(%s::text,4326) END)""",
            [tuple(s) + (s[-1],) for s in satirlar],
        )
    return len(satirlar)


def yukle() -> dict[str, int]:
    dosya_yaz()
    parquet = PROCESSED_DIR / "grid_25m.parquet"
    if not parquet.exists():
        raise FileNotFoundError("grid_25m.parquet yok; once process_grid.py calistir")
    with get_conn() as conn:
        n_grid = _grid_yukle(conn, parquet)
        n_olay = _olay_yukle(conn)
    return {"grid_cells": n_grid, "events": n_olay}


if __name__ == "__main__":
    print(yukle())
