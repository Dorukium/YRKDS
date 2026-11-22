# 1. Özet

Bu proje, Antalya Büyükşehir Belediyesi'nin merkez üç ilçesinde (Kepez,
Muratpaşa, Konyaaltı) yatırım yapılacak parsellerin afet ve zemin riskini
deterministik bir yöntemle 0–100 arası skorlayan bir karar destek sistemi
geliştirmeyi amaçlamaktadır. Sistem, yatırım öncesi karar sürecinde
belediyeye hızlı, tekrarlanabilir ve gerekçeli bir ön-tarama sunar; nihai
mühendislik kararının yerine geçmez.

Çalışmanın temel motivasyonu, Antalya'nın karmaşık jeolojik yapısıdır:
traverten plato, alüvyon dolgular, lagün çökelleri, falezler ve aktif fay
zonları kısa mesafeler içinde bir araya gelir. Aynı ilçede, hatta aynı mahallede
bile zemin koşulları belirgin biçimde değişebilir. Dolayısıyla ilçe düzeyinde
tek bir risk sınıfı üretmek bilimsel olarak yetersizdir. Proje, 25 metrelik
ortak bir ızgara üzerinde her hücre için beş tehlike bileşeni hesaplar ve
bunları ağırlıklandırarak parsel düzeyinde bir skor üretir.

Yöntem, ISO 31000/31000 risk yönetimi çerçevesi ve IPCC AR6'nın tehlike–
maruziyet–kırılganlık ayrımıyla uyumlu biçimde kurgulanmıştır. Skor;
zemin büyütmesi (ZB), sıvılaşma (L), oturma/çökme (S), heyelan/kaya düşmesi
(H) ve taşkın (F) bileşenlerinden oluşur. Ağırlıklar 0.25, 0.20, 0.25, 0.15
ve 0.15'tir. Her alt puan 0–1 aralığındadır. Makine öğrenmesi
kullanılmaz; tüm kurallar denetlenebilir ve kaynak kodunda açıktır. Bu
tercih, küçük ve yanlı etiketli veri kümeleriyle eğitilmiş bir modelin
üretebileceği sahte kesinliği önlemek içindir.

Sistemin ayırt edici özelliklerinden biri "dürüst belirsizlik" ilkesidir.
Bir katmanın verisi yoksa sayısal değer üretilmez; alan NULL olarak bırakılır
ve güven skoru düşürülür. Eksik bir ana bileşen varsa çıktı "kısmi skor"
olarak işaretlenir, karar olumlu yönde verilemez. Veri tamlığı %40'ın
altındaysa sayısal skor hiç gösterilmez ve "veri yetersiz — sondaj/etüt
gerekli" mesajı üretilir. Benzer biçimde, yasal kısıt katmanları
doğrulanamamışsa VETO kuralı sessizce devre dışı bırakılmaz; kullanıcıya
"doğrulanamadı" uyarısı gösterilir.

Veri tabanı, Copernicus/Terrarium DEM, SoilGrids v2 WCS, OpenStreetMap bina
ve su yolları, MTA jeoloji, TBDY2018 mikrobölgeleme, AFAD/KOERI deprem
kataloğu, MGM iklim normalleri ve Resmî Gazete kararlarından oluşur. Her
sayısal alanın kaynağı, erişim tarihi, lisansı ve SHA256 özeti manifest
dosyalarında tutulur. Tüm işleme adımları script'lerle yapılır; ham veri
asla elle değiştirilmez.

Doğrulama çalışmasında 2009 sel olayı kalibrasyon için kullanılmıştır:
Precision ve Recall 0.941, Wilson %95 güven aralığı [0.730, 0.990] bulunmuştur.
Ancak 2003 ve 2008 olayları için mahalle düzeyinde koordinatlı etiket
bulunamadığından olay bazlı bağımsız doğrulama gerçekleştirilememiştir; bu
durum ADR-0003 ve ADR-0018'de açıkça belgelenmiştir. Mekânsal blok tabanlı
ayrım (leave-one-district-out) alternatif ölçüm olarak uygulanmıştır.
Sismik çapraz kontrolde GEM açık tehlike modeli "araştırma" rozetiyle
kullanılmış, resmi TDTH grid verisi erişilemediği için PGA hücre bazında
NULL bırakılmıştır.

Elde edilen ürün, web haritası üzerinden parsel çizimi, skor ve tehlike
kırılımı, kanıt zinciri, duyarlılık aralığı, PDF raporu, portföy raporu,
what-if önlem senaryoları ve gömme widget sunan bir platformdur. Yazılım
kalitesi açısından birim, entegrasyon, uçtan uca, erişilebilirlik, yük,
güvenlik ve görsel regresyon kapıları tek bir `make gate-all` komutuyla
çalıştırılmakta ve düzenli olarak yeşil sonuç vermektedir.

Sonuç olarak sistem, TÜBİTAK 2204-A kapsamında sunulabilecek olgunlukta bir
araştırma prototipidir; ancak resmi kurum verilerinin (EGMS InSAR, SYGM
taşkın paftaları, TDTH grid) temini ve saha uzmanı incelemesi tamamlanmadan
belediye pilotunda nihai karar aracı olarak kullanılması önerilmez. Bu
sınırlılık, raporun ilgili bölümlerinde ve ürün arayüzünde açıkça ifade
edilmektedir.

**Zenodo DOI:** [10.5281/zenodo.24449066](https://doi.org/10.5281/zenodo.24449066)
