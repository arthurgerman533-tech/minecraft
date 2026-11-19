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
// установка на телефон: кнопка видна всегда; если браузер умеет «установить» — сразу диалог, иначе листаем к инструкции
let deferred=null;
const isIOS=/iphone|ipad|ipod/i.test(navigator.userAgent)||(navigator.platform==='MacIntel'&&navigator.maxTouchPoints>1);
const standalone=matchMedia('(display-mode: standalone)').matches||navigator.standalone===true;
function installClick(){
  if(deferred){deferred.prompt();deferred.userChoice.then(r=>{if(r.outcome==='accepted')toast(T('Приложение установлено','App installed'))});deferred=null;return}
  const a=$('#app'); if(a){a.scrollIntoView({behavior:'smooth',block:'start'});a.classList.add('flash');setTimeout(()=>a.classList.remove('flash'),1600)}
  toast(isIOS?T('Safari: «Поделиться» → «На экран Домой»','Safari: Share → Add to Home Screen'):T('Меню ⋮ → «Установить приложение»','Menu ⋮ → Install app'));
}
['#install','#install2'].forEach(id=>{const b=$(id);if(b){b.hidden=standalone;b.onclick=installClick}});
addEventListener('beforeinstallprompt',e=>{e.preventDefault();deferred=e});
addEventListener('appinstalled',()=>{deferred=null;['#install','#install2'].forEach(id=>{const b=$(id);if(b)b.hidden=true})});
(function(){
  const st=$('#appState'); if(!st) return;
  if(standalone) st.textContent=T('Вы уже открыли сайт как приложение. Всё установлено.','You are already using the installed app.');
  if(isIOS){const a=$('#stepsAndroid'),i=$('#stepsIOS');if(a&&i)i.parentNode.insertBefore(i,a)}
})();

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
  const C=await (await fetch('content.json?v=20261119225718')).json(), cfg=C.config;
  document.querySelectorAll('[data-k]').forEach(e=>{e.textContent=e.dataset.k in C?C[e.dataset.k]:cfg[e.dataset.k]||''});
  // IP и Discord
  const ipBtn=$('#copyip');
  if(ipBtn){ if(cfg.serverAddress){$('#ipText').textContent=cfg.serverAddress;ipBtn.onclick=()=>navigator.clipboard.writeText(cfg.serverAddress).then(()=>toast(T('Адрес скопирован','Address copied')))} else ipBtn.disabled=true;
    const d=$('#discord'); if(cfg.discordUrl) d.href=cfg.discordUrl; else {d.removeAttribute('href');d.style.opacity=.55;d.title=T('Ссылка появится перед открытием','The link will appear before launch')} }
  document.querySelectorAll('[data-boosty]').forEach(a=>{if(cfg.boostyUrl)a.href=cfg.boostyUrl;else a.hidden=true});
  renderNow(C); setInterval(()=>renderNow(C),30000);
  const apk=$('#apk'); if(apk&&cfg.appRepo&&!isIOS){
    fetch(`https://api.github.com/repos/${cfg.appRepo}/releases/tags/app-latest`).then(r=>r.ok?r.json():null).then(r=>{
      const f=r&&(r.assets||[]).find(x=>/\.apk$/i.test(x.name)); if(f){apk.href=f.browser_download_url;apk.hidden=false;
        apk.textContent=T('⬇️ Скачать APK для Android','⬇️ Download APK for Android')+` (${Math.round(f.size/1048576)} MB)`}}).catch(()=>{});
  }
  const apk2=$('#apk2'); if(apk2&&!isIOS) fetch('files/PaxVanila.apk',{method:'HEAD',cache:'no-store'}).then(r=>{if(r.ok){apk2.hidden=false;const n=+r.headers.get('content-length');if(n)apk2.textContent+=` (${Math.round(n/1048576)} MB)`}}).catch(()=>{});
  const jl=$('#joinList'); if(jl) jl.innerHTML=C.join.map(x=>`<li>${esc(x)}</li>`).join('')+(cfg.serverAddress?`<li>${T('Адрес','Address')}: ${code(cfg.serverAddress)}</li>`:'');
  const st=serverState(cfg);
  const wg=$('#weekGrid'); if(wg) wg.innerHTML=C.weeks.map(w=>`<div class="week${st.started&&st.week===w.n?' cur':''}">
    <img loading="lazy" src="img/${esc(w.image.replace('.png','.jpg'))}" alt="${T('Неделя','Week')} ${w.n}">
    <div class="b"><div class="meta">${T('Неделя','Week')} ${w.n} · ${esc(w.days)} · ${T('граница','border')} ${esc(w.border)}</div><h3>${esc(w.title)}</h3><p>${esc(w.text)}</p>
    <div class="cmds">${w.commands.map(code).join('')}</div></div></div>`).join('');
  const mg=$('#mechGrid'); if(mg) mg.innerHTML=C.mechanics.map(m=>`<details class="card" id="m-${m.id}"><summary><h3><span class="em">${m.icon}</span>${esc(m.title)}</h3><p>${esc(m.summary)}</p></summary>
    <ul>${m.points.map(p=>`<li>${esc(p)}</li>`).join('')}</ul>${m.commands.length?`<div class="cmds">${m.commands.map(code).join('')}</div>`:''}</details>`).join('');
  const dn=$('#donate'); if(dn&&C.donate){const D=C.donate,u=cfg.donateUrl;dn.innerHTML=`<h3><span class="em">💛</span>${esc(D.title)}</h3><p>${esc(D.text)}</p><div class="tiers">${(D.tiers||[]).map(t=>`<div class="tier tier-${esc(t.id)}"><div class="tn">${esc(t.name)}</div><div class="tp">${esc(t.price)}</div><ul>${t.items.map(r=>`<li>${esc(r)}</li>`).join('')}</ul>${t.button?(u?`<a class="btn primary" href="${esc(u)}" target="_blank" rel="noopener">${esc(t.button)}</a>`:`<button class="btn primary" disabled>${esc(t.button)}</button><p class="soon">${esc(D.soon)}</p>`):''}</div>`).join('')}</div>${D.note?`<p class="soon">${esc(D.note)}</p>`:''}`} else if(dn) dn.remove();
  const rl=$('#ruleList'); if(rl) rl.innerHTML=C.rules.map(r=>`<div class="rule"><h3>${esc(r.title)}</h3><ul>${r.items.map(i=>`<li>${esc(i)}</li>`).join('')}</ul></div>`).join('');
  // команды
  const rows=[]; C.mechanics.forEach(m=>m.commands.forEach(c=>rows.push([c,m.title,m.icon])));
  const seen=new Set(), uniq=rows.filter(r=>!seen.has(r[0])&&seen.add(r[0]));
  const ct=$('#cmdTable'); const draw=q=>{q=(q||'').toLowerCase();ct.innerHTML=uniq.filter(r=>!q||(r[0]+' '+r[1]).toLowerCase().includes(q)).map(r=>`<tr><td>${code(r[0])}</td><td>${r[2]} ${esc(r[1])}</td></tr>`).join('')||`<tr><td colspan="2">${T('Ничего не найдено','Nothing found')}</td></tr>`};
  if(ct){draw('');$('#q').oninput=e=>draw(e.target.value)}
  const ll=$('#loreList'); if(ll) ll.innerHTML=C.lore.map(l=>`<a href="lore/${l.id}.html"><div class="card">${l.cover?`<img class="cv" src="img/${l.cover}" alt="" loading="lazy" style="display:block;width:100%;max-width:100%;height:auto;aspect-ratio:16/9;object-fit:cover;border-radius:10px;margin:0 0 12px">`:''}<h3>📜 ${esc(l.title)}</h3><p>${esc(l.subtitle)}</p></div></a>`).join('')+
    (C.guides||[]).map(g=>`<a href="guides/${g.id}.html"><div class="card"><h3>🧭 ${esc(g.title)}</h3><p>${esc(g.subtitle)}</p></div></a>`).join('');
  renderMap(C);
  renderNether(C);
  renderEarth(C);
  renderRoster(C);
  renderWeather(C);
  checkStatus(cfg);
}
// ---- Державы и игроки (C.roster: content/players.json + content/nations_towny.json) ----
function renderRoster(C){
  const R=C.roster, host=$('#roster'); if(!R||!host){const s=$('#nations');if(s)s.remove();return}
  const X=R.text||{}; $('#rsKicker').textContent=X.kicker||''; $('#rsTitle').textContent=X.title||''; $('#rsSub').textContent=X.sub||'';
  const rows=R.rows, blocs=Object.assign({},C.map&&C.map.blocs||{},{new:T('Новые державы','New powers')});
  const ST={taken:[T('Занята','Taken'),'ok'],open:[T('Свободна','Free'),'free'],closed:[T('Закрыта','Closed'),'off'],new:[T('Новая','New'),'new']};
  const sum=k=>rows.reduce((a,r)=>a+(k==='towns'?r.towns.length:r[k]),0);
  const playersN=new Set(rows.flatMap(r=>r.players)).size, taken=rows.filter(r=>r.status==='taken'||r.status==='new').length;
  const started=rows.some(r=>r.towns.length);
  let filt='', sortK='', open=new Set();
  const tile=(n,l)=>`<div class="rstile"><b>${n}</b><span>${esc(l)}</span></div>`;
  const fl=[['',T('Все','All')],['open',T('Свободные','Free')],['taken',T('Занятые','Taken')],...Object.entries(blocs).filter(([k])=>rows.some(r=>r.bloc===k)).map(([k,v])=>['b:'+k,v])];
  const draw=()=>{
    let L=rows.filter(r=>!filt||(filt.startsWith('b:')?r.bloc===filt.slice(2):filt==='taken'?(r.status==='taken'||r.status==='new'):r.status===filt));
    if(sortK) L=[...L].sort((a,b)=>sortK==='towns'?b.towns.length-a.towns.length||b.residents-a.residents:sortK==='residents'?b.residents-a.residents:a.name.localeCompare(b.name));
    const th=(k,l,cls='')=>`<th class="${cls}">${k?`<button data-s="${k}" class="${sortK===k?'on':''}">${esc(l)}${sortK===k?' ↓':''}</button>`:esc(l)}</th>`;
    host.querySelector('.rsbody').innerHTML=`<table class="rstable"><thead><tr>${th('name',T('Держава','Power'))}${th('',T('Правитель','Ruler'))}${th('',T('Игроки','Players'))}${th('towns',T('Города','Towns'),'n')}${th('residents',T('Жители','Residents'),'n')}${th('',T('Статус','Status'))}</tr></thead><tbody>${L.map(r=>{
      const [sl,sc]=ST[r.status]||ST.open, isOpen=open.has(r.id), pl=r.players.filter(p=>p!==r.ruler);
      return `<tr class="rsrow${isOpen?' open':''}" data-id="${esc(r.id)}" tabindex="0" style="--c:${esc(r.color)}">
        <td data-l="${T('Держава','Power')}"><span class="rsdot"></span><b>${esc(r.name)}</b>${r.full!==r.name?`<small>${esc(r.full)}</small>`:''}<small class="rsbloc">${esc(blocs[r.bloc]||'')}</small></td>
        <td data-l="${T('Правитель','Ruler')}">${r.ruler?esc(r.ruler):'<span class="muted">—</span>'}${r.king&&r.king!==r.ruler?`<small>${T('король в Towny','Towny king')}: ${esc(r.king)}</small>`:''}</td>
        <td data-l="${T('Игроки','Players')}">${pl.length?pl.map(esc).join(', '):'<span class="muted">—</span>'}</td>
        <td data-l="${T('Города','Towns')}" class="n"><b>${r.towns.length}</b></td>
        <td data-l="${T('Жители','Residents')}" class="n">${r.residents}</td>
        <td data-l="${T('Статус','Status')}"><span class="rsst rs-${sc}">${esc(sl)}</span></td></tr>
        ${isOpen?`<tr class="rsdet"><td colspan="6">${r.note?`<p>${esc(r.note)}</p>`:''}${r.towns.length?`<p class="muted">${T('Столица','Capital')}: <b>${esc(r.capital)}</b></p><ul class="rstowns">${r.towns.map(t=>`<li><b>${esc(t.name)}</b>${t.name===r.capital?' ★':''} · ${T('мэр','mayor')} ${esc(t.mayor||'—')} · ${t.residents} ${T('жит.','res.')}</li>`).join('')}</ul>`:`<p class="muted">${r.status==='open'?T('Держава свободна. Её можно занять.','This power is free to claim.'):T('Городов пока нет. Они появятся после старта сервера.','No towns yet. They will appear after the server opens.')}</p>`}${r.towny?`<p class="muted">${T('Нация в Towny','Towny nation')}: ${code(r.towny)}</p>`:''}</td></tr>`:''}`}).join('')}</tbody></table>`;
  };
  host.innerHTML=`<div class="rstiles">${tile(`${taken}/${rows.length}`,T('держав занято','powers taken'))}${tile(playersN,T('игроков','players'))}${tile(sum('towns'),T('городов','towns'))}${tile(sum('residents'),T('жителей','residents'))}</div>
    <div class="chips rsfilt">${fl.map(([k,v])=>`<button data-f="${esc(k)}" class="${k===filt?'on':''}">${esc(v)}</button>`).join('')}</div>
    <div class="rsbody"></div>
    <p class="mnote">${esc(X.join||'')} ${started?T('Города из Towny на ','Towny towns as of ')+esc(R.townyDate)+'.':serverState(C.config).started?T('Города появятся в таблице после следующей выгрузки из Towny.','Towns will appear after the next Towny export.'):T('Сервер стартует 1 декабря: до этого городов нет, после старта числа подтянутся из Towny.','The server opens on 1 December: no towns until then, after launch the numbers come from Towny.')}${R.freeTowns?' '+T(`Городов без нации: ${R.freeTowns}.`,`Towns without a nation: ${R.freeTowns}.`):''}</p>`;
  host.querySelector('.rsfilt').onclick=e=>{const b=e.target.closest('button');if(!b)return;filt=b.dataset.f;host.querySelectorAll('.rsfilt button').forEach(x=>x.classList.toggle('on',x===b));draw()};
  const body=host.querySelector('.rsbody');
  const tog=e=>{const s=e.target.closest('th button');if(s){sortK=sortK===s.dataset.s?'':s.dataset.s;draw();return}
    const tr=e.target.closest('tr.rsrow');if(!tr)return;const id=tr.dataset.id;open.has(id)?open.delete(id):open.add(id);draw();const n=body.querySelector(`tr[data-id="${CSS.escape(id)}"]`);n&&n.focus({preventScroll:true})};
  body.onclick=tog; body.onkeydown=e=>{if((e.key==='Enter'||e.key===' ')&&e.target.matches('tr.rsrow')){e.preventDefault();tog(e)}};
  draw();
}
// ---- ПаксГидромет и «Вестник Академии» (C.meteo/C.news — справочники, живые данные: config.liveUrl → meteo.json, news.json из paxmeteo.sk) ----
async function liveJson(cfg,name){
  if(!cfg.liveUrl) return null;
  try{const r=await fetch(new URL(name,cfg.liveUrl.replace(/\/?$/,'/')),{cache:'no-store'});return r.ok?await r.json():null}catch(e){return null}
}
const fmtTime=t=>new Date(t*1000).toLocaleString(EN?'en-GB':'ru-RU',{day:'numeric',month:'short',hour:'2-digit',minute:'2-digit'});
const mmss=s=>{s=Math.max(0,s|0);return `${Math.floor(s/60)}:${String(s%60).padStart(2,'0')}`};
async function renderWeather(C){
  const M=C.meteo, cfg=C.config; if(!M||!$('#wxBulletin')) return;
  const [lm,ln]=await Promise.all([liveJson(cfg,'meteo.json'),liveJson(cfg,'news.json')]);
  const D=lm||C.meteoDemo, N=ln||C.newsDemo;
  const all=[...M.events,...M.space], ev=n=>all.find(e=>e.n===n), lv=n=>M.levels[n]||M.levels[0];
  $('#wxDemo').hidden=!D.demo;
  // бюллетень
  let lvl=M.levels[0], head, body='';
  const cur=D.event&&D.event.n>0&&ev(D.event.n), pen=D.pending&&D.pending.n>0&&ev(D.pending.n);
  if(cur){lvl=lv(cur.level??1);head=`${cur.icon} ${T('Действует','In effect')}: ${esc(cur.name)}`;body=`${esc(cur.text||'')} ${T('Осталось','Time left')}: <b>${mmss(D.event.left)}</b>.${cur.advice?`<br><b>${T('Совет','Advice')}:</b> ${esc(cur.advice)}`:''}`}
  else if(pen){lvl=lv(pen.level??1);head=`⚠️ ${T('Штормовое предупреждение','Storm warning')}: ${pen.icon} ${esc(pen.name)}`;body=`${T('Начнётся через','Starts in')} <b>${mmss(D.pending.warn)}</b>. ${esc(pen.advice||pen.text||'')}`}
  else{head=`✅ ${T('Катаклизмов нет','No cataclysms')}`;body=D.next>0?`${T('Следующий ожидается примерно через','The next one is expected in about')} <b>${Math.round(D.next/60)} ${T('мин','min')}</b>.`:T('Ждём следующего окна: катаклизмы приходят раз в','Waiting for the next window: cataclysms come every')+` ${M.interval.min}–${M.interval.max} ${T('мин','min')}.`}
  const b=$('#wxBulletin'); b.style.setProperty('--lv',lvl.color);
  b.innerHTML=`<div class="lvtag">${T('Уровень','Level')}: ${esc(lvl.name)} · ${esc(lvl.text)}</div><h3>${head}</h3><p>${body}</p>
    <div class="upd">${D.demo?T('Демо-данные: живая сводка появится, когда сервер начнёт публиковать meteo.json.','Demo data: the live report appears once the server publishes meteo.json.'):T('Обновлено','Updated')+': '+fmtTime(D.updated)+((Date.now()/1000-D.updated>300)?' · '+T('данные устарели, сервер мог выключиться','data is stale, the server may be offline'):'')}</div>`;
  // плитки
  const tk=D.time||0, hh=Math.floor((tk/1000+6)%24), mi=Math.floor(tk%1000*0.06);
  const wxIcon={clear:'☀️',rain:'🌧️',thunder:'⛈️'}[D.weather]||'🌤️';
  const tiles=[[wxIcon,T('Погода в мире','World weather'),M.mc[D.weather]||D.weather],
    ['🕰️',T('Время в игре','In-game time'),`${String(hh).padStart(2,'0')}:${String(mi).padStart(2,'0')}`],
    ['🍂',T('Сезон','Season'),D.season>=0&&M.seasons[D.season]?M.seasons[D.season].name:T('Сезоны с 28-го дня','Seasons from day 28')],
    ['📅',T('День сервера','Server day'),D.day>0?D.day:T('ещё не начат','not started')],
    ['👥',T('Онлайн','Online'),D.online],
    ['🎲',T('Авто-катаклизмы','Auto cataclysms'),D.auto?T('включены','on'):T('выключены','off')]];
  $('#wxNow').innerHTML=tiles.map(t=>`<div class="stat"><div class="l">${t[0]} ${esc(t[1])}</div><div class="v wxv">${esc(t[2])}</div></div>`).join('');
  $('#wxLevels').innerHTML=M.levels.map(l=>`<div class="lv" style="--lv:${l.color}"><b>${esc(l.name)}</b><span>${esc(l.text)}</span></div>`).join('');
  // сезоны: как seasonNow() в paxseasons.sk — с 28-го дня, по 7 дней
  const d0=D.day>0?D.day-1:-1; let si=-1, left=0;
  if(d0>=28){si=Math.floor((d0-28)/7)%4;left=7-((d0-28)%7)} else if(d0>=0){left=28-d0}
  $('#wxSeasons').innerHTML=M.seasons.map((x,i)=>{let tag='';
    if(i===si) tag=`<span class="tag on">${T('сейчас','now')} · ${T('ещё','left')} ${left} ${T('дн.','d')}</span>`;
    else if((si<0&&i===0&&d0>=0)||(si>=0&&i===(si+1)%4)) tag=`<span class="tag">${T('через','in')} ${left} ${T('дн.','d')}</span>`;
    return `<div class="card${i===si?' cur':''}"><h3>${esc(x.name)}</h3>${tag}<p>${esc(x.text)}</p></div>`}).join('');
  $('#wxInterval').textContent=T(`Катаклизм приходит раз в ${M.interval.min}–${M.interval.max} минут, за ${M.interval.warn} секунд до начала объявляется штормовое предупреждение. Шанс — какой из катаклизмов выпадет.`,`A cataclysm comes every ${M.interval.min}–${M.interval.max} minutes, with a storm warning ${M.interval.warn} seconds before. Chance is which cataclysm is rolled.`);
  $('#wxTable').innerHTML=`<tr class="th"><td>${T('Катаклизм','Cataclysm')}</td><td>${T('Шанс','Chance')}</td><td>${T('Длится','Lasts')}</td><td>${T('Что делать','What to do')}</td></tr>`+
    [...M.events].sort((a,b)=>b.p-a.p).map(e=>`<tr><td><span class="dot" style="background:${lv(e.level).color}"></span>${e.icon} <b>${esc(e.name)}</b><br><small>${esc(e.text)}</small></td><td>${e.p}%</td><td>${Math.round(e.min/60)}–${Math.round(e.max/60)} ${T('мин','min')}</td><td>${esc(e.advice)}</td></tr>`).join('');
  const h=[...(D.history||[])].sort((a,b)=>b.t-a.t);
  $('#wxLog').innerHTML=h.length?h.map(x=>{const e=ev(x.n);return `<li><time>${fmtTime(x.t)}</time> ${e?e.icon+' '+esc(e.name):'#'+x.n}</li>`}).join(''):`<li>${T('Пока ни одного катаклизма.','No cataclysms yet.')}</li>`;
  $('#wxSpace').innerHTML=M.space.map(e=>`<span class="pill">${e.icon} ${esc(e.name)}</span>`).join('');
  renderNews(C,N);
}
function renderNews(C,N){
  const W=C.news, host=$('#newsList'); if(!W||!host) return;
  $('#newsDemo').hidden=!N.demo;
  const found=[...(N.items||[])].sort((a,b)=>b.t-a.t).map(x=>{const t=W.templates[x.k];if(!t)return null;const p=esc(x.p);
    return {cat:t.cat,icon:t.icon,title:t.title,text:esc(t.text).split('{p}').join(`<b>${p}</b>`),reward:t.reward,date:fmtTime(x.t),demo:N.demo}}).filter(Boolean);
  const lore=W.items.map(x=>({cat:x.cat,icon:x.icon,title:x.title,text:esc(x.text),reward:x.reward,lore:true}));
  const items=[...found,...lore]; let cat='';
  const cats=Object.entries(W.categories).filter(([k])=>items.some(i=>i.cat===k));
  const bar=$('#newsCats');
  const draw=()=>{bar.innerHTML=`<button class="${cat?'':'on'}" data-c="">${T('Все','All')}</button>`+cats.map(([k,v])=>`<button class="${cat===k?'on':''}" data-c="${k}">${esc(v)}</button>`).join('');
    host.innerHTML=items.filter(i=>!cat||i.cat===cat).map(i=>`<article class="card news"><div class="meta"><span>${i.icon} ${esc(W.categories[i.cat]||'')}</span>${i.lore?`<span class="tag">${T('лор','lore')}</span>`:`<span>${i.date}</span>${i.demo?'<span class="demo">'+T('ДЕМО','DEMO')+'</span>':''}`}</div>
      <h3>${esc(i.title)}</h3><p>${i.text}</p>${i.reward?`<p class="reward">🎁 ${esc(i.reward)}</p>`:''}</article>`).join('')};
  bar.onclick=e=>{const c=e.target.closest('button');if(c){cat=c.dataset.c;draw()}};
  draw();
}

