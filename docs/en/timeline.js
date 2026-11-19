// PaxVanila — «Хроника держав» (timeline.html). Данные: <script id="tldata"> (собирает tools/build_site.py из content/timeline.json).
(function(){
const D = JSON.parse(document.getElementById('tldata').textContent);
const U = D.ui, $ = s => document.querySelector(s);
const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const TAGC = {absent:'transparent', roots:'#8a7a5c', sovereign:'#b0362b', vassal:'#b5652f', free:'#6f8f55', colony:'#3aa6a0',
  pact:'#c9a227', pax:'#d4a52a', steppe:'#9b3b3b', allied_r:'#c4574a', against_r:'#5a64a8', protect:'#2bb3a3',
  corp:'#d63fa0', outside:'#8b8b8b', newpax:'#e3cf8f'};
const N = D.nations, E = D.eras, byId = Object.fromEntries(N.map(n => [n.id, n]));
const yrs = e => e.from === e.to ? e.from : `${e.from} — ${e.to}`;
let cur = Math.max(0, E.findIndex(e => '#' + e.id === location.hash));
if (!location.hash) cur = 1;

const dot = t => `<i class="tl-dot${t === 'absent' ? ' tl-hollow' : ''}" style="--c:${TAGC[t] || '#888'}"></i>`;
const chip = t => `<span class="tl-tag">${dot(t)}${esc(D.tags[t] || t)}</span>`;
const crest = n => `<span class="tl-crest" style="--n:${n.color}">${esc(n.name.slice(0, 1))}</span>`;

// полоса эпох
const rail = $('#tlRail');
rail.innerHTML = E.map((e, i) => `<button type="button" data-i="${i}"><b>${esc(e.name)}</b><small>${esc(yrs(e))}</small></button>`).join('');
rail.onclick = ev => { const b = ev.target.closest('button'); if (b) go(+b.dataset.i, true); };
$('#tlPrev').onclick = () => go(cur - 1, true);
$('#tlNext').onclick = () => go(cur + 1, true);
const range = $('#tlRange');
range.max = E.length - 1;
range.oninput = () => go(+range.value, false);
document.addEventListener('keydown', ev => {
  if (ev.target.closest('input,textarea')) return;
  if (ev.key === 'ArrowLeft') go(cur - 1, true);
  if (ev.key === 'ArrowRight') go(cur + 1, true);
});

// таблица всех эпох
const tbl = $('#tlMatrix');
tbl.innerHTML = '<thead><tr><th></th>' + E.map((e, i) => `<th data-i="${i}"><b>${esc(e.name)}</b><small>${esc(yrs(e))}</small></th>`).join('') + '</tr></thead><tbody>' +
  N.map(n => `<tr><th><div>${crest(n)}<span>${esc(n.name)}</span></div></th>` + E.map((e, i) => {
    const c = D.cells[n.id][e.id];
    return `<td data-i="${i}" class="${c.tag === 'absent' ? 'tl-none' : ''}" style="--n:${n.color}" title="${esc(c.name + ' · ' + (D.tags[c.tag] || ''))}">` +
      `<span>${esc(c.name)}</span>${dot(c.tag)}</td>`;
  }).join('') + '</tr>').join('') + '</tbody>';
tbl.onclick = ev => { const c = ev.target.closest('[data-i]'); if (c) { go(+c.dataset.i, true); $('#tlEra').scrollIntoView({behavior: 'smooth', block: 'start'}); } };

function go(i, push){
  if (i < 0 || i >= E.length) return;
  cur = i; range.value = i;
  const e = E[i], prev = E[i - 1];
  if (push) history.replaceState(null, '', '#' + e.id);
  rail.querySelectorAll('button').forEach((b, k) => b.classList.toggle('on', k === i));
  const onBtn = rail.children[i];
  if (onBtn) rail.scrollTo({left: onBtn.offsetLeft - rail.clientWidth / 2 + onBtn.clientWidth / 2, behavior: 'smooth'});
  $('#tlPrev').disabled = i === 0; $('#tlNext').disabled = i === E.length - 1;
  $('#tlPos').textContent = `${i + 1} / ${E.length}`;

  // карточка эпохи
  $('#tlEraHead').innerHTML = `<div class="kicker">${esc(U.era)} ${i + 1} · ${esc(yrs(e))}</div><h2>${esc(e.name)}</h2>` +
    `<p class="tl-motto">${esc(e.motto)}</p><p>${esc(e.text)}</p>` +
    `<p class="tl-server"><span>${esc(U.server)}:</span> ${esc(e.server)}</p>`;
  $('#tlEvents').innerHTML = `<h3>${esc(U.events)}</h3><ol>` + e.events.map(v =>
    `<li><b>${esc(v.y)}</b><span>${esc(v.text)}${v.n.length ? '<em>' + v.n.map(id => `<i class="tl-mini" style="--n:${byId[id].color}" title="${esc(byId[id].name)}"></i>`).join('') + '</em>' : ''}</span></li>`).join('') + '</ol>';

  // расклад сил
  const cnt = {};
  N.forEach(n => { const t = D.cells[n.id][e.id].tag; cnt[t] = (cnt[t] || 0) + 1; });
  const order = Object.keys(cnt).sort((a, b) => (a === 'absent') - (b === 'absent') || cnt[b] - cnt[a]);
  $('#tlBlocs').innerHTML = `<h3>${esc(U.blocs)}</h3><div class="tl-bar">` +
    order.map(t => `<span class="${t === 'absent' ? 'tl-hollow' : ''}" style="flex:${cnt[t]};--c:${TAGC[t]}" title="${esc(D.tags[t])}: ${cnt[t]}"></span>`).join('') +
    '</div><div class="tl-legend">' + order.map(t => `<span>${dot(t)}${esc(D.tags[t])} <b>${cnt[t]}</b></span>`).join('') + '</div>';

  // державы
  $('#tlWorldH').textContent = U.world + ': ' + e.name;
  $('#tlGrid').innerHTML = N.map(n => {
    const c = D.cells[n.id][e.id], p = prev && D.cells[n.id][prev.id];
    const was = p && p.name !== c.name && p.tag !== 'absent' ? `<div class="tl-was">${esc(U.was)}: ${esc(p.name)}</div>` : '';
    return `<article class="card tl-n${c.tag === 'absent' ? ' tl-off' : ''}" style="--n:${n.color}">` +
      `<header>${crest(n)}<div><div class="tl-short">${esc(n.name)} <small>· ${esc(U.proto)}: ${esc(n.proto)}</small></div>` +
      `<h3>${esc(c.name)}${c.added ? '<sup title="' + esc(U.added) + '">*</sup>' : ''}</h3></div></header>` +
      was + `<div class="tl-form">${esc(c.form)}</div>${chip(c.tag)}<p>${esc(c.text)}</p></article>`;
  }).join('');
  $('#tlNote').hidden = !N.some(n => D.cells[n.id][e.id].added);

  tbl.querySelectorAll('[data-i]').forEach(c => c.classList.toggle('tl-cur', +c.dataset.i === i));
}
go(cur, false);
window.addEventListener('hashchange', () => { const k = E.findIndex(e => '#' + e.id === location.hash); if (k >= 0 && k !== cur) go(k, false); });
})();
