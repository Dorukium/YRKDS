# ADR-0024 — OWASP ZAP düşük seviye uyarıları (D1)

- Tarih: 2026-11-22
- Durum: Kabul

## Sonuç
Yerel ZAP baseline taraması (`ghcr.io/zaproxy/zaproxy:stable`):
**FAIL-NEW: 0**, PASS 59, WARN-NEW 9. Uyarılar düşük seviye:
Cross-Origin-Embedder-Policy / Cross-Origin-Opener-Policy başlıkları ve
benzeri tarayıcı izolasyonu önerileri.

## Gerekçe
COEP/COOP başlıkları, harita karoları ve CDN kaynakları (OSM/Esri/Leaflet)
ile çelişebilir; mevcut CSP `frame-ancestors` ile gömme widget güvenliği
sağlanmıştır. Yüksek/kritik bulgu yoktur. Bu nedenle düşük uyarılar
bilinçli olarak kabul edilmiştir (K2: ADR + dürüst etiket).
