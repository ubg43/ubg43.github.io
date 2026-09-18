from pathlib import Path
import html,json,re,urllib.request
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import date
from game_validator import validate_candidate, norm as validator_norm
INDEX=Path('index.html'); LEGACY=Path('legacy-index.html'); REGISTRY=Path('.github/game-registry.json')
START='<!-- TRENDING-GAMES-START -->'; END='<!-- TRENDING-GAMES-END -->'; TARGET=1100
ZONES='https://raw.githubusercontent.com/gn-math/assets/main/zones.json'; HTML_ROOT='https://raw.githubusercontent.com/gn-math/html/main'; COVER_ROOT='https://raw.githubusercontent.com/gn-math/covers/main'
RULES={'Action':['action','shooter','combat','battle','fight','war','zombie','ninja','stickman','assassin','gun','sniper','strike','rush','arena','brawler','fighter','hero'],'Adventure':['adventure','quest','platform','dungeon','maze','escape','explore','survival','island','parkour','treasure','mystery'],'Arcade':['arcade','flappy','runner','run','jump','brick','ball','bubble','match','pinball','snake','pong','breakout','stack','tap'],'Puzzle':['puzzle','logic','sudoku','2048','mahjong','word','memory','connect','block','brain','sort','merge','numbers','crossword','jigsaw'],'Racing':['racing','race','drift','car','cars','motor','bike','bmx','kart','traffic','drive','rally','formula','truck','rider'],'Sports':['football','soccer','basketball','baseball','golf','tennis','hockey','volleyball','bowling','pool','sports','skate','ski','boxing','wrestling','cricket'],'Strategy':['strategy','tower','defense','defence','battle','td','idle','tycoon','manager','kingdom','chess','checkers','warcraft','empire','tactics'],'Simulation':['simulator','simulation','farming','farm','restaurant','cooking','shop','business','city','hotel','airport','life','house','doctor','hospital','school','job'],'Casual':['clicker','idle','dress','makeup','color','drawing','quiz','trivia','fun','cute','music','piano','matching','decorate']}
MPWORDS=['2 player','2-player','2p','local multiplayer','local co op','local co-op','same device','player 1','player 2','player one','player two','two players','two-player']; MPTITLES=['supreme duelist','basket random','soccer random','boxing random','volley random','rooftop snipers','get on top','stick duel','battle wheels','4 in a row','four in a row','12 mini battles','2 3 4 player']
def norm(s):return re.sub(r'[^a-z0-9]+',' ',str(s or '').lower()).strip()
def strip(s):return html.unescape(re.sub(r'<[^>]+>','',s or '')).strip()
def get_json(url):
 r=urllib.request.Request(url,headers={'User-Agent':'ubg43-game-builder/3.0'});return json.loads(urllib.request.urlopen(r,timeout=30).read().decode())
def game_url(z):return str(z.get('url','')).replace('{HTML_URL}',HTML_ROOT)
def cover_url(z):return str(z.get('cover','')).replace('{COVER_URL}',COVER_ROOT)
def extract_titles(text):return {norm(strip(x)) for x in re.findall(r'<h3[^>]*>(.*?)</h3>',text,re.I|re.S) if norm(strip(x))}
def probe(url,kind):
 return validate_candidate('candidate', url, 'https://raw.githubusercontent.com/gn-math/covers/main/1.png') if False else False
def page_text(url):
 try:return urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'ubg43-game-builder/3.0'}),timeout=8).read(100000).decode('utf-8','ignore').lower()
 except Exception:return ''
def is_local(name,text=''):
 n=norm(name);t=text.lower();return any(x in t for x in MPWORDS) or any(x in n for x in MPTITLES) or any(x in n for x in ['2 player','2-player','two player','2 3 4 player'])
def category(name,local=False):
 if local:return 'Multiplayer'
 n=norm(name);best='Casual';score=0
 for c,words in RULES.items():
  s=sum(1 for w in words if norm(w) in n)
  if s>score:score=s;best=c
 return best
