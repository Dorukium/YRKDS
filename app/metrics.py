"""Prometheus metrikleri (Faz F)."""
from __future__ import annotations

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

ISTEK_SAYISI = Counter("yrkds_requests_total", "Toplam HTTP isteği", ["method", "path", "status"])
GECIKME = Histogram(
    "yrkds_request_duration_seconds", "İstek süresi (saniye)", ["method", "path"]
)


def metrikleri_uretip() -> tuple[bytes, str]:
    return generate_latest(), CONTENT_TYPE_LATEST
