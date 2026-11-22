# V5 — Kullanıcı kimlik adımları (2 adım)

Ajan bu iki adımı senin adına tamamlayamaz (tarayıcı oturumu ve Google/GitHub
onayı gerekir). Geri kalan tüm iş hazır; bu adımlar bitince `make gate-all`
dışındaki fazlar otomatik devam eder.

## 1) Google Earth Engine (A2 için zorunlu)

`earthengine` komutu bu oturumda kuruldu (`earthengine-api 1.7.53`).

```bash
cd /run/media/dorukersoy/8C3A1DA03A1D87FA/YRKDS
uv run earthengine authenticate
# Tarayıcı açılır → Google hesabını seç → "Allow" / "İzin ver"
```

Doğrulama (sen onayladıktan sonra):

```bash
make check-auth
# google_earth_engine.durum = "var" olmalı
uv run python -m app.data_pipeline.gee_auth
# baglanti = "ok" olmalı
```

Kimlik dosyası: `~/.config/earthengine/credentials`.

## 2) Zenodo token (DOI için zorunlu)

1. https://zenodo.org/account/settings/applications/tokens/new/ adresini aç.
2. **Sign in with GitHub** ile giriş yap (proje hesabın).
3. Token adı: `YRKDS v5`, scope: varsayılan (`deposit:write`, `deposit:actions`).
4. Oluşturulan token'ı kopyala, proje kökündeki `.env` dosyasına ekle:

```bash
ZENODO_TOKEN=zenodo_...buraya_token
```

5. Doğrula ve yayınla:

```bash
make check-auth     # zenodo.durum = "var"
make publish        # CITATION.cff + README + rapor güncellenir, DOI basılır
```

> **Dürüstlük:** Token eklenmeden `make publish` çalıştırılırsa sahte DOI
> üretilmez; `CITATION.cff` içinde `doi: 10.5281/zenodo.PENDING` kalır.

## Not: A2 merdiveni için teknik uyarı

Sentinel-1 (2014'te fırlatıldı) **2003 ve 2008 olayları için veri içermez**.
Bu nedenle v5 merdiveninin L2 basamağı (S1 değişim tespiti) bu iki tarih için
fiziksel olarak mümkün değildir. Gerçekçi basamaklar:

- **L1:** GFD MODIS (`GLOBAL_FLOOD_DB/MODIS_EVENTS/V1`, 2000+): GEE kimliği ile.
- **L2′:** Literatür jeoreferansı (2003 Boğaçay / 2008 Kundu raporları).
- **L3:** Hiçbiri olmazsa ADR-0003 kalıcı + 3 deneme kaydı (U12).

Bu uyarı `docs/veri_merdiveni.md`'ye de işlenecek.
