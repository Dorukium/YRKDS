"""U7: her katmanın yetkinlik rozeti, kapsamı ve güncelleme tarihi.

Rozetler: Otorite | Proxy | Tahmin | Araştırma | Eksik.
Bu bilgi katalogda ve kanıt zincirinde aynı kaynaktan gelir (tek doğruluk).
"""
from __future__ import annotations

from app.config import RAW_DIR

KATMANLAR: dict[str, dict[str, object]] = {
    "dem": {
        "ad": "DEM / eğim / TWI / HAND",
        "kaynak": "AWS Terrarium (SRTM-derived), zoom 13",
        "yetkinlik": "Proxy",
        "kapsam_pct": 100.0,
        "guncelleme": "2026-11-22",
        "lisans": "public",
        "not": "Copernicus GLO-30 yerine SRTM türevli; ADR-0001.",
    },
    "toprak": {
        "ad": "Toprak (clay/silt/sand/soc/pH)",
        "kaynak": "SoilGrids v2 WCS 250 m",
        "yetkinlik": "Otorite",
        "kapsam_pct": 100.0,
        "guncelleme": "2026-11-22",
        "lisans": "CC BY 4.0",
        "not": "WCS GetCoverage; REST nokta interpolasyonu kaldırıldı.",
    },
    "bina": {
        "ad": "Bina ayak izleri",
        "kaynak": "OpenStreetMap Overpass",
        "yetkinlik": "Otorite",
        "kapsam_pct": 100.0,
        "guncelleme": "2026-11-22",
        "lisans": "ODbL",
        "not": "68.810 geometri.",
    },
    "jeoloji": {
        "ad": "Jeoloji / karst / fay mesafesi",
        "kaynak": "MTA (proje veri seti, ilçe düzeyi)",
        "yetkinlik": "Tahmin",
        "kapsam_pct": 100.0,
        "guncelleme": "2026-11-22",
        "lisans": "proje veri seti",
        "not": "İlçe sabiti; parsel bazlı ölçüm değil.",
    },
    "vs30": {
        "ad": "Vs30 / zemin sınıfı",
        "kaynak": "TBDY2018 + belediye etütleri (ilçe düzeyi)",
        "yetkinlik": "Tahmin",
        "kapsam_pct": 100.0,
        "guncelleme": "2026-11-22",
        "lisans": "proje veri seti",
        "not": "USGS Vs30 nokta sorgusu başarısız (ADR-0005).",
    },
    "pga": {
        "ad": "PGA (475 yıl)",
        "kaynak": "Proje TDTH ilçe değerleri",
        "yetkinlik": "Eksik",
        "kapsam_pct": 0.0,
        "guncelleme": "2026-11-22",
        "lisans": "proje veri seti",
        "not": "Hücre bazlı resmi grid yok; GEM yalnızca Araştırma rozetli.",
    },
    "pga_gem": {
        "ad": "GEM PGA çapraz kontrol",
        "kaynak": "GEM GSHM v2023.1 (Zenodo)",
        "yetkinlik": "Araştırma",
        "kapsam_pct": 69.5,
        "guncelleme": "2026-11-22",
        "lisans": "CC BY-NC-SA 4.0",
        "not": "Kaya Vs30=800; resmi TDTH yerine geçmez (ADR-0008).",
    },
    "insar": {
        "ad": "InSAR deformasyon hızı",
        "kaynak": "COMET LiCSAR / Copernicus EGMS",
        "yetkinlik": "Eksik",
        "kapsam_pct": 0.0,
        "guncelleme": "2026-11-22",
        "lisans": "—",
        "not": "Hesap/Kimlik yok; S bileşeni NULL (ADR-0009).",
    },
    "taskin": {
        "ad": "Taşkın tehlikesi",
        "kaynak": "DEM TWI/HAND + OSM akarsu + kayıtlı olay",
        "yetkinlik": "Proxy",
        "kapsam_pct": 100.0,
        "guncelleme": "2026-11-22",
        "lisans": "türev",
        "not": "SYGM 100/500 yıllık pafta erişilemedi.",
    },
    "yasal": {
        "ad": "Yasal VETO katmanları",
        "kaynak": "Resmî Gazete 11600 sayılı karar",
        "yetkinlik": "Eksik",
        "kapsam_pct": 0.0,
        "guncelleme": "2026-11-22",
        "lisans": "kamuya açık",
        "not": "Karar kayıtlı; jeoreferanslı geometri yok (ADR-0002).",
    },
    "kiyi": {
        "ad": "Kıyı maruziyeti (<2m / <5m)",
        "kaynak": "DEM + IPCC AR6 DSH aralığı",
        "yetkinlik": "Tahmin",
        "kapsam_pct": 100.0,
        "guncelleme": "2026-11-22",
        "lisans": "türev",
        "not": "Danışmanlık göstergesi; yasal dayanak değil.",
    },
}


def katalog() -> list[dict[str, object]]:
    sonuc: list[dict[str, object]] = []
    for anahtar, k in KATMANLAR.items():
        satir = {"id": anahtar, **k}
        dosya = RAW_DIR / f"{anahtar}_kaynak.json"
        if dosya.exists():
            satir["manifest"] = f"/data/raw/{anahtar}_kaynak.json"
        sonuc.append(satir)
    return sonuc


def rozet(anahtar: str) -> str:
    return str(KATMANLAR.get(anahtar, {}).get("yetkinlik", "Eksik"))
