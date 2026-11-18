// PaxVanila — сайт/PWA. Данные: content.json (собирается tools/build_site.py из content/paxvanila.json).
(function(){
const BASE=new URL('.', document.currentScript.src);
const EN=document.documentElement.lang==='en', T=(ru,en)=>EN?en:ru;
const $ = s => document.querySelector(s);
const esc = s => String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const code = s => `<code>${esc(s)}</code>`;
function toast(t){const e=$('#toast');e.textContent=t;e.classList.add('show');setTimeout(()=>e.classList.remove('show'),1800)}

// тема
try{const t=localStorage.getItem('theme');if(t)document.documentElement.dataset.theme=t}catch(e){}
const themeBtn=$('#theme'); if(themeBtn) themeBtn.onclick=()=>{
  const cur=document.documentElement.dataset.theme||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light');
  const n=cur==='dark'?'light':'dark';document.documentElement.dataset.theme=n;try{localStorage.setItem('theme',n)}catch(e){}};

if(innerWidth<860) document.querySelectorAll('.doc aside details').forEach(d=>d.open=false);
// PWA
if('serviceWorker' in navigator) navigator.serviceWorker.register(new URL('sw.js',BASE),{scope:BASE.pathname}).catch(()=>{});
let deferred=null; addEventListener('beforeinstallprompt',e=>{e.preventDefault();deferred=e;const b=$('#install');if(b){b.hidden=false;b.onclick=async()=>{deferred.prompt();await deferred.userChoice;b.hidden=true}}});

// ---- календарь сервера (та же логика, что в paxborder.sk / paxwar.sk / paxseasons.sk) ----
function radiusForDay(b,d){
  const r=Math.round;
  if(d<=6) return r(b.start+(b.w1-b.start)*d/6);
  if(d<=13) return r(b.w1+(b.w2-b.w1)*(d-6)/7);
  if(d<=20) return r(b.w2+(b.w3-b.w2)*(d-13)/7);
  if(d<=27) return r(b.w3+(b.w4-b.w3)*(d-20)/7);
  if(d<=34) return r(b.w4+(b.w5-b.w4)*(d-27)/7);
  if(d<=41) return r(b.w5+(b.w6-b.w5)*(d-34)/7);
  return b.w6;
}
const SEASONS=EN?['Spring «Sowing»','Summer «Expeditions»','Autumn «Harvest»','Winter «Winter Campaign»']:['Весна «Посевная»','Лето «Экспедиции»','Осень «Сбор урожая»','Зима «Зимняя кампания»'];
function serverState(cfg,now=new Date()){
  const st={started:false};
  // прайм-тайм по МСК (UTC+3)
  const msk=new Date(now.getTime()+3*3600e3), h=msk.getUTCHours(), m=msk.getUTCMinutes();
  st.prime=h>=cfg.primeFrom&&h<cfg.primeTo;
  const mins=h*60+m, from=cfg.primeFrom*60, to=cfg.primeTo*60;
  st.primeIn=st.prime?(to-mins):((from-mins+1440)%1440);
  if(!cfg.launchDate) return st;
  const t0=new Date(cfg.launchDate); if(isNaN(t0)) return st;
  const ms=now-t0; if(ms<0){st.until=Math.ceil(ms/-864e5);return st}
  st.started=true; const day=Math.floor(ms/864e5); st.day=day+1;
  st.week=day>=21?4:day>=14?3:day>=7?2:1; if(day>=28) st.week=day>=35?6:5;
  st.radius=radiusForDay(cfg.border,day); st.tomorrow=radiusForDay(cfg.border,day+1);
  st.season=day>=28?SEASONS[Math.floor((day-28)/7)%4]:null;
  st.warPhase=day>=28?T('Мир, итоги войны','Peace, war results'):day>=24?T('Великая война','The Great War'):day>=23?T('Мобилизация','Mobilisation'):day>=21?T('Формирование наций','Nations forming'):null;
  return st;
}
function fmtMin(n){const h=Math.floor(n/60),m=n%60;return EN?(h?`${h} h ${m} min`:`${m} min`):(h?`${h} ч ${m} мин`:`${m} мин`)}

async function main(){
  const C=await (await fetch('content.json')).json(), cfg=C.config;
  document.querySelectorAll('[data-k]').forEach(e=>{e.textContent=e.dataset.k in C?C[e.dataset.k]:cfg[e.dataset.k]||''});
  // IP и Discord
  const ipBtn=$('#copyip');
  if(ipBtn){ if(cfg.serverAddress){$('#ipText').textContent=cfg.serverAddress;ipBtn.onclick=()=>navigator.clipboard.writeText(cfg.serverAddress).then(()=>toast(T('Адрес скопирован','Address copied')))} else ipBtn.disabled=true;
    const d=$('#discord'); if(cfg.discordUrl) d.href=cfg.discordUrl; else {d.removeAttribute('href');d.style.opacity=.55;d.title=T('Ссылка появится перед открытием','The link will appear before launch')} }
  renderNow(C); setInterval(()=>renderNow(C),30000);
  const jl=$('#joinList'); if(jl) jl.innerHTML=C.join.map(x=>`<li>${esc(x)}</li>`).join('')+(cfg.serverAddress?`<li>${T('Адрес','Address')}: ${code(cfg.serverAddress)}</li>`:'');
  const st=serverState(cfg);
  const wg=$('#weekGrid'); if(wg) wg.innerHTML=C.weeks.map(w=>`<div class="week${st.started&&st.week===w.n?' cur':''}">
    <img loading="lazy" src="img/${esc(w.image.replace('.png','.jpg'))}" alt="${T('Неделя','Week')} ${w.n}">
    <div class="b"><div class="meta">${T('Неделя','Week')} ${w.n} · ${esc(w.days)} · ${T('граница','border')} ${esc(w.border)}</div><h3>${esc(w.title)}</h3><p>${esc(w.text)}</p>
    <div class="cmds">${w.commands.map(code).join('')}</div></div></div>`).join('');
  const mg=$('#mechGrid'); if(mg) mg.innerHTML=C.mechanics.map(m=>`<details class="card" id="m-${m.id}"><summary><h3><span class="em">${m.icon}</span>${esc(m.title)}</h3><p>${esc(m.summary)}</p></summary>
    <ul>${m.points.map(p=>`<li>${esc(p)}</li>`).join('')}</ul>${m.commands.length?`<div class="cmds">${m.commands.map(code).join('')}</div>`:''}</details>`).join('');
  const rl=$('#ruleList'); if(rl) rl.innerHTML=C.rules.map(r=>`<div class="rule"><h3>${esc(r.title)}</h3><ul>${r.items.map(i=>`<li>${esc(i)}</li>`).join('')}</ul></div>`).join('');
  // команды
  const rows=[]; C.mechanics.forEach(m=>m.commands.forEach(c=>rows.push([c,m.title,m.icon])));
  const seen=new Set(), uniq=rows.filter(r=>!seen.has(r[0])&&seen.add(r[0]));
  const ct=$('#cmdTable'); const draw=q=>{q=(q||'').toLowerCase();ct.innerHTML=uniq.filter(r=>!q||(r[0]+' '+r[1]).toLowerCase().includes(q)).map(r=>`<tr><td>${code(r[0])}</td><td>${r[2]} ${esc(r[1])}</td></tr>`).join('')||`<tr><td colspan="2">${T('Ничего не найдено','Nothing found')}</td></tr>`};
  if(ct){draw('');$('#q').oninput=e=>draw(e.target.value)}
  const ll=$('#loreList'); if(ll) ll.innerHTML=C.lore.map(l=>`<a href="lore/${l.id}.html"><div class="card"><h3>📜 ${esc(l.title)}</h3><p>${esc(l.subtitle)}</p></div></a>`).join('')+
    (C.guides||[]).map(g=>`<a href="guides/${g.id}.html"><div class="card"><h3>🧭 ${esc(g.title)}</h3><p>${esc(g.subtitle)}</p></div></a>`).join('');
  checkStatus(cfg);
}
function renderNow(C){
  const g=$('#nowGrid'); if(!g) return; const cfg=C.config, s=serverState(cfg);
  const cells=[];
  cells.push(`<div class="stat"><div class="l">${T('Сервер','Server')}</div><div class="v" id="stV"><span class="dot"></span>…</div><div class="s" id="stS">${cfg.serverAddress?esc(cfg.serverAddress):T('адрес появится перед открытием','the address will appear before launch')}</div></div>`);
  cells.push(`<div class="stat"><div class="l">${T('Окно боёв','Battle window')} ${cfg.primeFrom}–${cfg.primeTo} ${T('МСК','Moscow time')}</div><div class="v">${s.prime?T('⚔️ Открыто','⚔️ Open'):T('🕊️ Закрыто','🕊️ Closed')}</div><div class="s">${s.prime?T('закроется через ','closes in '):T('откроется через ','opens in ')}${fmtMin(s.primeIn)}</div></div>`);
  if(s.started){
    const w=C.weeks.find(x=>x.n===s.week);
    cells.push(`<div class="stat"><div class="l">${T('День сезона','Season day')}</div><div class="v">${s.day}</div><div class="s">${T('Неделя','Week')} ${s.week}: ${esc(w?w.title:'')}</div></div>`);
    cells.push(`<div class="stat"><div class="l">${T('Граница мира','World border')}</div><div class="v">${s.radius} ${T('бл.','blocks')}</div><div class="s">${T('завтра','tomorrow')} ${s.tomorrow}</div></div>`);
    if(s.warPhase) cells.push(`<div class="stat"><div class="l">${T('Эпоха государств','Age of Nations')}</div><div class="v" style="font-size:1.15rem">${s.warPhase}</div></div>`);
    if(s.season) cells.push(`<div class="stat"><div class="l">${T('Сезон','Season')}</div><div class="v" style="font-size:1.15rem">${s.season}</div></div>`);
  } else {
    cells.push(`<div class="stat"><div class="l">${T('Открытие','Launch')}</div><div class="v">${s.until?T('через '+s.until+' дн.','in '+s.until+' days'):T('скоро','soon')}</div><div class="s">${T('следите в Discord','follow us on Discord')}</div></div>`);
  }
  const old=$('#stV')?$('#stV').outerHTML:null; g.innerHTML=cells.join('');
  if(window._st) applyStatus(window._st);
}
function applyStatus(d){const v=$('#stV'),s=$('#stS');if(!v)return;
  if(d.online){v.innerHTML=`<span class="dot on"></span>${d.players.online}/${d.players.max}`;s.textContent=T('онлайн · ','online · ')+(d.version||'')}
  else {v.innerHTML='<span class="dot off"></span>'+T('Офлайн','Offline');}}
async function checkStatus(cfg){
  if(!cfg.serverAddress){const v=$('#stV');if(v)v.innerHTML='<span class="dot"></span>'+T('Скоро','Soon');return}
  try{const r=await fetch('https://api.mcsrvstat.us/3/'+encodeURIComponent(cfg.serverAddress));const d=await r.json();window._st=d;applyStatus(d)}
  catch(e){const v=$('#stV');if(v)v.innerHTML='<span class="dot"></span>'+T('Нет данных','No data')}
}
if(document.getElementById('nowGrid')||document.getElementById('loreList')) main();
window.PaxCalendar={serverState,radiusForDay};
})();
