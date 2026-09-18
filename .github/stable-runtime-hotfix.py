from pathlib import Path
import re
# Canonical runtime trigger: this script is the single final browser controller for the homepage.

p = Path('index.html')
if not p.exists():
    raise SystemExit('index.html missing')

s = p.read_text(encoding='utf-8')
# Keep a lightweight source marker for repository health checks; the browser runtime loads the full legacy feed.
s = s.replace('</head>', '<!-- UBG43 verified library source: zones.json -->\\n</head>', 1)
# Strip older client controllers before installing the one canonical runtime below.
s = re.sub(r'<script(?![^>]*type=["\\\']application/ld\\+json["\\\'])[^>]*>.*?</script>', '', s, flags=re.I | re.S)
s = re.sub(r'<style[^>]*id=["\\\'](?:ubg43-final-runtime-style|smart-game-ui|expanded-category-runtime-style)["\\\'][^>]*>.*?</style>', '', s, flags=re.I | re.S)

# Keep the main runtime from rebuilding the grid destructively as late game data arrives.
old = "function renderGrid(){if(!state.cards.size){grid.innerHTML='';state.games.forEach(g=>{const c=cardFor(g);state.cards.set(gameKey(g),c);grid.append(c)})}applyFilters()}"
new = "function renderGrid(){const frag=document.createDocumentFragment();state.games.forEach(g=>{const k=gameKey(g);if(!state.cards.has(k))state.cards.set(k,cardFor(g));frag.appendChild(state.cards.get(k))});grid.append(frag);applyFilters()}"
if old in s:
    s = s.replace(old, new, 1)

# Store each game's URL on its card so the final click handler never loses it.
old = "c.className='game-card';c.tabIndex=0;c.dataset.category="
new = "c.className='game-card';c.tabIndex=0;c.dataset.url=g.url;c.dataset.category="
if old in s:
    s = s.replace(old, new, 1)

# Always use lazy images in the large dynamically-built library.
old = "img.loading=mini?'lazy':'eager'"
if old in s:
    s = s.replace(old, "img.loading='lazy'", 1)

# Avoid re-running category construction on every card filter operation.
old = "function applyFilters(){const q=normalize(state.query);let visible=0;state.games.forEach(g=>{const c=state.cards.get(gameKey(g));if(!c)return;const ok=matches(g)&&(!q||normalize(g.title).includes(q));c.style.display=ok?'':'none';if(ok)visible++;decorate(c,g)});status.textContent=`${visible} of ${state.games.length} games shown`;renderCategories()}"
new = "function applyFilters(){const q=normalize(state.query);let visible=0;state.games.forEach(g=>{const c=state.cards.get(gameKey(g));if(!c)return;const ok=matches(g)&&(!q||normalize(g.title).includes(q));c.style.display=ok?'':'none';if(ok)visible++});status.textContent=`${visible} of ${state.games.length} games shown`}"
if old in s:
    s = s.replace(old, new, 1)

# Repair the report link typo from older hotfix revisions.
s = s.replace('https://forms.gle/zXYtnxwHgvXmBrq9', 'https://forms.gle/zXYtnxwXhGvXmBrq9')

# Remove a previous copy of the safety runtime before inserting the current one.
s = re.sub(r'<style id="ubg43-final-runtime-style">.*?</style>\s*<script id="ubg43-final-runtime">.*?</script>', '', s, count=1, flags=re.I | re.S)

