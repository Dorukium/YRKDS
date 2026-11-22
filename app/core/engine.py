"""Analyze çıktılarını üreten orkestratör.

Sıra: VETO -> veri tamlığı/KARARSIZ -> alt puanlar -> skor/bant -> kanıt.
VETO, skordan bağımsız olarak kararı ezer (Spesifikasyon 2.3).

Kritik güvenlik kuralları (2026-11 revizyonu):
  * Bir ana bileşen (özellikle S) eksikse skor "kısmi" olarak işaretlenir,
    güven kareyle cezalandırılır ve karar asla "Uygun" olamaz.
  * Yasal VETO katmanlarından biri doğrulanmamışsa "Uygun" kararı verilemez.
  * Skor 0 varsayımıyla şişirilmez; eksik alt puanlar None kalır.
"""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.config import AGIRLIKLAR, SENARYOLAR
from app.core.confidence import (
    VETO_ALANLARI,
    guven_skoru,
    kararsiz_mi,
    katman_durumu,
    tamlık_aciklama,
    veri_tamligi,
)
from app.core.evidence import kanit_olustur
from app.core.scoring import alt_puanlar, karar_bandi, toplam_skor
from app.core.sensitivity import guven_ifadesi, skor_araligi
from app.core.veto_rules import veto_kontrol
from app.models.schemas import AnalyzeResponse, SkorInput

RUST_ALANLARI = {
    "vs30", "zemin_sinifi", "yass_m", "kum_orani", "insar_hiz", "karst",
    "egim", "kaya_dusmesi", "heyelan_envanter", "taskin_100y", "taskin_500y",
    "akarsu_mesafe_m", "twi", "hand_m", "gecmis_taskin_sayisi", "fay_mesafe_km",
    "pga_g", "turba", "organik", "yuksek_bina_yuku", "fay_sakinim_bandi",
    "afete_maruz_bolge", "taskin_yapi_yasagi", "falez_cekme_mesafesi",
}


def _rust_hesapla(girdi: SkorInput) -> tuple[float | None, dict[str, float | None]] | None:
    """Rust motoru varsa kullan; yoksa Python referansına düş."""
    try:
        import skor_motoru

        kwargs = {k: v for k, v in girdi.model_dump().items() if k in RUST_ALANLARI}
        skor, _bant, _veto, alt = skor_motoru.skor_hesapla(  # type: ignore[attr-defined]
            skor_motoru.SkorInput(**kwargs)  # type: ignore[attr-defined]
        )
        return skor, dict(alt)
    except Exception:  # modül build edilmemiş olabilir
        return None


_ONERILER = {
    "Düşük": "Standart zemin etüdü yeterli.",
    "Düşük-Orta": "Zemin etüdü ve yüzey drenajı koşuluyla yapılabilir.",
    "Orta-Yüksek": "Detaylı zemin etüdü ve temel iyileştirme önlemleri gerekli.",
    "Yüksek": "İyileştirme maliyeti yüksek; alternatif parsel değerlendirilmelidir.",
    "Kritik": "Uygun değil; yapılaşma önerilmez.",
}


def _oneri_uret(bant: str, alt: dict[str, float | None]) -> str:
    metin = _ONERILER.get(bant, "")
    baskin = [k for k, v in alt.items() if v is not None and v >= 0.6]
    if baskin:
        metin += " Baskın tehlikeler: " + ", ".join(baskin) + "."
    return metin


