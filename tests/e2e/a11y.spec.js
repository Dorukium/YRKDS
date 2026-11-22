const { test, expect } = require('playwright/test');
const AxeBuilder = require('@axe-core/playwright').default;

const SAYFALAR = ['/', '/harita.html', '/raporlar.html', '/veri-katalogu.html',
                  '/yontem.html', '/olay-izleme.html', '/yardim.html', '/login'];

for (const yol of SAYFALAR) {
  test(`WCAG 2.2 AA — ${yol}`, async ({ page }) => {
    await page.addInitScript(() => localStorage.setItem('yrkds-tur', '1'));
    await page.goto(yol, { waitUntil: 'networkidle' });
    if (yol.includes('harita')) {
      await page.locator('#turKapat').click({ force: true }).catch(() => {});
      await page.waitForTimeout(300);
    }
    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa'])
      .analyze();
    const onemli = results.violations.filter(v => ['critical', 'serious'].includes(v.impact));
    if (onemli.length) console.log(`${yol}: ${onemli.map(v => `${v.id}(${v.nodes.length})`).join(', ')}`);
    expect(onemli).toEqual([]);
  });
}

test('WCAG 2.2 AA — koyu tema harita', async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem('yrkds-tema', 'dark'));
  await page.goto('/harita.html', { waitUntil: 'networkidle' });
  const results = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']).analyze();
  const onemli = results.violations.filter(v => ['critical', 'serious'].includes(v.impact));
  if (onemli.length) console.log('koyu: ' + onemli.map(v => v.id).join(', '));
  expect(onemli).toEqual([]);
});