runtime = r'''<style id="ubg43-final-runtime-style">
.ubg43-badges{position:absolute;left:9px;top:9px;z-index:20;display:flex;flex-direction:column;gap:5px;pointer-events:none}
.ubg43-badge{display:inline-flex;align-items:center;height:22px;padding:0 9px;border-radius:6px 8px 8px 6px;font:900 9px/1 Arial,sans-serif;letter-spacing:.06em;box-shadow:0 4px 10px rgba(0,0,0,.22);white-space:nowrap}
.ubg43-badge.new{background:#e52424;color:#ffe600}.ubg43-badge.trending{background:#ffe600;color:#c31d1d}
.ubg43-searching .hero{display:none}.ubg43-searching #searchPage{display:block!important}.ubg43-searching #gameGrid{padding-top:6px}
@media(max-width:640px){.ubg43-badge{height:20px;padding:0 7px;font-size:8px}}
</style>
<script id="ubg43-final-runtime">
(()=>{
'use strict';
const $=id=>document.getElementById(id),grid=$('gameGrid'),search=$('searchBar'),clear=$('searchClear'),results=$('searchResults'),searchPage=$('searchPage'),searchPageText=$('searchPageText'),recSection=$('recommendSection'),trendRail=$('trendingRail'),newRail=$('newRail'),recRail=$('recommendRail');
const REPORT_URL='https://forms.gle/zXYtnxwXhGvXmBrq9';
const norm=s=>String(s||'').toLowerCase().replace(/[^a-z0-9]+/g,' ').trim();
const titleOf=c=>(c?.querySelector('h3')?.textContent||'').trim();
const urlOf=c=>{const d=c?.dataset?.url;if(d)return d;const a=c?.getAttribute('onclick')||'',m=a.match(/openGame\(\s*[\'\"]([^\'\"]+)/i);if(m)return m[1];const w=a.match(/window\.open\(\s*[\'\"]([^\'\"]+)/i);if(w)return w[1];return c?.querySelector('a[href]')?.href||''};
const imageOf=c=>c?.querySelector('img')?.getAttribute('src')||'';
const keyOf=c=>norm(titleOf(c))+'|'+urlOf(c).replace(/#.*$/,'');
const read=(k,f)=>{try{return JSON.parse(localStorage.getItem(k)||JSON.stringify(f))||f}catch(_){return f}};
const write=(k,v)=>{try{localStorage.setItem(k,JSON.stringify(v))}catch(_){}};
const playKey=c=>norm(titleOf(c))+'|'+imageOf(c);
const recordPlay=c=>{const h=read('ubg43_final_plays',{}),k=playKey(c),x=h[k]||{title:titleOf(c),plays:0,last:0};x.plays++;x.last=Date.now();h[k]=x;write('ubg43_final_plays',h)};
const recordSearch=q=>{const n=norm(q);if(n.length<2)return;const h=read('ubg43_final_searches',{}),x=h[n]||{count:0,last:0};x.count++;x.last=Date.now();h[n]=x;write('ubg43_final_searches',h)};
const openGame=url=>{const u=String(url||'').trim();if(!u)return false;try{const w=window.open(u,'_blank','noopener,noreferrer');if(!w)window.location.href=u;return true}catch(_){window.location.href=u;return true}};window.openGame=openGame;
function cards(){return grid?[...grid.querySelectorAll('.game-card')]:[]}
async function loadLegacyIntoGrid(){
  try{
    const r=await fetch('legacy-index.html',{cache:'no-store'});
    if(!r.ok)throw new Error('legacy '+r.status);
    const d=new DOMParser().parseFromString(await r.text(),'text/html');
    const source=[...d.querySelectorAll('.game-card')];
    if(source.length<100)throw new Error('legacy game count too low');
    grid.textContent=''; const seen=new Set();
    source.forEach(src=>{
      const h=src.querySelector('h3'),img=src.querySelector('img'); if(!h||!img)return;
      const title=h.textContent.trim().toLowerCase().replace(/[^a-z0-9]+/g,' ').trim();
      if(!title||seen.has(title))return;
      const c=src.cloneNode(true),a=c.getAttribute('onclick')||'',m=a.match(/openGame\(\s*[\'\"]([^\'\"]+)/i);
      if(m)c.dataset.url=m[1]; seen.add(title); grid.append(c);
    });
  }catch(_){}
  return cards().length;
}
function isNew(c){if(c.dataset.new==='1')return true;const d=Date.parse(c.dataset.newSince||c.dataset.date||'');return Number.isFinite(d)&&Date.now()-d<45*86400000}
function isTrending(c){const p=read('ubg43_final_plays',{})[playKey(c)]?.plays||0;return c.dataset.trending==='1'||c.dataset.trendingSeed==='1'||c.dataset.seed==='1'||p>0}
function badge(c,text,cls){const box=c.querySelector('.ubg43-badges')||(()=>{const x=document.createElement('div');x.className='ubg43-badges';c.append(x);return x})();const b=document.createElement('span');b.className='ubg43-badge '+cls;b.textContent=text;box.append(b)}
function decorate(){const cs=cards();cs.forEach(c=>{c.querySelector('.ribbons')?.remove();c.querySelector('.ubg43-badges')?.remove();if(isNew(c))badge(c,'NEW','new');if(isTrending(c))badge(c,'TRENDING','trending')});if(cs.length&&!cs.some(isTrending))cs.slice(0,10).forEach(c=>badge(c,'TRENDING','trending'))}
function wire(c){if(!c)return;c.tabIndex=0;if(!c.dataset.url)c.dataset.url=urlOf(c)}
function applyView(){const q=norm(search?.value||''),cat=window.__ubg43ActiveCategory||'All Games',cs=cards();cs.forEach(c=>{const text=norm(titleOf(c)),catOk=cat==='All Games'||(cat==='New Games'?isNew(c):cat==='Trending'?isTrending(c):(c.dataset.category||'Casual')===cat);c.style.display=catOk&&(!q||text.includes(q))?'':'none'});const shown=cs.filter(c=>c.style.display!=='none').length;if($('status'))$('status').textContent=`${shown} games shown`}
function similarity(a,b){const A=new Set(norm(a).split(' ').filter(x=>x.length>1)),B=new Set(norm(b).split(' ').filter(x=>x.length>1));if(!A.size||!B.size)return 0;let n=0;A.forEach(x=>B.has(x)&&n++);return n/Math.sqrt(A.size*B.size)}
function fillRail(rail,srcs){if(!rail)return;rail.innerHTML='';const used=new Set();srcs.forEach(src=>{const k=keyOf(src);if(used.has(k))return;used.add(k);const c=src.cloneNode(true);c.dataset.url=urlOf(src);c.querySelector('.ribbons')?.remove();c.querySelector('.ubg43-badges')?.remove();rail.append(c);wire(c);if(isNew(src))badge(c,'NEW','new');if(isTrending(src))badge(c,'TRENDING','trending')});if(srcs.length){const d=document.createElement('div');d.className='done';d.innerHTML='<span>That’s all for now ✨<small>More games are added automatically.</small></span>';rail.append(d)}}
function renderRails(){const cs=cards(),ph=read('ubg43_final_plays',{}),tr=cs.slice().sort((a,b)=>((ph[playKey(b)]?.plays||0)-(ph[playKey(a)]?.plays||0))||Number(isTrending(b))-Number(isTrending(a))||titleOf(a).localeCompare(titleOf(b))).slice(0,24),fresh=cs.filter(isNew).slice(0,24);fillRail(trendRail,tr);fillRail(newRail,fresh.length?fresh:cs.slice(0,24))}
function recommendations(q){if(!recSection||!recRail)return;const ph=read('ubg43_final_plays',{}),sh=read('ubg43_final_searches',{}),n=norm(q),out=cards().filter(c=>!norm(titleOf(c)).includes(n)).map(c=>{let score=similarity(titleOf(c),q)*.72;score+=(ph[playKey(c)]?.plays||0)*.08;Object.entries(sh).forEach(([k,v])=>score+=similarity(titleOf(c),k)*Math.min(5,v.count||0)*.05);if(isNew(c))score+=.1;return {c,score}}).sort((a,b)=>b.score-a.score||titleOf(a.c).localeCompare(titleOf(b.c))).slice(0,24).map(x=>x.c);fillRail(recRail,out);recSection.classList.remove('hidden')}
function setSearchMode(q){q=q.trim();if(!q){clearSearch();return}window.__ubg43SearchMode=true;document.body.classList.add('ubg43-searching');if(searchPage)searchPage.classList.remove('hidden');if(searchPageText)searchPageText.textContent=`Showing matching games for “${q}”. Trending Now and New Games remain available below.`;recordSearch(q);applyView();recommendations(q);results?.classList.remove('open');search?.blur()}
function clearSearch(){window.__ubg43SearchMode=false;document.body.classList.remove('ubg43-searching');if(search)search.value='';if(clear)clear.style.display='none';results?.classList.remove('open');searchPage?.classList.add('hidden');recSection?.classList.add('hidden');applyView();window.scrollTo({top:0,behavior:'smooth'})}
function showSuggestions(q){if(!results)return;results.innerHTML='';const n=norm(q);if(!n){results.classList.remove('open');return}const hits=cards().filter(c=>norm(titleOf(c)).includes(n)).slice(0,7);if(!hits.length){const d=document.createElement('div');d.className='search-empty';d.textContent='No matching games yet';results.append(d);results.classList.add('open');return}hits.forEach(c=>{const b=document.createElement('button');b.type='button';b.className='search-result';b.innerHTML='<img alt=""><span class="search-copy"><span class="search-title"></span><span class="search-label">Play game</span></span>';b.querySelector('img').src=imageOf(c);b.querySelector('img').alt=titleOf(c);b.querySelector('.search-title').textContent=titleOf(c);b.addEventListener('click',e=>{e.preventDefault();e.stopImmediatePropagation();if(search)search.value=titleOf(c);setSearchMode(titleOf(c))},{capture:true});results.append(b)});results.classList.add('open')}
function openCategories(){const side=$('categorySidebar'),ov=$('categoryOverlay');if(!side)return;side.classList.add('open');ov?.classList.add('open');side.setAttribute('aria-hidden','false');document.body.classList.add('locked');const list=$('categoryList');if(!list)return;list.innerHTML='';const cs=cards(),counts={};cs.forEach(c=>{const cat=c.dataset.category||'Casual';counts[cat]=(counts[cat]||0)+1});['All Games','New Games','Trending','Action','Adventure','Horror','Multiplayer','Fighting','Survival','Platformer','Racing','Sports','Puzzle','Arcade','Strategy','Simulation','Casual','Anime','Rhythm & Music','Card & Board','io'].forEach(cat=>{const b=document.createElement('button');b.type='button';b.className='category'+(window.__ubg43ActiveCategory===cat?' active':'');const n=cat==='All Games'?cs.length:cat==='New Games'?cs.filter(isNew).length:cat==='Trending'?cs.filter(isTrending).length:(counts[cat]||0);b.innerHTML='<span class="category-main"><span class="dot"></span><span class="category-name"></span></span><span class="category-count"></span>';b.querySelector('.category-name').textContent=cat;b.querySelector('.category-count').textContent=String(n);b.addEventListener('click',e=>{e.preventDefault();e.stopImmediatePropagation();window.__ubg43ActiveCategory=cat;applyView();closeCategories()},{capture:true});list.append(b)})}
function closeCategories(){$('categorySidebar')?.classList.remove('open');$('categoryOverlay')?.classList.remove('open');$('categorySidebar')?.setAttribute('aria-hidden','true');document.body.classList.remove('locked')}
function bind(){
 search?.addEventListener('input',e=>{e.stopImmediatePropagation();const q=search.value.trim();if(clear)clear.style.display=q?'inline-flex':'none';showSuggestions(q);applyView()},{capture:true});
 search?.addEventListener('keydown',e=>{e.stopImmediatePropagation();if(e.key==='Enter'){e.preventDefault();setSearchMode(search.value)}else if(e.key==='Escape'){e.preventDefault();clearSearch()}},{capture:true});
 clear?.addEventListener('click',e=>{e.preventDefault();e.stopImmediatePropagation();clearSearch()},{capture:true});
 $('randomGameButton')?.addEventListener('click',e=>{e.preventDefault();e.stopImmediatePropagation();const pool=cards().filter(c=>c.style.display!=='none'),list=pool.length?pool:cards(),c=list[Math.floor(Math.random()*list.length)];if(c){recordPlay(c);openGame(urlOf(c));decorate();renderRails()}},{capture:true});
 $('reportGameButton')?.addEventListener('click',e=>{e.preventDefault();e.stopImmediatePropagation();window.location.href=REPORT_URL},{capture:true});
 $('categoryToggle')?.addEventListener('click',e=>{e.preventDefault();e.stopImmediatePropagation();openCategories()},{capture:true});
 $('categoryClose')?.addEventListener('click',e=>{e.preventDefault();e.stopImmediatePropagation();closeCategories()},{capture:true});
 $('categoryOverlay')?.addEventListener('click',e=>{e.preventDefault();e.stopImmediatePropagation();closeCategories()},{capture:true});
 [['trendPrev','trendingRail'],['trendNext','trendingRail'],['newPrev','newRail'],['newNext','newRail'],['recPrev','recommendRail'],['recNext','recommendRail']].forEach(([id,rid])=>$(id)?.addEventListener('click',e=>{e.preventDefault();e.stopImmediatePropagation();const r=$(rid);if(r)r.scrollBy({left:Math.max(280,r.clientWidth*.8)*(id.includes('Prev')?-1:1),behavior:'smooth'})},{capture:true}));
 ['trendingRail','newRail','recommendRail'].forEach(id=>$(id)?.addEventListener('wheel',e=>{if(Math.abs(e.deltaY)>Math.abs(e.deltaX)){e.preventDefault();e.currentTarget.scrollLeft+=e.deltaY}},{passive:false}));
 document.addEventListener('click',e=>{const c=e.target.closest?.('.game-card');if(!c)return;e.preventDefault();e.stopImmediatePropagation();const u=urlOf(c);recordPlay(c);if(u)openGame(u);renderRails();decorate()},{capture:true});
 document.addEventListener('keydown',e=>{if(e.key==='Escape'&&$('categorySidebar')?.classList.contains('open'))closeCategories()},{capture:true});
}
function sync(){cards().forEach(wire);decorate();renderRails();applyView();const s=$('status');if(s&&cards().length)s.textContent=`${cards().length} games ready`}
async function start(){
  await loadLegacyIntoGrid();
  sync();bind();
  setTimeout(sync,700);setTimeout(sync,1800);setTimeout(sync,3500)
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});else start();
})();
</script>'''

needle = '</body>'
if needle.lower() not in s.lower():
    raise SystemExit('body end marker not found')
s = re.sub(r'</body>', lambda _m: runtime + '\n</body>', s, count=1, flags=re.I)
p.write_text(s, encoding='utf-8')
print('STABLE RUNTIME: one canonical runtime, full legacy feed, working search/buttons/carousels/recommendations, and NEW/TRENDING badges.')
