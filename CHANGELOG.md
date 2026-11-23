# Changelog

Tüm önemli değişiklikler bu dosyada kaydedilir. Semantik sürüm: MAJOR.MINOR.PATCH.

## [5.0.0] — 2026-11-22

V5 kapanış sprinti:
- Zenodo DOI alındı: **10.5281/zenodo.24449066** (ADR-0023 kapandı);
  `CITATION.cff`, `README.md` ve TÜBİTAK raporu özeti güncellendi.
- TDTH kaynağı deaktif: ADR-0004 kalıcı açık, GEM+USGS "Araştırma" rozeti,
  yeni erişim denemesi yok.
- A3 (Resmî Gazete 11600) ve A7 (SYGM/JRC) için 3'er erişim yolu denendi;
  resmî vektör geometri/pafta bulunamadı, mevcut proxy'ler dürüst etiketle
  korundu (ADR-0007, ADR-0017).
- A2: GFD v1'in tamamı (913 olay) tarandı; Antalya AOI'sinde olay yok.
  GEE hesabı Earth Engine'e kayıtlı olmadığı için L1 erişilemedi; S1 2003/2008
  için fiziksel olarak olanaksız; literatürde jeoreferanslı etiket yok.
  4 denemeli kanıt `data/labels/gfd_2003_2008_manifest.json`'de; Recall ≥0.60
  hedefi doğrulanmadı (ADR-0003/0018/0025 kalıcı açık). K4 korundu.
- K2 regresyon fix'i: `ensure_schema()` advisory lock ile 8 worker DDL
  deadlock'u giderildi; k6 hata oranı %34.29 → %0.00.
- `make check-auth`, `make publish`, `earthengine` CLI kurulumu; 57 kaynak
  dosya, 117 pytest, kapsam >%90.
- A7 eki: JRC CEMS-GLOFAS v2.1 RP100/RP500 gerçek rasteri (Otorite, 93 m)
  indirildi, `make data-jrc` eklendi. 2009 "Ağır" noktalarıyla çakışma 0/6
  olduğu için ≥%60 DoD sağlanamadı; ADR-0007 açık kalır, F proxy olarak kalır.

## [4.0.0] — 2026-11-22

V4 master sprint:
- A1: NASA Earthdata ARIA S1 GUNW (40 granül) ile S bileşeni gerçek ölçüme
  geçti; kapsam %100 (otorite %79.19, proxy %20.81), ADR-0009 kapandı.
- A8: TKGM kamu parsel API'si entegre edildi (24 saat Redis önbellek,
  Otorite rozeti, WKT/GeoJSON yapıştırma sihirbazı).
- U9 veri merdiveni, TDTH insan adımı SOP (`make data-tdth`), ASF EULA akışı.
- U10 araç denetim matrisi E2E + snapshot'ları.
- Sürüm 4.0.0, ADR-0025 (A2) ve ADR-0026 (A7) ile kalan veri eksiklikleri
  dürust etiketli.

## [3.0.0] — 2026-11-22

TÜBİTAK jürisi ve belediye pilotu için master sprint:
A1 EGMS (kimlik yok → ADR-0009 açık), A2 bağımsız etiket (ADR-0018),
A3 üç Resmî Gazete VETO geometrisi (ADR-0017), A4 PC maruziyet (ADR-0015),
A5 ERA5 ekstrem (ADR-0014), A6 GEM/USGS (ADR-0008/0016);
B1 what-if, B2 portföy PDF, B3 beklenen kayıp, B4 embed, B5 PWA;
C1 SALib duyarlılık, C2 literatür kıyas, C3 TÜBİTAK raporu, C4 Marp sunum,
C5 video senaryosu; D1 ZAP CI, D2 Redis tile + 500 VU, D3 Grafana, D4 TR/EN.
Zenodo DOI bekliyor (ADR-0023).

## [0.4.0] — 2026-11-22

### Eklenen (V2 yükseltme)
- D3: GEM PGA (Araştırma rozeti, ADR-0008) + kullanıcı kararıyla resmi olmayan çapraz kontrol.
- D4: SoilGrids WCS 250 m, soc dahil 5 katman, IDW kaldırıldı (Otorite rozeti).
- D5/D6: PC STAC referansları; D7/D2 için ADR-0011/0012.
- D8: DEM'den kıyı <2m/<5m zonları; D9: 300 m önlem bölgesi (VETO değil).
- D10: U7 yetkinlik rozetleri, kapsam %, güncelleme tarihi, katalog API'si.
- F1 kılavuz ray + spotlight tur, F2 karşılaştırma, F3 toplu aday listesi,
  F4 senaryo anahtarı, F5 derin bağlantı, F6 sunucu PNG tile + nokta API,
  F7 durum/yeniden dene, F8 Ctrl+K komut paleti, F9 mobil.
- G1 /design galerisi, G3 skor halkası + bant çubukları + sparkline,
  G4 katlanır panel, G5 favicon/OG/baskı/rapor kapağı, G6 çift tema axe.
- EGMS InSAR (D1) erişilemedi → ADR-0009 + Eksik rozeti + güven cezası.

## [0.3.0] — 2026-11-22

### Eklenen (Frontend/UX/Kimlik/Veri eki)
- 9 sayfalık bilgi mimarisi, sticky menü, alt bilgi, sitemap.xml.
- Self-host Inter woff2 + inline SVG ikonlar; Okabe-Ito palet; açık/koyu tema.
- Koç marks (4 adım), klavye kısayolları, arama/Git, lejant, ölçek/imleç koordinatı,
  baz harita değiştirici (OSM/Esri/OpenTopoMap), mobil alt sheet, boş durum.
- Kimlik: argon2id, imzalı çerez, CSRF, roller, giriş hız sınırı, denetim kaydı,
  KVKK beyanı.
- 4 ek açık veri kaynağı manifest'li entegrasyon (KOERI, USGS metadata,
  ESA WorldCover, MS Buildings) + 3 ADR.

### Kapılar
- E2E 16 test, axe tüm sayfalarda temiz, Lighthouse 100/100/100/91,
  görsel regresyon snapshot'ları.

## [0.2.0] — 2026-11-22

### Eklenen
- Faz A kaynak araştırması; Resmî Gazete 11600 sayılı karar kaydı.
- Faz B `legal_constraints` tablosu ve Resmî Gazete VETO motoru.
- Faz C bağımsızlık denetimi (ADR-0003), Wilson CI, kalibrasyon ifşası.
- Faz D sismik çapraz kontrol durumu (ADR-0004).
- Faz F: mypy --strict, kapsam kapısı, Playwright E2E, axe WCAG, pip-audit,
  cargo audit, SBOM, Prometheus, healthz/readyz, Redis hız sınırı, Alembic,
  yedekleme/geri yükleme tatbikatı.
- Faz G: ±%10 ağırlık duyarlılığı (p5–p95), IPCC güven dili, renk körlüğü
  güvenli palet, PDF teknik olmayan özet.
- Faz H: CI iş akışı, datasheet, model kartı, metodoloji, soy zinciri.

### Değişen
- pyo3 0.23 → 0.29 (güvenlik açıkları nedeniyle).
- DEM kapsama hatası düzeltildi (NaN %22 → 0).

## [0.1.0] — 2026-11-22

İlk çalışan dikey kesit: skor motoru, API, harita, PDF, Docker Compose.
