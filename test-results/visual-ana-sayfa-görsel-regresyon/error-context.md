# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: visual.spec.js >> ana sayfa görsel regresyon
- Location: tests/e2e/visual.spec.js:3:1

# Error details

```
Error: expect(page).toHaveScreenshot(expected) failed

  Expected an image 1440px by 2267px, received 1440px by 2311px. 232392 pixels (ratio 0.07 of all image pixels) are different.

  Snapshot: anasayfa.png

Call log:
  - Expect "toHaveScreenshot(anasayfa.png)" with timeout 5000ms
    - verifying given screenshot expectation
  - taking page screenshot
    - disabled all CSS animations
  - waiting for fonts to load...
  - fonts loaded
  - Expected an image 1440px by 2267px, received 1440px by 2311px. 232392 pixels (ratio 0.07 of all image pixels) are different.
  - waiting 100ms before taking screenshot
  - taking page screenshot
    - disabled all CSS animations
  - waiting for fonts to load...
  - fonts loaded
  - captured a stable screenshot
  - Expected an image 1440px by 2267px, received 1440px by 2311px. 232392 pixels (ratio 0.07 of all image pixels) are different.

```

# Page snapshot

```yaml
- generic [active] [ref=e1]:
  - banner [ref=e2]:
    - generic [ref=e3]:
      - link "YRKDS ana sayfa" [ref=e4] [cursor=pointer]:
        - /url: /
        - generic [ref=e5]: YRKDS
      - heading "Antalya Yatırım Riski Karar Destek Sistemi" [level=1] [ref=e7]
    - navigation "Ana menü" [ref=e8]:
      - link "Ana Sayfa" [ref=e9] [cursor=pointer]:
        - /url: /
      - link "Harita & Analiz" [ref=e10] [cursor=pointer]:
        - /url: /harita.html
      - link "Raporlar" [ref=e11] [cursor=pointer]:
        - /url: /raporlar.html
      - link "Veri Kataloğu" [ref=e12] [cursor=pointer]:
        - /url: /veri-katalogu.html
      - link "Yöntem" [ref=e13] [cursor=pointer]:
        - /url: /yontem.html
      - link "Olay İzleme" [ref=e14] [cursor=pointer]:
        - /url: /olay-izleme.html
      - link "Yardım" [ref=e15] [cursor=pointer]:
        - /url: /yardim.html
      - link "Giriş" [ref=e16] [cursor=pointer]:
        - /url: /login
      - combobox "Dil / Language" [ref=e17]:
        - option "TR" [selected]
        - option "EN"
    - button "Temayı değiştir" [ref=e19] [cursor=pointer]: ◐
  - main [ref=e20]:
    - generic [ref=e21]:
      - generic [ref=e22]:
        - heading "Antalya'da yatırım parsellerinin afet riskini şeffafça ön-tara" [level=2] [ref=e23]
        - paragraph [ref=e24]: Kepez, Muratpaşa ve Konyaaltı için 25 m grid üzerinde deterministik, kural tabanlı risk skoru üretir. Neden bu kararı verdiğimizi kanıtlarıyla gösteririz.
        - generic [ref=e25]:
          - link "Haritayı Aç" [ref=e26] [cursor=pointer]:
            - /url: /harita.html
          - link "Yöntemi İncele" [ref=e27] [cursor=pointer]:
            - /url: /yontem.html
      - generic [ref=e28]:
        - generic [ref=e29]:
          - generic [ref=e30]: Grid hücresi
          - generic [ref=e31]: "799.594"
        - generic [ref=e32]:
          - generic [ref=e33]: Olay kaydı
          - generic [ref=e34]: "45"
        - generic [ref=e35]:
          - generic [ref=e36]: Katman
          - generic [ref=e37]: "10"
        - generic [ref=e38]:
          - generic [ref=e39]: Veri durumu
          - generic [ref=e40]: InSAR/SYGM yok
    - generic [ref=e41]:
      - heading "Nasıl çalışır?" [level=2] [ref=e42]
      - generic [ref=e43]:
        - generic [ref=e44]:
          - heading "1 — Çiz" [level=3] [ref=e47]
          - paragraph [ref=e48]: Haritada parsel poligonunu çiz veya koordinat gir.
        - generic [ref=e49]:
          - heading "2 — Hesapla" [level=3] [ref=e53]
          - paragraph [ref=e54]: Beş tehlike bileşeni kuralla hesaplanır; eksik veri cezalandırılır.
        - generic [ref=e55]:
          - heading "3 — Raporla" [level=3] [ref=e59]
          - paragraph [ref=e60]: Gerekçeli PDF raporu ve GeoJSON çıktısını indir.
    - generic [ref=e61]:
      - heading "Risk bantları" [level=2] [ref=e62]
      - generic [ref=e63]:
        - generic [ref=e64]: Düşük0–25standart etüt
        - generic [ref=e65]: Düşük-Orta25–50zemin etüdü + drenaj
        - generic [ref=e66]: Orta-Yüksek50–70detaylı etüt
        - generic [ref=e67]: Yüksek70–85alternatif parsel
        - generic [ref=e68]: Kritik85–100uygun değil
      - generic [ref=e69]:
        - generic [ref=e70]: "VETO — yasal kısıt: skor ne olursa olsun \"Uygun Değil\"."
        - paragraph [ref=e71]: Renk körlüğü güvenli Okabe-Ito paleti kullanılır; tek başına renge güvenilmez.
    - generic [ref=e72]:
      - heading "Dürüst sınırlar" [level=2] [ref=e73]
      - generic [ref=e74]:
        - heading "Bu sistem neyi iddia etmez?" [level=3] [ref=e75]
        - list [ref=e76]:
          - listitem [ref=e77]: Yasal izin veya imar hakkı yerine geçmez.
          - listitem [ref=e78]: "\"Bina yıkılır / yıkılmaz\" demez; olasılıksal risk ve belirsizlik sunar."
          - listitem [ref=e79]: Eksik veriyi ölçüm gibi sunmaz; NULL bırakıp güveni düşürür.
          - listitem [ref=e80]: InSAR, SYGM taşkın haritası ve TDTH grid verisi bu kurulumda yoktur.
        - link "Tüm sınırlılıkların detayı →" [ref=e81] [cursor=pointer]:
          - /url: /yontem.html
    - generic [ref=e82]:
      - heading "Veri kaynakları" [level=2] [ref=e83]
      - generic [ref=e84]:
        - link "AFAD" [ref=e85] [cursor=pointer]:
          - /url: https://deprem.afad.gov.tr
        - link "MTA" [ref=e86] [cursor=pointer]:
          - /url: https://yerbilimleri.mta.gov.tr
        - link "MGM" [ref=e87] [cursor=pointer]:
          - /url: https://mgm.gov.tr
        - link "SYGM" [ref=e88] [cursor=pointer]:
          - /url: https://www.tarimorman.gov.tr/SYGM
        - link "Copernicus" [ref=e89] [cursor=pointer]:
          - /url: https://dataspace.copernicus.eu
        - link "SoilGrids" [ref=e90] [cursor=pointer]:
          - /url: https://soilgrids.org
        - link "OpenStreetMap" [ref=e91] [cursor=pointer]:
          - /url: https://www.openstreetmap.org
        - link "Resmî Gazete" [ref=e92] [cursor=pointer]:
          - /url: https://www.resmigazete.gov.tr
        - link "Veri Kataloğu" [ref=e93] [cursor=pointer]:
          - /url: /veri-katalogu.html
    - generic [ref=e94]:
      - heading "Son olaylar" [level=2] [ref=e95]
      - list [ref=e97]:
        - listitem [ref=e98]:
          - generic [ref=e99]: deprem
          - text: 0068-01-01 — Tsunami | MS 68 Misir depremi sonrasi tsunami Patara-Myra'yi vurdu
        - listitem [ref=e100]:
          - generic [ref=e101]: deprem
          - text: 0529-01-01 — Yikim | Demre-Myra bolgesi buyuk felaket
        - listitem [ref=e102]:
          - generic [ref=e103]: deprem
          - text: 1911-01-01 — Yivli Minare yikildi | Yivli Minare serefeden yikildi
        - listitem [ref=e104]:
          - generic [ref=e105]: deprem
          - text: 1914-10-03 — Antalya'da hissedildi | 4000 olum 17000 bina yikildi
        - listitem [ref=e106]:
          - generic [ref=e107]: deprem
          - text: 1926-03-18 — Antalya'da hissedildi | 27 olum
    - generic [ref=e108]:
      - heading "Örnek rapor" [level=2] [ref=e109]
      - generic [ref=e110]:
        - paragraph [ref=e111]:
          - text: Aşağıda örnek bir parsemin PDF raporu önizlenir. Kendi parseliniz için
          - link "Harita & Analiz" [ref=e112] [cursor=pointer]:
            - /url: /harita.html
          - text: yapın.
        - generic "Örnek PDF rapor" [ref=e113]:
          - paragraph [ref=e114]:
            - text: PDF önizleme desteklenmiyor.
            - link "Raporu indir" [ref=e115] [cursor=pointer]:
              - /url: /api/report/1.pdf
            - text: .
        - link "PDF indir" [ref=e117] [cursor=pointer]:
          - /url: /api/report/1.pdf
    - generic [ref=e118]:
      - heading "Sık sorulan sorular" [level=2] [ref=e119]
      - generic [ref=e120]:
        - group [ref=e121]:
          - generic "Neden ML yok?" [ref=e122] [cursor=pointer]
        - group [ref=e123]:
          - generic "Skor ne demek?" [ref=e124] [cursor=pointer]
        - group [ref=e125]:
          - generic "Veri eksikse ne olur?" [ref=e126] [cursor=pointer]
        - group [ref=e127]:
          - generic "Yasal geçerliliği var mı?" [ref=e128] [cursor=pointer]
        - group [ref=e129]:
          - generic "Kaynaklar nerede?" [ref=e130] [cursor=pointer]
        - group [ref=e131]:
          - generic "Nasıl katkı yapabilirim?" [ref=e132] [cursor=pointer]
  - contentinfo [ref=e133]:
    - generic [ref=e134]:
      - text: v5.0.0 · MIT ·
      - link "API docs" [ref=e135] [cursor=pointer]:
        - /url: /api/docs
    - link "Veri kaynakları" [ref=e136] [cursor=pointer]:
      - /url: /yardim.html#veri-kaynaklari
    - link "Erişilebilirlik beyanı" [ref=e137] [cursor=pointer]:
      - /url: /yardim.html#erisilebilirlik
    - link "KVKK" [ref=e138] [cursor=pointer]:
      - /url: /yardim.html#kvkk
    - link "İletişim" [ref=e139] [cursor=pointer]:
      - /url: /yardim.html#iletisim
```

# Test source

```ts
  1  | const { test, expect } = require('playwright/test');
  2  | 
  3  | test('ana sayfa görsel regresyon', async ({ page }) => {
  4  |   await page.goto('/', { waitUntil: 'networkidle' });
> 5  |   await expect(page).toHaveScreenshot('anasayfa.png', {
     |                      ^ Error: expect(page).toHaveScreenshot(expected) failed
  6  |     fullPage: true,
  7  |     mask: [page.locator('#canliIstatistik'), page.locator('#sonOlaylar')],
  8  |   });
  9  | });
  10 | 
  11 | test('harita sayfası görsel regresyon', async ({ page }) => {
  12 |   await page.goto('/harita.html', { waitUntil: 'networkidle' });
  13 |   await page.locator('#turKapat').click().catch(() => {});
  14 |   await expect(page).toHaveScreenshot('harita.png', {
  15 |     fullPage: false,
  16 |     mask: [page.locator('#harita'), page.locator('#katmanDurumu')],
  17 |   });
  18 | });
  19 | 
```