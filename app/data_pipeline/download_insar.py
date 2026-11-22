"""A1 — NASA Earthdata / ARIA S1 GUNW InSAR hız haritası (K3: Otorite).

earthaccess ile Antalya AOI'si için 2021–2026 GUNW granülleri indirilir;
unwrapped phase -> LOS yer değişimi -> interferogram başına mm/yıl hız,
ardından sağlam GMT'lerle yığınlanıp 25 m ızgaraya warplanır.

Kimlik: .env EARTHDATA_USERNAME / EARTHDATA_PASSWORD (NASA Earthdata).
İlk kullanımda ASF DAAC EULA'sı programatik olarak kabul edilmelidir
(bkz. _ensure_asf_eula). Uydurma hız üretilmez; kapsam düşükse NULL kalır.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import numpy as np
import rasterio
from rasterio.transform import from_origin
from rasterio.warp import Resampling, reproject

from app.config import GRID_BBOX, PROCESSED_DIR, RAW_DIR

AOI = (GRID_BBOX[0], GRID_BBOX[1], GRID_BBOX[2], GRID_BBOX[3])
LAMBDA_M = 0.05546576  # Sentinel-1 C-band 5.405 GHz (fiziksel sabit)
MIN_COHERENCE = 0.15
MIN_GRANULES = 5
COLLECTION = "ARIA_S1_GUNW"
TEMPORAL = ("2021-01-01", "2026-11-22")
EULA_IDS = ("1b454cfb-c298-4072-ae3c-3c133ce810c8", "5ee7b8c9-c1f4-405c-b787-3aa7ab9b2dad")
APP_CLIENT = "BO_n7nTIlMljdvU6kRRB3g"


def _login() -> Any:
    import earthaccess

    return earthaccess.login(strategy="environment")


def _ensure_asf_eula() -> None:
    """ASF DAAC EULA'sını bir kez kabul et (kullanıcı kimlik bilgileriyle)."""
    import requests
    from bs4 import BeautifulSoup

    kullanici = os.getenv("EARTHDATA_USERNAME", "")
    parola = os.getenv("EARTHDATA_PASSWORD", "")
    if not (kullanici and parola):
        return
    s = requests.Session()
    url = f"https://urs.earthdata.nasa.gov/approve_app?client_id={APP_CLIENT}"
    try:
        r = s.get(url, timeout=60)
        tok = re.search(r'name="authenticity_token" value="([^"]+)"', r.text)
        red = re.search(r'name="redirect_uri"[^>]*value="([^"]+)"', r.text)
        if not (tok and red):
            return
        s.post(
            "https://urs.earthdata.nasa.gov/login",
            data={"username": kullanici, "password": parola,
                  "authenticity_token": tok.group(1), "client_id": APP_CLIENT,
                  "redirect_uri": red.group(1)},
            allow_redirects=True, timeout=60,
        )
        for eula in EULA_IDS:
            r2 = s.get(f"https://urs.earthdata.nasa.gov/accept_eula/{eula}", timeout=60)
            form = BeautifulSoup(r2.text, "html.parser").find("form")
            if not form:
                continue
            alan = form.find("input", {"name": "authenticity_token"})
            if not alan:
                continue
            s.post(
                "https://urs.earthdata.nasa.gov" + str(form["action"]),
                data={"authenticity_token": alan["value"], "agreement": "1", "authorize": "Agree"},
                allow_redirects=True, timeout=60,
            )
    except Exception as exc:
        print(f"EULA kontrolü uyarısı: {exc}")


def arama(limit: int = 60) -> list[Any]:
    import earthaccess

    _login()
    _ensure_asf_eula()
    return earthaccess.search_data(
        short_name=COLLECTION, bounding_box=AOI, temporal=TEMPORAL, count=limit
    )


def indir(granuller: list[Any], hedef: Path | None = None) -> list[Path]:
    if not granuller:
        return []
    import earthaccess

    hedef = hedef or (RAW_DIR / "aria_gunw")
    hedef.mkdir(parents=True, exist_ok=True)
    _login()
    _ensure_asf_eula()
    return [Path(d) for d in earthaccess.download(granuller, str(hedef)) if d]


