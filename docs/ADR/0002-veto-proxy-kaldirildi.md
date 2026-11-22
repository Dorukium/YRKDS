# ADR-0002 — DEM tabanlı Hisarçandır VETO proxy'sinin kaldırılması

- Tarih: 2026-11-22
- Durum: Kabul

## Bağlam
"Hisarçandır 1965 afete maruz bölge" için jeoreferanslı resmi geometri yoktu.
Önceki sürüm "Konyaaltı + DEM>400 m + eğim>15°" proxy'si kullandı. Bu kural
Hisarçandır dışındaki (30.583, 36.852) dağlık hücrelerde yasal kısıt üretti —
yanlış pozitif.

## Karar
Dört yasal VETO katmanı da `NULL` bırakıldı; `yasal_kisit_durumu=dogrulanamadi`
üretiliyor ve karar "Uygun" olamıyor.

## Sonuçlar
- Yanlış yerde yasal kısıt üretme riski ortadan kalktı.
- Gerçek VETO artık yalnızca doğrulanmış geometri (Faz B) ile tetiklenir.
- K3 uyarınca proxy değil, bilinmeyen olarak etiketlendi.
