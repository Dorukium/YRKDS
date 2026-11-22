"""DEM indirme.

Oncelik: Copernicus GLO-30 (DATASPACE erisim bilgisi varsa).
Yedek: AWS Terrarium (SRTM-turevli) -- anahtarsiz, herkese acik.
Kaynak etiketi asla karistirilmaz; hangi kaynaktan gelindiyse o yazilir.
"""
from __future__ import annotations

import json
import math
import time
from pathlib import Path

import numpy as np
import rasterio
import requests
from rasterio.transform import from_origin

from app.config import GRID_BBOX, PROCESSED_DIR, RAW_DIR

TILE_URL = "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png"
ZOOM = 13  # ~19 m -> 25 m hedef ızgaraya resample edilecek
UA = {"User-Agent": "YRKDS/0.1 (TUBITAK 2204-A; open-data research)"}


def _deg2tile(lon: float, lat: float, z: int) -> tuple[int, int]:
    n = 2**z
    x = int((lon + 180.0) / 360.0 * n)
    lat_r = math.radians(lat)
    y = int((1.0 - math.asinh(math.tan(lat_r)) / math.pi) / 2.0 * n)
    return x, y


def _tile_bounds(x: int, y: int, z: int) -> tuple[float, float, float, float]:
    n = 2**z
    lon0 = x / n * 360.0 - 180.0
    lon1 = (x + 1) / n * 360.0 - 180.0
    lat0 = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))
    lat1 = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * (y + 1) / n))))
    return lon0, lat1, lon1, lat0  # left, top, right, bottom


def indir_terrarium() -> Path:
    min_lon, min_lat, max_lon, max_lat = GRID_BBOX
    x0, y_top = _deg2tile(min_lon, max_lat, ZOOM)
    x1, y_bot = _deg2tile(max_lon, min_lat, ZOOM)
    # _deg2tile dunya sinirinda floor yapar; kenar tile'lari garanti icin
    # birer tane genisletiyoruz (onceki surumde 22% grid alani DEM disinda kalmisti).
    xs = range(x0 - 2, x1 + 3)
    ys = range(y_top - 2, y_bot + 3)
    nx, ny = len(xs), len(ys)

    # Tile'larin gercek dunya sinirlari -- GENISLETILMIS araligin ilk/son
    # tile'larindan turetilir (onceki surumde orijinal indeksler kullanildigi
    # icin mosaic georeferansi 22% alan disinda kaldi).
    left = _tile_bounds(xs.start, ys.start, ZOOM)[0]
    top = _tile_bounds(xs.start, ys.start, ZOOM)[1]
    right = _tile_bounds(xs.stop - 1, ys.stop - 1, ZOOM)[2]
    bottom = _tile_bounds(xs.stop - 1, ys.stop - 1, ZOOM)[3]

    mosaic = np.full((ny * 256, nx * 256), np.nan, dtype=np.float32)
    session = requests.Session()
    session.headers.update(UA)
    indirilen = 0
    for jy, y in enumerate(ys):
        for jx, x in enumerate(xs):
            url = TILE_URL.format(z=ZOOM, x=x, y=y)
            for deneme in range(3):
                try:
                    r = session.get(url, timeout=30)
                    r.raise_for_status()
                    import io

                    from PIL import Image

                    img = np.asarray(Image.open(io.BytesIO(r.content)).convert("RGB"), dtype=np.float32)
                    if img.shape != (256, 256, 3):
                        raise ValueError(f"beklenmeyen tile boyutu {img.shape}")
                    # Terrarium: elevation = R*256 + G + B/256 - 32768
                    elev = img[:, :, 0] * 256 + img[:, :, 1] + img[:, :, 2] / 256 - 32768
                    mosaic[jy * 256 : (jy + 1) * 256, jx * 256 : (jx + 1) * 256] = elev
                    indirilen += 1
                    break
                except Exception as exc:
                    if deneme == 2:
                        print(f"UYARI: tile {x}/{y} indirilemedi: {exc}")
                    time.sleep(0.5 * (deneme + 1))

    if np.all(np.isnan(mosaic)):
        raise RuntimeError("Hiçbir DEM tile'ı indirilemedi")

    if not (left <= min_lon and right >= max_lon and top >= max_lat and bottom <= min_lat):
        raise RuntimeError(
            f"DEM mozaiği çalışma alanını kapsamıyor: {left, bottom, right, top} "
            f"vs {GRID_BBOX}"
        )

    hedef = PROCESSED_DIR / "dem_raw.tif"
    res_x = (right - left) / mosaic.shape[1]
    res_y = (top - bottom) / mosaic.shape[0]
    with rasterio.open(
        hedef,
        "w",
        driver="GTiff",
        height=mosaic.shape[0],
        width=mosaic.shape[1],
        count=1,
        dtype="float32",
        crs="EPSG:4326",
        transform=from_origin(left, top, res_x, res_y),
        nodata=np.nan,
        compress="deflate",
    ) as ds:
        ds.write(mosaic, 1)

    meta = {
        "kaynak": "AWS Terrarium (SRTM-derived), zoom 13",
        "url": "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png",
        "tile_sayisi": indirilen,
        "beklenen_tile": nx * ny,
        "bounds": [left, bottom, right, top],
        "not": "Copernicus GLO-30 kimlik bilgisi bulunmadigi icin anahtarsiz yedek kullanildi.",
    }
    (RAW_DIR / "dem_kaynak.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"DEM indirildi: {indirilen}/{nx * ny} tile -> {hedef}")
    return hedef


def indir() -> Path:
    """Copernicus kimlik bilgisi varsa onceliklidir; yoksa Terrarium."""
    from app.config import COPERNICUS_CLIENT_ID

    if COPERNICUS_CLIENT_ID:
        # GLO-30 erisimi ODC/STAC uzerinden yapilir; bu ortamda kimlik
        # dogrulanamadiysa yedegi kullan (sahte kaynak etiketi yazilmaz).
        print("Copernicus kimlik bilgisi var; dogrudan GLO-30 export denenecek.")
        try:
            return _indir_copernicus()
        except Exception as exc:
            print(f"GLO-30 basarisiz ({exc}); Terrarium yedegine geciliyor.")
    return indir_terrarium()


def _indir_copernicus() -> Path:
    raise RuntimeError(
        "Copernicus Data Space STAC erisimi bu ortamda dogrulanmadi. "
        "Kimlik bilgileri DOTENV uzerinden saglanip ODC/STAC istemcisi kurulmalidir."
    )


if __name__ == "__main__":
    indir()
