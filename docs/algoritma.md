# Algoritma (Spesifikasyon 2.1–2.4 + 2026-11 güvenlik revizyonu)

## Skor

```
skor = 100 × (0.25·ZB + 0.20·L + 0.25·S + 0.15·H + 0.15·F)
```

Her alt puan 0–1. Bir alt puanın birincil girdisi yoksa `None` üretilir,
**0 varsayılmaz**. Toplam skor mevcut alt puanların ağırlıkları yeniden
normalize edilerek hesaplanır; eksik bileşenler `skor_kapsami.eksik` içinde
ve `uyarilar` metninde açıkça bildirilir.

## Alt puan kuralları

| Kod | Kural |
|---|---|
| ZB | Vs30 ≥760→0.0, 360–760→0.3, 180–360→0.7, <180→1.0; fay <5 km +0.15, <15 +0.10, <35 +0.05 |
| L | YASS<3 m ve kum>60%→1.0; YASS<5 ve kum>40%→0.7; YASS<10→0.3; diğer→0.0 |
| S | InSAR >10 mm/y→1.0, 5–10→0.6, 1–5→0.3, <1→0.0; karst +0.2; turba +0.2; karst+yüksek yük +0.2 |
| H | Eğim >30°→1.0, 15–30→0.6, 5–15→0.2, <5→0.0; kaya düşmesi +0.2; heyelan envanteri →1.0 override |
| F | 100 yıllık→1.0; 500 yıllık→0.6; TWI>8→0.7; TWI>6 ve (HAND<5 m veya geçmiş≥2)→0.7; TWI>5→0.4; geçmiş 3+ olay +0.15 |

## Hidroloji (`app/core/hydro.py`)

Önceki sürümde TWI düz DEM'den, HAND 11×11 yerel minimum farkından
hesaplanıyordu. Şimdi:

1. **Priority-flood depresyon doldurma** (Barnes vd., 2014) — kapalı çukurlar
   taşma seviyesine yükseltilir.
2. **D8 akış birikimi** (O'Callaghan & Mark, 1984).
3. **TWI** = ln(a / tan β), a = birikim × hücre alanı / hücre genişliği.
4. **Gerçek HAND** — her hücre akış yoluyla ulaştığı kanal hücresine göre
   yüksekliği (Rennó vd., 2008). Kanal eşiği: 100 hücre ≈ 0.0625 km².

`tests/test_hydro.py` kapalı çukur, tek çıkışlı havza ve kanal/HAND
davranışlarını sentetik DEM'lerle doğrular.

## Kritik güvenlik revizyonu (2026-11)

Önceki sürümde Hisarçandır afete maruz bölgesi, "Konyaaltı + DEM>400 m +
eğim>15°" proxy'siyle temsil ediliyordu. Bu kural **Hisarçandır dışındaki**
(30.583, 36.852) dağlık hücrelerde yasal VETO üretiyordu — yanlış pozitif.

**Düzeltme:** Hiçbir yasal VETO katmanı için jeoreferanslı resmi geometri
olmadığından dört katman da (fay sakınım bandı, afete maruz bölge, taşkın
yapı yasağı, falez çekme mesafesi) `NULL` bırakılır. `veto=False` varsayılmaz;
`yasal_kisit_durumu="dogrulanamadi"` üretilir ve uyarı eklenir.

Ek kurallar:

- Bir ana bileşen eksikse (`skor_kapsami.tur="kısmi"`): güven
  `tamlık × ağırlık_kapsamı²` ile cezalandırılır ve karar asla "Uygun" olmaz.
- Kapsam %50 altındaysa sayısal skor gösterilmez (KARARSIZ).
- VETO katmanları kısmen/doğrulanamamışsa "Uygun" kararı "Koşullu"ya çevrilir.

## Veri tamlığı

dem .15 · soil .15 · jeoloji .10 · mikrobölge .15 · zemin hareketi .05 ·
fay .10 · insar .10 · taskin .10 · sondaj .05 · bina .05.
Güven = tamlık; eksik VETO katmanı varsa ×0.85, sondaj yoksa ×0.90,
eksik ana bileşen varsa ayrıca ×kapsam².

## Doğrulama (2009 sel)

17 pozitif ANT-2009 etiketi (su derinliği ≥0.5 m), 100 DEM-türevli negatif
kontrol hücre. Doğrulama ilçe bloklarıyla leave-one-district-out.

**Sonuç:** Precision 0.941 · **Recall 0.941** · F1 0.941 ·
Wilson %95 recall aralığı **[0.730, 0.990]**.

**Uyarı:** Eşikler aynı etiketler üzerinde kalibre edildiği için bu bir
**bağımsız doğrulama değildir**. Recall'ün geniş güven aralığı ve 17 noktalık
örneklem göz önüne alınırsa sistem yalnızca *ön tarama* aracıdır. ML eğitimi
yoktur.
