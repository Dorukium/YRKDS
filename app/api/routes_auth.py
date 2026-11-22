"""Kimlik sayfaları: /login, /logout, /profile, /admin/* (Faz: kimlik)."""
from __future__ import annotations

import os
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates

from app import auth
from app.config import TEMPLATES_DIR
from app.db import get_conn

router = APIRouter()
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
SECURE = os.getenv("COOKIE_SECURE", "true").lower() == "true"


def _cookie(response: Response, session: dict[str, Any]) -> None:
    response.set_cookie(
        auth.COOKIE, auth.cerez_deger(session), httponly=True,
        samesite="strict", secure=SECURE, max_age=auth.OTURUM_DK * 60, path="/",
    )


def _ip(request: Request) -> str:
    return request.client.host if request.client else "bilinmiyor"


def _oturum_veya_csrf(request: Request) -> tuple[dict[str, Any] | None, str]:
    oturum = auth.oturum_oku(request)
    if oturum:
        return (oturum if oturum.get("u") else None), oturum["csrf"]
    yeni = auth.oturum_olustur("", "anonim")
    return None, yeni["csrf"]


def _kullanici_listesi() -> list[dict[str, Any]]:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT username, role, last_login, must_change_password FROM users ORDER BY id"
        )
        satirlar = cur.fetchall()
    return [
        dict(zip(["username", "role", "last_login", "must_change_password"], s))
        for s in satirlar
    ]


def _kullanici(username: str) -> dict[str, Any] | None:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT username, role, last_login, must_change_password FROM users WHERE username=%s",
            (username,),
        )
        s = cur.fetchone()
    if not s:
        return None
    return dict(zip(["username", "role", "last_login", "must_change_password"], s))


@router.get("/login", response_class=HTMLResponse)
def login_sayfasi(request: Request) -> Response:
    oturum, csrf = _oturum_veya_csrf(request)
    if oturum:
        return RedirectResponse("/profile", status_code=303)
    yanit = templates.TemplateResponse(
        request, "login.html", {"csrf": csrf, "oturum": None, "hata": None}
    )
    if not request.cookies.get(auth.COOKIE):
        _cookie(yanit, auth.oturum_olustur("", "anonim", csrf))
    return yanit


@router.post("/login", response_class=HTMLResponse)
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    csrf: str = Form(...),
) -> Response:
    oturum = auth.oturum_oku(request)
    ip = _ip(request)
    asildi, kalan = auth.giris_siniri_asildi_mi(ip)
    if asildi:
        auth.denetim(None, "login_rate_limited", ip)
        return templates.TemplateResponse(
            request, "login.html",
            {"csrf": oturum.get("csrf") if oturum else "", "oturum": None,
             "hata": "Çok fazla başarısız deneme.", "kalan_saniye": kalan},
            status_code=429,
        )
    if not auth.csrf_dogrula(request, oturum, csrf):
        raise HTTPException(403, "CSRF doğrulaması başarısız")
    auth.giris_denemesi_ekle(ip)
    k = auth.kullanici_getir(username.strip())
    if not k or not auth.parola_dogrula(k["password_hash"], password):
        auth.denetim(username if k else None, "login_failed", ip)
        return templates.TemplateResponse(
            request, "login.html",
            {"csrf": oturum.get("csrf") if oturum else "", "oturum": None,
             "hata": "Kullanıcı adı veya parola hatalı", "kalan_saniye": None},
            status_code=401,
        )
    yeni = auth.oturum_olustur(k["username"], k["role"], oturum.get("csrf") if oturum else None)
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("UPDATE users SET last_login=%s WHERE username=%s", (datetime.now(UTC), k["username"]))
    auth.denetim(k["username"], "login_success", ip)
    hedef = "/profile?degistir=1" if k["must_change_password"] else "/"
    yanit = RedirectResponse(hedef, status_code=303)
    _cookie(yanit, yeni)
    return yanit


@router.get("/api/me")
def api_me(request: Request) -> dict[str, Any]:
    oturum = auth.oturum_oku(request)
    if not oturum or not oturum.get("u"):
        raise HTTPException(401, "Oturum gerekli")
    return {"username": oturum["u"], "role": oturum.get("r")}


