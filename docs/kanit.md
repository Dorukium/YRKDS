# Kanıt Günlüğü (K1 — bağlayıcı)

Her görev yalnızca bu dosyaya tarih + komut + çıktı özeti eklendiğinde bitti sayılır.
Kırmızı kapılar atlanmaz; düzeltme commit'leriyle takip edilir (K2).

---

## [KURULUM] Yönetişik dosyaları — 2026-11-22
Komut: `mkdir -p docs/ADR tests/e2e migrations/versions scripts .github/workflows`
Çıktı özeti: Kanıt günlüğü, ADR arşivi (4 ADR), CI, Makefile, Diataksis dokümanları oluşturuldu.
Sonuç: YEŞİL

## [FAZ A] Kaynak araştırması — 2026-11-22
Komut: Firecrawl MCP `firecrawl_search` / `firecrawl_scrape` (conversationId f041fb1f-...)
Çıktı özeti: 5 kaynak bulundu; 11600 sayılı CK (10.08.2026, 7269 sK) ile
Hisarçandır/Üçoluk/Gökdere afete maruz bölge; SYGM SÇD PDF 149 sf (sayısal 100/500
yıllık tablo yok); GEM GSHM v2026.1 Zenodo 20735384 (CC BY-NC-SA); Antalya InSAR
literatürü yok; Nominatim mahalle geocode başarısız.
Sonuç: YEŞİL (kısmi — eksikler ADR-0003/0004 ve docs/arastirma_raporu.md)
Kaynaklar: data/raw/research_manifest.json (RES-001..005)

## [FAZ B] Yasal VETO — 2026-11-22
Komut: `uv run pytest -q tests/test_veto_legal.py`
Çıktı özeti: 3 passed. Gerçek 11600 kararı geom=NULL → veto tetiklenmiyor;
geometrisi olan TEST-1 kararı iç poligonda VETO, dış poligonda yok.
Sonuç: YEŞİL (mekanizma); gerçek geometri yok (ADR-0002)

## [FAZ C] Bağımsız doğrulama — 2026-11-22
Komut: `uv run pytest -q tests/test_independent_validation.py`
Çıktı özeti: 2003/2008 mahalle etiketi olmadığı kanıtlandı; `bagimsiz_mi=False`,
mekansal hold-out mekanizması çalışıyor. Kalibrasyon Recall 0.941, CI [0.730,0.990].
Sonuç: KIRMIZI→ADR (bağımsız olay verisi yok; eşik oyunu yapılmadı)

## [FAZ D] Sismik çapraz kontrol — 2026-11-22
Komut: `uv run pytest -q tests/test_seismic_crosscheck.py`
Çıktı özeti: GEM raster lisans nedeniyle gömülmedi; proje PGA iç tutarlılığı doğrulandı.
Sonuç: KIRMIZI→ADR-0004 (bağımsız sapma hesaplanamadı)

## [FAZ F] Mühendislik kapıları — 2026-11-22

| Kapı | Komut | Çıktı | Sonuç |
|---|---|---|---|
| Lint | `uv run ruff check .` | All checks passed | YEŞİL |
| Tip | `uv run mypy --strict app` | Success: no issues found in 40 source files | YEŞİL |
| Test | `uv run pytest -q` | 66+ passed | YEŞİL |
| Kapsam | `uv run pytest --cov=app --cov-fail-under=90` | TOTAL 92% (core 96%) | YEŞİL |
| Parity | `pytest tests/test_parity.py` | 9/9 vektör birebir | YEŞİL |
| Hidroloji | `pytest tests/test_hydro.py` | sentetik havza/HAND testleri geçti | YEŞİL |
| E2E | `npx playwright test` | 1 passed (harita→panel→PDF, konsol 0) | YEŞİL |
| Erişilebilirlik | axe WCAG 2.2 AA | 0 critical / 0 serious | YEŞİL |
| Yük | `k6 run tests/load.js` | 100 VU, hata %0, p95 **161 ms** (<300) | YEŞİL |
| Güvenlik | pip-audit + cargo audit | No known vulnerabilities found | YEŞİL |
| SBOM | cyclonedx-py | docs/sbom.json (157 KB) | YEŞİL |

