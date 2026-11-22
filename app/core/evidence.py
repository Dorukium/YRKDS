"""Kanıt zinciri — U7: her kanıt yetkinlik rozeti taşır."""
from __future__ import annotations

from app.core.provenance import rozet
from app.core.scoring import vs30_etkin
from app.models.schemas import EvidenceItem, SkorInput

KAYNAKLAR = {
    "dem": "AWS Terrarium (SRTM-derived)",
    "soil": "SoilGrids v2 WCS 250 m",
    "jeoloji": "MTA 1:25.000 (proje veri seti)",
    "mikrobölge": "TBDY2018 + belediye etütleri (proje veri seti)",
    "fay": "MTA diri fay (proje veri seti)",
    "insar": "COMET LiCSAR / EGMS (erişilemedi)",
    "taskin": "DEM TWI/HAND + OSM akarsu + DSİ kayıtları",
    "sondaj": "SK-01 / SK-02 / SK-03 (ilçe profili)",
    "olay": "AFAD / KOERI / MGM (proje veri seti)",
}


def kanit_olustur(girdi: SkorInput, ek: dict[str, str] | None = None) -> list[EvidenceItem]:
    out: list[EvidenceItem] = []
    ek = ek or {}

    if girdi.egim is not None or girdi.twi is not None:
        out.append(EvidenceItem(
            katman="DEM", kaynak=ek.get("dem", KAYNAKLAR["dem"]),
            deger="Eğim {}, TWI {}".format(
                f"{girdi.egim:.1f}°" if girdi.egim is not None else "yok",
                f"{girdi.twi:.1f}" if girdi.twi is not None else "yok",
            ),
            yetkinlik=rozet("dem"),
        ))
    else:
        out.append(EvidenceItem(katman="DEM", kaynak=KAYNAKLAR["dem"],
                                deger="Bilinmiyor — veri yok", guven="eksik",
                                yetkinlik=rozet("dem")))

    if girdi.kum_orani is not None:
        out.append(EvidenceItem(
            katman="Toprak", kaynak=KAYNAKLAR["soil"],
            deger="Kum %{:.1f}, organik {}".format(
                girdi.kum_orani,
                "var" if girdi.organik else ("yok" if girdi.organik is False else "veri yok"),
            ),
            guven="turetilmis" if ek.get("soil_interpolated") else "kaynakli",
            yetkinlik=rozet("toprak"),
        ))

    if girdi.vs30 is not None or girdi.zemin_sinifi is not None:
        vs30, kaynak_tur = vs30_etkin(girdi)
        out.append(EvidenceItem(
            katman="Mikrobölge", kaynak=KAYNAKLAR["mikrobölge"],
            deger=f"{girdi.zemin_sinifi or 'sınıf yok'}, Vs30 {vs30:g} m/s",
            guven="kaynakli" if kaynak_tur == "dogrudan" else "turetilmis",
            yetkinlik=rozet("vs30"),
        ))

    if girdi.fay_mesafe_km is not None:
        out.append(EvidenceItem(
            katman="Diri fay", kaynak=KAYNAKLAR["fay"],
            deger=f"Fay mesafesi {girdi.fay_mesafe_km:g} km",
            yetkinlik=rozet("jeoloji"),
        ))

    out.append(EvidenceItem(
        katman="InSAR", kaynak=KAYNAKLAR["insar"],
        deger=(f"Deformasyon {girdi.insar_hiz:g} mm/yıl" if girdi.insar_hiz is not None
               else "Bilinmiyor — veri yok"),
        guven="kaynakli" if girdi.insar_hiz is not None else "eksik",
        yetkinlik=rozet("insar"),
    ))

    if any(v is not None for v in (girdi.taskin_100y, girdi.taskin_500y,
                                   girdi.akarsu_mesafe_m, girdi.twi)):
        details = []
        if girdi.taskin_100y is not None:
            details.append(f"100 yıllık={girdi.taskin_100y}")
        if girdi.taskin_500y is not None:
            details.append(f"500 yıllık={girdi.taskin_500y}")
        if girdi.akarsu_mesafe_m is not None:
            details.append(f"akarsu {girdi.akarsu_mesafe_m:g} m")
        out.append(EvidenceItem(katman="Taşkın", kaynak=KAYNAKLAR["taskin"],
                                deger=", ".join(details), yetkinlik=rozet("taskin")))

    if girdi.yass_m is not None:
        out.append(EvidenceItem(
            katman="Sondaj / YASS", kaynak=KAYNAKLAR["sondaj"],
            deger=f"Yeraltı su seviyesi {girdi.yass_m:g} m",
            guven="turetilmis", yetkinlik=rozet("jeoloji"),
        ))

    if girdi.gecmis_taskin_sayisi:
        out.append(EvidenceItem(
            katman="Geçmiş olay", kaynak=KAYNAKLAR["olay"],
            deger=f"Kayıtlı taşkın olayı: {girdi.gecmis_taskin_sayisi}",
            yetkinlik="Otorite",
        ))

    return out
