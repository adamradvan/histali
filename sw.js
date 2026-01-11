const CACHE_NAME = 'histali-1768123469';
const ASSETS_TO_CACHE = [
  '/histali/',
  '/histali/index.html',
  '/histali/data/sk.json',
  '/histali/icons/icon-192.png',
  '/histali/icons/icon-512.png',
  '/histali/icons/apple-touch-icon.png',
  '/histali/manifest.json',
  '/histali/robots.txt',
  '/histali/sitemap.xml'
];

// Install - cache assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS_TO_CACHE))
  );
  self.skipWaiting();
});

// Activate - clean old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((names) =>
      Promise.all(names.filter((n) => n !== CACHE_NAME).map((n) => caches.delete(n)))
    )
  );
  self.clients.claim();
});

// Fetch - Stale-While-Revalidate
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.match(event.request).then((cachedResponse) => {
        const fetchPromise = fetch(event.request).then((networkResponse) => {
          // Update cache with fresh response
          if (networkResponse && networkResponse.status === 200) {
            cache.put(event.request, networkResponse.clone());
          }
          return networkResponse;
        }).catch(() => cachedResponse); // Network failed, use cache

        // Return cached response immediately, or wait for network
        return cachedResponse || fetchPromise;
      });
    })
  );
});