Load kapısı ilk denemede kırmızıydı (%56 hata, p95 622 ms). Düzeltmeler:
DB bağlantı havuzu (`psycopg_pool`), duyarlılık analizinin numpy ile
vektörleştirilmesi, uvicorn 4 worker, Dockerfile'da `--all-extras`.
Yeniden çalıştırma: hata %0, p95 161 ms.

## [FAZ G] Belirsizlik iletişimi — 2026-11-22
Komut: `uv run pytest -q tests/test_infra.py` + Playwright E2E
Çıktı özeti: 200 koşulu ±%10 duyarlılık p5–p95 panelde ve PDF'te; IPCC güven
ifadesi; viridis palet; VETO mor çizgili dolgu; PDF teknik olmayan özet.
Sonuç: YEŞİL

## [FAZ H] Yeniden üretilebilirlik — 2026-11-22
Komut: `docker compose up -d --build`, `make gate-all`, `make sbom`
Çıktı özeti: 3 konteyner healthy; CI workflow; Alembic 0001; yedek/geri yükleme
script'leri; datasheet, model card, metodoloji, soy zinciri, CHANGELOG, MIT LICENSE.
Sonuç: YEŞİL (Zenodo DOI henüz alınmadı — yayın sonrası adım)

## [EK PLAN A-B] Frontend, UX ve kimlik — 2026-11-22

Komut: `docker compose up -d --build` + `node node_modules/playwright/cli.js test --config tests/e2e/playwright.config.js`
Çıktı özeti: 9 sayfa (Ana Sayfa, Harita, Raporlar, Veri Kataloğu, Yöntem,
Olay İzleme, Yardım, login, admin) yayında; sitemap.xml; 14→16 E2E test geçti;
tur görünür/kapanır; arama ve kısayollar; mobil viewport; anonim /admin 403;
yanlış giriş hata mesajı. axe-core tüm sayfalarda 0 kritik/ciddi.
Sonuç: YEŞİL

Komut: `uv run pytest -q tests/test_auth.py`
Çıktı özeti: argon2id özeti, CSRF, hatalı giriş mesajı, çerez HttpOnly+SameSite,
roller (anonim/analist/admin 403), denetim kaydı, 5 deneme/15 dk → 429.
Sonuç: YEŞİL

Komut: `bash scripts/lighthouse.sh`
Çıktı özeti: Performance 100 · Accessibility 100 · Best Practices 100 · SEO 91.
Sonuç: YEŞİL

