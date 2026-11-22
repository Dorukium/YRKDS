# 2. Giriş: Problem, Amaç ve Kapsam

## 2.1 Problem tanımı

Antalya, Türkiye'nin en hızlı kentleşen bölgelerinden biridir. Kentsel
büyüme, jeolojik açıdan karmaşık bir zemin üzerinde gerçekleşmektedir.
Kepez traverteni ve kireçtaşı, Muratpaşa traverten platosu ve kıyı
falezleri, Konyaaltı'nda Boğaçay alüvyonu, lagün çökelleri ve Beydağları
yamaçları birkaç kilometrelik mesafe içinde bir arada bulunur. Bu durum,
yatırım kararı verilecek bir parselin zemin davranışının komşu parselden
farklı olabileceği anlamına gelir.

Belediyelerin arsa tahsisi, kamu binası yapımı veya kentsel dönüşüm
kararlarında hızlı bir ön değerlendirme ihtiyacı vardır. Detaylı zemin
etüdü, sondaj ve laboratuvar çalışmaları zaman ve bütçe gerektirir; her
aday parsel için bu çalışmaların yapılması ön aşamada pratik değildir.
Buna karşılık, hiçbir ön değerlendirme yapmadan karar vermek de risksiz
değildir. İhtiyaç duyulan şey, ucuz, hızlı, tekrarlanabilir ve en
önemlisi hangi veriye dayandığını açıkça söyleyen bir ön-tarama
mekanizmasıdır.

Mevcut uygulamalarda iki yaygın eksiklik göze çarpar. Birincisi, risk
değerlendirmelerinin ilçe veya mahalle ortalaması düzeyinde kalmasıdır.
Bu yaklaşım, alüvyon dolgulu bir sahil mahallesi ile traverten plato
üzerindeki bir mahalleyi aynı sınıfa sokabilir. İkincisi, skor veya
sınıflandırmaların nasıl üretildiğinin şeffaf olmamasıdır. Kullanıcı,
"yüksek risk" etiketini gördüğünde hangi ölçümün bu sonucu doğurduğunu,
hangi katmanın eksik olduğunu ve kararın ne kadar güvenilir olduğunu
bilememektedir.

## 2.2 Amaç

Projenin birincil amacı, Antalya merkez üç ilçede 25 metrelik ortak bir
ızgara üzerinde çalışan, deterministik ve kural tabanlı bir risk
skorlama sistemi geliştirmektir. Sistem; (i) her parsel için 0–100 arası
bir skor, (ii) beş tehlike bileşeninin kırılımı, (iii) her sayının
kaynağını gösteren kanıt zinciri, (iv) veri tamlığı ve güven ifadesi,
(v) yasal kısıt durumunu içeren bir karar metni üretecektir.

İkincil amaçlar şunlardır: eksik verinin ölçüm gibi sunulmasını önlemek;
katmanların yetkinlik rozetleriyle (Otorite, Proxy, Tahmin, Araştırma,
Eksik) etiketlenmesini sağlamak; bilimsel dürüstlüğü kanıt günlüğü ve
karar kayıtları (ADR) ile kurumsallaştırmak; ve ürünü TÜBİTAK jürisine
ve belediye pilotuna sunulabilir bir web platformuna dönüştürmek.

## 2.3 Kapsam

Çalışma alanı Kepez, Muratpaşa ve Konyaaltı ilçelerini kapsar; koordinat
aralığı 30.58–30.86°D, 36.82–37.00°K'dır. Bu alan yaklaşık 800 bin 25 m
hücre içerir. Sistem beş tehlike bileşeni hesaplar: zemin büyütmesi,
sıvılaşma, oturma/çökme, heyelan/kaya düşmesi ve taşkın. Ek olarak dört
yasal VETO katmanı (fay sakınım bandı, afete maruz bölge, taşkın yapı
yasağı, falez çekme mesafesi) ve kıyı maruziyeti göstergesi bulunur.

Kapsam dışında kalan konular açıkça belirtilmelidir: sistem bina
yıkılabilirliği tahmini yapmaz; parsel bazlı sondaj verisi üretmez; resmi
imar izni yerine geçmez; ML modeli eğitmez; ve kurumlara resmi veri
talebinde bulunmaz. Yalnızca kamuya açık veri portalları kullanılır.
Erişilemeyen veriler için ADR yazılır ve alan NULL bırakılır.

## 2.4 Yaklaşımın gerekçesi

Deterministik kural tabanlı yaklaşım tercih edilmiştir çünkü: (1) mevcut
etiket sayısı (2009 seli için 18 nokta) bir ML modeli eğitmek için yetersizdir;
(2) kuralların denetlenebilir olması bilimsel dürüstlük açısından
zorunludur; (3) aynı girdi her zaman aynı skoru üretmelidir; (4) eksik veri
durumunda modelin "öğrendiği" sahte bir değer üretme riski ortadan kalkar.
Bu tercih, sistemin bir ön-tarama aracı olarak kalmasını ve nihai kararın
yetkili mühendis ve belediye organlarında kalmasını destekler.
