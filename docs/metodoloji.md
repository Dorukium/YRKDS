# Metodoloji Notu (ISO 31000 / IPCC AR6)

## Risk bileşenleri

IPCC AR6 çerçevesinde risk = **Tehlike (H) × Maruziyet (E) × Kırılganlık (V)**.
YRKDS skoru bu çarpımı doğrudan hesaplamaz; deterministik bir **tehlike
endeksi** üretir ve belediye kararında maruziyet/kırılganlık bilgisini
kullanıcı girdisi olarak bekler. Bu ayrım kasıtlıdır: elimizde parsel bazlı
bina değeri/kırılganlık verisi yoktur (3.12 yalnızca ilçe toplamıdır).

| Kod | Sınıf | Açıklama |
|---|---|---|
| ZB | Tehlike | Zemin büyütmesi (sismik) |
| L | Tehlike | Sıvılaşma |
| S | Tehlike | Oturma/çökme |
| H | Tehlike | Heyelan/kaya düşmesi |
| F | Tehlike | Taşkın |
| VETO | Mevzuat | Yasal kısıt (skoru ezer) |
| güven | Belirsizlik | Veri tamlığı + kapsam cezası |

## ISO 31010 teknik eşlemesi

| Teknik | YRKDS'teki karşılığı |
|---|---|
| Kontrol listesi | VETO katmanları, veri tamlığı kontrol listesi |
| Risk indeksi / puan kartı | 0–100 skor ve alt puanlar |
| Senaryo analizi | 2009 sel kalibrasyonu, 2003/2008 (veri yok) |
| Duyarlılık analizi | ±%10 ağırlık pertürbasyonu, 200 koşu, p5–p95 |
| Olay ağacı | VETO → KARARSIZ → skor karar zinciri |

## Karar dili

Skor bir **olasılık** değildir; göreli risk sıralamasıdır. IPCC kalibre edilmiş
olasılık dili uyarınca güven ifadesi: ≥0.70 "yüksek güven", 0.40–0.70 "orta
güven", <0.40 "düşük güven — karar için yetersiz".

## Sınırlar

ML eğitimi yok; ek veri geldiğinde formül güncellenir, model "öğrenmez".
Tüm türetilmiş değerler kanıt zincirinde `kaynakli`/`turetilmis`/`eksik`
olarak etiketlenir.