def analiz_et(
    girdi: SkorInput,
    parsel_id: str | None = None,
    legal: dict[str, Any] | None = None,
    senaryo_adi: str = "bugun",
) -> AnalyzeResponse:
    pid = parsel_id or "Q-" + datetime.now(UTC).strftime("%Y%m%d-%H%M%S-%f")[:-3]
    durum = katman_durumu(girdi)
    tamlik = veri_tamligi(durum)
    guven = guven_skoru(tamlik, durum)
    aciklama = tamlık_aciklama(durum, tamlik)

    veto, veto_neden, veto_uyarilari = veto_kontrol(girdi)
    rust = _rust_hesapla(girdi)
    alt = rust[1] if rust is not None else alt_puanlar(girdi)
    durum["skor_motoru"] = "Rust (PyO3)" if rust is not None else "Python (referans)"
    uyarilar = list(veto_uyarilari)

    # F4 — iklim senaryosu: yalnız F çarpanı (CMIP6 yağış değişimi), S nötr.
    senaryo = SENARYOLAR.get(senaryo_adi, SENARYOLAR["bugun"])
    f_carpan = float(str(senaryo["F"]))
    if f_carpan != 1.0 and alt.get("F") is not None:
        alt["F"] = round(min(1.0, float(alt["F"] or 0.0) * f_carpan), 3)
        uyarilar.append(
            f"Senaryo '{senaryo['etiket']}': F bileşeni CMIP6 yağış değişimi "
            f"({senaryo['yagis_degisim_pct']}%) ile çarpıldı (Tahmin rozetli). "
            "S bileşeni için güvenilir iklim çarpanı yok; nötr bırakıldı (ADR-0010)."
        )
    senaryo_bilgi = {
        "ad": senaryo["etiket"],
        "F_carpani": senaryo["F"],
        "S_carpani": senaryo["S"],
        "rozet": "Tahmin",
        "kaynak": "CMIP6 projeksiyonu (proje veri seti 3.10)",
    }

    eksik_alt = [k for k, v in alt.items() if v is None]
    mevcut_alt = [k for k, v in alt.items() if v is not None]
    kapsam = sum(AGIRLIKLAR[k] for k in mevcut_alt) / sum(AGIRLIKLAR.values())
    skor_kapsami = {
        "tur": "tam" if not eksik_alt else "kısmi",
        "mevcut": mevcut_alt,
        "eksik": eksik_alt,
        "agirlik_kapsami": round(kapsam, 3),
    }
    if eksik_alt:
        uyarilar.append(
            "Kısmi skor: " + ", ".join(eksik_alt) + " bileşen(leri) hesaplanamadı. "
            f"Skor yalnızca %{kapsam * 100:.0f} ağırlıkla hesaplandı ve güven "
            "buna göre düşürüldü. Eksik bileşenler 0 kabul edilmedi."
        )

    dogrulanan_veto = sum(1 for a in VETO_ALANLARI if getattr(girdi, a) is not None)
    if dogrulanan_veto == 4:
        yasal_durum = "dogrulandi"
    elif dogrulanan_veto == 0:
        yasal_durum = "dogrulanamadi"
    else:
        yasal_durum = "kismi"
    if yasal_durum != "dogrulandi":
        uyarilar.append(
            "Yasal kısıt katmanlarının "
            f"{4 - dogrulanan_veto}/4'ü doğrulanamadı; imar/afet mevzuatı kontrolü "
            "resmi kayıtlarla yapılmalıdır."
        )

    # Resmî Gazete kaynaklı VETO (Faz B)
    if legal is not None:
        if legal.get("durum") == "dogrulandi":
            yasal_durum = "dogrulandi"
        if legal.get("onlem_bolgesi"):
            uyarilar.append(
                "300 m önlem bölgesi (danışmanlık göstergesi — VETO değildir)."
            )
        if legal.get("uyari"):
            uyarilar.append(legal["uyari"])
        if legal.get("veto"):
            veto = True
            veto_neden = legal["neden"]
            guven = round(guven * 0.95, 3)

    # Kapsam %50 altındaysa sayısal skor gösterilmez (sahte kesinlik yasağı).
    kararsiz = kararsiz_mi(tamlik) or kapsam < 0.5
    skor: float | None = None
    bant = "KARARSIZ"
    karar = "Veri yetersiz — sondaj/etüt gerekli"
    oneri = "Yerinde sondaj ve zemin etüdü tamamlanmadan yatırım kararı verilmemelidir."

    if not kararsiz:
        skor = (
            toplam_skor(alt) if f_carpan != 1.0
            else (rust[0] if rust is not None else toplam_skor(alt))
        )
        if skor is not None:
            bant, karar = karar_bandi(skor)
            oneri = _oneri_uret(bant, alt)
            if eksik_alt:
                # Eksik ana bileşen varsa güveni kareyle cezalandır.
                guven = round(guven * kapsam**2, 3)
                if bant in ("Düşük", "Düşük-Orta"):
                    karar = "Koşullu — eksik bileşen: " + ", ".join(eksik_alt)
                oneri += " Eksik bileşenler tamamlanmadan olumlu karar verilmez."
            if yasal_durum != "dogrulandi" and karar.startswith("Uygun"):
                karar = "Koşullu — yasal kısıt doğrulanamadı"
                oneri += " Resmi imar/afet mevzuatı kontrolü zorunludur."
        else:
            uyarilar.append("Hiçbir alt puan hesaplanamadı; sayısal skor üretilmedi.")

    if veto:
        karar = "Uygun Değil (Yasal Kısıt)"
        oneri = "Yasal kısıt nedeniyle yapılaşma önerilmez. " + (veto_neden or "")

    return AnalyzeResponse(
        parsel_id=pid,
        skor=skor,
        bant=bant,
        karar=karar,
        tehlike_kirilimi=alt,
        veto=veto,
        veto_neden=veto_neden,
        guven_skoru=guven,
        veri_tamligi=tamlik,
        veri_tamligi_aciklama=aciklama,
        katman_durumu=durum,
        skor_kapsami=skor_kapsami,
        skor_araligi=skor_araligi(alt),
        guven_ifadesi=guven_ifadesi(guven),
        senaryo=senaryo_bilgi,
        yasal_kisit_durumu=yasal_durum,
        onlem_bolgesi=bool(legal.get("onlem_bolgesi")) if legal else False,
        oneri=oneri,
        kanit=kanit_olustur(girdi),
        uyarilar=uyarilar,
    )