// ---- карта мира (данные: C.map из content/map.json и content/map_towns.json) ----
function renderMap(C){
  const host=$('#pxmap'); if(!host||!C.map) return;
  const M=C.map, cfg=C.config, b=cfg.border, st=serverState(cfg);
  const rings=[['start',T('Старт','Start')],['w1',T('Н1','W1')],['w2',T('Н2','W2')],['w3',T('Н3','W3')],['w5',T('Н5','W5')],['w6',T('Н6','W6')]];
  const R=b.w6, ext=R*1.12, NS='http://www.w3.org/2000/svg';
  const layers={powers:true,ancient:true,towns:true,grid:true,far:true,lore:true,wx:false,terrain:true}; const TR=M.terrain, Z=M.zones; M.far=M.far||[]; M.lore=M.lore||[];
  let sel=st.started?null:'w6';
  host.innerHTML=`<div class="mtools">
     <div class="chips" id="mLayers">
       <button data-l="powers" class="on">${T('Державы','Powers')}</button><button data-l="ancient" class="on">${T('Древние места','Ancient sites')}</button>
       <button data-l="towns" class="on">${T('Города','Towns')}${M.towns.length?' ('+M.towns.length+')':''}</button><button data-l="grid" class="on">${T('Сетка','Grid')}</button>${TR?`<button data-l="terrain" class="on">${T('Рельеф','Terrain')}</button>`:''}<button data-l="wx" class="hl">🌦️ ${T('Погода','Weather')}</button>${M.lore.length?`<button data-l="lore" class="on">${T('Метки лора','Lore tags')} (${M.lore.length})</button>`:''}${M.far.length?`<button data-l="far" class="on">${T('За границей','Beyond the border')}</button><button id="mAll" class="hl">🌍 ${T('Все миры','All worlds')} (${M.far.length})</button>`:''}</div>
     <div class="chips" id="mRings"><span class="lbl">${T('Граница','Border')}</span>${rings.map(r=>`<button data-r="${r[0]}">${r[1]}</button>`).join('')}</div>
   </div>
   <div class="mbox"><svg id="msvg" class="msvg" role="img" aria-label="${T('Карта мира PaxVanila','PaxVanila world map')}"></svg>
     <div class="mzoom"><button data-z="0.67" aria-label="${T('Приблизить','Zoom in')}">+</button><button data-z="1.5" aria-label="${T('Отдалить','Zoom out')}">−</button><button data-z="0" aria-label="${T('Сбросить','Reset')}">⟲</button></div>
     <div class="mcoord" id="mcoord">X 0 · Z 0</div><div class="mcomp">${T('С','N')}↑</div></div>
   <div class="mwx" id="mwx" hidden></div>
   <div class="minfo" id="minfo"></div>
   <p class="mnote">${TR?T(`Рельеф, реки, озёра и леса нарисованы блок в блок с настоящего мира PaxVanila (те же датапаки: Terralith, Towns and Towers, Structory). Разведано ${TR.bounds[2]-TR.bounds[0]}×${TR.bounds[3]-TR.bounds[1]} блоков вокруг спавна, дальше карта показывает схему и будет расти`,`Terrain, rivers, lakes and forests are rendered block by block from the real PaxVanila world (same datapacks: Terralith, Towns and Towers, Structory). ${TR.bounds[2]-TR.bounds[0]}×${TR.bounds[3]-TR.bounds[1]} blocks around spawn are explored; beyond that the map shows the schematic and will grow`)+(TR.date?' · '+esc(TR.date):'')+`. <a href="${esc(TR.big)}" target="_blank" rel="noopener">${T('Подробная карта 1:1','Full-size map 1:1')}</a>. `:''}${T('Державы и древние места показаны схемой по лору: настоящие столицы строят игроки.','Powers and ancient sites are a schematic based on the lore: the real capitals are built by players.')}
     ${M.towns.length?T(' Города Towny выгружены ',' Towny towns exported ')+esc(M.townsDate)+'.':T(' Реальные города появятся после открытия сервера.',' Real towns will appear after the server opens.')}
     ${cfg.mapUrl?` <a class="btn" href="${esc(cfg.mapUrl)}" target="_blank" rel="noopener">🗺️ ${T('Живая карта BlueMap','Live BlueMap')}</a>`:''}</p>`;
  const svg=$('#msvg'), el=(n,a,p)=>{const e=document.createElementNS(NS,n);for(const k in a)e.setAttribute(k,a[k]);(p||svg).appendChild(e);return e};
  const cp=el('clipPath',{id:'mclip'},el('defs',{})); el('circle',{cx:0,cy:0,r:R},cp);
  const g={}; ['base','terrain','wx','grid','powers','rings','ancient','towns','lore','far','top'].forEach(k=>g[k]=el('g',{class:'g-'+k}));
  el('circle',{cx:0,cy:0,r:R,class:'land'},g.base);
  if(TR){const [x0,z0,x1,z1]=TR.bounds, q=8000; el('image',{href:TR.src,x:x0,y:z0,width:x1-x0,height:z1-z0,preserveAspectRatio:'none',class:'terr'},g.terrain);
    el('rect',{x:x0,y:z0,width:x1-x0,height:z1-z0,class:'terrb'},g.terrain);
    el('path',{d:`M${-q} ${-q}H${q}V${q}H${-q}Z M${R} 0A${R} ${R} 0 1 0 ${-R} 0A${R} ${R} 0 1 0 ${R} 0Z`,'fill-rule':'evenodd',class:'outside'},g.terrain);}
  // слой погоды: где приходят катаклизмы (данные: content/meteo.json + зоны из настоящего мира)
  g.wx.style.display='none';
  const ME=(C.meteo&&C.meteo.events)||[], evk=k=>ME.find(e=>e.id===k)||{icon:'',name:''};
  const WZ=[['desert','sandstorm','#e8a33d',T('пустыни и бесплодные земли','deserts and badlands')],['peaks','storm','#f5c542',T('вершины выше Y 110: молнии бьют чаще','peaks above Y 110: lightning strikes more often')],
    ['snow','blizzard','#5fd4e8',T('снежные земли: метель сильнее','snowy lands: the blizzard is harsher')],['water','flood','#3b6fd9',T('океаны, реки, пляжи','oceans, rivers, beaches')]];
  const wxLegend=[];
  if(Z){const c=Z.cell||64; WZ.forEach(([k,ev,col,txt])=>{const L=Z[k]||[]; if(!L.length) return;
    el('path',{d:L.map(([x,z])=>`M${x} ${z}h${c}v${c}h${-c}z`).join(''),fill:col,class:'wxz'},g.wx); const e=evk(ev); wxLegend.push([col,`${e.icon} ${esc(e.name||ev)}`,txt]);});}
  { const a=evk('ash'); el('circle',{cx:0,cy:0,r:120,class:'wxash'},g.wx); wxLegend.push(['#8b1e1e',`${a.icon} ${esc(a.name||'ash')}`,T('столб огня над Монолитом 0,0','a pillar of fire over the Monolith at 0,0')]);
    el('rect',{x:-48,y:-48,width:96,height:96,class:'wxsafe'},g.wx); wxLegend.push(['#3fa34d','🛡️ '+T('Безопасная зона','Safe zone'),T('башня новичков ±48 блоков: урона нет','newcomer tower ±48 blocks: no damage')]); }
  const everywhere=['blizzard','drought','quake','meteor','fog','aurora','storm'].map(evk).filter(e=>e.name).map(e=>`${e.icon} ${esc(e.name)}`);
  const wxBox=$('#mwx'), iv=(C.meteo&&C.meteo.interval)||{min:45,max:90,warn:60};
  wxBox.innerHTML=`<div class="wxl">${wxLegend.map(([c,n,t])=>`<span><i style="background:${c}"></i><b>${n}</b> ${t}</span>`).join('')}</div>
    <p>${T('Везде под открытым небом','Everywhere under open sky')}: ${everywhere.join(', ')}. ${T(`Катаклизм приходит сам раз в ${iv.min}–${iv.max} минут, предупреждение за ${iv.warn} секунд. Блоки не ломаются, урон только при 5+ сердцах, новички первые 48 ч без урона. Живой погоды с сервера здесь нет, это справочник.`,`A cataclysm comes on its own every ${iv.min}–${iv.max} minutes, with a ${iv.warn}-second warning. Blocks are never broken, damage only above 5 hearts, newcomers are safe for 48 h. This is a reference, not live server weather.`)}
    ${Z?'':T(' Зоны пустынь, гор и морей появятся после рендера мира.',' Desert, mountain and sea zones appear once the world is rendered.')} <a href="#weather">${T('Все катаклизмы и шансы','All cataclysms and chances')} →</a></p>`; g.grid.setAttribute('clip-path','url(#mclip)');
  for(let v=-2000;v<=2000;v+=500){ if(Math.abs(v)>R) continue;
    el('line',{x1:v,y1:-R,x2:v,y2:R,class:'gl'+(v?'':' axis')},g.grid); el('line',{x1:-R,y1:v,x2:R,y2:v,class:'gl'+(v?'':' axis')},g.grid);
    if(v) {el('text',{x:v,y:-6,class:'gt'},g.grid).textContent=v; el('text',{x:6,y:v,class:'gt'},g.grid).textContent=v;} }
  const ringEls={};
  rings.forEach(([k,l])=>{const r=b[k]; const c=el('circle',{cx:0,cy:0,r,class:'ring','data-r':k},g.rings);
    const t=el('text',{x:r*.7071,y:-r*.7071,class:'rt'+(k==='start'?' st':'')},g.rings); t.textContent=`${l} · ${r}`; ringEls[k]=[c,t];});
  if(st.started){el('circle',{cx:0,cy:0,r:st.radius,class:'ring now'},g.rings);
    el('text',{x:0,y:st.radius,class:'rt now'},g.rings).textContent=T('Сейчас ','Now ')+st.radius;}
  el('circle',{cx:0,cy:0,r:80,class:'spawnz'},g.top);
  const info=$('#minfo');
  const pick=(o,kind)=>{info.innerHTML=`<b>${esc(o.name)}</b> <span class="mk">${esc(kind)}</span> <code>X ${o.x} · Z ${o.z}</code><div>${esc(o.text||'')}</div>`+(o.lore?`<p><a class="btn" href="lore/${esc(o.lore)}.html">📜 ${T('Читать лор','Read the lore')}</a></p>`:'')};
  M.powers.forEach(p=>{const a=el('g',{class:'pw',tabindex:0},g.powers);
    el('circle',{cx:p.x,cy:p.z,r:230,fill:p.color,class:'pwa'},a); el('circle',{cx:p.x,cy:p.z,r:26,fill:p.color,class:'pwd'},a);
    el('text',{x:p.x,y:p.z+60,class:'pt'},a).textContent=p.name;
    a.onclick=()=>pick(p,M.blocs[p.bloc]||''); a.onkeydown=e=>{if(e.key==='Enter')pick(p,M.blocs[p.bloc]||'')};});
  M.ancient.forEach(p=>{const a=el('g',{class:'an',tabindex:0},g.ancient);
    el('rect',{x:p.x-22,y:p.z-22,width:44,height:44,transform:`rotate(45 ${p.x} ${p.z})`,class:'and'},a);
    el('text',{x:p.x,y:p.z+62,class:'at'},a).textContent=p.name; a.onclick=()=>pick(p,T('Предтечи','Forerunners'));});
  M.towns.forEach(t=>{const a=el('g',{class:'tw',tabindex:0},g.towns); const col=t.color||'#9a6b12';
    (t.blocks||[]).forEach(([cx,cz])=>el('rect',{x:cx*16,y:cz*16,width:16,height:16,fill:col,class:'tb'},a));
    el('circle',{cx:t.x,cy:t.z,r:10,fill:col,class:'twd'},a); el('text',{x:t.x,y:t.z+30,class:'tt'},a).textContent=t.name;
    a.onclick=()=>pick({...t,text:(t.nation?T('Нация: ','Nation: ')+t.nation+'. ':'')+T('Занято чанков: ','Claimed chunks: ')+(t.blocks||[]).length},T('город','town'));});
  const LC={legend:['✦',T('легенда','legend')],cataclysm:['⚡',T('катаклизм','cataclysm')],battle:['⚔',T('битва','battle')],front:['☠',T('Хроника фронта','Front Chronicle')],old:['◉',T('Старые записи','Old Recordings')]};
  M.lore.forEach(p=>{const c=LC[p.cat]||['•',''], a=el('g',{class:'lt c-'+p.cat,tabindex:0},g.lore);
    el('circle',{cx:p.x,cy:p.z,r:9,class:'ld'},a); const tx=el('text',{x:p.x,y:p.z-14,class:'ltx'},a); tx.textContent=c[0]+' '+p.name;
    const go=()=>pick({...p,lore:p.lore||(p.cat==='front'?'front':'')},c[1]); a.onclick=go; a.onkeydown=e=>{if(e.key==='Enter')go()};});
  M.far.forEach(p=>{const a=el('g',{class:'far'+(p.kind?' k-'+p.kind:''),tabindex:0},g.far), d=Math.hypot(p.x,p.z)||1, ex=p.x/d*R, ez=p.z/d*R;
    el('line',{x1:ex,y1:ez,x2:p.x,y2:p.z,class:'fl'},a);
    el('text',{x:ex+(p.x-ex)*(p.kind?0.4:0.12),y:ez+(p.z-ez)*(p.kind?0.4:0.12)-14,class:'fh'},a).textContent=T('за границей → ','beyond the border → ')+Math.round(d)+T(' бл.',' bl.');
    el('circle',{cx:p.x,cy:p.z,r:160,class:'fa'},a);
    el('path',{d:`M${p.x-60} ${p.z-60}L${p.x+60} ${p.z+60}M${p.x+60} ${p.z-60}L${p.x-60} ${p.z+60}`,class:'fx'},a);
    el('text',{x:p.x,y:p.z+200,class:'ft'},a).textContent=p.name;
    const go=()=>{pick(p,p.kind==='old'?T('другой мир · Старые записи','another world · Old Recordings'):T('за границей мира','beyond the border'));const ar=svg.clientHeight/Math.max(1,svg.clientWidth)||1, x0=Math.min(-R,p.x-400), x1=Math.max(R,p.x+400), z0=Math.min(-R,p.z-400), z1=Math.max(R,p.z+400), nw=Math.max(x1-x0,(z1-z0)/ar)*1.08;vb={x:(x0+x1)/2-nw/2,y:(z0+z1)/2-nw*ar/2,w:nw,h:nw*ar};apply()};
    a.onclick=go; a.onkeydown=e=>{if(e.key==='Enter')go()};
    if(p.lore) info.dataset.far=p.lore;});
  M.places.forEach(p=>{const a=el('g',{class:'mono',tabindex:0},g.top);
    el('rect',{x:p.x-18,y:p.z-18,width:36,height:36,class:'md'},a); el('text',{x:p.x,y:p.z-34,class:'mt'},a).textContent=p.name;
    a.onclick=()=>pick(p,T('центр мира','world centre'));});
  pick(M.places[0],T('центр мира','world centre'));
  // слои и кольца
  $('#mLayers').onclick=e=>{const k=e.target.dataset.l;if(!k)return;layers[k]=!layers[k];e.target.classList.toggle('on',layers[k]);g[k].style.display=layers[k]?'':'none';if(k==='wx')wxBox.hidden=!layers.wx};
  const markRing=()=>{document.querySelectorAll('#mRings button').forEach(x=>x.classList.toggle('on',x.dataset.r===sel));
    for(const k in ringEls) ringEls[k].forEach(e=>e.classList.toggle('sel',k===sel));};
  $('#mRings').onclick=e=>{const k=e.target.dataset.r;if(!k)return;sel=sel===k?null:k;markRing()}; markRing();
  // приближение и перетаскивание (viewBox в блоках)
  let vb={x:-ext,y:-ext,w:2*ext,h:2*ext};
  const apply=()=>{const ar=svg.clientHeight/Math.max(1,svg.clientWidth)||1; vb.h=vb.w*ar;
    svg.setAttribute('viewBox',`${vb.x} ${vb.y} ${vb.w} ${vb.h}`); svg.style.setProperty('--k',vb.w/Math.max(1,svg.clientWidth));};
  const fitAll=()=>{const ar=svg.clientHeight/Math.max(1,svg.clientWidth)||1; let x0=-R,x1=R,z0=-R,z1=R; M.far.forEach(p=>{x0=Math.min(x0,p.x-1700);x1=Math.max(x1,p.x+1700);z0=Math.min(z0,p.z-700);z1=Math.max(z1,p.z+700)});
    const nw=Math.max(x1-x0,(z1-z0)/ar)*1.05; vb={x:(x0+x1)/2-nw/2,y:(z0+z1)/2-nw*ar/2,w:nw,h:nw*ar}; if(!layers.far){layers.far=true;g.far.style.display='';const b=host.querySelector('[data-l="far"]');b&&b.classList.add('on')} apply()};
  { const b=host.querySelector('#mAll'); if(b) b.onclick=e=>{e.stopPropagation();fitAll()}; }
  const reset=()=>{const ar=svg.clientHeight/Math.max(1,svg.clientWidth)||1, s=2*ext; vb=ar>1?{x:-ext,y:-ext*ar,w:s,h:s*ar}:{x:-ext/ar,y:-ext,w:s/ar,h:s};apply()};
  const toWorld=(cx,cy)=>{const r=svg.getBoundingClientRect();return [vb.x+(cx-r.left)/r.width*vb.w, vb.y+(cy-r.top)/r.height*vb.h]};
  const zoom=(f,cx,cy)=>{const nw=Math.min(14*ext,Math.max(120,vb.w*f)); f=nw/vb.w; const [wx,wy]=toWorld(cx,cy);
    vb.x=wx-(wx-vb.x)*f; vb.y=wy-(wy-vb.y)*f; vb.w=nw; apply()};
  host.querySelector('.mzoom').onclick=e=>{const z=+e.target.dataset.z; if(isNaN(z))return; if(!z)return M.far.length?fitAll():reset();
    const r=svg.getBoundingClientRect(); zoom(z,r.left+r.width/2,r.top+r.height/2)};
  svg.addEventListener('wheel',e=>{e.preventDefault();zoom(e.deltaY>0?1.2:1/1.2,e.clientX,e.clientY)},{passive:false});
  const pts=new Map(); let last=null, moved=0;
  svg.addEventListener('pointerdown',e=>{pts.set(e.pointerId,[e.clientX,e.clientY]);moved=0;last=null});
  svg.addEventListener('pointermove',e=>{const [wx,wy]=toWorld(e.clientX,e.clientY); $('#mcoord').textContent=`X ${Math.round(wx)} · Z ${Math.round(wy)}`;
    if(!pts.has(e.pointerId))return; const p0=pts.get(e.pointerId); pts.set(e.pointerId,[e.clientX,e.clientY]);
    if(pts.size===1){const r=svg.getBoundingClientRect(),dx=e.clientX-p0[0],dy=e.clientY-p0[1];moved+=Math.abs(dx)+Math.abs(dy);
      if(moved>4){svg.setPointerCapture(e.pointerId);vb.x-=dx/r.width*vb.w;vb.y-=dy/r.height*vb.h;apply()}}
    else if(pts.size===2){const [a,c]=[...pts.values()],d=Math.hypot(a[0]-c[0],a[1]-c[1]); if(last)zoom(last/d,(a[0]+c[0])/2,(a[1]+c[1])/2); last=d; moved=99}});
  const up=e=>{pts.delete(e.pointerId);if(pts.size<2)last=null};
  svg.addEventListener('pointerup',up); svg.addEventListener('pointercancel',up);
  svg.addEventListener('click',e=>{if(moved>4){e.stopPropagation();e.preventDefault()}},true);
  const fitTerrain=()=>{const [x0,z0,x1,z1]=TR.bounds, ar=svg.clientHeight/Math.max(1,svg.clientWidth)||1, cx=(x0+x1)/2, cz=(z0+z1)/2, nw=Math.max(x1-x0,(z1-z0)/ar)*1.7; vb={x:cx-nw/2,y:cz-nw*ar/2,w:nw,h:nw*ar};apply()};
  addEventListener('resize',apply); TR?fitTerrain():M.far.length?fitAll():reset();
}
// ---- карта Земли (данные: C.map.earth из content/earth.json, единица = 1 км) ----
function renderEarth(C){
  const host=$('#pxearth'); if(!host||!C.map||!C.map.earth){const s=$('#earth');if(s)s.remove();return}
  const E=C.map.earth, M=C.map, NS='http://www.w3.org/2000/svg', [bx0,by0,bx1,by1]=E.box;
  const layers={powers:true,seas:true,grid:true};
  host.innerHTML=`<div class="mtools"><div class="chips" id="eLayers"><button data-l="powers" class="on">${T('Державы','Powers')} (${E.powers.length})</button><button data-l="seas" class="on">${T('Моря','Seas')}</button><button data-l="grid" class="on">${T('Параллели','Graticule')}</button></div>
     <div class="chips">${Object.entries(M.blocs).map(([k,v])=>`<span class="pill eb-${k}">${esc(v)}</span>`).join('')}</div></div>
   <div class="mbox ebox"><svg id="esvg" class="msvg esvg" role="img" aria-label="${T('Карта Земли PaxVanila','PaxVanila map of the Earth')}"></svg>
     <div class="mzoom"><button data-z="0.67" aria-label="${T('Приблизить','Zoom in')}">+</button><button data-z="1.5" aria-label="${T('Отдалить','Zoom out')}">−</button><button data-z="0" aria-label="${T('Сбросить','Reset')}">⟲</button></div>
     <div class="mcoord" id="ecoord">48° N · 25° E</div><div class="mcomp">${T('С','N')}↑</div></div>
   <div class="minfo" id="einfo"></div>
   <p class="mnote">${T('Мир 2 строится по настоящей Земле. Контуры суши: Natural Earth 1:50 000 000. Державы стоят на местах своих исторических прообразов. В ванильном Мире 1 они стоят вокруг Монолита (карта выше), там у них свои координаты.','World 2 is built on the real Earth. Coastlines: Natural Earth 1:50,000,000. The powers stand where their historical prototypes were. In vanilla World 1 they surround the Monolith (map above) with their own coordinates.')}</p>`;
  const svg=$('#esvg'), el=(n,a,p)=>{const e=document.createElementNS(NS,n);for(const k in a)e.setAttribute(k,a[k]);(p||svg).appendChild(e);return e};
  const cp=el('clipPath',{id:'eclip'},el('defs',{})); el('rect',{x:bx0,y:by0,width:bx1-bx0,height:by1-by0},cp);
  const g={}; ['base','grid','seas','powers'].forEach(k=>g[k]=el('g',{class:'g-'+k})); g.base.setAttribute('clip-path','url(#eclip)'); g.grid.setAttribute('clip-path','url(#eclip)');
  el('rect',{x:bx0,y:by0,width:bx1-bx0,height:by1-by0,class:'esea'},g.base);
  el('path',{d:E.land.map(r=>{let d='M'+r[0]+' '+r[1];for(let i=2;i<r.length;i+=2)d+='L'+r[i]+' '+r[i+1];return d+'Z'}).join(''),'fill-rule':'evenodd',class:'eland'},g.base);
  const K=Math.cos(48*Math.PI/180)*111.32, gx=lon=>(lon-25)*K, gy=lat=>-(lat-48)*111.32;
  for(let lat=30;lat<=70;lat+=10){el('line',{x1:bx0,y1:gy(lat),x2:bx1,y2:gy(lat),class:'gl'},g.grid); el('text',{x:bx0+70,y:gy(lat)-6,class:'gt'},g.grid).textContent=lat+'° N';}
  for(let lon=-10;lon<=60;lon+=10){el('line',{x1:gx(lon),y1:by0,x2:gx(lon),y2:by1,class:'gl'},g.grid); el('text',{x:gx(lon)+6,y:by1-20,class:'gt'},g.grid).textContent=Math.abs(lon)+'°'+(lon<0?' W':' E');}
  E.seas.forEach(s=>{el('text',{x:s.x,y:s.z??s.y,class:'esn'},g.seas).textContent=s.name});
  const info=$('#einfo');
  const pick=p=>{info.innerHTML=`<b>${esc(p.name)}</b> <span class="mk">${esc(M.blocs[p.bloc]||'')}</span> <code>${p.lat.toFixed(1)}° N · ${p.lon.toFixed(1)}° E</code><div><b>${T('В реальной истории','In real history')}:</b> ${esc(p.real)}.</div><div>${esc(p.text||'')}</div><div class="mk">${T('В Мире 1','In World 1')}: X ${p.x0} · Z ${p.z0}</div>`};
  const pw=E.powers.map(p=>({...p,x0:(M.powers.find(q=>q.id===p.id)||{}).x,z0:(M.powers.find(q=>q.id===p.id)||{}).z}));
  pw.forEach(p=>{const a=el('g',{class:'pw',tabindex:0},g.powers);
    el('circle',{cx:p.x,cy:p.z,r:260,fill:p.color,class:'pwa'},a); el('circle',{cx:p.x,cy:p.z,r:34,fill:p.color,class:'pwd'},a);
    el('text',{x:p.x,y:p.z+60,class:'pt'},a).textContent=p.name;
    const go=()=>pick(p); a.onclick=go; a.onkeydown=e=>{if(e.key==='Enter')go()};});
  const rome=pw.find(p=>p.id==='romea')||pw[0]; if(rome) pick(rome);
  $('#eLayers').onclick=e=>{const k=e.target.dataset.l;if(!k)return;layers[k]=!layers[k];e.target.classList.toggle('on',layers[k]);g[k].style.display=layers[k]?'':'none'};
  let vb={x:bx0,y:by0,w:bx1-bx0,h:by1-by0};
  const apply=()=>{const ar=svg.clientHeight/Math.max(1,svg.clientWidth)||1; vb.h=vb.w*ar; svg.setAttribute('viewBox',`${vb.x} ${vb.y} ${vb.w} ${vb.h}`); svg.style.setProperty('--k',vb.w/Math.max(1,svg.clientWidth));};
  const reset=()=>{const ar=svg.clientHeight/Math.max(1,svg.clientWidth)||1, w=bx1-bx0, h=by1-by0, nw=Math.max(w,h/ar); vb={x:(bx0+bx1)/2-nw/2,y:(by0+by1)/2-nw*ar/2,w:nw,h:nw*ar};apply()};
  const toWorld=(cx,cy)=>{const r=svg.getBoundingClientRect();return [vb.x+(cx-r.left)/r.width*vb.w, vb.y+(cy-r.top)/r.height*vb.h]};
  const zoom=(f,cx,cy)=>{const nw=Math.min(2*(bx1-bx0),Math.max(300,vb.w*f)); f=nw/vb.w; const [wx,wy]=toWorld(cx,cy); vb.x=wx-(wx-vb.x)*f; vb.y=wy-(wy-vb.y)*f; vb.w=nw; apply()};
  host.querySelector('.mzoom').onclick=e=>{const z=+e.target.dataset.z; if(isNaN(z))return; if(!z)return reset(); const r=svg.getBoundingClientRect(); zoom(z,r.left+r.width/2,r.top+r.height/2)};
  svg.addEventListener('wheel',e=>{e.preventDefault();zoom(e.deltaY>0?1.2:1/1.2,e.clientX,e.clientY)},{passive:false});
  const pts=new Map(); let last=null, moved=0;
  svg.addEventListener('pointerdown',e=>{pts.set(e.pointerId,[e.clientX,e.clientY]);moved=0;last=null});
  svg.addEventListener('pointermove',e=>{const [wx,wy]=toWorld(e.clientX,e.clientY), lat=48-wy/111.32, lon=25+wx/K; $('#ecoord').textContent=`${Math.abs(lat).toFixed(1)}° ${lat<0?'S':'N'} · ${Math.abs(lon).toFixed(1)}° ${lon<0?'W':'E'}`;
    if(!pts.has(e.pointerId))return; const p0=pts.get(e.pointerId); pts.set(e.pointerId,[e.clientX,e.clientY]);
    if(pts.size===1){const r=svg.getBoundingClientRect(),dx=e.clientX-p0[0],dy=e.clientY-p0[1];moved+=Math.abs(dx)+Math.abs(dy);
      if(moved>4){svg.setPointerCapture(e.pointerId);vb.x-=dx/r.width*vb.w;vb.y-=dy/r.height*vb.h;apply()}}
    else if(pts.size===2){const [a,c]=[...pts.values()],d=Math.hypot(a[0]-c[0],a[1]-c[1]); if(last)zoom(last/d,(a[0]+c[0])/2,(a[1]+c[1])/2); last=d; moved=99}});
  const up=e=>{pts.delete(e.pointerId);if(pts.size<2)last=null};
  svg.addEventListener('pointerup',up); svg.addEventListener('pointercancel',up);
  svg.addEventListener('click',e=>{if(moved>4){e.stopPropagation();e.preventDefault()}},true);
  addEventListener('resize',apply); reset();
}
// ---- карта Незера (данные: C.map.nether из content/map.json; 1 блок Незера = 8 блоков наверху) ----
function renderNether(C){
  const host=$('#pxnether'); if(!host||!C.map||!C.map.nether) return;
  const N=C.map.nether, M=C.map, b=C.config.border, st=serverState(C.config);
  const rings=[['start',T('Старт','Start')],['w1',T('Н1','W1')],['w2',T('Н2','W2')],['w3',T('Н3','W3')],['w5',T('Н5','W5')],['w6',T('Н6','W6')]];
  const R=b.w6/8, ext=R*1.2, NS='http://www.w3.org/2000/svg', r8=v=>Math.round(v/8);
  const portals=M.powers.map(p=>({...p,ox:p.x,oz:p.z,x:r8(p.x),z:r8(p.z)}));
  const sites=N.sites||[], kinds={fortress:['▣',T('крепость Предтеч','Forerunner fortress')],bastion:['♜',T('бастион пиглинов','piglin bastion')],legend:['✦',T('легенда','legend')]};
  const layers={portals:true,sites:true,legend:true,roads:true,grid:true};
  let sel='w6';
  host.innerHTML=`<div class="mtools">
     <div class="chips" id="nLayers"><button data-l="portals" class="on">${T('Порталы держав','Powers\' portals')} (${portals.length})</button><button data-l="sites" class="on">${T('Крепости и бастионы','Fortresses and bastions')}</button><button data-l="legend" class="on">${T('Легенды','Legends')}</button><button data-l="roads" class="on">${T('Тракты','Roads')}</button><button data-l="grid" class="on">${T('Сетка','Grid')}</button></div>
     <div class="chips" id="nRings"><span class="lbl">${T('Граница ÷ 8','Border ÷ 8')}</span>${rings.map(r=>`<button data-r="${r[0]}">${r[1]}</button>`).join('')}</div>
   </div>
   <div class="mbox nbox"><svg id="nsvg" class="msvg nsvg" role="img" aria-label="${T('Карта Незера PaxVanila','PaxVanila Nether map')}"></svg>
     <div class="mzoom"><button data-z="0.67" aria-label="${T('Приблизить','Zoom in')}">+</button><button data-z="1.5" aria-label="${T('Отдалить','Zoom out')}">−</button><button data-z="0" aria-label="${T('Сбросить','Reset')}">⟲</button></div>
     <div class="mcoord" id="ncoord">X 0 · Z 0</div><div class="mcomp">${T('С','N')}↑</div></div>
   <div class="minfo" id="ninfo"></div>
   <p class="mnote">${T('Порталы держав посчитаны из карты мира: координаты столицы ÷ 8. Крепости, бастионы и легенды показаны схемой по лору, настоящие генерирует мир. Кольца это граница мира ÷ 8: если уйти дальше, портал выведет к краю границы.','The powers\' portals are taken from the world map: capital coordinates ÷ 8. Fortresses, bastions and legends are a schematic of the lore; the real ones are generated by the world. The rings are the world border ÷ 8: go further and a portal will drop you at the edge of the border.')}</p>`;
  const svg=$('#nsvg'), el=(n,a,p)=>{const e=document.createElementNS(NS,n);for(const k in a)e.setAttribute(k,a[k]);(p||svg).appendChild(e);return e};
  const g={}; ['base','grid','rings','roads','legend','sites','portals','top'].forEach(k=>g[k]=el('g',{class:'g-'+k}));
  const L=ext*3; el('rect',{x:-L,y:-L,width:2*L,height:2*L,class:'nrack'},g.base);
  // лава и леса: постоянный узор (одинаковый у всех)
  let seed=7; const rnd=()=>(seed=(seed*16807)%2147483647)/2147483647;
  for(let i=0;i<46;i++){const x=(rnd()*2-1)*ext*1.5, z=(rnd()*2-1)*ext*1.5, r=6+rnd()*22, t=rnd(); if(Math.hypot(x,z)<30) continue;
    el('ellipse',{cx:x,cy:z,rx:r*1.5,ry:r,class:t<.55?'nlava':t<.8?'ncrim':'nwarp',transform:`rotate(${Math.round(rnd()*180)} ${x} ${z})`},g.base);}
  const sea=sites.find(s=>s.id==='ash_sea'); if(sea) el('ellipse',{cx:sea.x,cy:sea.z,rx:110,ry:34,class:'nlava sea'},g.base);
  for(let v=-250;v<=250;v+=50){ el('line',{x1:v,y1:-ext*1.5,x2:v,y2:ext*1.5,class:'gl'+(v?'':' axis')},g.grid); el('line',{x1:-ext*1.5,y1:v,x2:ext*1.5,y2:v,class:'gl'+(v?'':' axis')},g.grid);
    if(v){el('text',{x:v,y:-3,class:'gt'},g.grid).textContent=v; el('text',{x:3,y:v,class:'gt'},g.grid).textContent=v;} }
  const ringEls={};
  rings.forEach(([k,l])=>{const r=b[k]/8; const c=el('circle',{cx:0,cy:0,r,class:'ring','data-r':k},g.rings);
    const t=el('text',{x:r*.7071,y:-r*.7071,class:'rt'+(k==='start'?' st':'')},g.rings); t.textContent=`${l} · ${Math.round(r)} (${T('наверху','above')} ${b[k]})`; ringEls[k]=[c,t];});
  if(st.started){el('circle',{cx:0,cy:0,r:st.radius/8,class:'ring now'},g.rings); el('text',{x:0,y:st.radius/8,class:'rt now'},g.rings).textContent=T('Сейчас ','Now ')+Math.round(st.radius/8);}
  const info=$('#ninfo');
  const pick=(o,kind,extra)=>{info.innerHTML=`<b>${esc(o.name)}</b> <span class="mk">${esc(kind)}</span> <code>${T('Незер','Nether')} X ${o.x} · Z ${o.z}</code> <code>${T('наверху','above')} X ${o.ox??o.x*8} · Z ${o.oz??o.z*8}</code><div>${esc(o.text||'')}</div>${extra||''}`};
  const roadInfo={name:N.roadName,text:N.roadText}, lk=id=>`<p><a class="btn" href="lore/${id}.html">📜 ${T('Читать лор','Read the lore')}</a></p>`;
  (N.roads||[]).forEach(r=>{const a=el('g',{class:'rd',tabindex:0},g.roads); el('line',{x1:0,y1:0,x2:r.x,y2:r.z,class:'rdl'},a); el('line',{x1:0,y1:0,x2:r.x,y2:r.z,class:'rdc'},a);
    const go=()=>pick({...roadInfo,x:r.x,z:r.z},T('магистраль','highway')); a.onclick=go; a.onkeydown=e=>{if(e.key==='Enter')go()};});
  sites.forEach(p=>{const k=kinds[p.kind]||['•',''], a=el('g',{class:'ns k-'+p.kind,tabindex:0},p.kind==='legend'?g.legend:g.sites);
    if(p.kind==='fortress') el('rect',{x:p.x-7,y:p.z-7,width:14,height:14,class:'nsd'},a);
    else if(p.kind==='bastion') el('path',{d:`M${p.x-8} ${p.z+7}L${p.x-8} ${p.z-5}L${p.x-4} ${p.z-5}L${p.x-4} ${p.z-8}L${p.x+4} ${p.z-8}L${p.x+4} ${p.z-5}L${p.x+8} ${p.z-5}L${p.x+8} ${p.z+7}Z`,class:'nsd'},a);
    else el('circle',{cx:p.x,cy:p.z,r:4.5,class:'nsd'},a);
    el('text',{x:p.x,y:p.z+(p.kind==='legend'?-8:13),class:'nst'},a).textContent=(p.kind==='legend'?'✦ ':'')+p.name;
    const go=()=>pick(p,k[1],lk(p.id==='crimson_rift'?'pozdnie':'predtechi')); a.onclick=go; a.onkeydown=e=>{if(e.key==='Enter')go()};});
  portals.forEach(p=>{const a=el('g',{class:'np',tabindex:0},g.portals);
    el('rect',{x:p.x-4,y:p.z-6,width:8,height:12,rx:1,class:'npf',stroke:p.color},a);
    el('text',{x:p.x,y:p.z+9,class:'npt'},a).textContent=p.name;
    const go=()=>pick({...p,text:T('Портал державы. Встань в Незере на эти координаты и построй рамку: выйдешь у столицы. ','The power\'s portal. Build a frame at these Nether coordinates and you will come out at the capital. ')+(p.text||'')},T('портал','portal')); a.onclick=go; a.onkeydown=e=>{if(e.key==='Enter')go()};});
  (N.places||[]).forEach(p=>{const a=el('g',{class:'ng',tabindex:0},g.top);
    el('circle',{cx:p.x,cy:p.z,r:10,class:'ngo'},a); el('rect',{x:p.x-4,y:p.z-6,width:8,height:12,class:'ngi'},a);
    el('text',{x:p.x,y:p.z-15,class:'ngt'},a).textContent=p.name;
    const go=()=>pick(p,T('под Монолитом','beneath the Monolith'),lk('predtechi')); a.onclick=go; a.onkeydown=e=>{if(e.key==='Enter')go()};});
  if(N.places&&N.places[0]) pick(N.places[0],T('под Монолитом','beneath the Monolith'),lk('predtechi'));
  $('#nLayers').onclick=e=>{const k=e.target.dataset.l;if(!k)return;layers[k]=!layers[k];e.target.classList.toggle('on',layers[k]);g[k].style.display=layers[k]?'':'none'};
  const markRing=()=>{host.querySelectorAll('#nRings button').forEach(x=>x.classList.toggle('on',x.dataset.r===sel)); for(const k in ringEls) ringEls[k].forEach(e=>e.classList.toggle('sel',k===sel));};
  $('#nRings').onclick=e=>{const k=e.target.dataset.r;if(!k)return;sel=sel===k?null:k;markRing()}; markRing();
  let vb={x:-ext,y:-ext,w:2*ext,h:2*ext};
  const apply=()=>{const ar=svg.clientHeight/Math.max(1,svg.clientWidth)||1; vb.h=vb.w*ar; svg.setAttribute('viewBox',`${vb.x} ${vb.y} ${vb.w} ${vb.h}`); svg.style.setProperty('--k',vb.w/Math.max(1,svg.clientWidth));};
  const reset=()=>{const ar=svg.clientHeight/Math.max(1,svg.clientWidth)||1, s=2*ext; vb=ar>1?{x:-ext,y:-ext*ar,w:s,h:s*ar}:{x:-ext/ar,y:-ext,w:s/ar,h:s};apply()};
  const toWorld=(cx,cy)=>{const r=svg.getBoundingClientRect();return [vb.x+(cx-r.left)/r.width*vb.w, vb.y+(cy-r.top)/r.height*vb.h]};
  const zoom=(f,cx,cy)=>{const nw=Math.min(6*ext,Math.max(30,vb.w*f)); f=nw/vb.w; const [wx,wy]=toWorld(cx,cy); vb.x=wx-(wx-vb.x)*f; vb.y=wy-(wy-vb.y)*f; vb.w=nw; apply()};
  host.querySelector('.mzoom').onclick=e=>{const z=+e.target.dataset.z; if(isNaN(z))return; if(!z)return reset(); const r=svg.getBoundingClientRect(); zoom(z,r.left+r.width/2,r.top+r.height/2)};
  svg.addEventListener('wheel',e=>{e.preventDefault();zoom(e.deltaY>0?1.2:1/1.2,e.clientX,e.clientY)},{passive:false});
  const pts=new Map(); let last=null, moved=0;
  svg.addEventListener('pointerdown',e=>{pts.set(e.pointerId,[e.clientX,e.clientY]);moved=0;last=null});
  svg.addEventListener('pointermove',e=>{const [wx,wy]=toWorld(e.clientX,e.clientY); $('#ncoord').textContent=`X ${Math.round(wx)} · Z ${Math.round(wy)}  →  ${T('наверху','above')} ${Math.round(wx)*8} · ${Math.round(wy)*8}`;
    if(!pts.has(e.pointerId))return; const p0=pts.get(e.pointerId); pts.set(e.pointerId,[e.clientX,e.clientY]);
    if(pts.size===1){const r=svg.getBoundingClientRect(),dx=e.clientX-p0[0],dy=e.clientY-p0[1];moved+=Math.abs(dx)+Math.abs(dy);
      if(moved>4){svg.setPointerCapture(e.pointerId);vb.x-=dx/r.width*vb.w;vb.y-=dy/r.height*vb.h;apply()}}
    else if(pts.size===2){const [a,c]=[...pts.values()],d=Math.hypot(a[0]-c[0],a[1]-c[1]); if(last)zoom(last/d,(a[0]+c[0])/2,(a[1]+c[1])/2); last=d; moved=99}});
  const up=e=>{pts.delete(e.pointerId);if(pts.size<2)last=null};
  svg.addEventListener('pointerup',up); svg.addEventListener('pointercancel',up);
  svg.addEventListener('click',e=>{if(moved>4){e.stopPropagation();e.preventDefault()}},true);
  addEventListener('resize',apply); reset();
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
