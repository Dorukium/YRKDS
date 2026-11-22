# Datasheet — YRKDS 25 m Grid ve Etiketler (Gebru vd.)

## Motivasyon
Belediye yatırım parselleri için afet riski ön-tarama skoru üretmek.
TÜBİTAK 2204-A; ticari ürün hedefi.

## Bileşim
799.594 hücre, EPSG:4326, 25 m; `data/processed/grid_25m.parquet`.
Ham kaynaklar: AWS Terrarium DEM, SoilGrids v2, OSM Overpass, MGM/TÜİK/AFAD
proje veri seti. Koordinatlar Antalya merkez üç ilçe + çevresi.

## Toplama süreci
REST/WMS/Overpass indirmeleri script'lerle; SHA256 manifest `data/raw/`.
İnsan müdahalesi: yok (otomatik). Örnekleme: SoilGrids ~1.1 km nokta, 551
istek, geçerli oran %32.8; 25 m'e bilineer enterpolasyon.

## Ön işleme
Havza doldurma + D8 + TWI + akış yolu HAND; ilçe bazlı jeoteknik profiller.
K3 uyarınca tüm vekil değerler "proxy/türetilmiş" etiketli.

## Kullanım
Deterministik skorlama, harita paneli, PDF rapor. **Karar amaçlı değil;**
yerinde etüt yerine geçmez.

## Dağıtım
MIT (proje kodu); veri kaynaklarının lisansları ayrıdır (OSM ODbL, SoilGrids
CC BY, Terrarium public, GEM CC BY-NC-SA — ürüne gömülmedi).

## Bakım
Ek veri (InSAR, SYGM, TDTH, yasal geometri) geldiğinde pipeline güncellenir;
eşikler yalnızca kalibrasyon setinde değiştirilir (K4).

## Sınırlılıklar
InSAR/YASS parsel ölçümü yok; yasal VETO geometrisi yok; 17 etiket; bağımsız
olay bazlı doğrulama yok. Ayrıntı: `docs/dogrulama_raporu.md`.
