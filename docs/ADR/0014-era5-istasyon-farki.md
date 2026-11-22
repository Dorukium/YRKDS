# ADR-0014 — ERA5 ızgara vs istasyon ekstremi (A5)

- Tarih: 2026-11-22
- Durum: Kabul

## Bulgu
Open-Meteo Archive API (ERA5 tabanlı, 36.90/30.70 hücresi) 1969-01-17 için
**57.1 mm** günlük toplam veriyor. Proje veri seti 3.13'teki Antalya istasyon
kaydı **331.5 mm**.

## Açıklama
ERA5 hücre ortalaması ~25–30 km ölçeğindedir; kısa süreli konvektif yağışın
nokta ölçümü bu değeri kat kat aşabilir. İki değer aynı büyüklükte değildir;
biri gök sürecinin alan ortalaması, diğeri istasyon extremidir.

## Karar
ERA5 serisi **Proxy — araştırma** rozetiyle saklanır; istasyon kaydı "proje
veri seti" etiketini korur. 331.5 mm resmi MGM doğrulaması yoktur (ADR-0012).
p99 = 42.6 mm/gün (1991–2024 seçili yıllar) göstergedir.
