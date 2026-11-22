"""Resmî Gazete kaynaklı yasal kısıt kayıtları (Faz B).

K5: karar_no, tarih, URL ve erişim tarihi kayıtlıdır.
K3: jeoreferanslı sınır olmadığı için `geom = None`; asla proxy üretilmez.
"""
from __future__ import annotations

KARARLAR: list[dict[str, object]] = [
    {
        "karar_no": "11600",
        "karar_tarihi": "2026-08-10",
        "tur": "afete_maruz_bolge",
        "ilce": "Konyaaltı",
        "mahalle": "Hisarçandır, Üçoluk, Gökdere (belirli bölümleri)",
        "geom": None,
        "kaynak_url": "https://www.antalyakorfez.com/antalyada-3-mahalle-afet-bolgesi-ilan-edildi-yapilasma-kisitlandi",
        "konum_guveni": "yok",
        "aciklama": (
            "10 Ağustos 2026 tarihli 11600 sayılı Cumhurbaşkanı Kararı, 7269 sayılı "
            "Kanun. Sınırlar 10.11.2023 Jeolojik Etüt Raporu ile belirlenmiş; "
            "rapor kamuya açık değil. Mahalle bazlı geocode başarısız (ADR-0002). "
            "Bu yüzden VETO tetiklenmez, 'doğrulanamadı' üretilir."
        ),
    },
]


def yukle() -> int:
    from app.db import get_conn

    with get_conn() as conn, conn.cursor() as cur:
        for k in KARARLAR:
            cur.execute(
                """INSERT INTO legal_constraints
                       (karar_no, karar_tarihi, tur, ilce, mahalle, geom,
                        kaynak_url, konum_guveni, aciklama)
                       VALUES (%s,%s,%s,%s,%s,NULL,%s,%s,%s)
                       ON CONFLICT DO NOTHING""",
                (
                    k["karar_no"], k["karar_tarihi"], k["tur"], k["ilce"],
                    k["mahalle"], k["kaynak_url"], k["konum_guveni"], k["aciklama"],
                ),
            )
    return len(KARARLAR)


if __name__ == "__main__":
    print({"yuklenen_karar": yukle()})
