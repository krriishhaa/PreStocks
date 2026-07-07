// PreStocks Service Worker — Offline support & caching
const CACHE_NAME = 'prestocks-v3';
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/css/style.css',
  '/css/pages.css',
  '/css/performance.css',
  '/js/app.js',
  '/js/performance.js',
  '/js/data/stocks.js',
  '/js/data/lessons.js',
  '/js/components/charts.js',
  '/js/components/portfolio.js',
  '/js/components/academy.js',
  '/js/components/predictor.js',
  '/js/components/visualizations.js',
  '/js/core/mobile.js',
  '/js/core/store.js',
  '/js/core/router.js',
  '/js/core/errorBoundary.js',
  '/js/core/tokens.js',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const { request } = event;

  if (request.method !== 'GET') return;

  // API calls: network-first, cache-fallback
  if (request.url.includes('/api/') || request.url.includes(':8000')) {
    event.respondWith(
      fetch(request)
        .then(response => {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(request, clone));
          return response;
        })
        .catch(() => caches.match(request))
    );
    return;
  }

  // Static assets: cache-first
  event.respondWith(
    caches.match(request).then(cached => cached || fetch(request))
  );
});

// Push notification handler
self.addEventListener('push', (event) => {
  const data = event.data ? event.data.json() : { title: 'PreStocks', body: 'New notification' };
  event.waitUntil(
    self.registration.showNotification(data.title, {
      body: data.body,
      icon: '/favicon.ico',
      badge: '/badge.png',
      data: data.url || '/',
      vibrate: [200, 100, 200]
    })
  );
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  event.waitUntil(clients.openWindow(event.notification.data));
});
