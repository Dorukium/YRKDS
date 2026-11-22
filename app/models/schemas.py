"""API ve skorlama katmani arasindaki tek veri sozlesmesi.

Butun sayisal ciktilar kaynakli oldugu surede "kesin" kabul edilir; kaynagi
olmayan hucreler None birakilir ve bunun yerine katman_durumu uyarisi uretilir.
"""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

TehlikeKodu = Literal["ZB", "L", "S", "H", "F"]


class SkorInput(BaseModel):
    """Tek bir grid hucresi / parsel icin deterministik girdi vektoru.

    None degerleri "bu katman icin kaynak veri yok" anlamina gelir; asla 0
    varsayilmaz. Bos girdi KARARSIZ uretilmesini saglar.
    """

    model_config = ConfigDict(extra="forbid")

    vs30: float | None = Field(default=None, ge=0, le=2000)
    zemin_sinifi: str | None = None
    jeoloji: str | None = None
    toprak_tipi: str | None = None
    sivilasma: str | None = None
    oturma: str | None = None
    drenaj: str | None = None
    yass_m: float | None = Field(default=None, ge=0)
    kum_orani: float | None = Field(default=None, ge=0, le=100)
    insar_hiz: float | None = Field(default=None, ge=-100, le=100)
    karst: bool | None = None
    egim: float | None = Field(default=None, ge=0, le=90)
    kaya_dusmesi: bool | None = None
    heyelan_envanter: bool | None = None
    taskin_100y: bool | None = None
    taskin_500y: bool | None = None
    akarsu_mesafe_m: float | None = Field(default=None, ge=0)
    twi: float | None = Field(default=None, ge=0)
    hand_m: float | None = Field(default=None, ge=0)
    gecmis_taskin_sayisi: int | None = Field(default=None, ge=0)
    fay_mesafe_km: float | None = Field(default=None, ge=0)
    pga_g: float | None = Field(default=None, ge=0)
    turba: bool | None = None
    organik: bool | None = None
    yuksek_bina_yuku: bool | None = None
    # Yasal VETO katmanlari: bilinmiyorsa None, asla False varsayilmaz.
    fay_sakinim_bandi: bool | None = None
    afete_maruz_bolge: bool | None = None
    taskin_yapi_yasagi: bool | None = None
    falez_cekme_mesafesi: bool | None = None


class EvidenceItem(BaseModel):
    katman: str
    kaynak: str
    deger: str
    guven: str = "kaynakli"  # kaynakli | turetilmis | eksik
    yetkinlik: str = "Otorite"  # U7: Otorite | Proxy | Tahmin | Araştırma | Eksik


class AnalyzeResponse(BaseModel):
    parsel_id: str
    skor: float | None = None
    bant: str = "KARARSIZ"
    karar: str = "Veri yetersiz — sondaj/etüt gerekli"
    tehlike_kirilimi: dict[str, float | None] = Field(default_factory=dict)
    veto: bool = False
    veto_neden: str | None = None
    guven_skoru: float = 0.0
    veri_tamligi: float = 0.0
    veri_tamligi_aciklama: str = ""
    katman_durumu: dict[str, str] = Field(default_factory=dict)
    # Skorun hangi bileşenlerle hesaplandığı (kısmi skor şeffaflığı)
    skor_kapsami: dict[str, Any] = Field(default_factory=dict)
    skor_araligi: dict[str, Any] = Field(default_factory=dict)
    guven_ifadesi: str = "düşük güven — karar için yetersiz"
    senaryo: dict[str, Any] = Field(default_factory=dict)
    beklenen_kayip: dict[str, Any] = Field(default_factory=dict)
    yasal_kisit_durumu: str = "dogrulanamadi"
    onlem_bolgesi: bool = False
    oneri: str = ""
    kanit: list[EvidenceItem] = Field(default_factory=list)
    uyarilar: list[str] = Field(default_factory=list)
    olusturulma: datetime = Field(default_factory=lambda: datetime.now(UTC))


class AnalyzeRequest(BaseModel):
    """POST /api/analyze gövdesi: GeoJSON Polygon veya Feature kabul eder."""

    model_config = ConfigDict(extra="allow")

    geojson: dict[str, Any] = Field(description="GeoJSON Polygon / Feature")
    parsel_id: str | None = None
    senaryo: str = "bugun"


class MitigateRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    geojson: dict[str, Any]
    onlemler: list[str] = Field(default_factory=list)
    senaryo: str = "bugun"


class LayerInfo(BaseModel):
    ad: str
    kaynak: str
    aciklama: str
    guncel: str | None = None


class EventItem(BaseModel):
    id: str
    olay_turu: str
    tarih: str
    ilce: str
    mahalle: str
    lat: float
    lon: float
    buyukluk: float | None = None
    etki: str = ""
    kaynak_url: str = ""
    konum_guveni: float | None = None
    # Etiket mi, olay mi? Doğrulama etiketi olarak kullanilacaksa True.
    dogrulama_etiketi: bool = False


class BacktestMetric(BaseModel):
    precision: float
    recall: float
    f1: float
    tp: int
    fp: int
    fn: int
    tn: int
    esik: float
    recall_ci95: list[float] = Field(default_factory=lambda: [0.0, 1.0])
    precision_sadece_etiket: float | None = None
    dogrulama: str
    not_: str = Field(default="", alias="not")

    model_config = ConfigDict(populate_by_name=True)


class BacktestResponse(BaseModel):
    metrikler: BacktestMetric
    yontem: str
    kaynak: str
    kalibrasyon: dict[str, Any] = Field(default_factory=dict)
    bloklar: dict[str, Any] = Field(default_factory=dict)
    uyarilar: list[str] = Field(default_factory=list)


class StatsResponse(BaseModel):
    ilce: str
    veri: dict[str, Any]
