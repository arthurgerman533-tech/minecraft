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
  renderMap(C);
  checkStatus(cfg);
}
// ---- карта мира (данные: C.map из content/map.json и content/map_towns.json) ----
function renderMap(C){
  const host=$('#pxmap'); if(!host||!C.map) return;
  const M=C.map, cfg=C.config, b=cfg.border, st=serverState(cfg);
  const rings=[['start',T('Старт','Start')],['w1',T('Н1','W1')],['w2',T('Н2','W2')],['w3',T('Н3','W3')],['w5',T('Н5','W5')],['w6',T('Н6','W6')]];
  const R=b.w6, ext=R*1.12, NS='http://www.w3.org/2000/svg';
  const layers={powers:true,ancient:true,towns:true,grid:true,far:true,lore:true}; M.far=M.far||[]; M.lore=M.lore||[];
  let sel=st.started?null:'w6';
  host.innerHTML=`<div class="mtools">
     <div class="chips" id="mLayers">
       <button data-l="powers" class="on">${T('Державы','Powers')}</button><button data-l="ancient" class="on">${T('Древние места','Ancient sites')}</button>
       <button data-l="towns" class="on">${T('Города','Towns')}${M.towns.length?' ('+M.towns.length+')':''}</button><button data-l="grid" class="on">${T('Сетка','Grid')}</button>${M.lore.length?`<button data-l="lore" class="on">${T('Метки лора','Lore tags')} (${M.lore.length})</button>`:''}${M.far.length?`<button data-l="far" class="on">${T('Дальний сектор','Far Sector')}</button>`:''}</div>
     <div class="chips" id="mRings"><span class="lbl">${T('Граница','Border')}</span>${rings.map(r=>`<button data-r="${r[0]}">${r[1]}</button>`).join('')}</div>
   </div>
   <div class="mbox"><svg id="msvg" role="img" aria-label="${T('Карта мира PaxVanila','PaxVanila world map')}"></svg>
     <div class="mzoom"><button data-z="0.67" aria-label="${T('Приблизить','Zoom in')}">+</button><button data-z="1.5" aria-label="${T('Отдалить','Zoom out')}">−</button><button data-z="0" aria-label="${T('Сбросить','Reset')}">⟲</button></div>
     <div class="mcoord" id="mcoord">X 0 · Z 0</div><div class="mcomp">${T('С','N')}↑</div></div>
   <div class="minfo" id="minfo"></div>
   <p class="mnote">${T('Державы и древние места показаны схемой по лору: настоящие столицы строят игроки.','Powers and ancient sites are a schematic based on the lore: the real capitals are built by players.')}
     ${M.towns.length?T(' Города Towny выгружены ',' Towny towns exported ')+esc(M.townsDate)+'.':T(' Реальные города появятся после открытия сервера.',' Real towns will appear after the server opens.')}
     ${cfg.mapUrl?` <a class="btn" href="${esc(cfg.mapUrl)}" target="_blank" rel="noopener">🗺️ ${T('Живая карта BlueMap','Live BlueMap')}</a>`:''}</p>`;
  const svg=$('#msvg'), el=(n,a,p)=>{const e=document.createElementNS(NS,n);for(const k in a)e.setAttribute(k,a[k]);(p||svg).appendChild(e);return e};
  const cp=el('clipPath',{id:'mclip'},el('defs',{})); el('circle',{cx:0,cy:0,r:R},cp);
  const g={}; ['base','grid','powers','rings','ancient','towns','lore','far','top'].forEach(k=>g[k]=el('g',{class:'g-'+k}));
  el('circle',{cx:0,cy:0,r:R,class:'land'},g.base); g.grid.setAttribute('clip-path','url(#mclip)');
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
  const LC={legend:['✦',T('легенда','legend')],cataclysm:['⚡',T('катаклизм','cataclysm')],battle:['⚔',T('битва','battle')],front:['☠',T('Хроника фронта','Front Chronicle')]};
  M.lore.forEach(p=>{const c=LC[p.cat]||['•',''], a=el('g',{class:'lt c-'+p.cat,tabindex:0},g.lore);
    el('circle',{cx:p.x,cy:p.z,r:9,class:'ld'},a); const tx=el('text',{x:p.x,y:p.z-14,class:'ltx'},a); tx.textContent=c[0]+' '+p.name;
    const go=()=>pick({...p,lore:p.cat==='front'?'front':''},c[1]); a.onclick=go; a.onkeydown=e=>{if(e.key==='Enter')go()};});
  M.far.forEach(p=>{const a=el('g',{class:'far',tabindex:0},g.far), d=Math.hypot(p.x,p.z)||1, ex=p.x/d*R, ez=p.z/d*R;
    el('line',{x1:ex,y1:ez,x2:p.x,y2:p.z,class:'fl'},a);
    el('text',{x:ex+(p.x-ex)*0.12,y:ez+(p.z-ez)*0.12-14,class:'fh'},a).textContent=T('за границей → ','beyond the border → ')+Math.round(d)+T(' бл.',' bl.');
    el('circle',{cx:p.x,cy:p.z,r:160,class:'fa'},a);
    el('path',{d:`M${p.x-60} ${p.z-60}L${p.x+60} ${p.z+60}M${p.x+60} ${p.z-60}L${p.x-60} ${p.z+60}`,class:'fx'},a);
    el('text',{x:p.x,y:p.z+200,class:'ft'},a).textContent=p.name;
    const go=()=>{pick(p,T('за границей мира','beyond the border'));const ar=svg.clientHeight/Math.max(1,svg.clientWidth)||1, nw=Math.max(vb.w,(d+900)/Math.min(1,1/ar));vb={x:p.x/2-nw/2,y:p.z/2-nw*ar/2,w:nw,h:nw*ar};apply()};
    a.onclick=go; a.onkeydown=e=>{if(e.key==='Enter')go()};
    if(p.lore) info.dataset.far=p.lore;});
  M.places.forEach(p=>{const a=el('g',{class:'mono',tabindex:0},g.top);
    el('rect',{x:p.x-18,y:p.z-18,width:36,height:36,class:'md'},a); el('text',{x:p.x,y:p.z-34,class:'mt'},a).textContent=p.name;
    a.onclick=()=>pick(p,T('центр мира','world centre'));});
  pick(M.places[0],T('центр мира','world centre'));
  // слои и кольца
  $('#mLayers').onclick=e=>{const k=e.target.dataset.l;if(!k)return;layers[k]=!layers[k];e.target.classList.toggle('on',layers[k]);g[k].style.display=layers[k]?'':'none'};
  const markRing=()=>{document.querySelectorAll('#mRings button').forEach(x=>x.classList.toggle('on',x.dataset.r===sel));
    for(const k in ringEls) ringEls[k].forEach(e=>e.classList.toggle('sel',k===sel));};
  $('#mRings').onclick=e=>{const k=e.target.dataset.r;if(!k)return;sel=sel===k?null:k;markRing()}; markRing();
  // приближение и перетаскивание (viewBox в блоках)
  let vb={x:-ext,y:-ext,w:2*ext,h:2*ext};
  const apply=()=>{const ar=svg.clientHeight/Math.max(1,svg.clientWidth)||1; vb.h=vb.w*ar;
    svg.setAttribute('viewBox',`${vb.x} ${vb.y} ${vb.w} ${vb.h}`); svg.style.setProperty('--k',vb.w/Math.max(1,svg.clientWidth));};
  const reset=()=>{const ar=svg.clientHeight/Math.max(1,svg.clientWidth)||1, s=2*ext; vb=ar>1?{x:-ext,y:-ext*ar,w:s,h:s*ar}:{x:-ext/ar,y:-ext,w:s/ar,h:s};apply()};
  const toWorld=(cx,cy)=>{const r=svg.getBoundingClientRect();return [vb.x+(cx-r.left)/r.width*vb.w, vb.y+(cy-r.top)/r.height*vb.h]};
  const zoom=(f,cx,cy)=>{const nw=Math.min(6*ext,Math.max(120,vb.w*f)); f=nw/vb.w; const [wx,wy]=toWorld(cx,cy);
    vb.x=wx-(wx-vb.x)*f; vb.y=wy-(wy-vb.y)*f; vb.w=nw; apply()};
  host.querySelector('.mzoom').onclick=e=>{const z=+e.target.dataset.z; if(isNaN(z))return; if(!z)return reset();
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
