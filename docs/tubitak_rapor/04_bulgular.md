# 4. Bulgular

## 4.1 Skor haritası ve mekânsal dağılım

25 m ızgara üzerinde 799.594 hücre işlenmiştir. DEM kapsama oranı %100'dür
(ilk sürümdeki %22'lik tile sınır hatası giderilmiştir). SoilGrids WCS
katmanlarında soc dahil tüm özellikler %100 doludur. Kıyı maruziyeti
göstergesinde DEM yüksekliği 2 m ve altında olan 210.926 hücre, 5 m
altında olan 222.937 hücre belirlenmiştir. Bu hücreler Konyaaltı sahil
şeridi, Boğaçay ağzı ve densiz düşük alanlarda yoğunlaşır.

İlçe bazlı ortalama eğim, Vs30 ve kum oranları, jeolojik beklentilerle
uyumludur: Kepez'de sert traverten ve yüksek Vs30, Konyaaltı'nda yumuşak
alüvyon ve düşük Vs30 öne çıkar. Ancak skor haritası yalnızca ilçe
ortalamalarından ibaret değildir; DEM türevleri (eğim, TWI, HAND) ve OSM
akarsu mesafesi hücreler arasında fark yaratır. Sunucu tarafı PNG tile'lar
bu farkı harita üzerinde gösterir.

## 4.2 Tehlike kırılımı ve örnek parsel

Örnek bir Boğaçay parselinde skor 48.3 (Düşük-Orta) bulunmuştur. Kırılım
ZB 0.7, L 0.7, S NULL, H 0.0, F 0.85 şeklindedir. S bileşeninin NULL
olması nedeniyle skor "kısmi" olarak işaretlenmiş, güven 0.383'e
düşürülmüş ve karar "Koşullu — eksik bileşen: S" olarak verilmiştir.
Bu çıktı, sistemin eksik veri karşısında nasıl davrandığını gösteren
tipik bir örnektir: sayı üretilir ama kesinlik iddia edilmez.

VETO mekanizması, üç Resmî Gazete kararının geocode proxy geometrileri
üzerinden test edilmiştir. 2016/9615 sayılı kararla ilişkili Gülveren
Mahallesi merkezindeki bir test poligonu "Uygun Değil (Yasal Kısıt)"
kararı üretir; alan dışındaki poligon üretmez. Geometrilerin resmi sınır
olmadığı `konum_guveni=dusuk (geocode proxy)` alanıyla açıkça belirtilir
(ADR-0017).

## 4.3 Doğrulama sonuçları

2009 kalibrasyon verisinde Precision 0.941, Recall 0.941 ve F1 0.941
elde edilmiştir. Wilson %95 güven aralığı [0.730, 0.990] geniştir; 17
noktalık örneklem nedeniyle tek bir Recall değerine güvenilmemelidir.
Mekânsal blok bazlı doğrulamada çoğu ilçede Recall 0.60 üzerindedir;
Döşemealtı'nda etiket olmadığı için hesaplanamamıştır.

2003 ve 2008 olayları için Global Flood Database (Earth Engine), Sentinel-1
değişim tespiti ve literatür jeoreferans yöntemleri denenmiş; üçü de
kimlik veya koordinatlı etiket eksikliği nedeniyle başarısız olmuştur
(ADR-0018). Bu nedenle "bağımsız Recall ≥0.60" hedefi doğrulanamamış,
durum rapor ve arayüzde açıkça belirtilmiştir.

## 4.4 Sismik ve iklim çapraz kontrolleri

GEM GSHM v2023.1 PGA değerleri proje TDTH ilçe değerleriyle
karşılaştırılmıştır: Kepez %20.2, Muratpaşa %56.8, Konyaaltı %77.8
sapma bulunmuştur. Farkın ana nedeni GEM'in Vs30=800 kaya referansı,
proje değerlerinin ise zemin sınıfına göre düzeltilmiş olmasıdır
(ADR-0008). USGS Vs30 export uç noktası PNG görüntüsü döndürdüğü için
sayısal çapraz kontrol yapılamamıştır (ADR-0016).

ERA5 tabanlı Open-Meteo serisinde 1969-01-17 için 57.1 mm ızgara değeri
bulunmuş, istasyon kaydı 331.5 mm ile arasındaki fark ADR-0014'te
istasyon–ızgara ölçek farkı olarak açıklanmıştır. p99 günlük yağış
42.6 mm/gün olarak hesaplanmıştır.

## 4.5 Ürün ve kalite kapıları

Sistem, web haritası, what-if önlem modülü, portföy PDF'i, beklenen kayıp
görünümü, gömme widget, PWA saha modu ve İngilizce arayüz içerir. Tüm
kalite kapıları `make gate-all` ile tek komuttan çalışır: 83+ pytest,
%90 üzeri kapsam, Playwright E2E, axe-core, Lighthouse, k6 yük testi,
pip-audit/cargo audit ve SBOM üretimi. Son koşuda tüm kapılar yeşildir;
ayrıntılar docs/kanit.md'dedir.

Elde edilen bulguların genel yorumu şudur: sistem mühendislik kalitesi
ve şeffaflık açısından güçlü, ancak bilimsel geçerlilik açısından resmi
veri teminiyle sınırlıdır. Bu ayrım, jüri sunumunda ve belediye pilotunda
açıkça korunmalıdır.
