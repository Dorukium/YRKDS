"""Proje veri seti (kullanici tarafindan saglandi) -- ham kayitlar.

KIRMIZI CIZGI: Bu veriler "dogrulanmis resmi veri" olarak sunulmaz. Kaynak
etiketi daima "Proje veri seti (kullanici tarafindan saglandi)"dir. Ham icerik
oldugu gibi decode edilir; ustunde hicbir sayisal degisiklik yapilmaz.

AVC-1999-xxx kayitlari Istanbul Avcilar'a aittir (40.98, 28.72) ve bu
modulden hicbir ciktiya giremez.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
from datetime import UTC, datetime
from pathlib import Path

from app.config import RAW_DIR

KAYNAK_ETIKETI = "Proje veri seti (kullanici tarafindan saglandi)"
YASAKLI_PREFIX = "AVC-"

ILCE_TEMEL = """ilce,nufus_2025,alan_km2,yogunluk
Kepez,649102,292,2223
Muratpasa,510887,96,5322
Konyaalti,199414,546,365
"""

DEPREM_TEHLIKESI = """ilce,fay,merkezde_fay,zemin,zemin_buyutme,risk_skoru
Kepez,Fethiye-Burdur + Aksu,false,traverten,dusuk,2
Muratpasa,Fethiye-Burdur + Helen-Kibris,false,traverten + yogun yapi,orta,3
Konyaalti,Helen-Kibris + Aksu,false,aluvyon + sahil,yuksek,3
"""

DEPREM_KATALOGU = """tarih,yer,mw,derinlik_km,kaynak,antalya_etkisi,not
0068,Myra-Kas-Kumluca,-,-,Tarihsel,Tsunami,MS 68 Misir depremi sonrasi tsunami Patara-Myra'yi vurdu
0529,Demre-Myra,-,-,Tarihsel,Yikim,Demre-Myra bolgesi buyuk felaket
1911,Antalya Merkez,6.1,-,Tarihsel,Yivli Minare yikildi,Yivli Minare serefeden yikildi
1914-10-03,Burdur,7.0,-,AFAD-Kandilli,Antalya'da hissedildi,4000 olum 17000 bina yikildi
1926-03-18,Finike,6.9,-,Tarihsel,Antalya'da hissedildi,27 olum
1931,Antalya Merkez,6.2,-,Tarihsel,Yikim,Merkez ussu Antalya
1957-04-24,Fethiye,7.1,35,USGS,Antalya'da hissedildi,25 sn surdu
1957-04-25,Fethiye,7.3,35,USGS,Antalya-Kas-Finike'de hissedildi,60 sn surdu 19-67 olum
2025-12-08,Konyaalti-Yarbascandir,4.3,20.75,AFAD,Konyaalti'nda hissedildi,Olumsuz durum yok
2025-12-08,Serik,4.9,28.25,AFAD,Tum Antalya'da hissedildi,Kandilli 5.2 olctu
2025-12-08,Kemer Aciklari,3.6,16.93,AFAD,Hafif hissedildi,Ayni gun 3. deprem
2026-10-21,Aksu,2.8,7.0,AFAD,Hafif hissedildi,Olumsuz durum yok
2026-11-16,Ucoluk-Konyaalti,1.5,-,AFAD,Cok hafif,Mikro deprem
"""

JEOLOJI = """ilce,jeoloji_birimi,yas,zemin_tipi,buyutme,karst_obruk_riski,fay_mesafe_km,heyelan_duyarlilik,heyelan_mahalle,kaya_dusmesi
Kepez,Kepez Traverteni + Oymapinar Kirectasi,Miyosen,traverten_plato,dusuk,var,85,dusuk,yok,yok
Muratpasa,Antalya Traverten Platosu,Kuvaterner,traverten + falez,dusuk-orta,var,90,dusuk,falez kenari,sinirli
Konyaalti,Aluvyon + Bogacay Aluvyonu + Beydaglari Kirectasi,Kuvaterner+Mesozoyik,aluvyon+sahil+yamac,yuksek,yok,35,yuksek,Hisarcandir-Ucoluk-Gokdere,var
"""

TOPRAK = """ilce,toprak_tipi,ana_kaya,ph,drenaj,yeralti_su,oturma_riski,sivilasma_riski
Kepez,Terra Rossa + Rendzina,Kirectasi+Traverten,7.5-8.0,iyi-karstik,derin 20m+,dusuk-tufa cokmesi,dusuk
Muratpasa,Terra Rossa + Tufa,Traverten-Antalya Tufasi,7.5-8.2,orta-bosluklu,10-15m,orta,dusuk
Konyaalti,Aluvyal + Lagun + Kahverengi Orman,Aluvyon-Kil-Kum,7.0-7.8,kotu-su tutar,sig 1-3m,yuksek 20-80m kil,yuksek Bogacay/Lara kanitli
"""

MIKROBOLGELEME = """ilce,mahalle,zemin_sinifi,vs30_ms,buyutme,sivilasma,heyelan,oturma,onerilen_temel,kat_siniri
Kepez,Masa Dagi,ZB,700-760,1.0-1.2,yok,yok,dusuk,tekil temel,8
Kepez,Varsak,ZC,400-600,1.2-1.4,dusuk,dusuk,dusuk,radye,6
Muratpasa,Falez-Lara,ZC,450-600,1.2-1.5,dusuk,sinirli,orta,radye+drenaj,5
Muratpasa,Lara-Kundu,ZD,250-350,1.5-1.8,yuksek,yok,yuksek,kazik+iyilestirme,4
Konyaalti,Sahil-Liman,ZD-ZE,180-300,1.8-2.5,yuksek,yok,yuksek,kazik+derin,3
Konyaalti,Hisarcandir-Ucoluk,ZC-ZD,300-450,1.4-1.8,dusuk,yuksek(1965 Afete Maruz),orta,fore kazik+istinat,2(imara kapali onerisi)
Konyaalti,Gokdere-Bogacay,ZE,150-250,2.0-2.8,cok yuksek,dusuk,yuksek lagun,kazik+zemin iyilestirme,imara acilmamali
"""

SONDAJ = """sondaj_no,ilce,mahalle,derinlik_m,katman,kalinlik_m,zemin_tanimi,SPT_N,Vs_ms,su_m,not
SK-01,Konyaalti,Bogacay,0-3.5,Ust Kabuk,3.5,kahverengi kil CH,10,220,1.5,kabuk sert
SK-01,Konyaalti,Bogacay,3.5-25,Lagun Camuru,21.5,mavi-gri yumusak siltli kil CH-MH,6,150,1.5,cu=0.3 cok dusuk
SK-01,Konyaalti,Bogacay,25-30,Turba+Kum,5,siyah turba+kumlu bant,8,180,1.5,sivilasma var
SK-01,Konyaalti,Bogacay,30-35,Ana Kaya,5+,kirectasi,50+,650,-,saglam
SK-02,Muratpasa,Lara,0-5,Tufa Kabuk,5,beyaz-sari traverten tufa,25,550,8,bosluklu
SK-02,Muratpasa,Lara,5-15,Tufa,10,bosluklu tufa cokme riski,15,400,8,islaninca cokme
SK-02,Muratpasa,Lara,15-20,Aluvyon Kum,5,kum sivilasma sinirli,20,300,8,dikkat
SK-03,Kepez,Masa Dagi,0-2,Toprak,2,kirmizi terra rossa,20,350,20+,kuru
SK-03,Kepez,Masa Dagi,2-15,Traverten,13,saglam traverten,40+,700,20+,en saglam
SK-03,Kepez,Masa Dagi,15-20,Kirectasi,5+,masif kirectasi,50+,760,-,kaya
"""

IKLIM_NORMALLERI = """ay,ort_sicaklik_C,aylik_yagis_mm,yagisli_gun
Ocak,9.8,210.6,12.6
Subat,10.8,112.7,10.8
Mart,13.1,94.5,9.6
Nisan,16.4,63.1,8.4
Mayis,20.9,37.0,7.1
Haziran,25.7,10.1,3.3
Temmuz,28.9,4.0,1.2
Agustos,29.0,5.0,0.7
Eylul,25.6,22.0,2.6
Ekim,20.9,76.6,6.2
Kasim,15.3,152.1,8.5
Aralik,11.4,271.7,12.4
Yillik,19.0,1059.4,83.5
"""

ISTASYON_MIKROKLIMA = """istasyon,ilce,rakim_m,ort_sicaklik_C,yillik_yagis_mm,not
Antalya Bolge Md,Muratpasa,51,18.9,1059,Referans 1930'dan beri
Antalya Havalimani,Aksu-Muratpasa,54,19.5,980,+0.6C beton etkisi
Konyaalti Sahil,Konyaalti,5,19.8,950,Nem %75+
Kepez Merkez,Kepez,120,18.2,1080,Gece 2-3C serin
Hisarcandir,Konyaalti dag,1050,12.5,1350,-7C kar yagar
Aksu Ova,Aksu,20,19.0,1020,Sera isitmasi +2C
"""

IKLIM_PROJEKSIYONLARI = """senaryo,donem,sicaklik_C,artisi,yagis_degisim
Baz,1991-2020,19.0,0,1059mm
SSP245,2050,21.5,+2.5,-%15
SSP245,2100,22.3,+3.3,-%20
SSP585,2050,22.8,+3.8,-%22
SSP585,2100,24.6,+5.6,-%27
"""

ZEMIN_HAREKETI = """ilce,mahalle,zemin_sinifi,vs30,pga_g,pgv_cm_s,ss_g,s1_g,buyutme
Kepez,Masa Dagi,ZB,760,0.28,18,0.65,0.18,1.0
Kepez,Varsak,ZC,500,0.32,22,0.75,0.22,1.2
Muratpasa,Falez,ZC,550,0.33,24,0.78,0.24,1.3
Muratpasa,Lara-Kundu,ZD,300,0.38,32,0.90,0.30,1.6
Konyaalti,Sahil-Liman,ZD-ZE,250,0.42,38,1.05,0.38,2.0
Konyaalti,Bogacay-Gokdere,ZE,180,0.48,45,1.20,0.45,2.5
"""

BINA_MARUZIYETI = """ilce,toplam_bina,toplam_nufus,toplam_konut,ort_bina_yasi,yapi_degeri_TL
Kepez,85000,615000,210000,18,850 milyar
Muratpasa,65000,512000,195000,28,780 milyar
Konyaalti,32000,198000,95000,14,480 milyar
Toplam,182000,1325000,500000,20,2.11 trilyon
"""

TASKIN_OLAYLARI = """tarih,olay,ilce,yagis,etki
1969-01-17,Rekor yagis,Merkez,331.5mm/1gun,Tarihi sel
2003-12-10,Bogacay taskini,Konyaalti,180mm/2gun,500 ev su basti
2008-01-27,Kundu seli,Muratpasa-Aksu,150mm,3000 dekar sera
2009-12-16,Bogacay + Sarisu,Konyaalti,100km/s firtina,60 ev su basti yol kapandi
2009-12-16,Sarisu tasmasi,Konyaalti-Kemer,100km/s,Sarisu denize bosalamadi
2009-10-21,Kumluca seli,Kumluca,Siddetli yagis,2000 donum sera 1m su altinda
"""

DOGRULAMA_ETIKETLERI = """id,mahalle,ilce,hasar,lat,lon,su_derinligi_m
ANT-2009-001,Gundogdu,Kepez,Agir,36.9050,30.7050,1.2
ANT-2009-002,Gundogdu,Kepez,Agir,36.9065,30.7075,1.0
ANT-2009-003,Teomanpasa,Kepez,Orta,36.9100,30.7000,0.8
ANT-2009-004,Varsak Karsiyaka,Kepez,Agir,36.9500,30.6800,1.5
ANT-2009-005,Varsak Karsiyaka,Kepez,Orta,36.9520,30.6825,0.9
ANT-2009-006,Kultur,Kepez,Orta,36.9000,30.6800,0.7
ANT-2009-007,Sutculer,Kepez,Agir,36.9055,30.6950,1.1
ANT-2009-008,Yeşildere,Muratpasa,Orta,36.8950,30.6900,0.6
ANT-2009-009,Guzeloba,Muratpasa,Orta,36.8500,30.7800,0.8
ANT-2009-010,Lara,Muratpasa,Hafif,36.8450,30.8000,0.4
ANT-2009-011,Konyaalti,Konyaalti,Orta,36.8800,30.6500,0.7
ANT-2009-012,Hurma,Konyaalti,Hafif,36.8700,30.6300,0.5
ANT-2009-013,Aksu,Aksu,Agir,36.9450,30.8400,1.3
ANT-2009-014,Aksu,Aksu,Orta,36.9400,30.8350,0.9
ANT-2009-015,Dosemealti,Dosemealti,Orta,36.9900,30.6000,0.8
ANT-2009-016,Calkaya,Aksu,Hafif,36.9200,30.8200,0.5
ANT-2009-017,Altinova,Kepez,Orta,36.9150,30.7500,0.7
ANT-2009-018,Kuzeyyaka,Kepez,Agir,36.9250,30.6900,1.0
"""

KONTROL_ORNEKLERI = """id,mahalle,ilce,konum_guveni
BLN-1042,Sirinyali,Muratpasa,0.95
BLN-1089,Sirinyali,Muratpasa,0.35
BLN-2015,Meltem,Muratpasa,0.88
BLN-3120,Arapsuyu,Konyaalti,0.42
BLN-3145,Arapsuyu,Konyaalti,0.91
BLN-4022,Liman,Konyaalti,0.85
BLN-5011,Cankaya,Kepez,0.28
BLN-5098,Cankaya,Kepez,0.92
"""

RAW_DATASETS: dict[str, str] = {
    "ilce_temel.csv": ILCE_TEMEL,
    "deprem_tehlikesi.csv": DEPREM_TEHLIKESI,
    "deprem_katalogu.csv": DEPREM_KATALOGU,
    "jeoloji.csv": JEOLOJI,
    "toprak.csv": TOPRAK,
    "mikrobolegeleme.csv": MIKROBOLGELEME,
    "sondaj.csv": SONDAJ,
    "iklim_normalleri.csv": IKLIM_NORMALLERI,
    "istasyon_mikroklima.csv": ISTASYON_MIKROKLIMA,
    "iklim_projeksiyonlari.csv": IKLIM_PROJEKSIYONLARI,
    "zemin_hareketi.csv": ZEMIN_HAREKETI,
    "bina_maruziyeti.csv": BINA_MARUZIYETI,
    "taskin_olaylari.csv": TASKIN_OLAYLARI,
    "dogrulama_etiketleri_2009.csv": DOGRULAMA_ETIKETLERI,
    "kontrol_ornekleri.csv": KONTROL_ORNEKLERI,
}


def _parse(csv_text: str) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(csv_text)))


def yuklenen_kayitlar() -> list[dict[str, str]]:
    """Tum ham kayitlar, AVC-1999 disinda. Her kayda kaynak etiketi eklenir."""
    kayitlar: list[dict[str, str]] = []
    for dosya, icerik in RAW_DATASETS.items():
        for satir in _parse(icerik):
            kimlik = str(satir.get("id", satir.get("sondaj_no", "")))
            if kimlik.startswith(YASAKLI_PREFIX):
                continue  # Istanbul Avcilar -> asla Antalya modeline girmez
            kayit = dict(satir)
            kayit["_kaynak_dosya"] = dosya
            kayit["_kaynak_etiket"] = KAYNAK_ETIKETI
            kayit["_id"] = kimlik
            kayitlar.append(kayit)
    return kayitlar


def dogrulama_etiketleri() -> list[dict[str, str]]:
    return [k for k in yuklenen_kayitlar() if k["_kaynak_dosya"] == "dogrulama_etiketleri_2009.csv"]


def kontrol_ornekleri() -> list[dict[str, str]]:
    return [k for k in yuklenen_kayitlar() if k["_kaynak_dosya"] == "kontrol_ornekleri.csv"]


def dosya_yaz() -> Path:
    """Ham veriyi ve SHA256 manifestini diske yazar (tekrarlanabilirlik)."""
    manifest: list[dict[str, str]] = []
    for ad, icerik in RAW_DATASETS.items():
        hedef = RAW_DIR / ad
        hedef.write_text(icerik, encoding="utf-8")
        manifest.append(
            {
                "dosya": ad,
                "kaynak": KAYNAK_ETIKETI,
                "sha256": hashlib.sha256(icerik.encode("utf-8")).hexdigest(),
                "bayt": str(len(icerik.encode("utf-8"))),
                "indirilme": datetime.now(UTC).isoformat(),
            }
        )
    (RAW_DIR / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return RAW_DIR / "manifest.json"
