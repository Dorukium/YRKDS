"""Kimlik doğrulama: argon2id, imzalı oturum çerezi, CSRF, roller, denetim.

U6: yalnızca kullanıcı adı + parola özeti + rol + son giriş saklanır.
"""
from __future__ import annotations

import os
from collections import defaultdict, deque
from datetime import UTC, datetime, timedelta
from typing import Any

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import Request
from itsdangerous import BadSignature, URLSafeSerializer

from app.db import get_conn

PH = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=4, hash_len=32, salt_len=16)
SECRET = os.getenv("YRKDS_SECRET", "yrkds-dev-secret-change-me-in-production")
SERIALIZER = URLSafeSerializer(SECRET, salt="yrkds-session")
COOKIE = "yrkds_session"
OTURUM_DK = 30
GIRIS_LIMIT = 5
GIRIS_PENCERE_DK = 15
_denemeler: dict[str, deque[float]] = defaultdict(deque)


def parola_olustur(parola: str) -> str:
    if len(parola) < 12:
        raise ValueError("Parola en az 12 karakter olmalı")
    return PH.hash(parola)


def parola_dogrula(ozet: str, parola: str) -> bool:
    try:
        return PH.verify(ozet, parola)
    except VerifyMismatchError:
        return False


def _yeni_csrf() -> str:
    import secrets

    return secrets.token_urlsafe(32)


def oturum_olustur(username: str, role: str, csrf: str | None = None) -> dict[str, Any]:
    simdi = datetime.now(UTC)
    return {
        "u": username,
        "r": role,
        "csrf": csrf or _yeni_csrf(),
        "son": simdi.isoformat(),
    }


def cerez_deger(session: dict[str, Any]) -> str:
    return SERIALIZER.dumps(session)


def oturum_oku(request: Request) -> dict[str, Any] | None:
    ham = request.cookies.get(COOKIE)
    if not ham:
        return None
    try:
        veri: dict[str, Any] = SERIALIZER.loads(ham)
    except BadSignature:
        return None
    try:
        son = datetime.fromisoformat(veri["son"])
    except (KeyError, ValueError):
        return None
    if datetime.now(UTC) - son > timedelta(minutes=OTURUM_DK):
        return None
    return veri


def csrf_dogrula(request: Request, session: dict[str, Any] | None, verilen: str | None) -> bool:
    if session is None or not verilen:
        return False
    return verilen == session.get("csrf")


def giris_siniri_asildi_mi(ip: str) -> tuple[bool, int]:
    import time

    simdi = time.monotonic()
    kuyruk = _denemeler[ip]
    while kuyruk and simdi - kuyruk[0] > GIRIS_PENCERE_DK * 60:
        kuyruk.popleft()
    if len(kuyruk) >= GIRIS_LIMIT:
        kalan = int(GIRIS_PENCERE_DK * 60 - (simdi - kuyruk[0]))
        return True, max(0, kalan)
    return False, 0


def giris_denemesi_ekle(ip: str) -> None:
    import time

    _denemeler[ip].append(time.monotonic())


def denetim(username: str | None, action: str, ip: str, detail: dict[str, Any] | None = None) -> None:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO audit_log (username, action, ip, detail) VALUES (%s,%s,%s,%s)",
            (username, action, ip, __import__("json").dumps(detail or {})),
        )


def kullanici_getir(username: str) -> dict[str, Any] | None:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT username, password_hash, role, must_change_password FROM users WHERE username=%s",
            (username,),
        )
        satir = cur.fetchone()
    if not satir:
        return None
    return dict(zip(["username", "password_hash", "role", "must_change_password"], satir))


def bootstrap_admin() -> None:
    ad = os.getenv("YRKDS_ADMIN_USER", "admin")
    parola = os.getenv("YRKDS_ADMIN_PASSWORD", "")
    if not parola or kullanici_getir(ad):
        return
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """INSERT INTO users (username, password_hash, role, must_change_password)
               VALUES (%s,%s,'admin',TRUE) ON CONFLICT DO NOTHING""",
            (ad, parola_olustur(parola)),
        )
