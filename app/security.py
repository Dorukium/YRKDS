"""Üretim güvenliği: başlıklar, hız sınırı, isteğe bağlı API anahtarı."""
from __future__ import annotations

import logging
import os
import time
from collections import defaultdict, deque
from collections.abc import Awaitable, Callable
from threading import Lock

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

API_KEY = os.getenv("YRKDS_API_KEY", "")
RATE_LIMIT = int(os.getenv("YRKDS_RATE_LIMIT", "30"))
REDIS_URL = os.getenv("REDIS_URL", "")
_redis_client = None
if REDIS_URL:
    try:
        import redis

        _redis_client = redis.Redis.from_url(REDIS_URL, socket_timeout=1)
    except Exception:
        _redis_client = None
_pencere: dict[str, deque[float]] = defaultdict(deque)
_kilit = Lock()
CallNext = Callable[[Request], Awaitable[Response]]


class GuvenlikBasliklari(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: CallNext) -> Response:
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self' https://unpkg.com "
            "https://cdn.jsdelivr.net https://cdnjs.cloudflare.com 'unsafe-inline'; "
            "style-src 'self' https://unpkg.com https://cdn.jsdelivr.net "
            "https://cdnjs.cloudflare.com 'unsafe-inline'; img-src 'self' data: https:; "
            "connect-src 'self' https://tile.openstreetmap.org https://server.arcgisonline.com",
        )
        return response


class HizSiniri(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: CallNext) -> Response:
        if not request.url.path.startswith("/api/"):
            return await call_next(request)
        ip = request.client.host if request.client else "bilinmiyor"
        if _redis_client is not None:
            try:
                anahtar = f"yrkds:rate:{ip}"
                sayi = _redis_client.incr(anahtar)
                if sayi == 1:
                    _redis_client.expire(anahtar, 60)
                if sayi > RATE_LIMIT:
                    return JSONResponse(
                        {"hata": "Çok fazla istek; lütfen bir dakika sonra tekrar deneyin"},
                        status_code=429, headers={"Retry-After": "60"},
                    )
            except Exception as exc:  # Redis down -> yerel sayaç
                logging.getLogger("yrkds.security").warning("Redis hız sınırı hatası: %s", exc)
        else:
            simdi = time.monotonic()
            with _kilit:
                kuyruk = _pencere[ip]
                while kuyruk and simdi - kuyruk[0] > 60:
                    kuyruk.popleft()
                if len(kuyruk) >= RATE_LIMIT:
                    return JSONResponse(
                        {"hata": "Çok fazla istek; lütfen bir dakika sonra tekrar deneyin"},
                        status_code=429, headers={"Retry-After": "60"},
                    )
                kuyruk.append(simdi)
        return await call_next(request)


class ApiAnahtari(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: CallNext) -> Response:
        if not API_KEY or not request.url.path.startswith("/api/"):
            return await call_next(request)
        if request.url.path.endswith("/saglik") or request.url.path == "/health":
            return await call_next(request)
        if request.headers.get("X-API-Key") != API_KEY:
            return JSONResponse({"hata": "Geçersiz veya eksik API anahtarı"}, status_code=401)
        return await call_next(request)