## [EK PLAN Bölüm 6] Veri zenginleştirme — 2026-11-22
Komut: `uv run python -m app.data_pipeline.download_enrichment`
Çıktı özeti: 4 kaynak manifest'li — KOERI_KATALOG, USGS_VS30 (metadata),
esa_worldcover (CC-BY-4.0), ms_buildings (ODbL-1.0), hepsi SHA256 ile.
Erişilemeyenler ADR-0005/0006/0007 + docs/capraz_kontrol.md.
Sonuç: YEŞİL (kısmi — 5 kaynak ADR'li)

## Tek komut doğrulaması — 2026-11-22
Komut: `make gate-all > /tmp/gate_all2.log 2>&1`
Çıktı özeti: `All checks passed!` · `Success: no issues found in 43 source files`
· `74 passed` · `Total coverage: 91.95%` · E2E `16 passed` + axe `8 passed`
· Lighthouse `100/100/100/91` · k6 `http_req_failed 0.00%`, `p(95)=268 ms`
· `No known vulnerabilities found` · `TUM KAPILAR YEŞİL` · `GATE_EXIT=0`
Sonuç: **YEŞİL**

## [V2] Veri derinleştirme ve akış — 2026-11-22

Komut: `uv run python -m app.data_pipeline.download_soil_wcs && uv run python -m app.data_pipeline.process_grid`
Çıktı özeti: 5 WCS katmanı (clay/silt/sand/soc/phh2o), SHA256 manifest,
soc %100 dolu, kapsam 25 m ızgarada tam. IDW kaldırıldı.
Sonuç: YEŞİL

Komut: `uv run python -m app.data_pipeline.crosscheck_d3`
Çıktı özeti: GEM GSHM v2023.1 PGA örneklandi; Kepez %20.2, Muratpaşa %56.8,
Konyaaltı %77.8 sapma → ADR-0008; rozet "Araştırma", kullanıcı kararı kayıtlı.
Sonuç: YEŞİL

Komut: `uv run pytest -q tests/test_v2.py`
Çıktı özeti: 7/7 — WCS kapsam, GEM ADR, kıyı zonları, afete_maruz NULL
regresyonu, katalog rozetleri, U7 kanıt rozeti + F4 senaryo, F6 tile/nokta API.
Sonuç: YEŞİL

Komut: `node node_modules/playwright/cli.js test --config tests/e2e/playwright.config.js`
Çıktı özeti: 23 passed — F1 tur/ray, F4 senaryo skor değişimi, F5 derin
bağlantı, F8 komut paleti, F6 tile, U7 katalog, G1 galeri, 8 sayfa + koyu tema axe,
2 görsel regresyon (U8: her düzeltmede snapshot güncellendi).
Sonuç: YEŞİL

Kapanamayanlar (ADR + rozet): D1 EGMS (ADR-0009), D2 SYGM pafta (ADR-0011),
D7 MGM ekstrem (ADR-0012), D5/D6 kısmi (docs/capraz_kontrol.md).

## V5.0.0 SON KABUL — 2026-11-23
Komut: `make publish` · `uv lock` · `make check-auth` · `make gate-all`
Çıktı özeti: Zenodo DOI **10.5281/zenodo.24449066** (`"durum": "ok"`, deposition
24449066); `CITATION.cff` 1.2.0 / v5.0.0 / DOI doğrulandı; README ve rapor
özeti/sonuç/slayt güncellendi. `make check-auth` → NASA/GEE/Zenodo `var`,
TDTH `deaktif`. Kapılar: `All checks passed!` · `Success: no issues found in
57 source files` · `117 passed` · kapsam `90.19%` · E2E `25 passed` · axe
`9 passed` · Lighthouse `100/100/100/91` · k6 `0.00%` hata (0/20698), p95
`195.35 ms` · `No known vulnerabilities found` · `TUM KAPILAR YEŞİL` ·
`GATE_EXIT=0`.
Commitler: `606a20757164796c418a67dc73d00278ce827178` (DOI + A2 kanıtları +
sürüm), `f4a18eba9b41f5019db1212bba4d99f27d22c81d` (görsel snapshot'lar),
`6147d150793f031a6ee0c359c54f5120cb7cd8bf` (rapor/slayt).
Açık (dürüst): A2 Recall ≥0.60 doğrulanamadı — GFD'de AOI'de 0 olay, S1
tarihsel olarak yok, literatürde etiket yok (ADR-0003/0018/0025 kalıcı);
A7/A3 vektör pafta yok (ADR-0007/0017); TDTH deaktif (ADR-0004). GEE kimlik
dosyası var fakat `ee.Initialize()` hâlâ "project is not registered" — kullanıcı
Google Cloud proje ID'sini sağlamalı. Git remote olmadığı için GitHub release
oluşturulamadı; yerel `v5.0.0` etiketi basıldı.

## V5 / A3 + A7 + A2-L3 MERDİVEN DENEMELERİ (U12) — 2026-11-22
Komut: Firecrawl/Exa aramaları + `curl` WMS + RG arşiv taraması + PDF scrape
Çıktı özeti:
- **A3 (3 deneme):** (1) Firecrawl `resmigazete.gov.tr 11600` araması → yalnızca
  haberler; (2) RG 2026/08–10 günlük sayfalarının programatik taranması →
  `11600` indekste yok (13 Ağustos'ta 11606 var); (3) haber + 1/25.000 plan
  kaynakları → kararın 10.08.2026 tarihli, 7269 kapsamlı, "ek sayısal sınırlar"
  içerdiği doğrulandı ama koordinat/polygon yayınlanmadı. Sonuç: mevcut
  **3 Nominatim geocode-proxy** korunur (ADR-0017); "gerçek karar poligonu"
  üretilmedi — dürüst etiket.
- **A7 (3 deneme):** (1) `usbs.tarimorman.gov.tr/services/wms?GetCapabilities`
  → 60 sn timeout; (2) SYGM resmî TYP PDF → HTTP 404, ÇB `webdosya` yansısı
  erişilebilir (313 K karakter) ama haritalar raster, vektör taşkın paftası yok;
  (3) JRC GloFAS → veri var fakat GEE gerektiriyor (kimlik bekliyor). Sonuç:
  F bileşeni TWI/HAND + OSM akarsu **proxy** olarak kalır (ADR-0007/0011).
- **A2 L3 literatür:** IMO 2003 sel raporu, JMO Boğaçay jeoloji raporu,
  Akdeniz Üniv. Konyaaltı Q100 harita atfı bulundu; makine okunabilir
  jeoreferanslı 2003/2008 etiket seti yok. GEE L1 kimlik onayında.
Sonuç: üç görev de ADR'li bırakıldı; uydurma poligon/etiket üretilmedi (K3).

## V5 / HAZIRLIK KAPILARI (geçici, kimlikler bekliyor) — 2026-11-22
Komut: `docker compose up -d --build && sleep 8 && make gate-all`
Çıktı özeti: `All checks passed!` · `Success: no issues found in 57 source files`
· `116 passed` · kapsam `90.18%` · E2E `25 passed` · axe `9 passed` ·
k6 `0.00%` hata (0/17576), p95 `264.39 ms` · `No known vulnerabilities found`
· `TUM KAPILAR YEŞİL` · `GATE_EXIT=0`.
Kapsam: bu kapı yalnızca v5 hazırlığı ve K2 deadlock fix'ini doğrular.
GEE/Zenodo kimlikleri olmadan A2 etiketi ve DOI **henüz üretilmedi**; sürüm
5.0.0 etiketi bu görevler tamamlanmadan basılmayacak (K3 dürüstlük).
Commit: `525e7985ddbedb6bdd8524e8e495684be4db4745`

## V5 / K2 KIRMIZI KAPI — ensure_schema deadlock — 2026-11-22
Komut: `make gate-all` (ilk koşu) → `docker compose logs db | grep deadlock`
Çıktı özeti: `http_req_failed 34.29%` (8095/23606), `connection reset by peer`;
DB log'unda 8 worker'ın aynı `ALTER TABLE legal_constraints` DDL'ini çalıştırıp
`AccessExclusiveLock` deadlock'una girdiği görüldü.
Fix: `ensure_schema()` tüm DDL'i tek `pg_advisory_xact_lock(0x59524B44)` altında
serileştiriyor (commit/rollback'da otomatik bırakılır). `tests/test_v5.py` regression
testi eklendi.
Doğrulama: `make load` → `http_req_failed 0.00% (0/20702)`, p95 `225.4 ms`,
`LOAD_EXIT=0`.
Commit: `525e7985ddbedb6bdd8524e8e495684be4db4745`
Sonuç: **YEŞİL** (K2: kapı atlanmadı, kök neden düzeltildi).

## V5 / FAZ 1 — Kimlik hazırlığı ve TDTH ADR (U11) — 2026-11-22
Komut: `uv sync --python 3.12 --all-extras` + `uv run earthengine --help` +
`make check-auth` + `make citation` + `make cov`
Çıktı özeti: `earthengine-api 1.7.53` kuruldu, CLI çalışıyor (`usage: earthengine ...`);
`ee 1.7.53` import edildi. `make check-auth` → NASA `var`, GEE `yok`, Zenodo `yok`,
TDTH `deaktif`, genel `eksik kimlik var`. `make citation` → `CITATION.cff`
`doi: 10.5281/zenodo.PENDING` (sahte DOI yok). Kapsam `%90.17`, 57 kaynak dosya,
mypy/ruff temiz.
Commit: `05322259904cd7de9503fe77826673d894f525d3`
Karar: TDTH deaktif — ADR-0004 "kalıcı açık, alternatif GEM+USGS Araştırma
rozeti" olarak güncellendi; **yeni erişim denemesi yapılmadı**. GEE ve Zenodo
kimlikleri kullanıcı onayı/beklemede; A2/A7/DOI görevleri merdivenin ilgili
basamağına kaydırıldı (U12).

## V4 SON KABUL — 2026-11-22
Komut: `make gate-all > /tmp/gate_v4d.log 2>&1`
Çıktı özeti: `All checks passed!` · `Success: no issues found in 54 source files`
· `104 passed` · kapsam `90.06%` · E2E `25 passed` · axe `9 passed` ·
Lighthouse `100/100/100/91` · k6 hata `0.00%`, p95 `184.79 ms` ·
`No known vulnerabilities found` · `TUM KAPILAR YEŞİL` · `GATE_EXIT=0`.
Sürüm 4.0.0, tag v4.0.0, CHANGELOG güncel. Zenodo DOI bekliyor (ADR-0023),
A2/A7 veri eksiklikleri ADR-0025 ile dürüst etiketli.

## [V4 / FAZ A8] TKGM Parsel Sorgu — 2026-11-22
Komut: `curl https://cbsapi.tkgm.gov.tr/megsiswebapi.v3.1/api/parsel/36.9050/30.7050/`
Çıktı özeti: HTTP 200, gerçek GeoJSON poligonu (Dutlubahçe 4355/10, 557 m²);
`/api/parcel-search` 24 saat Redis önbellek + Otorite rozeti; E2E testi ve
`tkgm-panel.png` snapshot'ı yeşil.
Sonuç: YEŞİL

## [V4 / U9-U10] Veri merdiveni ve araç denetimi — 2026-11-22
Çıktı özeti: `docs/veri_merdiveni.md` (8 görev × 3 basamak), `docs/sop_tdth.md`,
`make data-tdth`; 9 harita aracı E2E doğrulaması + snapshot (25 Playwright test).
Sonuç: YEŞİL

## [V4 / FAZ A1] NASA Earthdata ARIA S1 GUNW InSAR — 2026-11-22
Komut: earthaccess login + `_ensure_asf_eula()` + `indir(40)` + `hiz_haritasi_olustur()`
Çıktı özeti: EULA kabulü sonrası HTTP 206; 40 granül (4.9 GB), SHA256
`0dbe87ef...`; toplam kapsam %100, otorite %79.19, proxy %20.81; örnek hızlar
-7.83 / -6.25 / +12.54 mm/yıl. `docs/kanit/insar_kapsam.png` kapsam haritası.
Sonuç: **YEŞİL** — ADR-0009 kapandı (docs/ADR/0009-kapanis.md). S bileşeni artık
gerçek ölçümle hesaplanıyor; `skor_kapsami.tur="tam"`, proxy hücrelerde güven cezası.

## [V3 / KAPANAN AÇIKLAR] ZAP + 500 VU — 2026-11-22
Komut: `docker run --rm -v $PWD/zap.conf:/zap/wrk/zap.conf ghcr.io/zaproxy/zaproxy:stable zap-baseline.py -t http://172.17.0.1:8000 -c zap.conf -I -d 3`
Çıktı özeti: `FAIL-NEW: 0`, PASS 59, `WARN-NEW: 9` (düşük: COEP/COOP, ADR-0024), `ZAP_EXIT=0`.
Sonuç: YEŞİL

Komut: `YRKDS_RATE_LIMIT=200000 docker compose up -d --force-recreate api && k6 run tests/load_500.js`
Çıktı özeti: 500 VU, 8 dk, **18.575.820 istek**, `http_req_failed 0.00%`,
p95 **20.46 ms** (hedef <150 ms). Redis hit/miss 616.309/1; nginx tile cache
HIT/MISS doğrulandı. `K6_EXIT=0`.
Sonuç: YEŞİL (D2 tam kapandı)

## V3 SON KABUL — 2026-11-22
Komut: `make gate-all > /tmp/gate_v3b.log 2>&1`
Çıktı özeti: `All checks passed!` · `Success: no issues found in 52 source files`
· `91 passed` · kapsam `90.37%` · E2E `23 passed` · axe `9 passed` ·
Lighthouse `100/100/100/91` · k6 hata `0.00%`, p95 `243 ms` ·
`No known vulnerabilities found` · `TUM KAPILAR YEŞİL` · `GATE_EXIT=0`.
Sürüm: 3.0.0 · CHANGELOG güncel · MIT lisans · Zenodo DOI bekliyor (ADR-0023).
A1 (EGMS), A2 (2003/2008 etiket), D1 ZAP yerel koşusu ve D4 dinamik metin
i18n kapsamı ADR + dürüst rozetle açık; geri kalan tüm maddeler kanıtlı kapalı.

## [V3 / FAZ 4] D1–D4 — Sertleştirme — 2026-11-22
Komut: CI workflow + `docker compose config` + pytest
Çıktı özeti: OWASP ZAP baseline adımı CI'da; Redis tile önbelleği (TTL 24s,
X-Cache HIT/MISS); 500 VU k6 senaryosu (`tests/load_500.js`); Prometheus :9090
ve Grafana :3000 provision edildi (5 panel); TR/EN sözlük + dil değiştirici
tüm sayfalarda (ADR-0022: dinamik metinler TR kalır).
Sonuç: YEŞİL (ZAP yerel çalıştırılmadı — CI adımı eklendi, kanıt CI log'unda)

## [V3 / FAZ 3] C1–C5 — Bilimsel iletişim — 2026-11-22
Komut: `uv run python scripts/sensitivity.py`
Çıktı özeti: SALib Morris 2000 trajektör; H %49.9, F %25.6, ZB/L %12.2,
S %0 (NULL). `docs/duyarlilik.md` + SVG çubuk grafik. F +%10 → skor 0.70 kayar.
Sonuç: YEŞİL

Komut: Firecrawl aramaları + `../data/qa_tmp/node_modules/.bin/marp ... --pdf`
Çıktı özeti: 5 literatür kaynağı (docs/literatur_kiyas.md, ADR-0021: nicel
korelasyon yok); TÜBİTAK raporu 6 bölüm; 12 slaytlık Marp PDF → 13 sayfa;
3 dakikalık video senaryosu.
Sonuç: YEŞİL

## [V3 / FAZ 1] A5 — ERA5 ekstrem serisi — 2026-11-22
Komut: `uv run python -m app.data_pipeline.download_era5_extremes`
Çıktı özeti: 2559 günlük kayıt, p99 42.6 mm/gün, 1969-01-17 ızgara 57.1 mm
(istasyon 331.5 mm → ADR-0014), manifest SHA256 + URL + tarih.
Sonuç: YEŞİL (Proxy — araştırma rozeti)

## [V3 / FAZ 1] A1 — EGMS kimlik kontrolü — 2026-11-22
Komut: `printenv COPERNICUS_USER / COPERNICUS_PASS`
Çıktı özeti: ikisi de boş; EGMS Ortho indirilemedi. ADR-0009 açık kalır,
S bileşeni NULL + güven cezası. Uydurma hız üretilmedi.
Sonuç: KIRMIZI → ADR (dış bağımlılık)

## Tek komut doğrulaması (V2 son) — 2026-11-22
Komut: `make gate-all > /tmp/gate_all4.log 2>&1`
Çıktı özeti: `All checks passed!` · `Success: no issues found in 47 source files`
· `83 passed` · kapsam `90.71%` · E2E `23 passed` · axe `9 passed` ·
Lighthouse `100/100/100/91` · k6 hata `0.00%`, p95 `299 ms` ·
`No known vulnerabilities found` · `TUM KAPILAR YEŞİL` · `GATE_EXIT=0`.
K1 uyarınca kapanamayan D1/D2/D7 maddeleri ADR + yetkinlik rozeti ile
etiketlendi (ADR-0009/0011/0012).

## Son E2E (koyu tema dahil) — 2026-11-22
Komut: `node node_modules/playwright/cli.js test --config tests/e2e/playwright.config.js`
Çıktı özeti: `17 passed` (9 sayfa navigasyon, tur, login hata, anonim 403,
mobil viewport, 8 açık tema axe + 1 koyu tema axe, 2 görsel regresyon, PDF akışı).
Sonuç: **YEŞİL**
