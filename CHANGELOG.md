# Changelog

Tüm önemli değişiklikler bu dosyada kaydedilir. Semantik sürüm: MAJOR.MINOR.PATCH.

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
