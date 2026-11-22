# Model Kartı (Mitchell vd.) — YRKDS Deterministik Skorlayıcı

## Model detayları
Python (`app/core/scoring.py`) + Rust (`skor_motoru/src/lib.rs`), PyO3 ile
aynı formül. **ML modeli eğitilmez**, parametreler spesifikasyondan sabittir.

## Amaç
Parsel bazlı göreli afet riski ön-tarama; "yapılabilir/koşullu/yapılmamalı"
karar metni üretimi (VETO ve KARARSIZ üst kurallarla).

## Eğitim/Doğrulama verisi
Eğitim yok. Kalibrasyon: 2009 ANT-2009 (17 pozitif). Bağımsız doğrulama:
yok (ADR-0003). Mekansal blok CV mevcut.

## Metrikler
Kalibrasyon Precision/Recall/F1 0.941; Wilson %95 CI [0.730, 0.990].
Bu sayılar bağımsız genelleme performansını göstermez.

## Etik değerlendirme
- Yanlış pozitif yasal kısıt riski: ADR-0002 ile proxy kaldırıldı.
- Yanlış güven riski: kısmi skor ve düşük güven cezası eklendi.
- Erişilebilirlik: WCAG 2.2 AA taraması (axe) yeşil.

## Sınırlılıklar
Parsel bazlı ölçüm az; ilçe sabitleri proxy; InSAR/SYGM/TDTH yok.
İnsan gözetimi zorunludur; nihai karar belediye yetkilisindedir.
