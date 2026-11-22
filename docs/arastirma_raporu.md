# Faz A — Kaynak Araştırma Raporu (2026-11-22)

Exa kotası nedeniyle Firecrawl MCP kullanıldı (conversationId:
`f041fb1f-577e-4e8c-b63f-67cdbd6c1a8e`). Tüm çıktılar K1 kanıt günlüğüne
bağlıdır. Erişim tarihi: **2026-11-22**.

## 1. Yasal VETO kararı (BULUNDU)

- **10 Ağustos 2026 tarihli, 11600 sayılı Cumhurbaşkanı Kararı**
- Dayanak: **7269 sayılı Kanun**
- Kapsam: Konyaaltı / Hisarçandır, Üçoluk, Gökdere mahallelerinin belirli
  bölümleri "Afete Maruz Bölge"; sınırlar **10 Kasım 2023 tarihli Jeolojik
  Etüt Raporu** ile sayısal olarak belirlenmiş.
- Kaynak: Antalya Körfez Gazetesi haberi (Firecrawl `query` çıktısı):
  https://www.antalyakorfez.com/antalyada-3-mahalle-afet-bolgesi-ilan-edildi-yapilasma-kisitlandi
- İkincil kaynak: Akdeniz Gerçek, 05.11.2024:
  https://www.akdenizgercek.com.tr/ozel-haber/bu-nasil-afet-bolgesi-yeniden-tespit-sart/311461

**Kritik bulgu:** Nominatim ile mahalle düzeyinde geocode başarısız; tek eşleşen
Hisarçandır köyü **36.7706, 30.4682** (mevcut 25 m grid'in dışında). Dolayısıyla
kararın **jeoreferanslı geometrisi yok** → K2/K3 uyarınca `legal_constraints`
kaydı `geom=NULL`, VETO "DOĞRULANAMADI" kalır. Proxy üretilmez (ADR-0002).

## 2. SYGM taşkın planı (KISMEN)

- Antalya Havzası Taşkın Yönetim Planı (SYGM, 26.12.2022) doğrudan URL'si
  artık 404 sayfası dönüyor.
- Güncelleme projesi SÇD taslak raporu (Aralık 2024, 149 sayfa) Firecrawl ile
  okundu; hedefli sorguda **100/500 yıllık tehlike alanı sayısal tabloları yok**
  yanıtı alındı.
- Kaynak: https://webdosya.csb.gov.tr/db/scd/icerikler/antalya-havzasi-typ---scd_taslak-20250206120431.pdf
- Yerel indirme TLS/kesilme nedeniyle başarısız → SHA256 yok (K5'te dürüst
  etiket: `indirilemedi`).
- Sonuç: F bileşeni otorite katman olmadan çalışmaya devam eder (proxy etiketli).

## 3. GEM sismik model (BULUNDU, indirilmedi)

- GEM Global Seismic Hazard Map **v2026.1**, PGA (10% aşılma / 50 yıl, Vs30=800).
- Zenodo kaydı https://zenodo.org/records/20735384
  (DOI 10.5281/zenodo.8409646), dosya `gshm_v2026_1_vector.zip` 935.5 MB,
  MD5 `7470e54534f4a4307a7310aa766ab11b`, lisans CC BY-NC-SA 4.0.
- Ticari kullanım planlandığı için CC BY-NC lisansı uyumsuz → ADR-0004'te
  lisans/kullanım kararı ve alternatif (kamuya açık hesaplama) değerlendirilir.
- Kaynak sayfa: https://www.globalquakemodel.org/product/global-seismic-hazard-map

## 4. Literatür (ANTALYA İÇİN BULUNAMADI)

"Antalya InSAR subsidence travertine" araması Karapınar/Konya çalışmalarını
döndürdü (ör. 15→70 mm/yıl, Orhan 2021). Antalya'ya özgü yayınlanmış mm/yıl
değeri bulunamadı → S bileşeni için mm/yıl **proxy üretilmez**; `NULL` kalır
(ADR-0003).

## 5. TÜİK / DSİ

TÜİK güncel bina istatistikleri ve DSİ kuyu serileri için kamuya açık sayfa
araması yapıldı; proje veri setindeki 3.12/3.13 değerleri kullanılmaya devam
edilir ve kaynak etiketi "proje veri seti" olarak kalır (K5).
