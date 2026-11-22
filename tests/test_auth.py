"""Kimlik doğrulama kapıları: roller, argon2id, CSRF, hız sınırı, denetim."""
from __future__ import annotations

import re

from fastapi.testclient import TestClient

from app import auth
from app.db import get_conn
from app.main import app

ADMIN_PAROLA = "GucluBirParola2026!"
ANALYST = "test_analyst_yrkds"


def _csrf(client: TestClient) -> str:
    r = client.get("/login")
    assert r.status_code == 200
    bul = re.search(r'name="csrf" value="([^"]+)"', r.text)
    assert bul, "CSRF token bulunamadı"
    return bul.group(1)


def _temizle() -> None:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM users WHERE username LIKE 'test\\_%'")
        cur.execute("DELETE FROM audit_log WHERE username LIKE 'test\\_%'")


def test_parola_ozeti_argon2id():
    ozet = auth.parola_olustur("BirCokUzunParola2026!")
    assert ozet.startswith("$argon2id$")
    assert auth.parola_dogrula(ozet, "BirCokUzunParola2026!")
    assert not auth.parola_dogrula(ozet, "yanlis")


def test_giris_hatasi_ve_csrf_ve_cerez_flags():
    _temizle()
    with TestClient(app, follow_redirects=False) as c:
        csrf = _csrf(c)
        r = c.post("/login", data={"username": "yok", "password": "BirCokUzunParola2026!", "csrf": csrf})
        assert r.status_code == 401
        assert "kullanıcı adı veya parola hatalı" in r.text.lower()
        r = c.post("/login", data={"username": "yok", "password": "BirCokUzunParola2026!"})
        assert r.status_code in (403, 422)  # CSRF alanı yok -> şema reddi

        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (username,password_hash,role,must_change_password) "
                "VALUES (%s,%s,'admin',FALSE)",
                ("test_admin_yrkds", auth.parola_olustur(ADMIN_PAROLA)),
            )
        csrf = _csrf(c)
        r = c.post("/login", data={"username": "test_admin_yrkds", "password": ADMIN_PAROLA, "csrf": csrf})
        assert r.status_code == 303
        baslik = r.headers.get("set-cookie", "")
        assert "yrkds_session=" in baslik
        assert "HttpOnly" in baslik
        assert "SameSite=strict" in baslik


def test_rol_yetkileri_ve_denetim():
    _temizle()
    with TestClient(app, follow_redirects=False) as c:
        assert c.get("/admin/users").status_code == 403  # anon
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (username,password_hash,role,must_change_password) "
                "VALUES (%s,%s,'admin',FALSE)",
                ("test_admin_yrkds", auth.parola_olustur(ADMIN_PAROLA)),
            )
        csrf = _csrf(c)
        assert c.post("/login", data={"username": "test_admin_yrkds", "password": ADMIN_PAROLA,
                                      "csrf": csrf}).status_code == 303
        csrf2 = c.get("/admin/users").text
        token = re.search(r'name="csrf" value="([^"]+)"', csrf2).group(1)
        r = c.post("/admin/users", data={"username": ANALYST,
                                         "password": "AnalistParola2026!", "csrf": token})
        assert r.status_code == 303
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT role FROM users WHERE username=%s", (ANALYST,))
            assert cur.fetchone()[0] == "analyst"
            cur.execute("SELECT count(*) FROM audit_log WHERE action='user_created'")
            assert cur.fetchone()[0] >= 1
        c.get("/logout")
        csrf = _csrf(c)
        c.post("/login", data={"username": ANALYST, "password": "AnalistParola2026!", "csrf": csrf})
        assert c.get("/admin/users").status_code == 403  # analist admin alanına giremez


def test_api_me_sorgu_gecmisi_ve_parola_degisimi():
    _temizle()
    with TestClient(app, follow_redirects=False) as c:
        assert c.get("/api/me").status_code == 401
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (username,password_hash,role,must_change_password) "
                "VALUES (%s,%s,'analyst',TRUE)",
                ("test_me_yrkds", auth.parola_olustur(ADMIN_PAROLA)),
            )
        csrf = _csrf(c)
        c.post("/login", data={"username": "test_me_yrkds", "password": ADMIN_PAROLA, "csrf": csrf})
        assert c.get("/api/me").json()["role"] == "analyst"
        assert isinstance(c.get("/api/queries/me").json(), list)
        assert c.get("/api/query/999999.geojson").status_code == 404
        profil = c.get("/profile")
        token = re.search(r'name="csrf" value="([^"]+)"', profil.text).group(1)
        r = c.post("/profile/password", data={"old": ADMIN_PAROLA,
                                              "new": "YeniGucluParola2026!", "csrf": token})
        assert r.status_code == 303
        assert c.get("/admin/audit").status_code == 403  # analist
    _temizle()


def test_giris_hiz_siniri_429():
    from collections import deque

    import app.auth as auth_mod

    auth_mod._denemeler["testclient"] = deque()
    with TestClient(app, follow_redirects=False) as c:
        csrf = _csrf(c)
        for _ in range(5):
            c.post("/login", data={"username": "yok", "password": "BirCokUzunParola2026!", "csrf": csrf})
        r = c.post("/login", data={"username": "yok", "password": "BirCokUzunParola2026!", "csrf": csrf})
        assert r.status_code == 429
        assert "saniye" in r.text
    auth_mod._denemeler["testclient"] = deque()
