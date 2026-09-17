from pathlib import Path

p = Path('index.html')
if not p.exists():
    raise SystemExit('index.html missing')

s = p.read_text(encoding='utf-8')

old = "function renderGrid(){if(!state.cards.size){grid.innerHTML='';state.games.forEach(g=>{const c=cardFor(g);state.cards.set(gameKey(g),c);grid.append(c)})}applyFilters()}"
new = "function renderGrid(){const frag=document.createDocumentFragment();state.games.forEach(g=>{const k=gameKey(g);if(!state.cards.has(k))state.cards.set(k,cardFor(g));frag.appendChild(state.cards.get(k))});grid.append(frag);applyFilters()}"
if old not in s:
    raise SystemExit('renderGrid target not found')
s = s.replace(old, new, 1)

old = "img.loading=mini?'lazy':'eager'"
if old not in s:
    raise SystemExit('image loading target not found')
s = s.replace(old, "img.loading='lazy'", 1)

old = "function applyFilters(){const q=normalize(state.query);let visible=0;state.games.forEach(g=>{const c=state.cards.get(gameKey(g));if(!c)return;const ok=matches(g)&&(!q||normalize(g.title).includes(q));c.style.display=ok?'':'none';if(ok)visible++;decorate(c,g)});status.textContent=`${visible} of ${state.games.length} games shown`;renderCategories()}"
new = "function applyFilters(){const q=normalize(state.query);let visible=0;state.games.forEach(g=>{const c=state.cards.get(gameKey(g));if(!c)return;const ok=matches(g)&&(!q||normalize(g.title).includes(q));c.style.display=ok?'':'none';if(ok)visible++});status.textContent=`${visible} of ${state.games.length} games shown`}"
if old not in s:
    raise SystemExit('applyFilters target not found')
s = s.replace(old, new, 1)

