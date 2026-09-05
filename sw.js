/* ============================================================
   Smart PLE — service worker (template; the build stamps the
   version below from the app file's content hash, so EVERY
   deployment automatically produces a new version).

   The whole application is ONE self-contained HTML file, so this
   worker caches exactly that document:
     • launch: served instantly from cache (fast, even on 2G)
     • in the background: a fresh copy is fetched and stored
     • every deployment: newly stamped sw.js -> browser installs
       the new worker -> old caches are deleted -> installed PWAs
       update themselves. No cache clearing, ever.

   Safety rules:
     • non-GET requests are never touched (auth, database writes)
     • cross-origin requests (Supabase, CDNs) always go to the
       network — never cached here
     • only caches whose names start with 'smart-ple-' are ever
       deleted, so other applications are never affected
   ============================================================ */
const VERSION = 'c9239eebaae8';
const CACHE = 'smart-ple-' + VERSION;

self.addEventListener('install', (e) => {
  e.waitUntil((async () => {
    const cache = await caches.open(CACHE);
    await cache.add(new Request('./', { cache: 'reload' }));   // the entire app
    await self.skipWaiting();
  })());
});

self.addEventListener('activate', (e) => {
  e.waitUntil((async () => {
    const names = await caches.keys();
    await Promise.all(
      names.filter(n => n.startsWith('smart-ple-') && n !== CACHE && n !== 'smart-ple-audio')
           .map(n => caches.delete(n)));
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;                    // never touch POST/PUT
  const url = new URL(req.url);
  if (url.origin !== location.origin) return;          // Supabase/CDN: network
  if (url.pathname.endsWith('sw.js')) return;          // never cache the worker
  if (url.pathname.includes('/audio/')) {
    /* lesson recordings: cached once on first play, kept across app
       updates (they are content, not app shell), refreshed by revalidation */
    e.respondWith(swrInto(req, 'smart-ple-audio'));
    return;
  }
  const isDoc = req.mode === 'navigate' ||
                (req.headers.get('accept') || '').includes('text/html');
  const target = isDoc ? new Request('./', { cache: 'reload' }) : req;
  e.respondWith(staleWhileRevalidate(target));
});

/* Serve the cached copy immediately, refresh it in the background. */
async function swrInto(req, cacheName) {
  const cache = await caches.open(cacheName);
  const cached = await cache.match(req);
  const fresh = fetch(req).then(async (res) => {
    if (res && res.ok) await cache.put(req, res.clone());
    return res;
  }).catch(() => null);
  if (cached) return cached;
  const res = await fresh;
  if (res) return res;
  return new Response('Offline and not yet cached.', { status: 503 });
}
async function staleWhileRevalidate(req) {
  const cache = await caches.open(CACHE);
  const cached = await cache.match(req);
  const fresh = fetch(req).then(async (res) => {
    if (res && res.ok) await cache.put(req, res.clone());
    return res;
  }).catch(() => null);
  if (cached) return cached;
  const res = await fresh;
  if (res) return res;
  return new Response('Offline and not yet cached.', { status: 503 });
}
