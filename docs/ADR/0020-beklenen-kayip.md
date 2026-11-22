# ADR-0020 — Beklenen kayıp katsayıları (B3)

- Tarih: 2026-11-22
- Durum: Kabul

## Bağlam
B3, skor × maruziyet ile TL/yıl mertebesi istiyor. Parcel bazlı bina değeri
ve resmi hasar fonksiyonu mevcut değil; 3.12'de yalnızca ilçe toplam bina
değeri ve bina sayısı var.

## Karar
`birim_değer = ilçe toplam yapı değeri / ilçe bina sayısı` (TÜİK/proje veri seti),
`beklenen = birim_değer × bant_katsayısı`. Katsayılar (0.001/0.003/0.01/0.03/0.06)
uzman varsayımıdır, resmi hasar fonksiyonu DEĞİLDİR. Sonuç her yerde
**Tahmin**, **±%50 aralık** ve gerekçe metniyle gösterilir.

## Sonuç
Sayı, karar için değil portföy sıralaması ve farkındalık içindir; belediye
pilotunda resmi hasar eğrileriyle değiştirilmelidir.
