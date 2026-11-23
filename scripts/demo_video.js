/* C5 — YRKDS demo videosu (Playwright recordVideo, altyazılı, doğal tempolu).
 * Çıktı: docs/sunum/demo.webm → ffmpeg ile docs/sunum/demo.mp4
 */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const POLY = { type: 'Polygon', coordinates: [[[30.640, 36.880], [30.642, 36.880],
  [30.642, 36.882], [30.640, 36.882], [30.640, 36.880]]] };
const BASE = 'http://localhost';
const OUT = path.join('docs', 'sunum', 'video');
const HIZ = 6; // ~25 sn × 6 ≈ 2.5 dk
const bekle = ms => new Promise(r => setTimeout(r, ms * HIZ));

const ALTYAZI_CSS = `
  #demoAltYazi { position: fixed; left: 24px; bottom: 24px; right: 24px;
    background: rgba(11,18,32,.88); color: #fff; padding: 14px 20px;
    border-radius: 10px; font: 500 18px/1.4 system-ui, sans-serif;
    z-index: 999999; border-left: 4px solid #0F766E; pointer-events: none; }
`;

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({
    viewport: { width: 1280, height: 720 },
    recordVideo: { dir: OUT, size: { width: 1280, height: 720 } },
    deviceScaleFactor: 1,
  });
  await ctx.addInitScript(css => {
    document.addEventListener('DOMContentLoaded', () => {
      const d = document.createElement('div');
      d.id = 'demoAltYazi';
      document.body.appendChild(d);
    });
  }, ALTYAZI_CSS);
  const page = await ctx.newPage();
  const video = page.video();

  async function sahne(metin, ms) {
    await page.evaluate(({ css, metin }) => {
      let d = document.getElementById('demoAltYazi');
      if (!d) {
        const s = document.createElement('style'); s.textContent = css; document.head.appendChild(s);
        d = document.createElement('div'); d.id = 'demoAltYazi'; document.body.appendChild(d);
      }
      d.textContent = metin;
    }, { css: ALTYAZI_CSS, metin });
    await bekle(ms);
  }

  await page.goto(BASE + '/', { waitUntil: 'networkidle' });
  await page.addStyleTag({ content: ALTYAZI_CSS });
  await sahne('YRKDS — Antalya Yatırım Riski Karar Destek Sistemi. Deterministik, kanıtlı, belirsizliği açık.', 2500);

  await page.goto(BASE + '/harita.html', { waitUntil: 'networkidle' });
  await page.addStyleTag({ content: ALTYAZI_CSS });
  await page.locator('#turKapat').click().catch(() => {});
  await sahne('Haritayı açıyoruz: üç merkez ilçe, 25 metrelik ızgara.', 1800);

  await page.locator('[data-action=layers]').click().catch(() => {});
  await sahne('Katmanları açıp kapatıyoruz: zemin, sıvılaşma, InSAR, taşkın ve yasal kısıtlar.', 1200);
  await page.locator('[data-action=legend]').click().catch(() => {});
  await sahne('Lejant renk körlüğü güvenli Okabe-Ito paleti; her katmanın yetkinlik rozeti görünür.', 1200);

  await page.evaluate(p => window.YRKDraw.analizGeojson(p), POLY);
  await page.locator('.sonuc').waitFor({ state: 'visible' });
  const skor = await page.locator('.skor-buyuk').innerText().catch(() => '—');
  await sahne(`Parseli çizdik. Risk skoru ${skor}/100 — karar, bant ve kırılım kanıtlarla gösteriliyor.`, 2500);

  await page.locator('.sonuc').scrollIntoViewIfNeeded().catch(() => {});
  await sahne('Skor; zemin büyütme, sıvılaşma, oturma, heyelan ve taşkın bileşenlerinin ağırlıklı toplamı.', 1800);

  await page.locator('[data-sekme=ayarlar]').click().catch(() => {});
  await page.selectOption('#senaryoSec', 'ssp585_2050').catch(() => {});
  await page.evaluate(p => window.YRKDraw.analizGeojson(p), POLY);
  await sahne('What-if: 2050 SSP5-8.5 senaryosunda skor değişir; maliyet etkisi Tahmin rozetiyle etiketli.', 1800);

  await page.locator('[data-sekme=analiz]').click().catch(() => {});
  await page.fill('#tkEnlem', '36.9050').catch(() => {});
  await page.fill('#tkBoylam', '30.7050').catch(() => {});
  await page.locator('#tkgmButon').click().catch(() => {});
  await sahne('TKGM Parsel Sorgu ile koordinattan gerçek ada/parsel bilgisi aktarılıyor — Otorite rozeti.', 2000);

  await page.goto(BASE + '/veri-katalogu.html', { waitUntil: 'networkidle' });
  await page.addStyleTag({ content: ALTYAZI_CSS });
  await sahne('Veri kataloğu: Otorite, Proxy, Tahmin, Araştırma ve Eksik rozetleri. Eksik veri NULL ve güven cezası.', 1800);

  await page.goto(BASE + '/raporlar.html', { waitUntil: 'networkidle' });
  await page.addStyleTag({ content: ALTYAZI_CSS });
  await sahne('PDF rapor ve portföy çıktıları. Akademik atıf: DOI 10.5281/zenodo.24449066.', 1500);

  await page.goto(BASE + '/', { waitUntil: 'networkidle' });
  await page.addStyleTag({ content: ALTYAZI_CSS });
  await sahne('YRKDS v5.0 — Veri yoksa karar vermez; belirsizliği gizlemez. Teşekkürler.', 1500);

  await ctx.close();
  const hedef = path.join('docs', 'sunum', 'demo.webm');
  fs.copyFileSync(await video.path(), hedef);
  console.log('Video:', hedef, fs.statSync(hedef).size, 'bytes', 'skor:', skor);
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
