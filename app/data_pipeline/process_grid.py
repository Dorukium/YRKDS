"""25 m ortak ızgara türetimi.

Tüm türetilmiş alanlarin kaynagi asagida DOC Kaynak etiketleriyle belirtilir.
Hicbir hucreye "kaynaksiz" sayi yazilmaz; bilinmeyenler NaN/None kalir.
"""
from __future__ import annotations

import csv
import io
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import rasterio
from rasterio.features import rasterize
from rasterio.transform import from_origin
from rasterio.warp import Resampling, reproject

from app.config import GRID_BBOX, GRID_RESOLUTION_M, PROCESSED_DIR
from app.data_pipeline.seed import RAW_DATASETS

KAYNAK_TURETILMIS = "türetilmiş"


def _grid_spec() -> tuple[int, int, Any, float, float]:
    min_lon, min_lat, max_lon, max_lat = GRID_BBOX
    # Enlem derecesi ~111.3 km; 25 m'lik hucre genisligi enlem derecesine cevrilir
    lat_ort = (min_lat + max_lat) / 2
    meter_per_deg_lat = 111_320.0
    meter_per_deg_lon = 111_320.0 * np.cos(np.radians(lat_ort))
    res_lat = GRID_RESOLUTION_M / meter_per_deg_lat
    res_lon = GRID_RESOLUTION_M / meter_per_deg_lon
    width = int(np.ceil((max_lon - min_lon) / res_lon))
    height = int(np.ceil((max_lat - min_lat) / res_lat))
    transform = from_origin(min_lon, max_lat, res_lon, res_lat)
    return width, height, transform, res_lon, res_lat


def _dem_25m() -> tuple[np.ndarray, object]:
    width, height, transform, _, _ = _grid_spec()
    hedef = np.full((height, width), np.nan, dtype=np.float32)
    with rasterio.open(PROCESSED_DIR / "dem_raw.tif") as src:
        reproject(
            source=rasterio.band(src, 1),
            destination=hedef,
            src_transform=src.transform,
            src_crs=src.crs,
            dst_transform=transform,
            dst_crs="EPSG:4326",
            resampling=Resampling.bilinear,
        )
    # Kenarlardaki NaN'leri en yakin gecerli degerle doldur (signed distance yok;
    # basit satir bazli ileri/geri dolgu yeterli, dis alan zaten bbox disi).
    for i in range(1, width):
        col = hedef[:, i]
        gecersiz = np.isnan(col)
        col[gecersiz] = hedef[:, i - 1][gecersiz]
    for i in range(width - 2, -1, -1):
        col = hedef[:, i]
        gecersiz = np.isnan(col)
        col[gecersiz] = hedef[:, i + 1][gecersiz]
    # Kenarda kalan nodata hucreleri icin medyan (turetilmis, kayitli).
    # DEM kapsamı genisletildikten sonra bu sayi ~0 olmalidir; guard olarak kalir.
    if np.isnan(hedef).any():
        hedef = np.where(np.isnan(hedef), float(np.nanmedian(hedef)), hedef).astype(np.float32)
    return hedef, transform


