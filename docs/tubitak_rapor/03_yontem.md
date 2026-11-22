# 3. Yöntem: Algoritma, Veri ve Doğrulama

## 3.1 Skor formülü

Skor, beş tehlike bileşeninin ağırlıklı toplamıdır:
`skor = 100 × (0.25·ZB + 0.20·L + 0.25·S + 0.15·H + 0.15·F)`.
Her alt puan 0–1 aralığındadır. Bir alt puanın birincil girdisi yoksa
değer None/NULL bırakılır, 0 varsayılmaz. Bu durumda toplam skor mevcut
alt puanların ağırlıkları yeniden normalize edilerek hesaplanır; eksik
bileşenler `skor_kapsami` alanında listelenir ve güven skoru kapsam
kareyle cezalandırılır. Kapsam %50 altındaysa sayısal skor gösterilmez.

ZB kuralı Vs30 eşiklerine dayanır: 760 m/s üzeri 0.0, 360–760 arası 0.3,
180–360 arası 0.7, altı 1.0. Fay mesafesi 5 km altındaysa +0.15, 15 km
altındaysa +0.10, 35 km altındaysa +0.05 eklenir. L kuralı yeraltı su
seviyesi ve kum oranını birleştirir: YASS<3 m ve kum>%60 → 1.0; YASS<5 m
ve kum>%40 → 0.7; YASS<10 m → 0.3. S kuralı InSAR hızını kullanır:
>10 mm/yıl → 1.0, 5–10 → 0.6, 1–5 → 0.3; karst, turba ve yüksek bina
yükü eklemeleri yapılır. H kuralı eğim ve heyelan envanterine dayanır:
>30° → 1.0, 15–30° → 0.6, 5–15° → 0.2; envanterde ise doğrudan 1.0.
F kuralı TWI, HAND, akarsu mesafesi ve geçmiş taşkın sayısını birleştirir;
resmi SYGM paftası olmadığı için bu bileşen "Proxy" etiketlidir.

Karar bantları 0–25 Düşük, 25–50 Düşük-Orta, 50–70 Orta-Yüksek, 70–85
Yüksek, 85–100 Kritik şeklindedir. VETO kuralları skoru ezerek "Uygun
Değil (Yasal Kısıt)" kararı üretir. Yasal katman doğrulanamamışsa "Uygun"
kararı verilemez; "Koşullu — yasal kısıt doğrulanamadı" ifadesi kullanılır.

## 3.2 Hidrolojik türevler

DEM'den eğim, Topografik Islaklık İndeksi (TWI) ve Height Above Nearest
Drainage (HAND) türetilir. Önce priority-flood algoritmasıyla kapalı
çukurlar doldurulur; ardından D8 yönleri ve akış birikimi hesaplanır. TWI
`ln(a/tanβ)` formülüyle, HAND her hücrenin akış yoluyla ulaştığı kanal
hücresinin yüksekliğine göre hesaplanır. Bu yöntem, önceki sürümdeki yerel
minimum farkı yaklaşımının yerini almıştır ve sentetik havza testleriyle
doğrulanmıştır.

## 3.3 Veri kaynakları ve işleme

DEM, AWS Terrarium (SRTM türevli, ADR-0001); toprak, SoilGrids v2 WCS
250 m; bina ve su yolları, OpenStreetMap Overpass; maruziyet, Planetary
Computer STAC item'leri (ESA WorldCover, Microsoft Buildings); iklim
ekstremleri, Open-Meteo/ERA5 (ADR-0014); deprem kataloğu, AFAD/KOERI;
yasal kararlar, Resmî Gazete (ADR-0017). Her dosya için URL, erişim
tarihi, lisans ve SHA256 manifest'te saklanır. Ham veri değiştirilmez;
tüm işleme tekrarlanabilir script'lerle yapılır.

25 m ızgara, DEM reprojeksiyonu ve zonal istatistiklerle üretilir. İlçe
bazlı jeoteknik profiller (Vs30, fay mesafesi, YASS, karst) "Tahmin"
etiketlidir; parsel bazlı ölçüm olarak sunulmaz.

## 3.4 Doğrulama ve duyarlılık

2009 sel etiketleri kalibrasyon verisidir: 17 pozitif nokta, Precision
0.941, Recall 0.941, Wilson %95 CI [0.730, 0.990]. 2003/2008 olayları için
koordinatlı etiket bulunamadığından olay bazlı bağımsız doğrulama
yapılamamıştır (ADR-0018); bunun yerine ilçe bloklarıyla mekânsal ayrım
kullanılmıştır. Eşikler hiçbir zaman doğrulama olarak adlandırılan bir
sette değiştirilmemiştir.

Küresel duyarlılık analizi SALib Morris yöntemiyle 2000 trajektör ve ±%20
pertürbasyonla yapılmıştır (docs/duyarlilik.md). Sonuç, temsilî örnekte H
bileşeninin %49.9, F'nin %25.6, ZB ve L'nin %12.2 payına sahip olduğunu
göstermiştir. S bileşeni örnekte NULL olduğu için skora etkisi sıfırdır;
bu, model Hatası değil veri eksikliğinin dürüst yansımasıdır.
