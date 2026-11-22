"""Test ortamı: yerel HTTP üzerinde güvenli çerez kullanılmaz (production'da true)."""
import os

os.environ.setdefault("COOKIE_SECURE", "false")
os.environ.setdefault("YRKDS_ADMIN_PASSWORD", "GucluBirParola2026!")