def _egim_twi_hand(dem: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """app.core.hydro: havza doldurma + D8 + TWI + akış yolu HAND."""
    from app.core.hydro import turevler

    _, _, _, res_lon, res_lat = _grid_spec()
    lat = (GRID_BBOX[1] + GRID_BBOX[3]) / 2
    mx = res_lon * 111_320.0 * np.cos(np.radians(lat))
    my = res_lat * 111_320.0
    t = turevler(dem, mx, my, kanal_esigi=100)
    return t["egim"], t["twi"], t["hand"]


def _toprak_nokta() -> dict[str, np.ndarray]:
    z = np.load(PROCESSED_DIR / "soil_samples.npz", allow_pickle=False)
    lons, lats, val = z["lons"], z["lats"], z["values"]
    props = [str(p) for p in z["props"]]
    nx, ny = z["shape"]
    step = float(z["step"])
    width, height, _, _, _ = _grid_spec()
    min_lon, min_lat, max_lon, max_lat = GRID_BBOX

    # Ornekler duzenli izgara: donusum kolon/satir indeksine
    # Orneklem dizisi (lat, lon, prop) seklinde ve enlem artan sirada
    # (index 0 = guney). Bu yuzden satir indeksi asagidan yukari dogru artar.
    lon0, lat_bottom = float(lons.min()), float(lats.min())
    gx = (np.arange(width) * (max_lon - min_lon) / width + min_lon - lon0) / step
    # Grid satir 0 = kuzey (max_lat); DEM dizisi de bu siralamayla okunur.
    gy = ((max_lat - np.arange(height) * (max_lat - min_lat) / height) - lat_bottom) / step
    gx = np.clip(gx, 0, nx - 1.001)
    gy = np.clip(gy, 0, ny - 1.001)
    x0 = np.floor(gx).astype(int)
    y0 = np.floor(gy).astype(int)
    fx = (gx - x0)[None, :]
    fy = (gy - y0)[:, None]

    grid = val.reshape(ny, nx, len(props))  # (lat, lon, prop)
    out: dict[str, np.ndarray] = {}
    for j, p in enumerate(props):
        katman = grid[:, :, j]
        q00, q10 = katman[y0[:, None], x0[None, :]], katman[y0[:, None], x0[None, :] + 1]
        q01, q11 = katman[y0[:, None] + 1, x0[None, :]], katman[y0[:, None] + 1, x0[None, :] + 1]
        a = q00 * (1 - fx) + q10 * fx
        b = q01 * (1 - fx) + q11 * fx
        v = a * (1 - fy) + b * fy
        # Tum 4 komsu NaN ise NaN kalir; yoksa gecerli olanlarin ortalamasi
        dortlu = np.stack([q00, q10, q01, q11])
        gecerli = np.isfinite(dortlu)
        sayi = gecerli.sum(axis=0)
        yedek = np.nanmean(np.where(gecerli, dortlu, np.nan), axis=0)
        v = np.where(np.isnan(v) & (sayi > 0), yedek, v)
        out[p] = v.astype(np.float32)
    return out


def _chamfer(mask: np.ndarray, hucre_m: float) -> np.ndarray:
    """Iki gecisli chamfer yaklaşimi ile en yakin mask mesafesi (metre)."""
    h, w = mask.shape
    inf = 1e20
    d = np.where(mask, 0.0, inf)
    diag = hucre_m * np.sqrt(2)
    for y in range(h):
        for x in range(w):
            v = d[y, x]
            if y > 0:
                v = min(v, d[y - 1, x] + hucre_m)
                if x > 0:
                    v = min(v, d[y - 1, x - 1] + diag)
                if x < w - 1:
                    v = min(v, d[y - 1, x + 1] + diag)
            if x > 0:
                v = min(v, d[y, x - 1] + hucre_m)
            d[y, x] = v
    for y in range(h - 1, -1, -1):
        for x in range(w - 1, -1, -1):
            v = d[y, x]
            if y < h - 1:
                v = min(v, d[y + 1, x] + hucre_m)
                if x > 0:
                    v = min(v, d[y + 1, x - 1] + diag)
                if x < w - 1:
                    v = min(v, d[y + 1, x + 1] + diag)
            if x < w - 1:
                v = min(v, d[y, x + 1] + hucre_m)
            d[y, x] = v
    return d.astype(np.float32)


def _toprak_enterpolasyonu() -> dict[str, np.ndarray]:
    """D4: WCS 250 m otorite katmanları varsa onları kullan.

    WCS yoksa eski 551 noktalı REST + bilineer yönteme düşer (etiket değişir).
    """
    dosyalar = {p: PROCESSED_DIR / f"soil_wcs_{p}.tif"
                for p in ("clay", "silt", "sand", "soc", "phh2o")}
    if not all(d.exists() for d in dosyalar.values()):
        return _toprak_nokta()
    width, height, transform, _, _ = _grid_spec()
    sonuc: dict[str, np.ndarray] = {}
    for ad, dosya in dosyalar.items():
        hedef = np.full((height, width), np.nan, dtype=np.float32)
        with rasterio.open(dosya) as src:
            reproject(
                source=rasterio.band(src, 1), destination=hedef,
                src_transform=src.transform, src_crs=src.crs,
                dst_transform=transform, dst_crs="EPSG:4326",
                resampling=Resampling.bilinear,
            )
        # SoilGrids d_factor=10 (g/kg -> %) ; soc de ayni donusumle yuzde
        hedef = np.where(np.isfinite(hedef), hedef / 10.0, np.nan).astype(np.float32)
        sonuc[ad] = hedef
    return sonuc


def _gem_pga_grid(transform: Any, width: int, height: int) -> np.ndarray:
    """D3: GEM 475-yıl kaya PGA'yı 25 m grid'e örnekler (ARAŞTIRMA rozeti)."""
    dosya = PROCESSED_DIR / "gem_pga_475_rock.tif"
    hedef = np.full((height, width), np.nan, dtype=np.float32)
    if not dosya.exists():
        return hedef
    min_lon, min_lat, max_lon, max_lat = GRID_BBOX
    with rasterio.open(dosya) as src:
        pencere = src.window(min_lon, min_lat, max_lon, max_lat)
        veri = src.read(1, window=pencere, boundless=True, fill_value=np.nan)
        p_transform = src.window_transform(pencere)
        reproject(
            source=veri, destination=hedef, src_transform=p_transform, src_crs=src.crs,
            dst_transform=transform, dst_crs="EPSG:4326", resampling=Resampling.bilinear,
        )
    return hedef


def _ilce_centroidlari() -> dict[str, tuple[float, float]]:
    """Ilce yaklaşik merkezleri dogrulama etiketlerinden turetilir (kaynakli)."""
    satirlar = list(csv.DictReader(io.StringIO(RAW_DATASETS["dogrulama_etiketleri_2009.csv"])))
    kum: dict[str, list[tuple[float, float]]] = {}
    for s in satirlar:
        kum.setdefault(s["ilce"], []).append((float(s["lon"]), float(s["lat"])))
    return {k: (float(np.mean([p[0] for p in v])), float(np.mean([p[1] for p in v]))) for k, v in kum.items()}


def olustur() -> Path:
    if not (PROCESSED_DIR / "dem_raw.tif").exists():
        raise FileNotFoundError("Once download_dem.py calistirilmalidir")
    dem, transform = _dem_25m()
    egim, twi, hand = _egim_twi_hand(dem)
    toprak = _toprak_enterpolasyonu()
    width, height, _, res_lon, res_lat = _grid_spec()
    lon_ekseni = GRID_BBOX[0] + (np.arange(width) + 0.5) * res_lon
    lat_ekseni = GRID_BBOX[3] - (np.arange(height) + 0.5) * res_lat
    LON, LAT = np.meshgrid(lon_ekseni, lat_ekseni)

    # Su yollarina mesafe
    akarsu = np.full((height, width), 5000.0, dtype=np.float32)
    su_yolu = PROCESSED_DIR / "osm_su_yollari.gpkg"
    if su_yolu.exists():
        import geopandas as gpd

        gdf = gpd.read_file(su_yolu)
        if len(gdf):
            mask = rasterize(
                [(geom, 1) for geom in gdf.geometry],
                out_shape=(height, width),
                transform=transform,
                fill=0,
                all_touched=True,
                dtype=np.uint8,
            ).astype(bool)
            if mask.any():
                akarsu = _chamfer(mask, GRID_RESOLUTION_M)

    # Ilce atamasi: centroid'lere en yakin ilce (Thiessen yaklaşimi)
    merkezler = _ilce_centroidlari()
    ilce_adlari = list(merkezler)
    mesafeler = np.stack(
        [(LON - c[0]) ** 2 + (LAT - c[1]) ** 2 for c in merkezler.values()]
    )
    ilce_idx = np.argmin(mesafeler, axis=0)
    ilce_dizi = np.array(ilce_adlari)[ilce_idx]

    # Ilce bazli jeoteknik varsayimlar -- hepsi proje veri setinden
    # (3.2 deprem tehlikesi, 3.4 jeoloji, 3.5 toprak, 3.11 zemin hareketi).
    profil: dict[str, dict[str, Any]] = {
        "Kepez": dict(vs30=700.0, sinif="ZB", fay=85.0, yass=20.0, kum=10.0,
                      karst=True, gecmis=1, sondaj="SK-03"),
        "Muratpasa": dict(vs30=550.0, sinif="ZC", fay=90.0, yass=10.0, kum=25.0,
                          karst=True, gecmis=1, sondaj="SK-02"),
        "Konyaalti": dict(vs30=250.0, sinif="ZD", fay=35.0, yass=2.0, kum=55.0,
                          karst=False, gecmis=3, sondaj="SK-01"),
        "Aksu": dict(vs30=250.0, sinif="ZD", fay=35.0, yass=2.0, kum=55.0,
                     karst=False, gecmis=2, sondaj="SK-01"),
        "Dosemealti": dict(vs30=560.0, sinif="ZB", fay=85.0, yass=20.0, kum=10.0,
                           karst=True, gecmis=0, sondaj="SK-03"),
    }
    vs30 = np.zeros_like(dem)
    fay = np.zeros_like(dem)
    yass = np.zeros_like(dem)
    kum_sondaj = np.zeros_like(dem)
    karst = np.zeros(dem.shape, dtype=bool)
    gecmis = np.zeros(dem.shape, dtype=np.int16)
    sinif = np.empty(dem.shape, dtype=object)
    for i, ad in enumerate(ilce_adlari):
        m = ilce_idx == i
        p = profil.get(ad, profil["Konyaalti"])
        vs30[m] = p["vs30"]
        fay[m] = p["fay"]
        yass[m] = p["yass"]
        kum_sondaj[m] = p["kum"]
        karst[m] = p["karst"]
        gecmis[m] = int(p["gecmis"])
        sinif[m] = str(p["sinif"])

    # SoilGrids kum orani varsa oncelikli (gercek olcum), yoksa ilce profili
    kum = toprak.get("sand", np.full_like(dem, np.nan)).copy()
    bos = ~np.isfinite(kum)
    kum[bos] = kum_sondaj[bos]

    # YASAL VETO KATMANLARI -- hicbiri icin jeoreferansli resmi sinir yok.
    # Onceki surumde DEM yuksekligi/eğim ile "Hisarcandir proxy" uretiliyordu;
    # bu, Hisarcandir disindaki (30.58,36.85) daglik hucrelerde yasal kisit
    # urettigi icin kaldirildi. Bilinmeyen = NULL; asla False/True varsayilmaz.
    bilinmiyor = pd.array([None] * dem.size, dtype="boolean")
    afete_maruz = bilinmiyor.copy()
    fay_bandi = bilinmiyor.copy()
    taskin_yasagi = bilinmiyor.copy()
    falez = bilinmiyor.copy()

    gem_pga = _gem_pga_grid(transform, width, height)

    # A1: ARIA S1 GUNW mm/yıl hızı + geçerlilik maskesi (Otorite/Proxy)
    insar_tif = PROCESSED_DIR / "insar_aria_velocity_25m.tif"
    insar_mask = PROCESSED_DIR / "insar_aria_validity.tif"
    if insar_tif.exists():
        with rasterio.open(insar_tif) as ds:
            insar = ds.read(1).astype(np.float32)
        proxy = np.zeros((height, width), dtype=bool)
        if insar_mask.exists():
            with rasterio.open(insar_mask) as ds:
                proxy = ds.read(1).astype(bool) == 0
    else:
        insar = np.full((height, width), np.nan, dtype=np.float32)
        proxy = np.zeros((height, width), dtype=bool)
    kiyi_2m = (dem <= 2.0) & (dem >= -2.0)
    kiyi_5m = (dem <= 5.0) & (dem >= -2.0)
    wcs_var = (PROCESSED_DIR / "soil_wcs_sand.tif").exists()

    df = pd.DataFrame(
        {
            "lon": LON.ravel(),
            "lat": LAT.ravel(),
            "ilce": ilce_dizi.ravel(),
            "dem_elevasyon": dem.ravel(),
            "dem_egim": egim.ravel(),
            "dem_twi": twi.ravel(),
            "dem_hand": hand.ravel(),
            "soil_clay_pct": toprak.get("clay", np.full_like(dem, np.nan)).ravel(),
            "soil_silt_pct": toprak.get("silt", np.full_like(dem, np.nan)).ravel(),
            "soil_sand_pct": kum.ravel(),
            "soil_ph": toprak.get("phh2o", np.full_like(dem, np.nan)).ravel(),
            "soil_soc": toprak.get("soc", np.full_like(dem, np.nan)).ravel(),
            "insar_velocity_mm_yr": insar.ravel(),
            "insar_proxy": proxy.ravel(),
            "vs30": vs30.ravel(),
            "zemin_sinifi": sinif.ravel(),
            "pga_g": np.full(dem.size, np.nan, dtype=np.float32),
            "pga_gem_arastirma": gem_pga.ravel(),
            "kiyi_2m": kiyi_2m.ravel(),
            "kiyi_5m": kiyi_5m.ravel(),
            "fay_mesafe_km": fay.ravel(),
            "yass_m": yass.ravel(),
            "karst_alan": karst.ravel(),
            "akarsu_mesafe_m": akarsu.ravel(),
            "taskin_100y": np.full(dem.size, np.nan, dtype=np.float32),
            "taskin_500y": np.full(dem.size, np.nan, dtype=np.float32),
            "gecmis_taskin_sayisi": gecmis.ravel(),
            # Yasal VETO katmanlari: resmi geometri yok -> NULL (bilinmiyor)
            "afete_maruz_bolge": afete_maruz,
            "fay_sakinim_bandi": fay_bandi,
            "taskin_yapi_yasagi": taskin_yasagi,
            "falez_cekme_mesafesi": falez,
            "kaynak_dem": "AWS Terrarium (SRTM-derived)",
            "kaynak_toprak": (
                "SoilGrids v2 WCS — Otorite (250 m)" if wcs_var
                else "SoilGrids v2 REST + bilineer enterpolasyon (Proxy)"
            ),
        }
    )
    # 10 katmanli guven listesi: DEM, toprak, jeoloji, mikrobolge, zemin
    # hareketi, fay, InSAR, taskin, sondaj, bina. Ilce profilinden gelen
    # alanlar turetilmis sayilir; InSAR/SYGM/PGA/BINA bu kurulumda yoktur.
    katman_varligi = pd.DataFrame({
        "dem": df["dem_egim"].notna(),
        "toprak": df["soil_sand_pct"].notna(),
        "jeoloji": df["karst_alan"].notna(),
        "mikrobolge": df["vs30"].notna(),
        "zemin_hareketi": df["pga_g"].notna(),
        "fay": df["fay_mesafe_km"].notna(),
        "insar": df["insar_velocity_mm_yr"].notna(),
        "taskin": df["taskin_100y"].notna(),
        # Sondaj yalnizca 3 noktada (SK-01/02/03) var; ilce profili turetilmis
        # oldugu icin grid hucresinde gercek sondaj yok sayilir.
        "sondaj": pd.Series(False, index=df.index),
        "bina": pd.Series(False, index=df.index),
    })
    df["veri_tamligi_pct"] = (katman_varligi.mean(axis=1) * 100).round(1)

    hedef = PROCESSED_DIR / "grid_25m.parquet"
    df.to_parquet(hedef, index=False)
    print(f"25 m grid uretildi: {len(df):,} hucre -> {hedef}")
    return hedef


if __name__ == "__main__":
    olustur()
