const CACHE_NAME = "lifestack-cache-v1";
const OFFLINE_URLS = ["/", "/manifest.webmanifest"];
const QUEUE_NAME = "lifestack-queue";

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(OFFLINE_URLS);
    })
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key)))
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") {
    return;
  }
  event.respondWith(
    caches.match(event.request).then((cached) => {
      return (
        cached ||
        fetch(event.request)
          .then((response) => {
            const responseClone = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(event.request, responseClone));
            return response;
          })
          .catch(() => caches.match("/"))
      );
    })
  );
});

self.addEventListener("sync", (event) => {
  if (event.tag === QUEUE_NAME) {
    event.waitUntil(flushQueue());
  }
});

async function flushQueue() {
  const db = await openDB();
  const tx = db.transaction("queue", "readwrite");
  const store = tx.objectStore("queue");
  let cursor = await store.openCursor();
  while (cursor) {
    try {
      await fetch(cursor.value.url, cursor.value.options);
      await cursor.delete();
    } catch (error) {
      console.error("Background sync failed", error);
      break;
    }
    cursor = await cursor.continue();
  }
  await transactionComplete(tx);
}

function openDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open("lifestack-sync", 1);
    request.onupgradeneeded = () => {
      const db = request.result;
      if (!db.objectStoreNames.contains("queue")) {
        db.createObjectStore("queue", { autoIncrement: true });
      }
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

function transactionComplete(tx) {
  return new Promise((resolve, reject) => {
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
    tx.onabort = () => reject(tx.error);
  });
}