marker = '</body>'
if 'id="ubg43-final-runtime"' not in s:
    runtime = r'''<style id="ubg43-final-runtime-style">
.ubg43-badges{position:absolute;left:9px;top:9px;z-index:20;display:flex;flex-direction:column;gap:5px;pointer-events:none}
.ubg43-badge{display:inline-flex;align-items:center;height:22px;padding:0 9px;border-radius:6px 8px 8px 6px;font:900 9px/1 Arial,sans-serif;letter-spacing:.06em;box-shadow:0 4px 10px rgba(0,0,0,.22);white-space:nowrap}
.ubg43-badge.new{background:#e52424;color:#ffe600}.ubg43-badge.trending{background:#ffe600;color:#c31d1d}
.ubg43-searching .hero{display:none}.ubg43-searching #searchPage{display:block!important}.ubg43-searching .game-grid{padding-top:6px}
@media(max-width:640px){.ubg43-badge{height:20px;padding:0 7px;font-size:8px}}
</style>
<script id="ubg43-final-runtime">
(()=>{
'use strict';
const $=id=>document.getElementById(id);
const grid=$('gameGrid'),search=$('searchBar'),clear=$('searchClear'),results=$('searchResults'),searchPage=$('searchPage'),searchPageText=$('searchPageText'),recSection=$('recommendSection'),trendRail=$('trendingRail'),newRail=$('newRail'),recRail=$('recommendRail');
const REPORT_URL='https://forms.gle/zXYtnxwHgvXmBrq9';
const ZONES_URL='https://raw.githubusercontent.com/gn-math/assets/main/zones.json';
const HTML_ROOT='https://raw.githubusercontent.com/gn-math/html/main';
const COVER_ROOT='https://raw.githubusercontent.com/gn-math/covers/main';
const norm=s=>String(s||'').toLowerCase().replace(/[^a-z0-9]+/g,' ').trim();
const titleOf=c=>(c?.querySelector('h3')?.textContent||'').trim();
const urlOf=c=>{const d=c?.dataset?.url;if(d)return d;const a=c?.getAttribute('onclick')||'';const m=a.match(/openGame\(\s*[\'\"]([^\'\"]+)/i);if(m)return m[1];const href=c?.querySelector('a[href]')?.href;return href||''};
const imageOf=c=>c?.querySelector('img')?.getAttribute('src')||'';
const keyOf=c=>norm(titleOf(c))+'|'+urlOf(c).replace(/#.*$/,'');
const read=(k,f)=>{try{return JSON.parse(localStorage.getItem(k)||JSON.stringify(f))||f}catch(_){return f}};
const write=(k,v)=>{try{localStorage.setItem(k,JSON.stringify(v))}catch(_) {}};
const playKey=c=>norm(titleOf(c))+'|'+imageOf(c);
const recordPlay=c=>{const h=read('ubg43_final_plays',{}),k=playKey(c),x=h[k]||{title:titleOf(c),plays:0,last:0};x.plays++;x.last=Date.now();h[k]=x;write('ubg43_final_plays',h)};
const recordSearch=q=>{const n=norm(q);if(n.length<2)return;const h=read('ubg43_final_searches',{}),x=h[n]||{count:0,last:0};x.count++;x.last=Date.now();h[n]=x;write('ubg43_final_searches',h)};
const openGame=url=>{const u=String(url||'').trim();if(!u)return;try{const w=window.open(u,'_blank','noopener,noreferrer');if(!w)window.location.href=u}catch(_){window.location.href=u}};window.openGame=openGame;
function addBadge(c,text,cls){const box=c.querySelector('.ubg43-badges')||(()=>{const x=document.createElement('div');x.className='ubg43-badges';c.append(x);return x})();const b=document.createElement('span');b.className='ubg43-badge '+cls;b.textContent=text;box.append(b)}
function decorate(){if(!grid)return;const cards=[...grid.querySelectorAll('.game-card')];cards.forEach(c=>{c.querySelector('.ubg43-badges')?.remove();const fresh=!!(c.dataset.new==='1'||c.dataset.newSince||(c.dataset.date&&Date.now()-Date.parse(c.dataset.date)<45*86400000));const plays=read('ubg43_final_plays',{})[playKey(c)]?.plays||0;const tr=c.dataset.trendingSeed==='1'||c.dataset.seed==='1'||plays>0||c.dataset.trending==='1';if(fresh)addBadge(c,'NEW','new');if(tr)addBadge(c,'TRENDING','trending')});if(!grid.querySelector('.ubg43-badge.trending'))cards.slice(0,Math.min(10,cards.length)).forEach(c=>{if(!c.querySelector('.ubg43-badge.trending'))addBadge(c,'TRENDING','trending')})}
function decorateCard(c,src){const fresh=!!(src.dataset.new==='1'||src.dataset.newSince||(src.dataset.date&&Date.now()-Date.parse(src.dataset.date)<45*86400000));const tr=src.dataset.trending==='1'||src.dataset.trendingSeed==='1'||src.dataset.seed==='1'||read('ubg43_final_plays',{})[playKey(src)]?.plays>0;if(fresh)addBadge(c,'NEW','new');if(tr)addBadge(c,'TRENDING','trending')}
function wireCard(c){if(!c)return;c.tabIndex=0;if(!c.dataset.url)c.dataset.url=urlOf(c)}
function allGridCards(){return grid?[...grid.querySelectorAll('.game-card')]:[]}
async function importLegacy(){if(!grid)return;try{const r=await fetch('legacy-index.html',{cache:'no-store'});if(!r.ok)return;const doc=new DOMParser().parseFromString(await r.text(),'text/html'),have=new Set(allGridCards().map(keyOf)),frag=document.createDocumentFragment();doc.querySelectorAll('.game-card').forEach(src=>{const t=titleOf(src),u=urlOf(src);if(!t||!/^https?:\/\//i.test(u))return;const clone=src.cloneNode(true);clone.querySelector('.ubg43-badges')?.remove();clone.dataset.url=u;wireCard(clone);const k=keyOf(clone);if(have.has(k))return;have.add(k);frag.append(clone)});grid.append(frag)}catch(_) {}}
async function importZones(){if(!grid||allGridCards().length>=900)return;try{const r=await fetch(ZONES_URL,{cache:'no-store'});if(!r.ok)return;const zones=await r.json(),have=new Set(allGridCards().map(keyOf)),frag=document.createDocumentFragment();let added=0;for(const z of zones){if(added>=700)break;const u=String(z.url||'').replace('{HTML_URL}',HTML_ROOT),im=String(z.cover||'').replace('{COVER_URL}',COVER_ROOT),t=String(z.name||'').trim();if(!t||!/^https?:\/\//i.test(u)||!im)continue;const c=document.createElement('article');c.className='game-card';c.dataset.url=u;c.dataset.new=z.new?'1':'0';c.dataset.seed='0';c.dataset.category='';const img=document.createElement('img');img.loading='lazy';img.src=im;img.alt=t;img.referrerPolicy='no-referrer';const h=document.createElement('h3');h.textContent=t;c.append(img,h);const k=keyOf(c);if(have.has(k))continue;have.add(k);wireCard(c);frag.append(c);added++}grid.append(frag)}catch(_) {}}
function similarity(a,b){const A=new Set(norm(a).split(' ').filter(x=>x.length>1)),B=new Set(norm(b).split(' ').filter(x=>x.length>1));if(!A.size||!B.size)return 0;let n=0;A.forEach(x=>B.has(x)&&n++);return n/Math.sqrt(A.size*B.size)}
function fillRail(rail,cards){if(!rail)return;rail.innerHTML='';const used=new Set();cards.forEach(src=>{const k=keyOf(src);if(used.has(k))return;used.add(k);const c=src.cloneNode(true);c.querySelector('.ubg43-badges')?.remove();c.dataset.url=urlOf(src);wireCard(c);rail.append(c);decorateCard(c,src)});if(cards.length){const done=document.createElement('div');done.className='done';done.innerHTML='<span>That’s all for now ✨<small>More games are added automatically.</small></span>';rail.append(done)}}
function renderRails(){const cards=allGridCards(),scores=read('ubg43_final_plays',{});const trending=cards.slice().sort((a,b)=>((scores[playKey(b)]?.plays||0)-(scores[playKey(a)]?.plays||0))||Number(b.dataset.trendingSeed==='1')-Number(a.dataset.trendingSeed==='1')||titleOf(a).localeCompare(titleOf(b))).slice(0,24);const fresh=cards.filter(c=>c.dataset.new==='1'||c.dataset.newSince).slice(0,24);fillRail(trendRail,trending);fillRail(newRail,fresh.length?fresh:cards.slice(0,24))}
function rebuildRecommendations(q){if(!recSection||!recRail)return;const cards=allGridCards(),ph=read('ubg43_final_plays',{}),sh=read('ubg43_final_searches',{});const out=cards.filter(c=>!norm(titleOf(c)).includes(norm(q))).map(c=>{let s=similarity(titleOf(c),q)*.7;s+=(ph[playKey(c)]?.plays||0)*.08;Object.entries(sh).forEach(([k,v])=>s+=similarity(titleOf(c),k)*Math.min(5,v.count||0)*.05);if(c.dataset.new==='1')s+=.1;return {c,s}}).sort((a,b)=>b.s-a.s||titleOf(a.c).localeCompare(titleOf(b.c))).slice(0,24).map(x=>x.c);fillRail(recRail,out);recSection.classList.remove('hidden')}
function statusLike(){const s=$('status');if(!s)return null;const visible=allGridCards().filter(c=>c.style.display!=='none').length;s.textContent=`${visible} matching games`;return s}
function clearSearch(){document.body.classList.remove('ubg43-searching');if(search)search.value='';if(clear)clear.style.display='none';results?.classList.remove('open');searchPage?.classList.add('hidden');recSection?.classList.add('hidden');allGridCards().forEach(c=>c.style.display='');statusLike();window.scrollTo({top:0,behavior:'smooth'})}
function setSearchMode(q){q=q.trim();if(!q){clearSearch();return}document.body.classList.add('ubg43-searching');searchPage?.classList.remove('hidden');if(searchPageText)searchPageText.textContent=`Showing matching games for “${q}”. Trending Now and New Games remain available below.`;const n=norm(q);allGridCards().forEach(c=>c.style.display=norm(titleOf(c)).includes(n)?'':'none');rebuildRecommendations(q);recordSearch(q);statusLike();searchPage?.scrollIntoView({behavior:'smooth',block:'start'})}
function showSuggestions(q){if(!results)return;results.innerHTML='';const n=norm(q);if(!n){results.classList.remove('open');return}const hits=allGridCards().filter(c=>norm(titleOf(c)).includes(n)).slice(0,7);if(!hits.length){const d=document.createElement('div');d.className='search-empty';d.textContent='No matching games yet';results.append(d);results.classList.add('open');return}hits.forEach(c=>{const b=document.createElement('button');b.type='button';b.className='search-result';b.innerHTML='<img alt=""><span class="search-copy"><span class="search-title"></span><span class="search-label">Play game</span></span>';b.querySelector('img').src=imageOf(c);b.querySelector('img').alt=titleOf(c);b.querySelector('.search-title').textContent=titleOf(c);b.addEventListener('click',e=>{e.preventDefault();e.stopImmediatePropagation();search.value=titleOf(c);setSearchMode(titleOf(c));results.classList.remove('open')},{capture:true});results.append(b)});results.classList.add('open')}
function openCategories(){const side=$('categorySidebar'),ov=$('categoryOverlay');if(!side)return;side.classList.add('open');ov?.classList.add('open');side.setAttribute('aria-hidden','false');document.body.classList.add('locked');const list=$('categoryList');if(!list)return;list.innerHTML='';const counts={};allGridCards().forEach(c=>{const cat=c.dataset.category||'Casual';counts[cat]=(counts[cat]||0)+1});['All Games','New Games','Trending','Action','Adventure','Horror','Multiplayer','Fighting','Survival','Platformer','Racing','Sports','Puzzle','Arcade','Strategy','Simulation','Casual','Anime','Rhythm & Music','Card & Board','io'].forEach(cat=>{const b=document.createElement('button');b.type='button';b.className='category';const n=cat==='All Games'?allGridCards().length:cat==='New Games'?allGridCards().filter(c=>c.dataset.new==='1'||c.dataset.newSince).length:cat==='Trending'?allGridCards().filter(c=>c.querySelector('.ubg43-badge.trending')).length:(counts[cat]||0);b.innerHTML='<span class="category-main"><span class="dot"></span><span class="category-name"></span></span><span class="category-count"></span>';b.querySelector('.category-name').textContent=cat;b.querySelector('.category-count').textContent=n;b.addEventListener('click',e=>{e.preventDefault();e.stopImmediatePropagation();allGridCards().forEach(c=>{const ok=cat==='All Games'||(cat==='New Games'?(c.dataset.new==='1'||c.dataset.newSince):cat==='Trending'?!!c.querySelector('.ubg43-badge.trending'):(c.dataset.category||'Casual')===cat);c.style.display=ok?'':'none'});side.classList.remove('open');ov?.classList.remove('open');document.body.classList.remove('locked')},{capture:true});list.append(b)})}
function closeCategories(){$('categorySidebar')?.classList.remove('open');$('categoryOverlay')?.classList.remove('open');$('categorySidebar')?.setAttribute('aria-hidden','true');document.body.classList.remove('locked')}
function bind(){
 search?.addEventListener('input',e=>{e.stopImmediatePropagation();const q=search.value.trim();if(clear)clear.style.display=q?'inline-flex':'none';showSuggestions(q);if(!q){clearSearch();return}statusLike()},{capture:true});
 search?.addEventListener('keydown',e=>{e.stopImmediatePropagation();if(e.key==='Enter'){e.preventDefault();const q=search.value.trim();results?.classList.remove('open');setSearchMode(q);search.blur()}else if(e.key==='Escape'){e.preventDefault();clearSearch()}},{capture:true});
 clear?.addEventListener('click',e=>{e.preventDefault();e.stopImmediatePropagation();clearSearch()},{capture:true});
 $('randomGameButton')?.addEventListener('click',e=>{e.preventDefault();e.stopImmediatePropagation();const pool=allGridCards().filter(c=>c.style.display!=='none');const list=pool.length?pool:allGridCards();const c=list[Math.floor(Math.random()*list.length)];if(c){recordPlay(c);openGame(urlOf(c))}},{capture:true});
 $('reportGameButton')?.addEventListener('click',e=>{e.preventDefault();e.stopImmediatePropagation();window.location.href=REPORT_URL},{capture:true});
 $('categoryToggle')?.addEventListener('click',e=>{e.preventDefault();e.stopImmediatePropagation();openCategories()},{capture:true});
 $('categoryClose')?.addEventListener('click',e=>{e.preventDefault();e.stopImmediatePropagation();closeCategories()},{capture:true});
 $('categoryOverlay')?.addEventListener('click',e=>{e.preventDefault();e.stopImmediatePropagation();closeCategories()},{capture:true});
 [['trendPrev','trendingRail'],['trendNext','trendingRail'],['newPrev','newRail'],['newNext','newRail'],['recPrev','recommendRail'],['recNext','recommendRail']].forEach(([id,rid])=>$(id)?.addEventListener('click',e=>{e.preventDefault();e.stopImmediatePropagation();const r=$(rid);if(r)r.scrollBy({left:Math.max(300,r.clientWidth*.8)*(id.includes('Prev')?-1:1),behavior:'smooth'})},{capture:true}));
 document.addEventListener('click',e=>{const c=e.target.closest?.('.game-card');if(!c)return;e.preventDefault();e.stopImmediatePropagation();recordPlay(c);openGame(urlOf(c));renderRails();decorate()},{capture:true});
 document.addEventListener('keydown',e=>{if(e.key==='Escape'){if($('categorySidebar')?.classList.contains('open'))closeCategories();else if(document.body.classList.contains('ubg43-searching'))clearSearch()}},{capture:true});
}
async function start(){if(!grid)return;allGridCards().forEach(wireCard);decorate();await importLegacy();allGridCards().forEach(wireCard);decorate();if(allGridCards().length<900)await importZones();allGridCards().forEach(wireCard);decorate();renderRails();bind();const count=allGridCards().length;const s=$('status');if(s)s.textContent=`${count} games ready`}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});else start();
})();
</script>'''
    s = s.replace(marker, runtime + '\n' + marker, 1)

p.write_text(s, encoding='utf-8')
print('STABLE RUNTIME HOTFIX: resilient controls, fallback library loading, carousels, and NEW/TRENDING badges applied')
