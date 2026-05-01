/**
 * Aetherstore Engine Service Worker
 * Caches heavy 3D assets (.glb, .gltf, textures) so returning shoppers have zero load times.
 */

const CACHE_NAME = 'aetherstore-3d-cache-v1';

// We want to cache specific heavy assets
const ASSET_EXTENSIONS = ['.glb', '.gltf', '.bin', '.png', '.jpg', '.jpeg', '.webp', '.ktx2', '.env'];

self.addEventListener('install', (event) => {
    // Skip waiting ensures the service worker activates immediately
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    // Claim clients immediately so caching starts working on the very first page load
    event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);

    // Check if the request is for a 3D asset
    const is3DAsset = ASSET_EXTENSIONS.some(ext => url.pathname.toLowerCase().endsWith(ext));

    if (is3DAsset && event.request.method === 'GET') {
        event.respondWith(
            caches.open(CACHE_NAME).then(async (cache) => {
                // Check if we already have it in the cache
                const cachedResponse = await cache.match(event.request);

                if (cachedResponse) {
                    console.log(`[ServiceWorker] Serving from cache: ${url.pathname}`);
                    return cachedResponse;
                }

                // If not in cache, fetch it from the network
                console.log(`[ServiceWorker] Fetching and caching: ${url.pathname}`);

                try {
                    const fetchResponse = await fetch(event.request);

                    // Only cache successful HTTP responses
                    if (fetchResponse.ok) {
                        // Clone the response because it can only be consumed once
                        cache.put(event.request, fetchResponse.clone());
                    }

                    return fetchResponse;
                } catch (err) {
                    console.error(`[ServiceWorker] Fetch failed for ${url.pathname}:`, err);
                    throw err; // Let the application handle the offline/failed state
                }
            })
        );
    }
    // If it's not a 3D asset, let the browser handle it normally
});
