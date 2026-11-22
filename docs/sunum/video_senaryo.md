# C5 — 3 Dakikalık Demo Video Senaryosu

Kayıt: 1920×1080, 30 fps, Playwright video export veya ekran kaydı.
Seslendirme metni sade Türkçe; jargon yok. Ekran görüntüleri `docs/sunum/frames/`
altına alınır (opsiyonel).

| Süre | Ekran | Seslendirme |
|---|---|---|
| 0:00–0:15 | Ana sayfa hero, canlı istatistikler | "Antalya'da bir arsaya yatırım yapacaksınız. Bu sistem o parselin afet riskini üç dakikada ön-tarar." |
| 0:15–0:30 | Üst menü, Harita & Analiz'e geçiş | "Haritayı açıyoruz. Merkez üç ilçe, 25 metrelik ızgara." |
| 0:30–0:45 | Kılavuz ray: Ara → Çiz → Sonuç → Rapor | "Dört adımlı kılavuz bize yol gösteriyor." |
| 0:45–1:00 | Katman aç/kapat, lejant, baz harita | "Katmanları açıp kapatabilir, lejanttan risk bantlarını okuyabiliriz." |
| 1:00–1:20 | Boğaçay çevresinde poligon çizimi | "Boğaçay yakınında bir parsel çiziyorum. Çift tıkla bitiriyorum." |
| 1:20–1:40 | Skor paneli: 48.3, Düşük-Orta | "Skor 48.3, Düşük-Orta bandı. Ama S bileşeni eksik, bu yüzden güven 0.38 ve karar koşullu." |
| 1:40–2:00 | Radar/çubuklar, kanıt zinciri, yetkinlik rozetleri | "Her sayının kaynağı ve yetkinliği görünüyor. Eksik veriyi gizlemiyoruz." |
| 2:00–2:20 | Önlem senaryosu: kazıklı temel + drenaj | "Kazıklı temel ve drenaj ekleyince skor düşüyor, maliyet yüksek rozeti çıkıyor. Bunlar tahmin." |
| 2:20–2:45 | Raporlar → Portföy Oluştur, 5 parsel PDF | "Beş aday parselden portföy raporu üretiyoruz; önerilen parsel ilk sayfada yazıyor." |
| 2:45–3:00 | Dürüst sınırlar slaytı + kapanış | "Sistem yıkım tahmini yapmaz, yasal izin yerine geçmez. Karar sizde." |

## Otomatik kayıt (opsiyonel)
`npx playwright test --config tests/e2e/playwright.config.js` koşusu sırasında
`recordVideo` açılarak ham görüntü alınabilir; kurgu için yukarıdaki zaman
çizelgesi kullanılır. Seslendirme ayrı kaydedilir.