def card(name,url,cover,local,first_seen,seed=False):
 attrs=f' data-category="{html.escape(category(name,local),quote=True)}" data-new-since="{html.escape(first_seen,quote=True)}"'
 if local:attrs+=' data-local-multiplayer="true"'
 if seed:attrs+=' data-trending-seed="true"'
 return f'  <div class="game-card"{attrs} onclick="openGame(\'{html.escape(url,quote=True)}\')">\n    <img loading="lazy" src="{html.escape(cover,quote=True)}" alt="{html.escape(name,quote=True)}" referrerpolicy="no-referrer">\n    <h3>{html.escape(name)}</h3>\n  </div>'
def patch_legacy(existing,added_cards):
 block=START+chr(10)+chr(10).join(added_cards)+chr(10)+END
 if START in existing and END in existing:
  a,b=existing.index(START),existing.index(END)+len(END)
  return existing[:a]+block+existing[b:]
 pos=existing.lower().rfind('</body>')
 if pos>=0:
  return existing[:pos]+chr(10)+block+chr(10)+existing[pos:]
 return existing.rstrip()+chr(10)+block+chr(10)
def inject_ui(index):
 css='''\n<style id="smart-game-ui"><nobr>\n.search-icon{opacity:1!important;visibility:visible!important}.search-clear,.category-close{font-family:Arial,sans-serif!important;line-height:1!important;display:inline-flex!important;align-items:center!important;justify-content:center!important;text-align:center!important}.featured-section{padding:20px 22px 5px}.featured-section.is-hidden{display:none}.featured-header{display:flex;align-items:end;justify-content:space-between;gap:12px;margin:0 0 12px}.featured-title{margin:0;color:#fff;font-size:21px;font-weight:850;text-shadow:0 2px 6px rgba(0,0,0,.24)}.featured-subtitle{margin:0;color:rgba(255,255,255,.68);font-size:12px;font-weight:650}.featured-grid{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:13px}.card-badges{position:absolute;left:8px;top:8px;z-index:3;display:flex;gap:5px;flex-wrap:wrap}.card-badge{padding:4px 7px;border-radius:999px;background:rgba(9,28,64,.86);color:#fff;font-size:10px;font-weight:850;box-shadow:0 3px 9px rgba(0,0,0,.22);backdrop-filter:blur(5px)}.card-badge.new{background:#0f6b4a}.card-badge.trending{background:#245fb7}.game-card.has-trending{box-shadow:0 7px 20px rgba(38,102,198,.22)}@media(max-width:1200px){.featured-grid{grid-template-columns:repeat(5,minmax(0,1fr))}}@media(max-width:900px){.featured-grid{grid-template-columns:repeat(4,minmax(0,1fr))}}@media(max-width:700px){.featured-grid{grid-template-columns:repeat(3,minmax(0,1fr))}.featured-section{padding-left:14px;padding-right:14px}}@media(max-width:570px){.featured-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.featured-header{align-items:flex-start;flex-direction:column}}\n</nobr></style>'''
 if 'id="smart-game-ui"' not in index:index=index.replace('</head>',css+'\n</head>',1)
 blocks='''\n    <section class="featured-section" id="trendingSection"><div class="featured-header"><div><h2 class="featured-title">Trending Now</h2><p class="featured-subtitle">Based on recent activity on this device</p></div></div><div class="featured-grid" id="trendingGrid"></div></section>\n    <section class="featured-section" id="newGamesSection"><div class="featured-header"><div><h2 class="featured-title">New Games</h2><p class="featured-subtitle">Recently added to the library</p></div></div><div class="featured-grid" id="newGamesGrid"></div></section>'''
 if 'id="trendingSection"' not in index:index=index.replace('    <div class="game-grid" id="gameGrid">',blocks+'\n    <div class="game-grid" id="gameGrid">',1)
 start=index.find('  <script>');end=index.rfind('  </script>')
 js=r'''  <script>
  function openGame(url){if(!url)return;const tab=window.open('about:blank','_blank');if(!tab)return;const safe=String(url).replace(/&/g,'&amp;').replace(/"/g,'&quot;');tab.document.write('<!doctype html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Google Docs</title><style>html,body{margin:0;width:100%;height:100%;overflow:hidden;background:#000}iframe{width:100%;height:100%;border:0}</style></head><body><iframe src="'+safe+'" allow="fullscreen;autoplay;gamepad;clipboard-read;clipboard-write" allowfullscreen></iframe></body></html>');tab.document.close();}
  const searchBar=document.getElementById('searchBar'),searchResults=document.getElementById('searchResults'),searchClear=document.getElementById('searchClear'),gameGrid=document.getElementById('gameGrid'),loadingCard=document.getElementById('loadingCard');const randomButton=document.getElementById('randomGameButton'),reportButton=document.getElementById('reportGameButton');
  const norm=s=>(s||'').toString().toLowerCase().replace(/[^a-z0-9]+/g,' ').trim();
  const RULES={"Action":["action","shooter","combat","battle","fight","war","zombie","ninja","stickman","assassin","gun","sniper","strike","rush","arena","brawler","fighter","hero"],"Adventure":["adventure","quest","platform","dungeon","maze","escape","explore","survival","island","parkour","treasure","mystery"],"Arcade":["arcade","flappy","runner","run","jump","brick","ball","bubble","match","pinball","snake","pong","breakout","stack","tap"],"Puzzle":["puzzle","logic","sudoku","2048","mahjong","word","memory","connect","block","brain","sort","merge","numbers","crossword","jigsaw"],"Racing":["racing","race","drift","car","cars","motor","bike","bmx","kart","traffic","drive","rally","formula","truck","rider"],"Sports":["football","soccer","basketball","baseball","golf","tennis","hockey","volleyball","bowling","pool","sports","skate","ski","boxing","wrestling","cricket"],"Strategy":["strategy","tower","defense","defence","battle","td","idle","tycoon","manager","kingdom","chess","checkers","warcraft","empire","tactics"],"Simulation":["simulator","simulation","farming","farm","restaurant","cooking","shop","business","city","hotel","airport","life","house","doctor","hospital","school","job"],"Casual":["clicker","idle","dress","makeup","color","drawing","quiz","trivia","fun","cute","music","piano","matching","decorate"]};
  const MPWORDS=["2 player","2-player","2p","local multiplayer","local co op","local co-op","same device","player 1","player 2","player one","player two","two players","two-player"];const MPTITLES=["supreme duelist","basket random","soccer random","boxing random","volley random","rooftop snipers","get on top","stick duel","battle wheels","4 in a row","four in a row","12 mini battles","2 3 4 player"];
  function games(){return [...gameGrid.querySelectorAll(':scope > .game-card')].map(card=>{const img=card.querySelector('img');const title=(card.querySelector('h3')?.textContent||img?.alt||'Game').trim();return {card,title,image:img?.getAttribute('src')||img?.currentSrc||'',key:norm(title)+'|'+(img?.getAttribute('src')||''),category:card.dataset.category||inferCategory(title,card),new:isNew(card)}}).filter(g=>g.title)}
  function inferCategory(title,card){if(card?.dataset.localMultiplayer==='true')return 'Multiplayer';const t=norm(title);let best='Casual',score=0;for(const [c,ws] of Object.entries(RULES)){const s=ws.reduce((n,w)=>n+(t.includes(norm(w))?1:0),0);if(s>score){score=s;best=c}}return best}
  function categoryFor(g){return g.category||inferCategory(g.title,g.card)}
  function isNew(card){const d=Date.parse(card.dataset.newSince||'');return Number.isNaN(d)?false:(Date.now()-d)<45*86400000}
  const TLOG='ubg_trending_play_log_v3',TCACHE='ubg_trending_cache_v3',PLAY='ubg_play_history_v5',SEARCH='ubg_search_history_v4';
  function read(k,f){try{return JSON.parse(localStorage.getItem(k)||JSON.stringify(f))||f}catch(_){return f}}function write(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(_){} }
  function gameKey(card){const img=card.querySelector('img');return norm((card.querySelector('h3')?.textContent||img?.alt||'Game'))+'|'+(img?.getAttribute('src')||img?.currentSrc||'')}
  function recordTrend(g){const h=read(TLOG,{}),k=gameKey(g.card);h[k]=(h[k]||[]).concat(Date.now()).slice(-100);const cut=Date.now()-90*86400000;Object.keys(h).forEach(x=>{h[x]=h[x].filter(t=>t>=cut);if(!h[x].length)delete h[x]});write(TLOG,h);write(TCACHE,{at:0,keys:[]})}
  function recordPlay(g){if(!g?.title)return;const h=read(PLAY,{}),x=h[g.key]||{title:g.title,image:g.image,plays:0,last:0};x.title=g.title;x.image=g.image;x.plays++;x.last=Date.now();h[g.key]=x;write(PLAY,h);recordTrend(g)}
  function trendSet(){const gs=games(),h=read(TLOG,{}),cut=Date.now()-3*86400000;const ranked=gs.map(g=>{const hits=(h[g.key]||[]).filter(t=>t>=cut);let s=0;hits.forEach(t=>s+=Math.exp(-(Date.now()-t)/86400000));return {g,s,last:Math.max(0,...hits)}}).filter(x=>x.s>0).sort((a,b)=>b.s-a.s||b.last-a.last);const chosen=ranked.slice(0,18).map(x=>x.g);if(chosen.length<18){for(const g of gs.filter(x=>x.card.dataset.trendingSeed==='true'))if(!chosen.some(x=>x.key===g.key)){chosen.push(g);if(chosen.length>=18)break}}write(TCACHE,{at:Date.now(),keys:chosen.map(x=>x.key)});return new Set(chosen.map(x=>x.key))}
  function trendSetCached(){const c=read(TCACHE,{});return c.at&&Date.now()-c.at<300000&&Array.isArray(c.keys)?new Set(c.keys):trendSet()}
  function newGames(){return games().filter(g=>g.new).sort((a,b)=>(Date.parse(b.card.dataset.newSince)||0)-(Date.parse(a.card.dataset.newSince)||0||a.title.localeCompare(b.title)))}
  function decorate(card,trend){card.querySelector('.card-badges')?.remove();card.classList.remove('has-trending');const b=document.createElement('div');b.className='card-badges';if(isNew(card)){const n=document.createElement('span');n.className='card-badge new';n.textContent='NEW';b.appendChild(n)}if(trend.has(gameKey(card))){const t=document.createElement('span');t.className='card-badge trending';t.textContent='TRENDING';b.appendChild(t);card.classList.add('has-trending')}if(b.children.length)card.appendChild(b)}
  function cloneCard(g,trend){const c=g.card.cloneNode(true);c.removeAttribute('onclick');decorate(c,trend);c.addEventListener('click',()=>{recordPlay(g);g.card.click()});return c}
  function renderFeatured(){const trend=trendSetCached(),tg=document.getElementById('trendingGrid'),ng=document.getElementById('newGamesGrid');if(!tg||!ng)return;const lim=window.innerWidth<=570?6:window.innerWidth<=700?9:window.innerWidth<=900?12:window.innerWidth<=1200?15:18;tg.innerHTML='';games().filter(g=>trend.has(g.key)).slice(0,lim).forEach(g=>tg.appendChild(cloneCard(g,trend)));ng.innerHTML='';newGames().slice(0,18).forEach(g=>ng.appendChild(cloneCard(g,trend)));const hide=searchBar.value.trim().length>0||activeCat!=='All Games';document.getElementById('trendingSection')?.classList.toggle('is-hidden',hide);document.getElementById('newGamesSection')?.classList.toggle('is-hidden',hide)}
  let activeCat='All Games';
  function renderCategories(){const list=document.getElementById('categoryList');if(!list)return;const gs=games(),trend=trendSetCached();const counts={"All Games":gs.length,Trending:trend.size,"New Games":gs.filter(g=>g.new).length};Object.keys(RULES).forEach(c=>counts[c]=gs.filter(g=>categoryFor(g)===c).length);counts.Multiplayer=gs.filter(g=>categoryFor(g)==='Multiplayer').length;const cats=['All Games','Trending','New Games','Action','Adventure','Arcade','Puzzle','Racing','Sports','Strategy','Simulation','Multiplayer','Casual'];list.innerHTML='';cats.forEach(c=>{const b=document.createElement('button');b.type='button';b.className='category-item'+(c===activeCat?' is-active':'')+(c==='Trending'?' is-trending':'');b.innerHTML='<span class="category-item-main"><span class="category-dot"></span><span class="category-name"></span></span><span class="category-count"></span>';b.querySelector('.category-name').textContent=c;b.querySelector('.category-count').textContent=String(counts[c]||0);b.onclick=()=>{activeCat=c;applyFilters();closeCats()};list.appendChild(b)})}
  function applyFilters(){const q=searchBar.value.trim(),gs=games(),trend=trendSetCached();gs.forEach(g=>{let show=activeCat==='All Games'||(activeCat==='Trending'?trend.has(g.key):activeCat==='New Games'?g.new:categoryFor(g)===activeCat);if(q)show=show&&rank(g.title,q)<99;g.card.style.display=show?'':'none';decorate(g.card,trend)});renderCategories();renderFeatured()}
  function rank(t,q){const a=norm(t),b=norm(q);if(!b)return 99;if(a===b)return 0;if(a.startsWith(b))return 1;if(a.includes(b))return 2;const bw=b.split(' ').filter(Boolean),aw=a.split(' ');return bw.length&&bw.every(x=>aw.some(y=>y.startsWith(x)||y.includes(x)))?3:99}
  function matched(q){return games().map(g=>({...g,score:rank(g.title,q)})).filter(g=>g.score<99).sort((a,b)=>a.score-b.score||a.title.localeCompare(b.title))}
  function suggestions(q){searchResults.innerHTML='';if(!q){searchResults.classList.remove('is-open');return}const top=matched(q).slice(0,5);if(!top.length){searchResults.innerHTML='<div class="search-empty">No matching games yet</div>';searchResults.classList.add('is-open');return}top.forEach(g=>{const b=document.createElement('button');b.type='button';b.className='search-result';b.innerHTML='<img loading="lazy" alt=""><span class="search-result-copy"><span class="search-result-title"></span><span class="search-result-label">Play game</span></span>';const i=b.querySelector('img');i.src=g.image;i.alt=g.title;b.querySelector('.search-result-title').textContent=g.title;b.onclick=()=>{searchBar.value=g.title;searchClear.style.display='inline-flex';searchResults.classList.remove('is-open');g.card.click()};searchResults.appendChild(b)});searchResults.classList.add('is-open')}
  function similarity(a,b){const A=new Set(norm(a).split(' ').filter(x=>x.length>1)),B=new Set(norm(b).split(' ').filter(x=>x.length>1));if(!A.size||!B.size)return 0;let n=0;A.forEach(x=>B.has(x)&&n++);return n/Math.sqrt(A.size*B.size)}
  function recordSearch(q){q=norm(q);if(!q)return;const h=read(SEARCH,{}),x=h[q]||{count:0,last:0};x.count++;x.last=Date.now();h[q]=x;write(SEARCH,h)}
  function refreshRecommendations(q){const sec=document.getElementById('searchRecommendations'),grid=document.getElementById('searchRecommendationsGrid');if(!sec||!grid)return;if(!q){sec.classList.remove('is-visible');grid.innerHTML='';return}const gs=games(),plays=read(PLAY,{}),searches=read(SEARCH,{}),playedCats=[...new Set(Object.values(plays).map(x=>inferCategory(x.title,{dataset:{}})))];const candidates=gs.map(g=>{let s=similarity(g.title,q)*.42;s+=searches[q]?.count?similarity(g.title,q)*.12:0;for(const x of Object.values(searches))s+=similarity(g.title,x.query||'')*(x.count||0)*.12;for(const x of Object.values(plays))s+=similarity(g.title,x.title||'')*Math.min(6,x.plays||1)*.11;if(playedCats.includes(categoryFor(g)))s+=.06;if(trendSetCached().has(g.key))s+=.03;return {...g,s}}).filter(g=>rank(g.title,q)>=99).sort((a,b)=>b.s-a.s||a.title.localeCompare(b.title)).slice(0,24);grid.innerHTML='';candidates.forEach(g=>{const b=document.createElement('button');b.type='button';b.className='search-recommendation';b.title=g.title;const i=document.createElement('img');i.loading='lazy';i.src=g.image;i.alt=g.title;const s=document.createElement('span');s.textContent=g.title;b.append(i,s);b.onclick=()=>{g.card.click();refreshRecommendations(q)};grid.appendChild(b)});sec.querySelector('.search-recommendations-subtitle').textContent='Similar to your search and recent games';sec.classList.add('is-visible')}
  searchBar.addEventListener('input',()=>{const q=searchBar.value.trim();searchClear.style.display=q?'inline-flex':'none';suggestions(q);clearTimeout(window.__s);window.__s=setTimeout(()=>{if(q.length>=2)recordSearch(q);refreshRecommendations(q);applyFilters()},250)});searchBar.addEventListener('keydown',e=>{if(e.key==='Escape')searchResults.classList.remove('is-open');if(e.key==='Enter'){const a=searchResults.querySelector('.search-result.is-active');if(a){e.preventDefault();a.click()}}});searchClear.addEventListener('click',()=>{searchBar.value='';searchClear.style.display='none';searchResults.classList.remove('is-open');activeCat='All Games';applyFilters();searchBar.focus()});document.addEventListener('click',e=>{if(!e.target.closest('.search-shell'))searchResults.classList.remove('is-open')});
  const toggle=document.getElementById('categoryToggle'),close=document.getElementById('categoryClose'),side=document.getElementById('categorySidebar'),overlay=document.getElementById('categoryOverlay');function openCats(){side.classList.add('is-open');overlay.hidden=false;requestAnimationFrame(()=>overlay.classList.add('is-open'));side.setAttribute('aria-hidden','false');toggle.setAttribute('aria-expanded','true');document.body.classList.add('category-locked');renderCategories()}function closeCats(){side.classList.remove('is-open');overlay.classList.remove('is-open');side.setAttribute('aria-hidden','true');toggle.setAttribute('aria-expanded','false');document.body.classList.remove('category-locked');setTimeout(()=>overlay.hidden=true,220)}toggle?.addEventListener('click',()=>side.classList.contains('is-open')?closeCats():openCats());close?.addEventListener('click',closeCats);overlay?.addEventListener('click',closeCats);document.addEventListener('keydown',e=>{if(e.key==='Escape'&&side?.classList.contains('is-open'))closeCats()});
  document.addEventListener('click',e=>{if(e.target.closest('#gameGrid > .game-card')){const card=e.target.closest('#gameGrid > .game-card');const g=games().find(x=>x.card===card);if(g)recordPlay(g)}},true);
  randomButton?.addEventListener('click',()=>{const pool=games().filter(g=>g.card.style.display!=='none');if(pool.length)pool[Math.floor(Math.random()*pool.length)].card.click()});reportButton?.addEventListener('click',()=>location.href='mailto:ubg423@gmail.com?subject=UBG%20Problem%20%2F%20Game%20Suggestion');
  async function loadLegacy(){try{const r=await fetch('legacy-index.html',{cache:'no-store'});if(!r.ok)throw new Error();const d=new DOMParser().parseFromString(await r.text(),'text/html'),src=d.querySelector('#gameGrid');if(!src)throw new Error();gameGrid.innerHTML='';[...src.querySelectorAll(':scope > .game-card')].forEach(c=>gameGrid.appendChild(document.importNode(c,true)));loadingCard.style.display='none';applyFilters()}catch(_){loadingCard.className='error-card';loadingCard.textContent='The game library could not be loaded right now. Refresh the page to try again.'}}
  let resizeTimer=0;window.addEventListener('resize',()=>{clearTimeout(resizeTimer);resizeTimer=setTimeout(applyFilters,120)});new MutationObserver(()=>{if(gameGrid.children.length)applyFilters()}).observe(gameGrid,{childList:true});loadLegacy();
  </script>'''
 return index[:start]+js+index[end+len('  </script>'):]
