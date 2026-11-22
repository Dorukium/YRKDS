const { defineConfig } = require('playwright/test');

module.exports = defineConfig({
  testDir: '.',
  timeout: 60000,
  reporter: 'list',
  use: {
    baseURL: process.env.YRKDS_BASE_URL || 'http://localhost:80',
    headless: true,
    viewport: { width: 1440, height: 900 },
  },
});
