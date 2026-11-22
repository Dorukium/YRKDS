const { test, expect } = require('playwright/test');

test('harita açılır, parsel analiz edilir, PDF iner, konsol hatasız', async ({ page, request }) => {
  const errors = [];
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  page.on('pageerror', e => errors.push(String(e)));

  await page.goto('/harita.html', { waitUntil: 'networkidle' });
  await expect(page.locator('.durum .nişan').last()).toHaveText(/HAZIR/);
  expect(await page.locator('.leaflet-draw-draw-polygon').count()).toBe(1);

  await page.evaluate(() => window.YRKDraw.analizGeojson({
    type: 'Polygon',
    coordinates: [[[30.640, 36.880], [30.642, 36.880], [30.642, 36.882],
                   [30.640, 36.882], [30.640, 36.880]]],
  }));

  await expect(page.locator('.sonuc')).toBeVisible();
  await expect(page.locator('.skor-buyuk')).not.toHaveText('');
  await expect(page.locator('.metrikler b').nth(2)).toHaveText('DOĞRULANAMADI');
  expect(await page.locator('.sonuc .kanit').count()).toBeGreaterThan(3);

  const href = await page.locator('a.btn').getAttribute('href');
  const pdf = await request.get(href);
  expect(pdf.ok()).toBeTruthy();
  expect((await pdf.body()).slice(0, 4).toString()).toBe('%PDF');
  expect(errors).toEqual([]);
});