@router.get("/api/queries/me")
def api_queries_me(request: Request) -> list[dict[str, Any]]:
    oturum = _gerekli_oturum(request)
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT id, query_time, parsel_id, skor, bant,
                      ST_AsGeoJSON(geom) AS geojson
               FROM parcel_queries WHERE username=%s ORDER BY id DESC LIMIT 200""",
            (oturum["u"],),
        )
        satirlar = cur.fetchall()
    return [
        {
            "sonuc_id": s[0],
            "tarih": str(s[1])[:19],
            "parsel": s[2],
            "skor": float(s[3]) if s[3] is not None else None,
            "bant": s[4],
            "ilce": None,
        }
        for s in satirlar
    ]


@router.get("/api/query/{query_id}.geojson")
def api_query_geojson(query_id: int, request: Request) -> dict[str, Any]:
    oturum = _gerekli_oturum(request)
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT parsel_id, skor, bant, ST_AsGeoJSON(geom)::json
               FROM parcel_queries WHERE id=%s AND username=%s""",
            (query_id, oturum["u"]),
        )
        satir = cur.fetchone()
    if not satir:
        raise HTTPException(404, "Sorgu bulunamadı")
    return {
        "type": "Feature",
        "geometry": satir[3],
        "properties": {"parsel_id": satir[0], "skor": satir[1], "bant": satir[2]},
    }


@router.get("/logout")
def logout(request: Request) -> Response:
    oturum = auth.oturum_oku(request)
    if oturum and oturum.get("u"):
        auth.denetim(oturum["u"], "logout", _ip(request))
    yanit = RedirectResponse("/", status_code=303)
    yanit.delete_cookie(auth.COOKIE, path="/")
    return yanit


def _gerekli_oturum(request: Request, rol: str | None = None) -> dict[str, Any]:
    oturum = auth.oturum_oku(request)
    if not oturum or not oturum.get("u"):
        raise HTTPException(403 if rol else 401, "Bu alan için oturum/gerekli yetki yok")
    if rol and oturum.get("r") != rol:
        raise HTTPException(403, "Bu işlem için yetki yok")
    return oturum


@router.get("/profile", response_class=HTMLResponse)
def profil(request: Request) -> Response:
    oturum = _gerekli_oturum(request)
    k = _kullanici(oturum["u"])
    if not k:
        raise HTTPException(401, "Kullanıcı yok")
    return templates.TemplateResponse(
        request, "profile.html",
        {"oturum": oturum, "csrf": oturum["csrf"], "kullanici": k,
         "bilgi": "Güvenlik için ilk girişte parolanızı değiştirin." if k["must_change_password"] else None},
    )


@router.post("/profile/password")
def parola_degistir(
    request: Request, old: str = Form(...), new: str = Form(...), csrf: str = Form(...)
) -> Response:
    oturum = _gerekli_oturum(request)
    if not auth.csrf_dogrula(request, oturum, csrf):
        raise HTTPException(403, "CSRF doğrulaması başarısız")
    k = auth.kullanici_getir(oturum["u"])
    if not k or not auth.parola_dogrula(k["password_hash"], old):
        auth.denetim(oturum["u"], "password_change_failed", _ip(request))
        raise HTTPException(401, "Mevcut parola hatalı")
    try:
        ozet = auth.parola_olustur(new)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "UPDATE users SET password_hash=%s, must_change_password=FALSE WHERE username=%s",
            (ozet, oturum["u"]),
        )
    auth.denetim(oturum["u"], "password_changed", _ip(request))
    return RedirectResponse("/profile?bilgi=parola_guncellendi", status_code=303)


@router.get("/admin/users", response_class=HTMLResponse)
def admin_kullanicilar(request: Request) -> Response:
    oturum = _gerekli_oturum(request, "admin")
    return templates.TemplateResponse(
        request, "admin_users.html",
        {"oturum": oturum, "csrf": oturum["csrf"], "kullanicilar": _kullanici_listesi()},
    )


@router.post("/admin/users")
def admin_kullanici_olustur(
    request: Request, username: str = Form(...), password: str = Form(...), csrf: str = Form(...)
) -> Response:
    oturum = _gerekli_oturum(request, "admin")
    if not auth.csrf_dogrula(request, oturum, csrf):
        raise HTTPException(403, "CSRF doğrulaması başarısız")
    try:
        ozet = auth.parola_olustur(password)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """INSERT INTO users (username, password_hash, role, must_change_password)
               VALUES (%s,%s,'analyst',TRUE) ON CONFLICT (username) DO NOTHING""",
            (username.strip(), ozet),
        )
    auth.denetim(oturum["u"], "user_created", _ip(request), {"username": username})
    return RedirectResponse("/admin/users", status_code=303)


@router.get("/admin/audit")
def admin_denetim(request: Request) -> list[dict[str, Any]]:
    _gerekli_oturum(request, "admin")
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT ts, username, action, ip FROM audit_log ORDER BY ts DESC LIMIT 200")
        satirlar = cur.fetchall()
    return [
        dict(zip(["ts", "username", "action", "ip"], s)) for s in satirlar
    ]
