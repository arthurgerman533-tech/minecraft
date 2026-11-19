// PaxVanila service worker: офлайн-кэш сайта. Версию меняет build_site.py.
const V='pax-en202611192258';
const CORE=["./", "index.html", "lore.html", "style.css", "app.js", "content.json", "icons/icon-192.png", "lore/predtechi.html", "lore/srednie.html", "lore/pozdnie.html", "lore/cataclysms.html", "lore/front.html", "lore/old_records.html", "lore/filosofy.html", "lore/religii.html", "lore/sudy.html", "guides/fokusy.html", "privacy.html", "img/week1.jpg", "img/week2.jpg", "img/week3.jpg", "img/week4.jpg", "img/week5.jpg", "img/week6.jpg", "img/about.jpg"];
self.addEventListener('install',e=>{e.waitUntil(caches.open(V).then(c=>c.addAll(CORE)).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==V).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))});
self.addEventListener('fetch',e=>{
  const u=new URL(e.request.url);
  if(e.request.method!=='GET') return;
  if(/\.apk$/i.test(u.pathname)) return; // APK качаем напрямую, мимо кэша
  if(u.origin!==location.origin){ // кэшируем только шрифты; статус, GitHub и живые данные — всегда из сети
    if(!/fonts\.(googleapis|gstatic)\.com$/.test(u.hostname)) return;
    e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request).then(res=>{const cp=res.clone();caches.open(V).then(c=>c.put(e.request,cp));return res}).catch(()=>r)));
    return;
  }
  e.respondWith(fetch(e.request).then(res=>{if(res.ok){const cp=res.clone();caches.open(V).then(c=>c.put(e.request,cp))}return res}).catch(()=>caches.match(e.request,{ignoreSearch:true})));
});