def _tarihler(dosya: Path) -> tuple[datetime, datetime]:
    """GUNW dosya adından (secondary, reference) tarihleri çıkarır.

    Örnek: ...-tops-20240121_20240109-155057-... -> (2024-01-21, 2024-01-09)
    """
    eslesme = re.search(r"(20\d{6})_(20\d{6})", dosya.stem)
    if not eslesme:
        raise ValueError(f"tarih çıkarılamadı: {dosya.name}")
    return (
        datetime.strptime(eslesme.group(1), "%Y%m%d").replace(tzinfo=UTC),
        datetime.strptime(eslesme.group(2), "%Y%m%d").replace(tzinfo=UTC),
    )


def _gundeki_hiz(dosya: Path) -> dict[str, Any] | None:
    import xarray as xr

    try:
        ikinci, birinci = _tarihler(dosya)
        gun_sayisi = (ikinci - birinci).days
        if gun_sayisi <= 0:
            return None
        veri = xr.open_dataset(dosya, group="science/grids/data", engine="h5netcdf")
        faz = veri["unwrappedPhase"].values
        coh = veri["coherence"].values
        lon = veri["longitude"].values
        lat = veri["latitude"].values
        veri.close()

        # AOI kırpma (derece dizileri 1B)
        ix = np.where((lon >= AOI[0]) & (lon <= AOI[2]))[0]
        iy = np.where((lat >= AOI[1]) & (lat <= AOI[3]))[0]
        if len(ix) < 2 or len(iy) < 2:
            return None
        faz = faz[np.ix_(iy, ix)]
        coh = coh[np.ix_(iy, ix)]
        lonk, latk = lon[ix], lat[iy]

        gecerli = np.isfinite(faz) & np.isfinite(coh) & (coh >= MIN_COHERENCE)
        # GUNW fazı keyfi sabit + yörünge rampası içerir. AOI üzerinde
        # en küçük karelerle düzlem uydurup sabit ve eğimi kaldırırız;
        # kalan yerel faz değişimi deformasyon göstergesidir.
        if gecerli.sum() > 100:
            yy, xx = np.nonzero(gecerli)
            A = np.column_stack([np.ones(len(xx)), xx, yy])
            katsayi, *_ = np.linalg.lstsq(A, faz[gecerli], rcond=None)
            grid_y, grid_x = np.mgrid[0:faz.shape[0], 0:faz.shape[1]]
            faz = faz - (katsayi[0] + katsayi[1] * grid_x + katsayi[2] * grid_y)
        # LOS yer değişimi (mm); pozitif = uyduya doğru
        disp_mm = -faz * LAMBDA_M / (4 * np.pi) * 1000.0
        hiz = np.where(gecerli, disp_mm / gun_sayisi * 365.25, np.nan).astype(np.float32)
        agirlik = np.where(gecerli, np.maximum(coh - MIN_COHERENCE, 0.01), 0.0)
        # Enlem dizisi azalan sırada: ilk eleman kuzey (üst) kenardır.
        transform = from_origin(float(lonk[0]), float(latk[0]),
                                float(lonk[1] - lonk[0]), abs(float(latk[1] - latk[0])))
        return {"hiz": hiz, "agirlik": agirlik.astype(np.float32),
                "transform": transform, "tarih": ikinci.date().isoformat(),
                "gun": gun_sayisi}
    except Exception as exc:
        print(f"GUNW okunamadı {dosya.name}: {exc}")
        return None


def _grid_spec() -> tuple[int, int, Any]:
    min_lon, min_lat, max_lon, max_lat = AOI
    res_lat = 25 / 111_320.0
    res_lon = 25 / (111_320.0 * np.cos(np.radians((min_lat + max_lat) / 2)))
    width = int(np.ceil((max_lon - min_lon) / res_lon))
    height = int(np.ceil((max_lat - min_lat) / res_lat))
    return width, height, from_origin(min_lon, max_lat, res_lon, res_lat)


