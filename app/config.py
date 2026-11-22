"""Merkezi yapilandirma. Tum yollar proje kokune gore cozulur."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
LABELS_DIR = DATA_DIR / "labels"
REPORTS_DIR = DATA_DIR / "reports"
TEMPLATES_DIR = ROOT / "templates"
FRONTEND_DIR = ROOT / "frontend"

for _d in (RAW_DIR, PROCESSED_DIR, LABELS_DIR, REPORTS_DIR):
    _d.mkdir(parents=True, exist_ok=True)

DATABASE_URL: str = os.getenv(
    "DATABASE_URL", "postgresql+psycopg://yrkds:yrkds@localhost:55432/yrkds"
)
GRID_RESOLUTION_M: float = float(os.getenv("GRID_RESOLUTION_M", "25"))

# min_lon, min_lat, max_lon, max_lat (WGS84 / EPSG:4326)
GRID_BBOX: tuple[float, float, float, float] = tuple(
    float(v) for v in os.getenv("GRID_BBOX", "30.58,36.82,30.86,37.00").split(",")
)  # type: ignore[assignment]

CDSAPI_KEY: str = os.getenv("CDSAPI_KEY", "")
COPERNICUS_CLIENT_ID: str = os.getenv("COPERNICUS_CLIENT_ID", "")

# Spesifikasyon 2.1: agirliklar toplami 1.0
AGIRLIKLAR: dict[str, float] = {
    "ZB": 0.25,
    "L": 0.20,
    "S": 0.25,
    "H": 0.15,
    "F": 0.15,
}

KARAR_BANTLARI: list[tuple[float, str, str]] = [
    (25.0, "Düşük", "Uygun — standart etüt yeterli"),
    (50.0, "Düşük-Orta", "Uygun — zemin etüdü + drenaj koşulu"),
    (70.0, "Orta-Yüksek", "Koşullu — detaylı etüt + temel önlemi"),
    (85.0, "Yüksek", "Alternatif parsel öner — iyileştirme maliyeti yüksek"),
    (100.0, "Kritik", "Uygun Değil"),
]

# veri_tamligi icin katman agirliklari. Toplam 1.0.
# Kilitli/erişilemeyen kaynaklar burada uygun sekilde dusuk agirlik alir;
# eksikse "var sayilmmaz" ve guven skoru dusurulur (sahte kesinlik yasak).
KATMAN_AGIRLIKLARI: dict[str, float] = {
    "dem": 0.15,
    "soil": 0.15,
    "jeoloji": 0.10,
    "mikrobölge_vs30": 0.15,
    "zemin_hareketi": 0.05,
    "fay": 0.10,
    "insar": 0.10,
    "taskin": 0.10,
    "sondaj": 0.05,
    "bina": 0.05,
}

KARARSIZ_ESIK = 0.40

# F4: 3.10 CMIP6 projeksiyonundan türetilen yağış değişimi çarpanları.
# S çarpanı yok: InSAR/oturma verisi olmadığı için nötr bırakılır (ADR-0010).
SENARYOLAR: dict[str, dict[str, object]] = {
    "bugun": {"etiket": "Bugün", "F": 1.0, "S": 1.0, "yagis_degisim_pct": 0},
    "ssp245_2050": {"etiket": "2050 · SSP2-4.5", "F": 1.15, "S": 1.0,
                    "yagis_degisim_pct": -15},
    "ssp585_2050": {"etiket": "2050 · SSP5-8.5", "F": 1.22, "S": 1.0,
                    "yagis_degisim_pct": -22},
}
