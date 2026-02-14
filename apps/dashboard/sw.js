// Service Worker — Dashboard App
const CACHE_NAME = 'dashboard-v1';
const ASSETS = [
    './',
    './index.html',
    './manifest.json',
    './css/dashboard.css',
    './js/config.js',
    './js/api.js',
    './js/i18n.js',
    './js/i18n/ja.js',
    './js/i18n/en.js',
    './js/websocket.js',
    './js/components.js',
    './js/pages/home.js',
    './js/pages/bookings.js',
    './js/pages/customers.js',
    './js/pages/devices.js',
    './js/pages/tables.js',
    './js/app.js',
    './assets/icon-192.png',
    './assets/icon-512.png',
    './assets/favicon.png'
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(ASSETS))
            .then(() => self.skipWaiting())
    );
});

self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys =>
            Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
        ).then(() => self.clients.claim())
    );
});

self.addEventListener('fetch', event => {
    const url = new URL(event.request.url);

    if (event.request.method !== 'GET' || url.pathname.startsWith('/api') || url.protocol === 'ws:') {
        return;
    }

    if (url.origin === location.origin) {
        event.respondWith(
            caches.match(event.request).then(cached => {
                const fetchPromise = fetch(event.request).then(response => {
                    if (response.ok) {
                        const clone = response.clone();
                        caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
                    }
                    return response;
                }).catch(() => cached);
                return cached || fetchPromise;
            })
        );
    }
});
