const { test, expect } = require('playwright/test');

test('ana sayfa görsel regresyon', async ({ page }) => {
  await page.goto('/', { waitUntil: 'networkidle' });
  await expect(page).toHaveScreenshot('anasayfa.png', {
    fullPage: true,
    // Canlı bloklar masked olsa da fullPage yüksekliğini değiştiriyordu;
    // layout'dan çıkararak snapshot'ı deterministik hale getiriyoruz.
    style: '#canliIstatistik, #sonOlaylar { display: none !important; }',
  });
});

test('harita sayfası görsel regresyon', async ({ page }) => {
  await page.goto('/harita.html', { waitUntil: 'networkidle' });
  await page.locator('#turKapat').click().catch(() => {});
  await expect(page).toHaveScreenshot('harita.png', {
    fullPage: false,
    mask: [page.locator('#harita'), page.locator('#katmanDurumu')],
  });
});
