const { test, expect } = require('playwright/test');

const SAYFALAR = ['/', '/harita.html', '/raporlar.html', '/veri-katalogu.html',
                  '/yontem.html', '/olay-izleme.html', '/yardim.html', '/login'];

test('navigasyon: tüm sayfalar açılır ve alt bilgi her sayfada var', async ({ page }) => {
  for (const yol of SAYFALAR) {
    const r = await page.goto(yol);
    expect(r.status()).toBeLessThan(400);
    await expect(page.locator('.ust-menu')).toBeVisible();
    await expect(page.locator('.alt-bilgi')).toBeVisible();
  }
});

test('sitemap ve tur', async ({ page }) => {
  await page.goto('/');
  const sitemap = await page.request.get('/sitemap.xml');
  expect(sitemap.ok()).toBeTruthy();
  expect((await sitemap.text())).toContain('/harita.html');
  await page.goto('/harita.html', { waitUntil: 'networkidle' });
  await expect(page.locator('#turKutu')).toBeVisible();
  await page.locator('#turKapat').click();
  await expect(page.locator('#turKutu')).toBeHidden();
});

test('giriş: yanlış parola hata gösterir', async ({ page }) => {
  await page.goto('/login');
  const csrf = await page.locator('input[name=csrf]').getAttribute('value');
  await page.fill('#kullanici', 'bilinmeyen_kullanici');
  await page.fill('#parola', 'YanlisBirParola2026!');
  expect(csrf).toBeTruthy();
  await page.locator('button[type=submit]').click();
  await expect(page.locator('.form-hata')).toContainText(/hatalı/i);
});

test('anonim admin alanına erişemez', async ({ request }) => {
  const r = await request.get('/admin/users', { maxRedirects: 0 });
  expect([401, 403]).toContain(r.status());
});

test('mobil viewport: harita ve sonuç paneli', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/harita.html', { waitUntil: 'networkidle' });
  await expect(page.locator('#harita')).toBeVisible();
  await expect(page.locator('.sag')).toBeVisible();
  const btn = page.locator('.arac-cubugu button').first();
  const box = await btn.boundingBox();
  expect(box.width).toBeGreaterThanOrEqual(40);
});
