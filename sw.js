// オフラインでも遊べるよう、アプリ一式をキャッシュする。
// ファイルを更新したら VERSION を上げること。
const VERSION = 'v6';
const CACHE = `minna-asobo-${VERSION}`;
const FILES = [
  './',
  'index.html',
  'manifest.webmanifest',
  'css/style.css',
  'css/characters.css',
  'js/characters.js',
  'css/world.css',
  'js/world.js',
  'js/spots/oekaki.js',
  'css/spots/oekaki.css',
  'js/spots/tsumiki.js',
  'css/spots/tsumiki.css',
  'js/spots/mamagoto.js',
  'css/spots/mamagoto.css',
  'js/spots/sunaba.js',
  'css/spots/sunaba.css',
  'js/spots/suberidai.js',
  'css/spots/suberidai.css',
  'js/core.js',
  'js/app.js',
  'js/games/color-quiz.js',
  'css/games/color-quiz.css',
  'js/games/tama-ire.js',
  'css/games/tama-ire.css',
  'js/games/memory.js',
  'css/games/memory.css',
  'icons/icon.svg',
  'icons/icon-192.png',
  'icons/icon-512.png',
];

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(CACHE).then((c) => c.addAll(FILES)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim()),
  );
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;
  event.respondWith(
    caches.match(event.request, { ignoreSearch: true }).then((hit) => hit || fetch(event.request)),
  );
});
