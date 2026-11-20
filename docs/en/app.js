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

// ---- телефон: нижняя панель, меню-шторка, оглавление и чтение лора ----
(function(){
  const nav=$('nav.main'), header=$('header.top'); if(!nav||!header) return;
  const U=h=>new URL(h,BASE).href, aside=$('.doc aside'), tocLinks=aside?[...aside.querySelectorAll('a[href^="#"]')]:[];
  const isIndex=!!$('#pxmap');
  // карта сайта: одна на все страницы (меню ПК, шторка телефона, быстрый переход, поиск)
  const SITE=[
    {t:T('Сервер','Server'),i:'🏰',l:[['#now','⚡',T('Сейчас','Now')],['news.html','📰',T('Новости сервера','Server news')],['#calendar','📅',T('Календарь','Calendar')],['#join','🧭',T('Как зайти','How to join')],['#weeks','📆',T('Недели','Weeks')],['#app','📲',T('Приложение','App')]]},
    {t:T('Карты','Maps'),i:'🗺️',l:[['#map','🗺️',T('Мир 1 · Ванильный','World 1 · Vanilla')],['#earth','🌍',T('Мир 2 · Земля','World 2 · Earth')],['#nether','🔥',T('Незер','Nether')],['#weather','⛈️',T('Погода и катаклизмы','Weather')]]},
    {t:T('Мир и лор','World & lore'),i:'📜',l:[['#nations','🏛️',T('Державы','Powers')],['lore.html','📚',T('Лор мира','World lore')],['timeline.html','⏳',T('Хроника держав','Timeline')],['#news','🔬',T('Вестник Академии','Academy herald')],['quiz.html','🧩',T('Викторина','Quiz')]]},
    {t:T('Как играть','How to play'),i:'⚔️',l:[['#mech','⚙️',T('Механики','Mechanics')],['#rules','📏',T('Правила','Rules')],['#cmds','⌨️',T('Команды','Commands')],['guides/fokusy.html','🎯',T('Гайд по фокусам','Focus guide')],['#donate','💛',T('Поддержать','Support')]]}];
  const H=h=>U((h[0]==='#'?'./':'')+h);
  const groupsHTML=G=>G.map(g=>`<div class="sg"><div class="sgh">${g.i} ${esc(g.t)}</div><div class="sgl">${g.l.map(([h,i,l])=>`<a href="${esc(H(h))}"><span class="i">${i}</span>${esc(l)}</a>`).join('')}</div></div>`).join('');
  const siteNav=true;
  // ПК: вместо длинной ленты из 18 ссылок четыре группы с выпадающими списками
  const chapters=[...nav.querySelectorAll('a')].filter(a=>!/#|index\.html|\.\/$/.test(a.getAttribute('href'))&&/lore\//.test(a.href));
  const sn=document.createElement('nav'); sn.className='site'; sn.setAttribute('aria-label',T('Разделы сайта','Site sections'));
  const G=SITE.slice(); if(chapters.length>2) G.push({t:T('Главы','Chapters'),i:'📖',l:chapters.map(a=>[a.href,'',a.textContent])});
  sn.innerHTML=`<a class="sgo home" href="${esc(U('./'))}">${T('Главная','Home')}</a>`+G.map((g,n)=>`<div class="grp"><button type="button" aria-expanded="false" aria-haspopup="true">${esc(g.t)}<span class="car">▾</span></button><div class="dd">${g.l.map(([h,i,l])=>`<a href="${esc(/^https?:/.test(h)?h:H(h))}"${/^https?:/.test(h)&&h.split('#')[0]===location.href.split('#')[0]?' class="on"':''}>${i?`<span class="i">${i}</span>`:''}${esc(l)}</a>`).join('')}</div></div>`).join('');
  nav.after(sn); document.documentElement.classList.add('sitenav');
  const here=location.href.split('#')[0]; sn.querySelectorAll('.dd a').forEach(a=>{if(!a.href.includes('#')&&a.href===here) a.classList.add('on')});
  const closeDD=except=>sn.querySelectorAll('.grp.open').forEach(g=>{if(g!==except){g.classList.remove('open');g.firstElementChild.setAttribute('aria-expanded','false')}});
  sn.addEventListener('click',e=>{if(e.target.closest('.dd a')) return closeDD(); const b=e.target.closest('.grp>button'); if(!b) return; const g=b.parentNode, o=!g.classList.contains('open'); closeDD(g); g.classList.toggle('open',o); b.setAttribute('aria-expanded',o)});
  sn.addEventListener('mouseover',e=>{const g=e.target.closest('.grp'); if(g&&matchMedia('(hover:hover)').matches&&sn.querySelector('.grp.open')&&!g.classList.contains('open')){closeDD();g.classList.add('open')}});
  document.addEventListener('click',e=>{if(!e.target.closest('nav.site')) closeDD()});
  sn.addEventListener('keydown',e=>{if(e.key==='Escape'){closeDD();const b=e.target.closest('.grp')?.firstElementChild;b&&b.focus()}});
  // кнопка поиска в шапке
  const sb=document.createElement('button'); sb.type='button'; sb.className='iconbtn'; sb.id='srch'; sb.title=T('Поиск по сайту (/)','Search the site (/)'); sb.setAttribute('aria-label',T('Поиск','Search')); sb.textContent='🔍';
  const lang=$('#lang')||$('#theme'); if(lang) lang.before(sb); else header.querySelector('.wrap').appendChild(sb);
  sb.onclick=()=>openSearch();
  addEventListener('keydown',e=>{const t=e.target; if(t&&(t.isContentEditable||/INPUT|TEXTAREA|SELECT/.test(t.tagName))) return;
    if(e.key==='/'||((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k')){e.preventDefault();openSearch()}});
  // поиск: разделы, главы лора, механики, команды, правила, державы
  let IDX=null;
  const norm=s=>String(s||'').toLowerCase().replace(/ё/g,'е');
  const buildIdx=C=>{const r=[];
    SITE.forEach(g=>g.l.forEach(([h,i,l])=>r.push({u:H(h),i,t:l,s:g.t,k:''})));
    (C.lore||[]).forEach(l=>r.push({u:U('lore/'+l.id+'.html'),i:'📜',t:l.title,s:l.subtitle,k:T('лор','lore')}));
    (C.guides||[]).forEach(l=>r.push({u:U('guides/'+l.id+'.html'),i:'🎯',t:l.title,s:l.subtitle,k:T('гайд','guide')}));
    (C.mechanics||[]).forEach(m=>{r.push({u:U('./#m-'+m.id),i:m.icon,t:m.title,s:m.summary,k:(m.points||[]).join(' ')+' '+m.commands.join(' ')});
      m.commands.forEach(c=>r.push({u:U('./#m-'+m.id),i:'⌨️',t:c,s:m.title,k:T('команда','command'),cmd:1}))});
    (C.rules||[]).forEach(x=>r.push({u:U('./#rules'),i:'📏',t:x.title,s:(x.items||[]).slice(0,2).join(' · '),k:(x.items||[]).join(' ')}));
    ((C.roster||{}).rows||[]).forEach(x=>r.push({u:U('./#nations'),i:'🏛️',t:x.name,s:x.full,k:[x.ruler,x.note,x.towny].join(' ')}));
    (C.weeks||[]).forEach(w=>r.push({u:U('./#weeks'),i:'📆',t:T('Неделя ','Week ')+w.n+': '+w.title,s:w.text,k:(w.commands||[]).join(' ')}));
    const seen=new Set(); return r.filter(x=>{const id=x.u+'|'+x.t; if(seen.has(id)) return false; seen.add(id); x.n=norm(x.t+' '+x.s+' '+x.k); x.nt=norm(x.t); return true})};
  const loadIdx=()=>IDX?Promise.resolve(IDX):fetch(new URL('content.json',BASE)).then(r=>r.json()).then(C=>IDX=buildIdx(C)).catch(()=>IDX=buildIdx({}));
  function openSearch(){ closeDD();
    openSheet(T('Поиск по сайту','Search the site'),`<input class="search" id="sq" type="search" autocomplete="off" placeholder="${T('Карта, война, Ромея, /t new, Предтечи…','Map, war, Romea, /t new, Forerunners…')}"><div class="sres" id="sres"></div>`,'searchc');
    const q=$('#sq'), out=$('#sres');
    const draw=()=>{const v=norm(q.value).trim().replace(/^\/town\b/,'/t').replace(/^\/nation\b/,'/n'), w=v.split(/\s+/).filter(Boolean);
      if(!w.length){out.innerHTML=`<p class="shint">${T('Начните печатать. Подсказка: на ПК поиск открывается клавишей /','Start typing. Tip: on a computer press / to open search')}</p>`+groupsHTML(SITE);return}
      const hit=(IDX||[]).filter(x=>w.every(t=>x.n.includes(t))).map(x=>[x,(x.nt.startsWith(w[0])?3:x.nt.includes(w[0])?2:0)+(x.cmd&&v[0]==='/'?2:0)]).sort((a,b)=>b[1]-a[1]).slice(0,30);
      out.innerHTML=hit.length?hit.map(([x])=>`<a href="${esc(x.u)}"><span class="i">${x.i}</span><span class="st"><b>${x.cmd?code(x.t):esc(x.t)}</b><small>${esc(String(x.s||'').slice(0,110))}</small></span></a>`).join('')
        :`<p class="shint">${T('Ничего не нашлось. Попробуйте другое слово.','Nothing found. Try another word.')}</p>`};
    q.addEventListener('input',draw);
    q.addEventListener('keydown',e=>{if(e.key==='Enter'){const a=out.querySelector('a'); if(a){e.preventDefault(); closeSheet(a.href)}}});
    draw(); loadIdx().then(draw); setTimeout(()=>q.focus(),60);
  }
  // главная: блок «Быстрый переход»
  const go=$('#goGrid'); if(go) go.innerHTML=groupsHTML(SITE);
  // ссылка на механику (#m-…) раскрывает карточку
  const openMech=()=>{const h=decodeURIComponent(location.hash.slice(1)); if(!/^m-/.test(h)) return; let n=0;
    const t=setInterval(()=>{const d=document.getElementById(h); if(d||++n>40){clearInterval(t); if(d){d.open=true; d.scrollIntoView({block:'start'}); d.classList.add('flash'); setTimeout(()=>d.classList.remove('flash'),1600)}}},100)};
  addEventListener('hashchange',openMech); openMech();
  // кнопка «Наверх»
  const tt=document.createElement('button'); tt.type='button'; tt.className='totop'; tt.setAttribute('aria-label',T('Наверх','Back to top')); tt.title=T('Наверх','Back to top'); tt.textContent='↑'; document.body.appendChild(tt);
  tt.onclick=()=>scrollTo({top:0,behavior:'smooth'});
  // шторка снизу: меню разделов или оглавление
  const sh=document.createElement('div'); sh.className='sheet'; sh.hidden=true;
  sh.innerHTML=`<div class="sheet-bg" data-close></div><div class="sheet-p" role="dialog" aria-modal="true"><div class="sheet-h"><b></b><button class="iconbtn" data-close aria-label="${T('Закрыть','Close')}">✕</button></div><div class="sheet-c"></div></div>`;
  document.body.appendChild(sh);
  let pending=null;
  const openSheet=(title,links,cls)=>{sh.querySelector('.sheet-h b').textContent=title; const c=sh.querySelector('.sheet-c'); c.className='sheet-c '+(cls||'');
    c.innerHTML=''; if(typeof links==='string') c.innerHTML=links; else links.forEach(a=>{const n=a.cloneNode(true); n.removeAttribute('id'); c.appendChild(n)});
    sh.hidden=false; document.body.classList.add('sheetopen'); history.pushState({pxsheet:1},'');
    const on=c.querySelector('.on'); if(on) on.scrollIntoView({block:'center'});};
  const closeSheet=go=>{if(sh.hidden) return; sh.hidden=true; document.body.classList.remove('sheetopen'); pending=go||null;
    if(history.state&&history.state.pxsheet) history.back(); else if(pending){location.href=pending;pending=null}};
  addEventListener('popstate',()=>{if(!sh.hidden){sh.hidden=true;document.body.classList.remove('sheetopen')} if(pending){const p=pending;pending=null;setTimeout(()=>location.href=p,0)}});
  sh.addEventListener('click',e=>{if(e.target.closest('[data-close]')) return closeSheet(); const a=e.target.closest('a'); if(a){e.preventDefault(); closeSheet(a.href)}});
  addEventListener('keydown',e=>{if(e.key==='Escape') closeSheet()});
  // нижняя панель
  const items=aside?[[U('./'),'🏠',T('Главная','Home')],[U('lore.html'),'📚',T('Весь лор','All lore')]]
    .concat(tocLinks.length?[['#toc','📑',T('Оглавление','Contents')]]:[]).concat([['#top','⬆️',T('Наверх','Top')],['#menu','☰',T('Главы','Chapters')]])
    :[['#maps','🗺️',T('Карты','Maps')],[U('news.html'),'📰',T('Новости','News')],['#search','🔍',T('Поиск','Search')],[U('lore.html'),'📜',T('Лор','Lore')],['#menu','☰',T('Меню','Menu')]];
  const bar=document.createElement('nav'); bar.className='tabbar'; bar.setAttribute('aria-label',T('Быстрые разделы','Quick sections'));
  bar.innerHTML=items.map(([h,i,l])=>h[0]==='#'?`<button type="button" data-act="${h.slice(1)}"><span class="i">${i}</span>${esc(l)}</button>`:`<a href="${esc(h)}"><span class="i">${i}</span>${esc(l)}</a>`).join('');
  document.body.appendChild(bar); document.documentElement.classList.add('hasbar');
  if(!isIndex&&!aside) bar.querySelectorAll('a').forEach(a=>{if(a.href===U('lore.html')&&/lore\.html$/.test(location.pathname)) a.classList.add('on')});
  bar.addEventListener('click',e=>{const b=e.target.closest('button'); if(!b) return; const k=b.dataset.act;
    if(k==='menu'){ if(aside||!siteNav) openSheet(aside?T('Главы лора','Lore chapters'):T('Разделы','Sections'),[...nav.querySelectorAll('a')],'grid2');
      else openSheet(T('Разделы','Sections'),groupsHTML(SITE),'groups'); }
    else if(k==='maps') openSheet(T('Карты','Maps'),groupsHTML([SITE[1]]),'groups');
    else if(k==='search') openSearch();
    else if(k==='toc') openSheet(T('Оглавление','Contents'),tocLinks);
    else if(k==='top') scrollTo({top:0,behavior:'smooth'});});
  // где мы сейчас: подсветка на панели, в меню и в оглавлении
  nav.querySelectorAll('a').forEach(a=>{if(!a.getAttribute('href').startsWith('#')&&a.href.split('#')[0]===location.href.split('#')[0]) a.classList.add('on')});
  const secs=isIndex?[...nav.querySelectorAll('a[href^="#"]')].map(a=>[a,document.getElementById(a.getAttribute('href').slice(1))]).filter(x=>x[1]):[];
  const heads=tocLinks.map(a=>[a,document.getElementById(decodeURIComponent(a.getAttribute('href').slice(1)))]).filter(x=>x[1]);
  let bar1=null, resumeKey='pxread:'+location.pathname, saveT=0, saved=null, armed=false;
  try{saved=JSON.parse(localStorage.getItem(resumeKey)||'null')}catch(e){}
  if(aside){bar1=document.createElement('div'); bar1.className='readbar'; header.appendChild(bar1)}
  const spy=()=>{const y=scrollY+innerHeight*.3;
    if(isIndex){let cur=null; secs.forEach(([a,s])=>{if(s.offsetTop<=y) cur=s.id});
      secs.forEach(([a,s])=>a.classList.toggle('on',s.id===cur));
      bar.querySelectorAll('a').forEach(a=>a.classList.toggle('on',!!cur&&a.href.endsWith('#'+cur)));
      sn.querySelectorAll('.grp').forEach(g=>{let on=false; g.querySelectorAll('a').forEach(a=>{const m=!!cur&&a.href.endsWith('#'+cur); a.classList.toggle('on',m); on=on||m}); g.classList.toggle('cur',on)});}
    else sn.querySelectorAll('.grp').forEach(g=>g.classList.toggle('cur',!!g.querySelector('a.on')));
    tt.classList.toggle('show',scrollY>900);
    if(heads.length){let cur=null; heads.forEach(([a,h])=>{if(h.offsetTop<=y) cur=a}); heads.forEach(([a])=>a.classList.toggle('on',a===cur));
      const max=document.documentElement.scrollHeight-innerHeight; if(bar1) bar1.style.transform=`scaleX(${max>0?Math.min(1,scrollY/max):0})`;
      const now=Date.now(); if(armed&&now-saveT>800){saveT=now; try{localStorage.setItem(resumeKey,JSON.stringify({y:scrollY,id:cur?cur.getAttribute('href').slice(1):'',t:cur?cur.textContent:''}))}catch(e){}}}};
  let raf=0; addEventListener('scroll',()=>{if(!raf) raf=requestAnimationFrame(()=>{raf=0;spy()})},{passive:true}); addEventListener('load',spy); spy();
  setTimeout(()=>{armed=true},1500);
  // «Продолжить чтение»: глава помнит, где вы остановились
  if(heads.length&&!location.hash){const s=saved;
    if(s&&s.y>1200&&scrollY<600){const r=document.createElement('div'); r.className='resume';
      r.innerHTML=`<button type="button" class="go">▶ ${T('Продолжить','Continue')}${s.t?': <span>'+esc(s.t)+'</span>':''}</button><button type="button" class="x" aria-label="${T('Скрыть','Hide')}">✕</button>`;
      document.body.appendChild(r); const hide=()=>r.remove(); setTimeout(hide,12000); addEventListener('scroll',()=>{if(scrollY>1500) hide()},{passive:true});
      r.querySelector('.x').onclick=hide;
      r.querySelector('.go').onclick=()=>{const h=s.id&&document.getElementById(decodeURIComponent(s.id)); if(h) h.scrollIntoView(); else scrollTo(0,s.y); hide()};}}
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

// ---- календарь событий (C.calendar.events: day — день от старта; сезоны добавляются сами) ----
function calEvents(C){
  const ev=((C.calendar||{}).events||[]).map(e=>({...e}));
  for(let k=0,d=28;d<=90;k++,d+=7) ev.push({day:d,icon:['🌱','☀️','🍂','❄️'][k%4],kind:'season',title:T('Сезон: ','Season: ')+SEASONS[k%4],text:''});
  return ev.sort((a,b)=>a.day-b.day||(a.kind==='season')-(b.kind==='season'));
}
const LOC=EN?'en-GB':'ru-RU';
const fmtDate=d=>d.toLocaleString(LOC,{weekday:'short',day:'numeric',month:'long',hour:'2-digit',minute:'2-digit'});
function fmtLeft(ms){ms=Math.max(0,ms);const s=Math.floor(ms/1e3),d=Math.floor(s/86400),h=Math.floor(s%86400/3600),m=Math.floor(s%3600/60),x=s%60,p=n=>String(n).padStart(2,'0');
  return `<span class="cd"><b>${d}</b><i>${T('дн','d')}</i><b>${p(h)}</b><i>${T('ч','h')}</i><b>${p(m)}</b><i>${T('мин','m')}</i><b>${p(x)}</b><i>${T('сек','s')}</i></span>`}
function icsFile(C,t0,ev){
  const z=d=>d.toISOString().replace(/[-:]/g,'').replace(/\.\d+/,''), q=s=>String(s).replace(/[\\,;]/g,m=>'\\'+m).replace(/\n/g,'\\n');
  const L=['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//PaxVanila//Calendar//'+(EN?'EN':'RU'),'CALSCALE:GREGORIAN','X-WR-CALNAME:PaxVanila'];
  ev.forEach((e,i)=>{const a=new Date(t0.getTime()+e.day*864e5);L.push('BEGIN:VEVENT',`UID:pax-${e.day}-${i}@paxvanila`,'DTSTAMP:'+z(new Date()),'DTSTART:'+z(a),'DTEND:'+z(new Date(a.getTime()+36e5)),'SUMMARY:'+q(e.icon+' '+e.title),'DESCRIPTION:'+q(e.text||''),'END:VEVENT')});
  L.push('END:VCALENDAR'); return new Blob([L.join('\r\n')],{type:'text/calendar'});
}
function renderCalendar(C){
  const box=$('#calBox'); if(!box) return;
  const cfg=C.config, t0=new Date(cfg.launchDate||''), ev=calEvents(C);
  if(isNaN(t0)){box.innerHTML=`<div class="calnow"><div class="l">${T('Старт','Launch')}</div><div class="v">${T('Скоро','Soon')}</div><p class="s">${T('Дата появится в Discord.','The date will be announced on Discord.')}</p></div>`;return}
  const at=e=>new Date(t0.getTime()+e.day*864e5);
  let tl='';
  const head=()=>{
    const now=new Date(), s=serverState(cfg,now), next=ev.find(e=>at(e)>now&&(s.started||e.day>0)), w=s.started?C.weeks.find(x=>x.n===s.week):null;
    const cur=s.started?[...ev].reverse().find(e=>at(e)<=now&&e.kind!=='season'):null;
    let h='';
    if(!s.started) h+=`<div class="calnow big"><div class="l">${T('До открытия сервера','Until the server opens')}</div><div class="v">${fmtLeft(t0-now)}</div><p class="s">${fmtDate(t0)} · ${T('граница','border')} ${cfg.border.start} ${T('блоков','blocks')}</p></div>`;
    else h+=`<div class="calnow big"><div class="l">${T('Сейчас','Now')} · ${T('день','day')} ${s.day}</div><div class="v sm">${T('Неделя','Week')} ${s.week}${w?': '+esc(w.title):''}</div><p class="s">${cur?esc(cur.icon+' '+cur.title):''}${s.warPhase&&!(cur&&cur.kind==='war'&&cur.title===s.warPhase)?' · '+s.warPhase:''}${s.season?' · '+s.season:''} · ${T('граница','border')} ${s.radius} → ${s.tomorrow}</p></div>`;
    if(next) h+=`<div class="calnow"><div class="l">${T('Следующее событие','Next event')}</div><div class="v sm">${next.icon} ${esc(next.title)}</div><p class="s">${fmtDate(at(next))}</p><div class="v">${fmtLeft(at(next)-now)}</div></div>`;
    h+=`<div class="calnow"><div class="l">${T('Окно боёв','Battle window')} ${cfg.primeFrom}:00–${cfg.primeTo}:00 ${T('МСК','Moscow')}</div><div class="v sm">${s.prime?T('⚔️ Открыто','⚔️ Open'):T('🕊️ Закрыто','🕊️ Closed')}</div><p class="s">${s.prime?T('закроется через ','closes in '):T('откроется через ','opens in ')}${fmtMin(s.primeIn)}</p></div>`;
    return {h,next};
  };
  const list=next=>{const now=new Date();return `<ol class="caltl">${ev.map(e=>{const d=at(e),past=d<=now,isNext=e===next;
    return `<li class="k-${e.kind}${past?' past':''}${isNext?' next':''}"><div class="when"><span class="dn">${T('День','Day')} ${e.day+1}</span>${d.toLocaleDateString(LOC,{day:'numeric',month:'short'})}</div><div class="what"><div class="t">${e.icon} ${esc(e.title)}${isNext?` <span class="tag">${T('дальше','next')}</span>`:''}</div>${e.text?`<p>${esc(e.text)}</p>`:''}</div></li>`}).join('')}</ol>`};
  box.innerHTML=`<div class="calhead" id="calHead"></div><div class="calbar"><button class="btn" id="calIcs">📅 ${T('Добавить в свой календарь (.ics)','Add to your calendar (.ics)')}</button><span class="tz">${T('Ваш часовой пояс','Your time zone')}: ${esc(Intl.DateTimeFormat().resolvedOptions().timeZone||'')}</span></div><div id="calList"></div>`;
  let lastNext;
  const tick=()=>{const r=head();$('#calHead').innerHTML=r.h; if(r.next!==lastNext||tl===''){lastNext=r.next;tl=list(r.next);$('#calList').innerHTML=tl}};
  tick(); setInterval(tick,1000);
  $('#calIcs').onclick=()=>{const u=URL.createObjectURL(icsFile(C,t0,ev)),a=document.createElement('a');a.href=u;a.download='PaxVanila.ics';document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(u),2000)};
}

async function main(){
  const C=await (await fetch('content.json?v=20261120185002')).json(), cfg=C.config; window.__C=C;
  document.querySelectorAll('[data-k]').forEach(e=>{e.textContent=e.dataset.k in C?C[e.dataset.k]:cfg[e.dataset.k]||''});
  // IP и Discord
  const ipBtn=$('#copyip');
  if(ipBtn){ if(cfg.serverAddress){$('#ipText').textContent=cfg.serverAddress;ipBtn.onclick=()=>navigator.clipboard.writeText(cfg.serverAddress).then(()=>toast(T('Адрес скопирован','Address copied')))} else ipBtn.disabled=true;
    const d=$('#discord'); if(cfg.discordUrl) d.href=cfg.discordUrl; else {d.removeAttribute('href');d.style.opacity=.55;d.title=T('Ссылка появится перед открытием','The link will appear before launch')} }
  document.querySelectorAll('[data-boosty]').forEach(a=>{if(cfg.boostyUrl)a.href=cfg.boostyUrl;else a.hidden=true});
  renderNow(C); setInterval(()=>renderNow(C),30000);
  renderCalendar(C);
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
  renderChronicleTeaser(C);
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
let _live=null; const meteoLive=cfg=>_live||(_live=Promise.all([liveJson(cfg,'meteo.json'),liveJson(cfg,'news.json')]));
const fmtTime=t=>new Date(t*1000).toLocaleString(EN?'en-GB':'ru-RU',{day:'numeric',month:'short',hour:'2-digit',minute:'2-digit'});
const mmss=s=>{s=Math.max(0,s|0);return `${Math.floor(s/60)}:${String(s%60).padStart(2,'0')}`};
async function renderWeather(C){
  const M=C.meteo, cfg=C.config; if(!M||!$('#wxBulletin')) return;
  const [lm,ln]=await meteoLive(cfg);
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
  $('#wxLog').innerHTML=h.length?h.map(x=>{const e=ev(x.n);return `<li><time>${fmtTime(x.t)}</time> ${e?e.icon+' '+esc(e.name):'#'+x.n}${x.w?` <small>· ${esc(cataPlace(x))}</small>`:''}</li>`}).join(''):`<li>${T('Пока ни одного катаклизма.','No cataclysms yet.')}</li>`;
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

// ---- общий движок карт: мышь, колёсико, жесты на телефоне, кнопки и полный экран ----
// На телефоне вне полного экрана один палец листает страницу, двумя пальцами двигаем и приближаем карту.
// В полном экране (кнопка ⛶) карта двигается одним пальцем, двойной тап приближает.
const TOUCH=matchMedia('(pointer:coarse)').matches;
const ZOOMBTNS=()=>`<div class="mzoom"><button data-z="0.67" aria-label="${T('Приблизить','Zoom in')}">+</button><button data-z="1.5" aria-label="${T('Отдалить','Zoom out')}">−</button><button data-z="0" aria-label="${T('Сбросить','Reset')}">⟲</button><button data-fs class="fsb" aria-label="${T('На весь экран','Full screen')}">⛶</button></div>`;
function panZoom(o){
  const {host,svg,info,minW,maxW,coord}=o; let vb={x:0,y:0,w:1,h:1};
  const box=host.querySelector('.mbox'), cEl=host.querySelector('.mcoord'), fsBtn=host.querySelector('[data-fs]');
  const ar=()=>svg.clientHeight/Math.max(1,svg.clientWidth)||1;
  const apply=()=>{const cy=vb.y+vb.h/2; vb.h=vb.w*ar(); vb.y=cy-vb.h/2;
    svg.setAttribute('viewBox',`${vb.x} ${vb.y} ${vb.w} ${vb.h}`); svg.style.setProperty('--k',vb.w/Math.max(1,svg.clientWidth));};
  const fit=(x0,y0,x1,y1,pad=1)=>{const a=ar(), nw=Math.max(x1-x0,(y1-y0)/a)*pad; vb={x:(x0+x1)/2-nw/2,y:(y0+y1)/2-nw*a/2,w:nw,h:nw*a}; apply()};
  const toWorld=(cx,cy)=>{const r=svg.getBoundingClientRect();return [vb.x+(cx-r.left)/r.width*vb.w, vb.y+(cy-r.top)/r.height*vb.h]};
  const zoom=(f,cx,cy)=>{const nw=Math.min(maxW,Math.max(minW,vb.w*f)); f=nw/vb.w; const [wx,wy]=toWorld(cx,cy);
    vb.x=wx-(wx-vb.x)*f; vb.y=wy-(wy-vb.y)*f; vb.w=nw; vb.h*=f; apply()};
  const pan=(dx,dy)=>{const r=svg.getBoundingClientRect(); vb.x-=dx/r.width*vb.w; vb.y-=dy/r.height*vb.h; apply()};
  const showCoord=(cx,cy)=>{if(cEl){const [x,y]=toWorld(cx,cy); cEl.textContent=coord(x,y)}};
  const isFs=()=>host.classList.contains('fs');
  // подсказка «двумя пальцами»
  const hintEl=document.createElement('div'); hintEl.className='mhint';
  hintEl.innerHTML=T('Двигай карту <b>двумя пальцами</b><br>или открой её на весь экран <b>⛶</b>','Move the map with <b>two fingers</b><br>or open it full screen <b>⛶</b>'); box.appendChild(hintEl);
  let hintTO; const hint=()=>{hintEl.classList.add('show'); clearTimeout(hintTO); hintTO=setTimeout(()=>hintEl.classList.remove('show'),1500)};
  // полный экран: масштаб в блоках на пиксель и центр сохраняются; «Назад» на телефоне закрывает
  const toggleFs=(on=!isFs(),fromPop)=>{ if(on===isFs()) return;
    const k=vb.w/Math.max(1,svg.clientWidth), cx=vb.x+vb.w/2, cy=vb.y+vb.h/2;
    host.classList.toggle('fs',on); document.body.classList.toggle('mapfs',on);
    fsBtn.textContent=on?'✕':'⛶'; fsBtn.setAttribute('aria-label',on?T('Закрыть полный экран','Exit full screen'):T('На весь экран','Full screen'));
    vb.w=k*svg.clientWidth; vb.h=vb.w*ar(); vb.x=cx-vb.w/2; vb.y=cy-vb.h/2; apply();
    if(on&&!fromPop) history.pushState({pxfs:host.id},'');
    else if(!on&&!fromPop&&history.state&&history.state.pxfs===host.id) history.back();
    if(!on) host.scrollIntoView({block:'start'});
  };
  addEventListener('popstate',()=>{if(isFs()) toggleFs(false,true)});
  addEventListener('keydown',e=>{if(e.key==='Escape'&&isFs()) toggleFs(false)});
  host.querySelector('.mzoom').addEventListener('click',e=>{const b=e.target.closest('button'); if(!b) return;
    if('fs' in b.dataset) return toggleFs(); const z=+b.dataset.z; if(isNaN(z)) return; if(!z) return o.reset();
    const r=svg.getBoundingClientRect(); zoom(z,r.left+r.width/2,r.top+r.height/2)});
  svg.addEventListener('wheel',e=>{e.preventDefault();zoom(e.deltaY>0?1.2:1/1.2,e.clientX,e.clientY)},{passive:false});
  // мышь и перо
  let moved=0, lastTouch=0; const pts=new Map();
  svg.addEventListener('pointerdown',e=>{if(e.pointerType==='touch')return; pts.set(e.pointerId,[e.clientX,e.clientY]); moved=0});
  svg.addEventListener('pointermove',e=>{if(e.pointerType==='touch')return; showCoord(e.clientX,e.clientY);
    const p0=pts.get(e.pointerId); if(!p0) return; pts.set(e.pointerId,[e.clientX,e.clientY]);
    const dx=e.clientX-p0[0], dy=e.clientY-p0[1]; moved+=Math.abs(dx)+Math.abs(dy);
    if(moved>4){svg.setPointerCapture(e.pointerId); pan(dx,dy)}});
  const up=e=>pts.delete(e.pointerId); svg.addEventListener('pointerup',up); svg.addEventListener('pointercancel',up);
  svg.addEventListener('dblclick',e=>{e.preventDefault(); if(Date.now()-lastTouch<800) return; zoom(0.5,e.clientX,e.clientY)});
  // пальцы
  let G=null, tapT=0, tapXY=null;
  const mid=t=>t.length>1?[(t[0].clientX+t[1].clientX)/2,(t[0].clientY+t[1].clientY)/2]:[t[0].clientX,t[0].clientY];
  const dist=t=>t.length>1?Math.hypot(t[0].clientX-t[1].clientX,t[0].clientY-t[1].clientY):0;
  svg.addEventListener('touchstart',e=>{lastTouch=Date.now(); const t=e.touches; if(t.length===1) moved=0; else moved=99; G={m:mid(t),d:dist(t),n:t.length}},{passive:true});
  svg.addEventListener('touchmove',e=>{const t=e.touches; if(!G||!t.length) return; const m=mid(t);
    if(t.length!==G.n){G={m,d:dist(t),n:t.length};return}
    const dx=m[0]-G.m[0], dy=m[1]-G.m[1];
    if(t.length===1&&!isFs()){moved+=Math.abs(dx)+Math.abs(dy); G.m=m; if(moved>14) hint(); return}
    if(!e.cancelable) return; e.preventDefault();
    moved+=Math.abs(dx)+Math.abs(dy); pan(dx,dy);
    if(t.length>1){const d=dist(t); if(G.d&&d) zoom(G.d/d,m[0],m[1]); G.d=d}
    G.m=m; showCoord(m[0],m[1]);},{passive:false});
  svg.addEventListener('touchend',e=>{lastTouch=Date.now(); const t=e.touches; if(t.length){G={m:mid(t),d:dist(t),n:t.length};return} G=null;
    if(moved<10){const c=e.changedTouches[0], now=Date.now(); showCoord(c.clientX,c.clientY);
      if(now-tapT<320&&tapXY&&Math.hypot(c.clientX-tapXY[0],c.clientY-tapXY[1])<30){zoom(0.5,c.clientX,c.clientY);tapT=0}
      else{tapT=now;tapXY=[c.clientX,c.clientY]}}});
  svg.addEventListener('touchcancel',()=>{G=null});
  svg.addEventListener('click',e=>{if(moved>8){e.stopPropagation();e.preventDefault();return}
    // на телефоне после выбора метки показываем карточку под картой
    if(info&&TOUCH&&!isFs()&&e.target.closest('[tabindex]')) setTimeout(()=>{const r=info.getBoundingClientRect(); if(r.bottom>innerHeight-70) scrollBy({top:Math.min(r.bottom-innerHeight+80,r.top-70),behavior:'smooth'})},30)},true);
  addEventListener('resize',apply);
  return {fit,apply,zoom,toWorld,get vb(){return vb},isFs,toggleFs};
}

// ---- карта мира (данные: C.map из content/map.json и content/map_towns.json) ----
function renderMap(C){
  const host=$('#pxmap'); if(!host||!C.map) return;
  const M=C.map, cfg=C.config, b=cfg.border, st=serverState(cfg);
  const rings=[['start',T('Старт','Start')],['w1',T('Н1','W1')],['w2',T('Н2','W2')],['w3',T('Н3','W3')],['w5',T('Н5','W5')],['w6',T('Н6','W6')]];
  const R=b.w6, ext=R*1.12, NS='http://www.w3.org/2000/svg';
  const layers={powers:true,ancient:true,towns:true,grid:true,far:true,lore:true,wx:false,terrain:true,recent:true}; const TR=M.terrain, Z=M.zones; M.far=M.far||[]; M.lore=M.lore||[];
  let sel=st.started?null:'w6';
  host.innerHTML=`<div class="mtools">
     <div class="chips" id="mLayers">
       <button data-l="powers" class="on">${T('Державы','Powers')}</button><button data-l="ancient" class="on">${T('Древние места','Ancient sites')}</button>
       <button data-l="towns" class="on">${T('Города','Towns')}${M.towns.length?' ('+M.towns.length+')':''}</button><button data-l="grid" class="on">${T('Сетка','Grid')}</button>${TR?`<button data-l="terrain" class="on">${T('Рельеф','Terrain')}</button>`:''}<button data-l="wx" class="hl">🌦️ ${T('Погода','Weather')}</button>${C.cata?`<button data-l="recent" class="on" id="mRecBtn">🕒 ${T('Недавние катаклизмы','Recent cataclysms')}</button>`:''}${M.lore.length?`<button data-l="lore" class="on">${T('Метки лора','Lore tags')} (${M.lore.length})</button>`:''}${M.far.length?`<button data-l="far" class="on">${T('За границей','Beyond the border')}</button><button id="mAll" class="hl">🌍 ${T('Все миры','All worlds')} (${M.far.length})</button>`:''}</div>
     <div class="chips" id="mRings"><span class="lbl">${T('Граница','Border')}</span>${rings.map(r=>`<button data-r="${r[0]}">${r[1]}</button>`).join('')}</div>
   </div>
   <div class="mbox"><svg id="msvg" class="msvg" role="img" aria-label="${T('Карта мира PaxVanila','PaxVanila world map')}"></svg>
     ${ZOOMBTNS()}
     <div class="mcoord" id="mcoord">X 0 · Z 0</div><div class="mcomp">${T('С','N')}↑</div></div>
   <div class="mwx" id="mwx" hidden></div>
   <div class="mrecent" id="mrecent"></div>
   <div class="minfo" id="minfo"></div>
   <p class="mnote">${TR?T(`Рельеф, реки, озёра и леса нарисованы блок в блок с настоящего мира PaxVanila (те же датапаки: Terralith, Towns and Towers, Structory). Разведано ${TR.bounds[2]-TR.bounds[0]}×${TR.bounds[3]-TR.bounds[1]} блоков вокруг спавна, дальше карта показывает схему и будет расти`,`Terrain, rivers, lakes and forests are rendered block by block from the real PaxVanila world (same datapacks: Terralith, Towns and Towers, Structory). ${TR.bounds[2]-TR.bounds[0]}×${TR.bounds[3]-TR.bounds[1]} blocks around spawn are explored; beyond that the map shows the schematic and will grow`)+(TR.date?' · '+esc(TR.date):'')+`. <a href="${esc(TR.big)}" target="_blank" rel="noopener">${T('Подробная карта 1:1','Full-size map 1:1')}</a>. `:''}${T('Державы и древние места показаны схемой по лору: настоящие столицы строят игроки.','Powers and ancient sites are a schematic based on the lore: the real capitals are built by players.')}
     ${M.towns.length?T(' Города Towny выгружены ',' Towny towns exported ')+esc(M.townsDate)+'.':T(' Реальные города появятся после открытия сервера.',' Real towns will appear after the server opens.')}
     ${cfg.mapUrl?` <a class="btn" href="${esc(cfg.mapUrl)}" target="_blank" rel="noopener">🗺️ ${T('Живая карта BlueMap','Live BlueMap')}</a>`:''}</p>`;
  const svg=$('#msvg'), el=(n,a,p)=>{const e=document.createElementNS(NS,n);for(const k in a)e.setAttribute(k,a[k]);(p||svg).appendChild(e);return e};
  const cp=el('clipPath',{id:'mclip'},el('defs',{})); el('circle',{cx:0,cy:0,r:R},cp);
  const g={}; ['base','terrain','wx','grid','powers','rings','ancient','towns','lore','recent','far','top'].forEach(k=>g[k]=el('g',{class:'g-'+k}));
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
    el('circle',{cx:p.x,cy:p.z,r:20,class:'hit'},a); el('rect',{x:p.x-22,y:p.z-22,width:44,height:44,transform:`rotate(45 ${p.x} ${p.z})`,class:'and'},a);
    el('text',{x:p.x,y:p.z+62,class:'at'},a).textContent=p.name; a.onclick=()=>pick(p,T('Предтечи','Forerunners'));});
  M.towns.forEach(t=>{const a=el('g',{class:'tw',tabindex:0},g.towns); const col=t.color||'#9a6b12';
    (t.blocks||[]).forEach(([cx,cz])=>el('rect',{x:cx*16,y:cz*16,width:16,height:16,fill:col,class:'tb'},a));
    el('circle',{cx:t.x,cy:t.z,r:20,class:'hit'},a); el('circle',{cx:t.x,cy:t.z,r:10,fill:col,class:'twd'},a); el('text',{x:t.x,y:t.z+30,class:'tt'},a).textContent=t.name;
    a.onclick=()=>pick({...t,text:(t.nation?T('Нация: ','Nation: ')+t.nation+'. ':'')+T('Занято чанков: ','Claimed chunks: ')+(t.blocks||[]).length},T('город','town'));});
  const LC={legend:['✦',T('легенда','legend')],cataclysm:['⚡',T('катаклизм','cataclysm')],battle:['⚔',T('битва','battle')],front:['☠',T('Хроника фронта','Front Chronicle')],old:['◉',T('Старые записи','Old Recordings')]};
  M.lore.forEach(p=>{const c=LC[p.cat]||['•',''], a=el('g',{class:'lt c-'+p.cat,tabindex:0},g.lore);
    el('circle',{cx:p.x,cy:p.z,r:20,class:'hit'},a); el('circle',{cx:p.x,cy:p.z,r:9,class:'ld'},a); const tx=el('text',{x:p.x,y:p.z-14,class:'ltx'},a); tx.textContent=c[0]+' '+p.name;
    const go=()=>pick({...p,lore:p.lore||(p.cat==='front'?'front':'')},c[1]); a.onclick=go; a.onkeydown=e=>{if(e.key==='Enter')go()};});
  M.far.forEach(p=>{const a=el('g',{class:'far'+(p.kind?' k-'+p.kind:''),tabindex:0},g.far), d=Math.hypot(p.x,p.z)||1, ex=p.x/d*R, ez=p.z/d*R;
    el('line',{x1:ex,y1:ez,x2:p.x,y2:p.z,class:'fl'},a);
    el('text',{x:ex+(p.x-ex)*(p.kind?0.4:0.12),y:ez+(p.z-ez)*(p.kind?0.4:0.12)-14,class:'fh'},a).textContent=T('за границей → ','beyond the border → ')+Math.round(d)+T(' бл.',' bl.');
    el('circle',{cx:p.x,cy:p.z,r:160,class:'fa'},a);
    el('path',{d:`M${p.x-60} ${p.z-60}L${p.x+60} ${p.z+60}M${p.x+60} ${p.z-60}L${p.x-60} ${p.z+60}`,class:'fx'},a);
    el('text',{x:p.x,y:p.z+200,class:'ft'},a).textContent=p.name;
    const go=()=>{pick(p,p.kind==='old'?T('другой мир · Старые записи','another world · Old Recordings'):T('за границей мира','beyond the border'));ctl.fit(Math.min(-R,p.x-400),Math.min(-R,p.z-400),Math.max(R,p.x+400),Math.max(R,p.z+400),1.08)};
    a.onclick=go; a.onkeydown=e=>{if(e.key==='Enter')go()};
    if(p.lore) info.dataset.far=p.lore;});
  M.places.forEach(p=>{const a=el('g',{class:'mono',tabindex:0},g.top);
    el('circle',{cx:p.x,cy:p.z,r:20,class:'hit'},a); el('rect',{x:p.x-18,y:p.z-18,width:36,height:36,class:'md'},a); el('text',{x:p.x,y:p.z-34,class:'mt'},a).textContent=p.name;
    a.onclick=()=>pick(p,T('центр мира','world centre'));});
  pick(M.places[0],T('центр мира','world centre'));
  // слои и кольца
  $('#mLayers').onclick=e=>{const k=e.target.dataset.l;if(!k)return;layers[k]=!layers[k];e.target.classList.toggle('on',layers[k]);g[k].style.display=layers[k]?'':'none';if(k==='wx')wxBox.hidden=!layers.wx;if(k==='recent')$('#mrecent').hidden=!layers.recent};
  const markRing=()=>{document.querySelectorAll('#mRings button').forEach(x=>x.classList.toggle('on',x.dataset.r===sel));
    for(const k in ringEls) ringEls[k].forEach(e=>e.classList.toggle('sel',k===sel));};
  $('#mRings').onclick=e=>{const k=e.target.dataset.r;if(!k)return;sel=sel===k?null:k;markRing()}; markRing();
  // приближение и перетаскивание (viewBox в блоках)
  const fitAll=()=>{let x0=-R,x1=R,z0=-R,z1=R; M.far.forEach(p=>{x0=Math.min(x0,p.x-1700);x1=Math.max(x1,p.x+1700);z0=Math.min(z0,p.z-700);z1=Math.max(z1,p.z+700)});
    if(!layers.far){layers.far=true;g.far.style.display='';const b=host.querySelector('[data-l="far"]');b&&b.classList.add('on')} ctl.fit(x0,z0,x1,z1,1.05)};
  { const b=host.querySelector('#mAll'); if(b) b.onclick=e=>{e.stopPropagation();fitAll()}; }
  const reset=()=>ctl.fit(-ext,-ext,ext,ext);
  const fitTerrain=()=>{const [x0,z0,x1,z1]=TR.bounds; ctl.fit(x0,z0,x1,z1,1.7)};
  const ctl=panZoom({host,svg,info,minW:120,maxW:14*ext,coord:(x,z)=>`X ${Math.round(x)} · Z ${Math.round(z)}`,reset:()=>M.far.length?fitAll():reset()});
  TR?fitTerrain():M.far.length?fitAll():reset();
  // слой «Недавние катаклизмы»: журнал meteo.json (живой с сервера или демо) → метки на карте
  if(C.cata) meteoLive(cfg).then(([lm])=>renderRecent(C,lm||C.meteoDemo,{g:g.recent,el,R,Z,pick,focus:(x,z,w)=>ctl.fit(x-w/2,z,x+w/2,z)}));
}
// ---- недавние катаклизмы на карте (справочник: C.cata из content/cataclysms.json ← weather_for_map.json датапака) ----
const cataEv=n=>((window.__C&&window.__C.cata&&window.__C.cata.events)||[]).find(e=>e.n===n);
const cataPlace=h=>{
  if(h.w==='moon') return '🌙 '+T('Луна','Moon');
  if(h.w==='mars') return '🔴 '+T('Марс','Mars');
  if(h.x!=null) return `${T('квадрат','square')} X ${h.x}…${h.x+(h.s||128)} · Z ${h.z}…${h.z+(h.s||128)}`;
  const e=cataEv(h.n); if(e&&e.area==='point:0,0') return T('Монолит 0,0','Monolith 0,0');
  if(e&&e.area.startsWith('zone:')) return {desert:T('пустыни','deserts'),water:T('моря и реки','seas and rivers'),snow:T('снежные земли','snowy lands'),peaks:T('вершины','peaks')}[e.area.slice(5)];
  return T('по всему миру','across the world')};
const agoText=s=>{s=Math.max(0,s);if(s<3600)return T(`${Math.max(1,Math.round(s/60))} мин назад`,`${Math.max(1,Math.round(s/60))} min ago`);
  if(s<172800)return T(`${Math.round(s/3600)} ч назад`,`${Math.round(s/3600)} h ago`);return T(`${Math.round(s/86400)} дн. назад`,`${Math.round(s/86400)} d ago`)};
function renderRecent(C,D,m){
  const host=$('#mrecent'); if(!host) return;
  const H=[...(D.history||[])].filter(h=>cataEv(h.n)).sort((a,b)=>b.t-a.t);
  const now=D.demo?D.updated:Date.now()/1000, cur=D.event&&D.event.n>0?D.event.n:0;
  const periods=[[86400,T('24 часа','24 hours')],[3*86400,T('3 дня','3 days')],[7*86400,T('7 дней','7 days')],[0,T('Все','All')]];
  let per=H.some(h=>now-h.t<=86400)?3*86400:0, sel=null;
  // где событие на карте Мира 1: квадрат наблюдения, точка или зона
  const spot=h=>{const e=cataEv(h.n), s=h.s||128;
    if(h.w&&h.w!=='earth') return null;
    if(h.x!=null) return {x:h.x+s/2,z:h.z+s/2,sq:[h.x,h.z,s]};
    if(e.area.startsWith('point:')){const [x,z]=e.area.slice(6).split(',').map(Number);return {x,z}}
    if(e.area.startsWith('zone:')&&m.Z){const L=m.Z[e.area.slice(5)]||[],c=m.Z.cell||64; if(!L.length) return null;
      const x=L.reduce((a,p)=>a+p[0],0)/L.length+c/2, z=L.reduce((a,p)=>a+p[1],0)/L.length+c/2; return {x,z,zone:L,cell:c}}
    return null};
  const info=h=>{const e=cataEv(h.n), live=h.n===cur&&h===H[0];
    return {name:`${e.icon} ${e.name}`,x:h.x??'',z:h.z??'',
      text:`${live?T('Идёт прямо сейчас. ','Happening right now. '):''}${fmtTime(h.t)} (${agoText(now-h.t)}). ${T('Где','Where')}: ${cataPlace(h)}. ${e.where}. ${T('Длится','Lasts')} ${Math.round(e.dur[0]/60)}–${Math.round(e.dur[1]/60)} ${T('мин','min')}.`+(h.p?` ${T('Игроков в том мире','Players in that world')}: ${h.p}.`:'')}};
  const show=h=>{sel=h; const e=cataEv(h.n), sp=spot(h), o=info(h);
    m.pick({name:o.name,x:sp?Math.round(sp.x):'—',z:sp?Math.round(sp.z):'—',text:o.text},T('катаклизм','cataclysm'));
    if(sp) m.focus(sp.x,sp.z,sp.zone?Math.max(900,m.R*0.9):900); draw()};
  const draw=()=>{
    const L=H.filter(h=>!per||now-h.t<=per);
    m.g.innerHTML='';
    // старые снизу, свежие сверху; прозрачность по возрасту
    [...L].reverse().forEach(h=>{const e=cataEv(h.n), sp=spot(h); if(!sp) return;
      const age=now-h.t, op=Math.max(.35,1-age/(per||7*86400)), live=h.n===cur&&h===H[0];
      const a=m.el('g',{class:'rc'+(live?' live':'')+(h===sel?' sel':''),tabindex:0,style:`--c:${e.color};opacity:${op.toFixed(2)}`},m.g);
      if(sp.zone) m.el('path',{d:sp.zone.map(([x,z])=>`M${x} ${z}h${sp.cell}v${sp.cell}h${-sp.cell}z`).join(''),class:'rcz'},a);
      if(sp.sq) m.el('rect',{x:sp.sq[0],y:sp.sq[1],width:sp.sq[2],height:sp.sq[2],class:'rcs'},a);
      m.el('circle',{cx:sp.x,cy:sp.z,r:90,class:'rch'},a);
      m.el('circle',{cx:sp.x,cy:sp.z,r:34,class:'rcd'},a);
      m.el('text',{x:sp.x,y:sp.z,class:'rci'},a).textContent=e.icon;
      m.el('text',{x:sp.x,y:sp.z+70,class:'rct'},a).textContent=`${e.name} · ${agoText(age)}`;
      const go=()=>show(h); a.onclick=go; a.onkeydown=k=>{if(k.key==='Enter')go()};});
    const off=L.filter(h=>!spot(h)).length, b=$('#mRecBtn'); if(b) b.textContent=`🕒 ${T('Недавние катаклизмы','Recent cataclysms')} (${L.length})`;
    host.innerHTML=`<div class="rhead"><h3>🕒 ${T('Недавние катаклизмы','Recent cataclysms')}</h3>${D.demo?`<span class="demo">${T('ДЕМО','DEMO')}</span>`:''}
      <div class="chips">${periods.map(([s,l])=>`<button data-p="${s}" class="${s===per?'on':''}">${l}</button>`).join('')}</div></div>
      ${L.length?`<ol class="rlist">${L.map((h,i)=>{const e=cataEv(h.n), live=h.n===cur&&h===H[0];
        return `<li><button data-i="${H.indexOf(h)}" class="${h===sel?'on':''}" style="--c:${e.color}"><i>${e.icon}</i><b>${esc(e.name)}</b>${live?`<span class="now">${T('сейчас','now')}</span>`:''}<span class="pl">${esc(cataPlace(h))}</span><time>${agoText(now-h.t)}</time></button></li>`}).join('')}</ol>`
        :`<p class="mnote">${T('За это время катаклизмов не было.','No cataclysms in this period.')}</p>`}
      <p class="mnote">${D.demo?T('Это демо-журнал: настоящий появится, когда сервер начнёт публиковать meteo.json (config.liveUrl). ','This is a demo log: the real one appears once the server publishes meteo.json (config.liveUrl). '):T('Журнал с сервера, последние 20 катаклизмов. ','Log from the server, the last 20 cataclysms. ')}${T('На карте отмечен квадрат 128×128 блоков, где катаклизм наблюдали (точные координаты игроков не публикуются), а для событий без места — их зона или Монолит.','The map marks the 128×128-block square where the cataclysm was observed (exact player coordinates are not published); events without a place show their zone or the Monolith.')}${off?' '+T(`${off} без метки: прошли по всему миру или на Луне и Марсе.`,`${off} without a marker: they swept the whole world or happened on the Moon and Mars.`):''}</p>`;
  };
  host.onclick=e=>{const p=e.target.closest('[data-p]'); if(p){per=+p.dataset.p;draw();return}
    const i=e.target.closest('[data-i]'); if(i) show(H[+i.dataset.i])};
  draw();
}
// ---- карта Земли (данные: C.map.earth из content/earth.json, единица = 1 км) ----
function renderEarth(C){
  const host=$('#pxearth'); if(!host||!C.map||!C.map.earth){const s=$('#earth');if(s)s.remove();return}
  const E=C.map.earth, M=C.map, NS='http://www.w3.org/2000/svg', [bx0,by0,bx1,by1]=E.box;
  const layers={powers:true,seas:true,grid:true};
  host.innerHTML=`<div class="mtools"><div class="chips" id="eLayers"><button data-l="powers" class="on">${T('Державы','Powers')} (${E.powers.length})</button><button data-l="seas" class="on">${T('Моря','Seas')}</button><button data-l="grid" class="on">${T('Параллели','Graticule')}</button></div>
     <div class="chips">${Object.entries(M.blocs).map(([k,v])=>`<span class="pill eb-${k}">${esc(v)}</span>`).join('')}</div></div>
   <div class="mbox ebox"><svg id="esvg" class="msvg esvg" role="img" aria-label="${T('Карта Земли PaxVanila','PaxVanila map of the Earth')}"></svg>
     ${ZOOMBTNS()}
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
  // на узком экране сразу показываем державы крупно, на широком — всю карту
  const reset=()=>{const xs=pw.map(p=>p.x), zs=pw.map(p=>p.z), m=420;
    if(svg.clientWidth<700) ctl.fit(Math.max(bx0,Math.min(...xs)-m),Math.max(by0,Math.min(...zs)-m),Math.min(bx1,Math.max(...xs)+m),Math.min(by1,Math.max(...zs)+m));
    else ctl.fit(bx0,by0,bx1,by1)};
  const ctl=panZoom({host,svg,info,minW:300,maxW:2*(bx1-bx0),reset,coord:(wx,wy)=>{const lat=48-wy/111.32, lon=25+wx/K; return `${Math.abs(lat).toFixed(1)}° ${lat<0?'S':'N'} · ${Math.abs(lon).toFixed(1)}° ${lon<0?'W':'E'}`}});
  reset();
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
     ${ZOOMBTNS()}
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
    el('circle',{cx:p.x,cy:p.z,r:8,class:'hit'},a); 
    if(p.kind==='fortress') el('rect',{x:p.x-7,y:p.z-7,width:14,height:14,class:'nsd'},a);
    else if(p.kind==='bastion') el('path',{d:`M${p.x-8} ${p.z+7}L${p.x-8} ${p.z-5}L${p.x-4} ${p.z-5}L${p.x-4} ${p.z-8}L${p.x+4} ${p.z-8}L${p.x+4} ${p.z-5}L${p.x+8} ${p.z-5}L${p.x+8} ${p.z+7}Z`,class:'nsd'},a);
    else el('circle',{cx:p.x,cy:p.z,r:4.5,class:'nsd'},a);
    el('text',{x:p.x,y:p.z+(p.kind==='legend'?-8:13),class:'nst'},a).textContent=(p.kind==='legend'?'✦ ':'')+p.name;
    const go=()=>pick(p,k[1],lk(p.id==='crimson_rift'?'pozdnie':'predtechi')); a.onclick=go; a.onkeydown=e=>{if(e.key==='Enter')go()};});
  portals.forEach(p=>{const a=el('g',{class:'np',tabindex:0},g.portals);
    el('circle',{cx:p.x,cy:p.z,r:8,class:'hit'},a); el('rect',{x:p.x-4,y:p.z-6,width:8,height:12,rx:1,class:'npf',stroke:p.color},a);
    el('text',{x:p.x,y:p.z+9,class:'npt'},a).textContent=p.name;
    const go=()=>pick({...p,text:T('Портал державы. Встань в Незере на эти координаты и построй рамку: выйдешь у столицы. ','The power\'s portal. Build a frame at these Nether coordinates and you will come out at the capital. ')+(p.text||'')},T('портал','portal')); a.onclick=go; a.onkeydown=e=>{if(e.key==='Enter')go()};});
  (N.places||[]).forEach(p=>{const a=el('g',{class:'ng',tabindex:0},g.top);
    el('circle',{cx:p.x,cy:p.z,r:10,class:'hit'},a); el('circle',{cx:p.x,cy:p.z,r:10,class:'ngo'},a); el('rect',{x:p.x-4,y:p.z-6,width:8,height:12,class:'ngi'},a);
    el('text',{x:p.x,y:p.z-15,class:'ngt'},a).textContent=p.name;
    const go=()=>pick(p,T('под Монолитом','beneath the Monolith'),lk('predtechi')); a.onclick=go; a.onkeydown=e=>{if(e.key==='Enter')go()};});
  if(N.places&&N.places[0]) pick(N.places[0],T('под Монолитом','beneath the Monolith'),lk('predtechi'));
  $('#nLayers').onclick=e=>{const k=e.target.dataset.l;if(!k)return;layers[k]=!layers[k];e.target.classList.toggle('on',layers[k]);g[k].style.display=layers[k]?'':'none'};
  const markRing=()=>{host.querySelectorAll('#nRings button').forEach(x=>x.classList.toggle('on',x.dataset.r===sel)); for(const k in ringEls) ringEls[k].forEach(e=>e.classList.toggle('sel',k===sel));};
  $('#nRings').onclick=e=>{const k=e.target.dataset.r;if(!k)return;sel=sel===k?null:k;markRing()}; markRing();
  const reset=()=>ctl.fit(-ext,-ext,ext,ext);
  const ctl=panZoom({host,svg,info,minW:30,maxW:6*ext,reset,coord:(x,z)=>`X ${Math.round(x)} · Z ${Math.round(z)}  →  ${T('наверху','above')} ${Math.round(x)*8} · ${Math.round(z)*8}`});
  reset();
}
// ---- «Новости сервера»: летопись по дням (C.chronicle из content/chronicle.json; живые записи: config.liveUrl → chronicle.json из paxchronicle.sk) ----
const MSK=3*3600e3, dayKey=ms=>new Date(ms+MSK).toISOString().slice(0,10);
const fill=(s,v)=>esc(s||'').replace(/\{(\w)\}/g,(m,k)=>k in v?(k==='n'||k==='d'?esc(v[k]):`<b>${esc(v[k])}</b>`):m);
function chronicleItems(C,live,news){
  const X=C.chronicle, cfg=C.config, out=[]; if(!X) return out;
  (X.entries||[]).forEach((e,i)=>out.push({key:e.date,ord:1e6-i,cat:e.cat,icon:e.icon,title:esc(e.title),text:esc(e.text)}));
  const t0=cfg.launchDate?new Date(cfg.launchDate).getTime():NaN;
  if(!isNaN(t0)){
    const now=Date.now(), days=Math.floor((now-t0)/864e5); // индекс сегодняшнего дня (0 = день 1)
    const at=d=>dayKey(t0+d*864e5);
    for(let d=1;d<=days&&d<=41;d++){const r=radiusForDay(cfg.border,d), r0=radiusForDay(cfg.border,d-1); if(r>r0){const L=X.border.lines;
      out.push({key:at(d),ord:d*10+1,cat:'border',icon:'🧭',day:d+1,title:esc(X.border.title),text:fill(L[d%L.length],{n:r,d:r-r0})})}}
    (X.calendar||[]).forEach(c=>{if(c.day-1<=days) out.push({key:at(c.day-1),ord:c.day*10+5,cat:c.cat,icon:c.icon,day:c.day,title:esc(c.title),text:esc(c.text)})});
    for(let d=35;d<=days;d+=7) out.push({key:at(d),ord:d*10+4,cat:'epoch',icon:'🍂',day:d+1,title:esc(X.seasons.title),text:fill(X.seasons.text,{a:SEASONS[Math.floor((d-28)/7)%4]})});
  }
  const live1=(L,map)=>(L&&L.items||[]).forEach(x=>{const t=map(x);if(t) out.push({key:dayKey(x.t*1000),ord:x.t,time:x.t,demo:!!L.demo,...t})});
  live1(live,x=>{const t=X.templates[x.k];if(!t) return null;const v={a:x.a||'',b:x.b||'',n:x.n??'',p:x.p||'',m:String(x.m||'').replace(/^\[[^\]]*\]\s*/,'')};
    return {cat:t.cat,icon:t.icon,title:fill(t.title,v),text:fill(t.text,v)}});
  const W=C.news; live1(news&&!news.demo?news:null,x=>{const t=W&&W.templates[x.k];if(!t) return null;
    return {cat:'find',icon:t.icon,title:esc(t.title),text:esc(t.text).split('{p}').join(`<b>${esc(x.p)}</b>`)}});
  return out.sort((a,b)=>a.key<b.key?1:a.key>b.key?-1:b.ord-a.ord);
}
function dayLabel(C,key){
  const d=new Date(key+'T12:00:00Z'), cfg=C.config;
  const s=d.toLocaleDateString(EN?'en-GB':'ru-RU',{day:'numeric',month:'long',year:'numeric',timeZone:'UTC'});
  const t0=cfg.launchDate?new Date(cfg.launchDate).getTime():NaN; if(isNaN(t0)) return [s,''];
  const n=Math.round((new Date(key+'T00:00:00Z')-new Date(dayKey(t0)+'T00:00:00Z'))/864e5);
  return [s,n>=0?T(`День ${n+1} сервера`,`Server day ${n+1}`):T(`За ${-n} ${plural(-n,'день','дня','дней')} до высадки`,`${-n} day${-n===1?'':'s'} before landfall`)];
}
function plural(n,a,b,c){n=Math.abs(n)%100;const m=n%10;return n>10&&n<20?c:m===1?a:m>=2&&m<=4?b:c}
function chronCard(C,i){const X=C.chronicle;
  return `<article class="card chron c-${esc(i.cat)}"><div class="meta"><span>${i.icon} ${esc(X.categories[i.cat]||'')}</span>${i.time?`<span>${new Date(i.time*1000).toLocaleTimeString(EN?'en-GB':'ru-RU',{hour:'2-digit',minute:'2-digit'})}</span>`:''}${i.demo?'<span class="demo">'+T('ДЕМО','DEMO')+'</span>':''}</div><h3>${i.title}</h3><p>${i.text}</p></article>`}
async function loadChronicle(C){
  const cfg=C.config, demo=/[?&]demo\b/.test(location.search);
  let [lv,ln]=await Promise.all([liveJson(cfg,'chronicle.json'),liveJson(cfg,'news.json')]);
  if(!lv&&demo&&C.chronicleDemo) lv=C.chronicleDemo;
  return chronicleItems(C,lv,ln);
}
async function renderChronicleTeaser(C){
  const host=$('#chronTeaser'); if(!host||!C.chronicle) return;
  const items=await loadChronicle(C), top=items.slice(0,3);
  host.innerHTML=top.map(i=>{const [d,s]=dayLabel(C,i.key);return chronCard(C,i).replace('<div class="meta">',`<div class="meta"><span class="dd">${esc(d)}</span>`)}).join('');
}
async function chronicleMain(){
  const C=await (await fetch('content.json?v=20261120185002')).json(), X=C.chronicle, cfg=C.config, host=$('#chron'); if(!X||!host) return;
  const st=serverState(cfg), items=await loadChronicle(C);
  const bits=[]; if(st.started) bits.push(T(`Сегодня день ${st.day}`,`Today is day ${st.day}`),T(`граница ${st.radius} ${plural(st.radius,'блок','блока','блоков')}`,`border ${st.radius} blocks`)+(st.season?' · '+st.season:''));
  else if(st.until) bits.push(T(`До высадки ${st.until} ${plural(st.until,'день','дня','дней')}`,`Landfall in ${st.until} day${st.until===1?'':'s'}`));
  else bits.push(T('Дата открытия скоро','Launch date coming soon'));
  $('#chronState').innerHTML=bits.map(b=>`<span class="pill">${esc(b)}</span>`).join('');
  // что впереди: ближайшие записи календаря
  const t0=cfg.launchDate?new Date(cfg.launchDate).getTime():NaN, today=st.started?st.day:0;
  const next=(X.calendar||[]).filter(c=>c.day>today).slice(0,3);
  $('#chronNext').innerHTML=isNaN(t0)?'':next.map(c=>{const [d]=dayLabel(C,dayKey(t0+(c.day-1)*864e5));
    return `<div class="stat"><div class="l">${esc(d)} · ${T('день','day')} ${c.day}</div><div class="v nx">${c.icon} ${esc(c.title)}</div></div>`}).join('');
  $('#chronNextWrap').hidden=!next.length||isNaN(t0);
  let cat=''; const cats=Object.entries(X.categories).filter(([k])=>items.some(i=>i.cat===k)), bar=$('#chronCats');
  const draw=()=>{bar.innerHTML=`<button class="${cat?'':'on'}" data-c="">${T('Все','All')}</button>`+cats.map(([k,v])=>`<button class="${cat===k?'on':''}" data-c="${k}">${esc(v)}</button>`).join('');
    const L=items.filter(i=>!cat||i.cat===cat), groups=[]; L.forEach(i=>{const g=groups[groups.length-1];if(g&&g.key===i.key)g.items.push(i);else groups.push({key:i.key,items:[i]})});
    host.innerHTML=groups.map(g=>{const [d,s]=dayLabel(C,g.key);return `<section class="cday" id="d-${g.key}"><header><time datetime="${g.key}">${esc(d)}</time>${s?`<span>${esc(s)}</span>`:''}</header><div class="cdayl">${g.items.map(i=>chronCard(C,i)).join('')}</div></section>`}).join('')||`<p class="sub">${T('Записей пока нет.','No entries yet.')}</p>`};
  bar.onclick=e=>{const c=e.target.closest('button');if(c){cat=c.dataset.c;draw()}};
  draw();
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
else if(document.getElementById('chron')) chronicleMain();
window.PaxCalendar={serverState,radiusForDay};
})();
