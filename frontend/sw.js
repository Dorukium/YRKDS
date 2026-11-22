/* B5 — saha modu: tile ve statik veri önbelleği, çevrimdışı uyarı. */
const VERSION = 'yrkds-v3';
const STATIK = ['/', '/harita.html', '/css/style.css', '/js/map.js',
  '/js/draw.js', '/js/v2.js', '/js/ux.js', '/assets/icons/favicon.svg',
  '/manifest.webmanifest'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(VERSION).then(c => c.addAll(STATIK)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== VERSION).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (url.origin !== location.origin) return;
  if (url.pathname.startsWith('/tiles/') || url.pathname.startsWith('/api/catalog')) {
    e.respondWith(caches.open(VERSION).then(async c => {
      const cached = await c.match(e.request);
      if (cached) return cached;
      try {
        const r = await fetch(e.request);
        if (r.ok) c.put(e.request, r.clone());
        return r;
      } catch (err) {
        return new Response(JSON.stringify({hata: 'Çevrimdışı — önbellekte yok'}),
          {status: 503, headers: {'Content-Type': 'application/json'}});
      }
    }));
  }
});
