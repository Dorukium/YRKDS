const { test, expect } = require('playwright/test');

const POLY = { type: 'Polygon', coordinates: [[[30.640, 36.880], [30.642, 36.880],
  [30.642, 36.882], [30.640, 36.882], [30.640, 36.880]]] };

test('F1 kılavuz ray ve spotlight tur', async ({ page }) => {
  await page.goto('/harita.html', { waitUntil: 'networkidle' });
  await expect(page.locator('#kilavuzRay .ray-adim')).toHaveCount(4);
  await page.locator('#turKapat').click({ force: true }).catch(() => {});
  await page.locator('#kilavuzRay .ray-adim').nth(1).click({ force: true });
  await expect(page.locator('#turKutu')).toBeVisible();
  await expect(page.locator('#turBaslik')).toContainText('Çiz');
  await page.locator('#turKapat').click({ force: true });
  await expect(page.locator('#turKutu')).toBeHidden();
});

test('F8 komut paleti Ctrl+K', async ({ page }) => {
  await page.goto('/harita.html', { waitUntil: 'networkidle' });
  await page.keyboard.press('Control+k');
  await expect(page.locator('#komutPaleti')).toBeVisible();
  await page.locator('#komutPaleti input').fill('yöntem');
  await expect(page.locator('#komutPaleti li button').first()).toContainText('Yöntem');
  await page.locator('#komutPaleti [data-kapat]').click();
  await expect(page.locator('#komutPaleti')).toBeHidden();
});

test('F4 senaryo skoru değiştirir ve rozet gösterir', async ({ page }) => {
  await page.goto('/harita.html', { waitUntil: 'networkidle' });
  await page.evaluate(p => window.YRKDraw.analizGeojson(p), POLY);
  await expect(page.locator('.sonuc')).toBeVisible();
  const bugun = await page.locator('.skor-buyuk').innerText();
  await page.locator('[data-sekme=ayarlar]').click();
  await page.selectOption('#senaryoSec', 'ssp585_2050');
  await page.evaluate(p => window.YRKDraw.analizGeojson(p), POLY);
  await expect(page.locator('.skor-buyuk')).not.toHaveText(bugun);
  const ssp = await page.locator('.skor-buyuk').innerText();
  expect(Number(ssp)).toBeGreaterThan(Number(bugun));
  await expect(page.locator('.sonuc')).toContainText('Tahmin');
});

test('F5 derin bağlantı', async ({ request }) => {
  const r = await request.post('/api/analyze', { data: { geojson: POLY } });
  expect(r.ok()).toBeTruthy();
  const j = await r.json();
  const id = j.parsel_id.split(':')[0];
  const q = await request.get(`/api/query/${id}`);
  expect(q.ok()).toBeTruthy();
  expect((await q.json()).parsel_id).toBe(j.parsel_id);
});

test('U7 katalog rozetleri ve G1 tasarım galerisi', async ({ page, request }) => {
  const r = await request.get('/api/catalog');
  const k = await r.json();
  expect(k.length).toBeGreaterThan(8);
  expect(k.every(x => ['Otorite', 'Proxy', 'Tahmin', 'Araştırma', 'Eksik'].includes(x.yetkinlik))).toBeTruthy();
  await page.goto('/veri-katalogu.html', { waitUntil: 'networkidle' });
  await expect(page.locator('.rozet').first()).toBeVisible();
  await page.goto('/design.html');
  await expect(page.locator('.bantlar .bant-kutu')).toHaveCount(5);
});

test('F6 tile PNG', async ({ request }) => {
  const r = await request.get('/tiles/11/1200/770.png');
  expect(r.ok()).toBeTruthy();
  expect(r.headers()['content-type']).toContain('image/png');
});