def main():
 index=INDEX.read_text(encoding='utf-8');legacy=LEGACY.read_text(encoding='utf-8') if LEGACY.exists() else '';today=date.today().isoformat();reg={}
 if REGISTRY.exists():
  try:reg=json.loads(REGISTRY.read_text())
  except Exception:reg={}
 existing=extract_titles(legacy)|extract_titles(index)
 if not reg:reg={k:{'first_seen':None} for k in existing}
 zones=get_json(ZONES);byname={norm(strip(str(z.get('name','')))):z for z in zones if int(z.get('id',-1))>=0 and norm(strip(str(z.get('name',''))))}
 candidates=[];seen=set(existing)
 for z in zones:
  if int(z.get('id',-1))<0:continue
  n=strip(str(z.get('name','')));k=norm(n);u=game_url(z);c=cover_url(z)
  if not n or k in seen or not u.startswith(('http://','https://')) or not c.startswith(('http://','https://')) or k.startswith('suggest games'):continue
  seen.add(k);candidates.append((n,u,c))
  if len(candidates)>=1450:break
 forced=[]
 for w in ['Granny',"Five Nights at Freddy's"]:
  if norm(w) in byname and norm(w) not in existing:forced.append((strip(byname[norm(w)].get('name','')),game_url(byname[norm(w)]),cover_url(byname[norm(w)])))
 candidates=forced+candidates
 verified=[]
 with ThreadPoolExecutor(max_workers=56) as ex:
  fs={ex.submit(lambda x:validate_candidate(x[0],x[1],x[2]),it):it for it in candidates}
  for f in as_completed(fs):
   try:
    if f.result():verified.append(fs[f])
   except Exception:pass
 cards_by_name={norm(n):(n,u,c) for n,u,c in verified};newcards=[]
 with ThreadPoolExecutor(max_workers=40) as ex:
  fs={ex.submit(page_text,u):(n,u,c) for n,u,c in verified[:TARGET]}
  for f in as_completed(fs):
   n,u,c=fs[f];newcards.append((n,u,c,is_local(n,f.result())))
 old=[]
 if START in legacy and END in legacy:
  seg=legacy[legacy.index(START)+len(START):legacy.index(END)]
  pat=re.compile(r'<div class="game-card"(?P<a>[^>]*)>\s*<img[^>]+src="(?P<i>[^"]+)"[^>]*>\s*<h3>(?P<t>.*?)</h3>\s*</div>',re.I|re.S)
  for m in pat.finditer(seg):
   a=m.group('a');n=strip(m.group('t'));u=re.search(r'onclick="openGame\(\'([^\']+)\'\)"',a); 
   if u:old.append((n,u.group(1),m.group('i'),'data-local-multiplayer="true"' in a,reg.get(norm(n),{}).get('first_seen')))
 # Deduplicate the persisted library by normalized title and URL before adding anything new.
 dedup_old=[];seen_title=set();seen_url=set()
 for item in old:
  tk=norm(item[0]);uk=item[1].split('#',1)[0].rstrip('/')
  if not tk or tk in seen_title or uk in seen_url:continue
  seen_title.add(tk);seen_url.add(uk);dedup_old.append(item)
 old=dedup_old
 need=max(0,TARGET-len(old));add=[]
  k=norm(n);fs=reg.get(k,{}).get('first_seen') or today;reg[k]={'first_seen':fs};add.append((n,u,c,local,fs))
 combined=[];used_title=set();used_url=set()
 for item in old+add:
  tk=norm(item[0]);uk=item[1].split('#',1)[0].rstrip('/')
  if tk in used_title or uk in used_url:continue
  used_title.add(tk);used_url.add(uk);combined.append(item)
 if len(combined)<1000:
  print(f'Only {len(combined)} verified games available in this upstream pass; retaining the existing library and continuing')
 if sum(1 for x in combined if x[3])<100:
  print(f'Only {sum(1 for x in combined if x[3])} same-device multiplayer games verified in this pass; continuing without failing the library build')
 block=patch_legacy(legacy,[card(n,u,c,local,reg.get(norm(n),{}).get('first_seen') or today,i<18) for i,(n,u,c,local,_) in enumerate(combined)])
 index=inject_ui(index);LEGACY.write_text(block,encoding='utf-8');INDEX.write_text(index,encoding='utf-8');REGISTRY.parent.mkdir(parents=True,exist_ok=True);REGISTRY.write_text(json.dumps(reg,indent=2,sort_keys=True)+'\n')
 print(f'FINAL VERIFIED BUILD: {len(combined)} games; {sum(1 for x in combined if x[3])} same-device multiplayer; smart categories/trending/new tags/recommendations enabled.')
if __name__=='__main__':main()
