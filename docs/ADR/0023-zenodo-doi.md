# ADR-0023 — Zenodo DOI (son kabul maddesi)

- Tarih: 2026-11-22
- Durum: **KAPANDI** — 2026-11-22, DOI `10.5281/zenodo.24449066`

Zenodo DOI almak için kurumsal/kişisel Zenodo hesabı ve depolama işlemi
gerekir; bu ortamda kimlik bilgisi yok. Semantik sürüm 3.0.0, CHANGELOG ve
MIT LICENSE hazırdır; DOI, yayın hesabı sağlandığında alınacaktır. Bu
eksiklik gizlenmez; son kabul kontrol listesinde "bekliyor" olarak işaretlidir.

## Kapanış (V5, 2026-11-22)
Kullanıcı Zenodo kişisel erişim anahtarını sağladı (`.env`, gitignore'da).
`make publish` → deposition 24449066 oluşturuldu, SBOM + CHANGELOG yüklendi,
yayınlandı ve **DOI `10.5281/zenodo.24449066`** üretildi. `CITATION.cff`,
`README.md` ve `docs/tubitak_rapor/01_ozet.md` DOI ile güncellendi.
Komut: `make publish` · Çıktı: `"durum": "ok"`.