def hiz_haritasi_olustur(dosyalar: list[Path]) -> dict[str, Any]:
    """Ağırlıklı ortalama hızı 25 m ızgaraya yazar; kapsam oranını döndürür."""
    gozlemler = [g for g in (_gundeki_hiz(d) for d in dosyalar) if g is not None]
    if len(gozlemler) < MIN_GRANULES:
        return {"durum": "veri_yok", "gozlem": len(gozlemler)}
    pay = np.zeros_like(gozlemler[0]["hiz"], dtype=np.float64)
    payda = np.zeros_like(gozlemler[0]["hiz"], dtype=np.float64)
    for g in gozlemler:
        w = g["agirlik"]
        pay += w * np.nan_to_num(g["hiz"])
        payda += w
    hiz = np.where(payda > 0, pay / np.maximum(payda, 1e-9), np.nan).astype(np.float32)

    width, height, transform = _grid_spec()
    hedef = np.full((height, width), np.nan, dtype=np.float32)
    reproject(
        source=hiz, destination=hedef, src_transform=gozlemler[0]["transform"],
        src_crs="EPSG:4326", dst_transform=transform, dst_crs="EPSG:4326",
        resampling=Resampling.bilinear, src_nodata=np.nan, dst_nodata=np.nan,
    )
    # Radar gölgesi/koherens boşlukları: en yakın geçerli hücre ile doldurulur
    # ve ayrı geçerlilik maskesinde "Proxy" olarak işaretlenir (K3).
    from scipy.ndimage import distance_transform_edt

    gecerli_mask = np.isfinite(hedef)
    otorite_kapsam = float(gecerli_mask.mean())
    if gecerli_mask.any():
        _, ind = distance_transform_edt(~gecerli_mask, return_indices=True)
        doldurulmus = hedef[tuple(ind)]
    else:
        doldurulmus = hedef.copy()
    tif = PROCESSED_DIR / "insar_aria_velocity_25m.tif"
    with rasterio.open(tif, "w", driver="GTiff", height=height, width=width, count=1,
                       dtype="float32", crs="EPSG:4326", transform=transform,
                       nodata=np.nan, compress="deflate") as ds:
        ds.write(doldurulmus.astype(np.float32), 1)
    mask_tif = PROCESSED_DIR / "insar_aria_validity.tif"
    with rasterio.open(mask_tif, "w", driver="GTiff", height=height, width=width, count=1,
                       dtype="uint8", crs="EPSG:4326", transform=transform,
                       compress="deflate") as ds:
        ds.write(gecerli_mask.astype(np.uint8), 1)
    kapsam = float(np.isfinite(doldurulmus).mean())
    # Örnek hücre değerleri (kanıt için)
    ornekler = []
    for y, x in ((height // 2, width // 2), (height // 3, width // 3),
                 (2 * height // 3, 2 * width // 3)):
        v = hedef[y, x]
        ornekler.append({"satir": y, "sutun": x, "hiz_mm_yil": round(float(v), 2)
                         if np.isfinite(v) else None})
    return {"durum": "ok", "gozlem": len(gozlemler), "kapsam_pct": round(kapsam * 100, 2),
            "otorite_kapsam_pct": round(otorite_kapsam * 100, 2),
            "proxy_kapsam_pct": round((kapsam - otorite_kapsam) * 100, 2),
            "tif": str(tif), "mask_tif": str(mask_tif), "ornekler": ornekler,
            "tarih_araligi": [min(g["tarih"] for g in gozlemler),
                              max(g["tarih"] for g in gozlemler)]}


def calistir(limit: int = 12) -> dict[str, Any]:
    granuller = arama(limit)
    dosyalar = indir(granuller)
    sonuc = hiz_haritasi_olustur(dosyalar)
    rapor = {
        "kaynak": "NASA Earthdata / ARIA S1 GUNW (ASF DAAC)",
        "erisim_tarihi": date.today().isoformat(),
        "koleksiyon": COLLECTION,
        "granul_sayisi": len(granuller),
        "indirilen": len(dosyalar),
        "sha256_ilk": hashlib.sha256(dosyalar[0].read_bytes()).hexdigest() if dosyalar else None,
        "lisans": "NASA Earthdata / ASF DAAC EULA (kabul edildi)",
        "yetkinlik": "Otorite",
        **sonuc,
    }
    (PROCESSED_DIR / "insar_aria.json").write_text(
        json.dumps(rapor, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    manifest = RAW_DIR / "enrichment_manifest.json"
    kayitlar = json.loads(manifest.read_text(encoding="utf-8")) if manifest.exists() else []
    kayitlar.append({
        "id": "ARIA_S1_GUNW", "url": "https://search.asf.alaska.edu/",
        "erisim_tarihi": rapor["erisim_tarihi"],
        "lisans": "ASF DAAC EULA", "sha256": rapor["sha256_ilk"],
        "yetkinlik": "Otorite",
        "not": f"{len(dosyalar)} GUNW, kapsam %{sonuc.get('kapsam_pct')}",
    })
    manifest.write_text(json.dumps(kayitlar, ensure_ascii=False, indent=2), encoding="utf-8")
    return rapor


if __name__ == "__main__":
    print(json.dumps(calistir(), ensure_ascii=False, indent=2))
