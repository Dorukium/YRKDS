# Tasarım Sistemi v1 (Ek plan Bölüm 4)

## Font
Inter (self-host `woff2`, OFL lisansı `frontend/assets/fonts/LICENSE-Inter.txt`):
400 gövde, 500 etiket, 600 başlık. Tablo rakamları `tabular-nums`.

## Renk — risk bantları (Okabe-Ito, renk körlüğü güvenli)
| Bant | Renk |
|---|---|
| Düşük | #009E73 |
| Düşük-Orta | #56B4E9 |
| Orta-Yüksek | #F0E442 |
| Yüksek | #E69F00 |
| Kritik | #D55E00 (metin için #A34300) |
| VETO | #CC79A7 çapraz tarama |
| NULL | gri noktalı desen |

Yüzey: açık #F8FAFC / koyu #0B1220 · kart #FFFFFF / #111827 · vurgu #0F766E
(koyu #2DD4BF) · odak halkası 2 px.

## Ölçek ve bileşenler
8 pt boşluk, 8 px radius, tek seviye gölge. Bileşenler: buton (3 boy), kart,
rozet, tablo, akordeon, modal, toast, skeleton, araç çubuğu, sekme paneli.
Örnekler: `frontend/index.html` ve `frontend/harita.html`.

## Tema ve hareket
`prefers-color-scheme` + manuel anahtar (`localStorage`). Geçişler 150–250 ms
ease-out; `prefers-reduced-motion` kapatır.

## Erişilebilirlik
Tüm etkileşimli öğeler klavye ile erişilebilir, `:focus-visible` halkası var,
hedef boyutu ≥24 px, sonuç paneli `aria-live`. axe-core tüm sayfalarda 0
kritik/ciddi; Lighthouse A11y 100.

## Kontrast raporu
Açık tema: metin #0B1220 / zemin #F8FAFC ≈ 18:1; muted #475569 / #F8FAFC ≈ 7:1;
vurgu #0F766E / beyaz ≈ 4.8:1. Koyu tema: #E5EDF5 / #0B1220 ≈ 15:1;
vurgu #2DD4BF / #0B1220 ≈ 11:1. Kritik metin #A34300 / beyaz ≈ 5.7:1.
Ölçüm kanıtı: `docs/lighthouse.json` + axe E2E çıktısı (`docs/kanit.md`).
