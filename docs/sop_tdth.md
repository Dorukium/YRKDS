# SOP — TDTH 2 km Izgara Sorgusu (İnsan Adımı, A6)

Bu adım e-Devlet kimlik doğrulaması gerektirdiği için **insan tarafından**
yapılır. Ajan bu adımı beklemez; GEM/OpenQuake ve USGS Vs30 çapraz
kontrolünü araştırma etiketiyle kurar. Veri gelince otorite katmanına
yükseltilir.

## Adımlar

1. `https://tdth.afad.gov.tr` adresini açın.
2. **e-Devlet ile giriş** yapın.
3. "Deprem Tehlike Parametreleri / Izgara Sorgulama" bölümüne gidin.
4. Çalışma alanını seçin: Antalya ili, Kepez / Muratpaşa / Konyaaltı ilçeleri.
5. Izgara aralığını **2 km** olarak ayarlayın (yaklaşık 230 nokta beklenir).
6. Her nokta için şu alanları sorgulayın: `PGA (g)`, `Ss (g)`, `S1 (g)`, `PGV (cm/s)`.
7. Sonuçları aşağıdaki başlıklarla CSV olarak kaydedin:
   `lon,lat,pga_g,ss_g,s1_g,pgv_cm_s`
8. Dosyayı proje kökünde `data/raw/tdth_grid.csv` olarak kaydedin. **Ham dosyayı düzenlemeyin.**
9. Ajan tarafından `make data-tdth` komutu çalıştırılır; SHA256 manifest'e yazılır,
   grid hücrelerine en yakın nokta atanır ve `pga_g` alanı Otorite rozetiyle dolár.

## Doğrulama
- Beklenen satır sayısı: 200–260 (AOI'ye bağlı).
- Değer aralığı: PGA 0.15–0.65 g, Ss 0.4–1.6 g, S1 0.15–0.7 g.
- Sapma >%20 olan hücreler için ADR-0008 güncellenir.

## Gelmezse
GEM/OpenQuake araştırma etiketli kalır; `pga_g` hücre bazında NULL ve güven
cezası uygulanır (K3). Hiçbir sayı üretilmez.
