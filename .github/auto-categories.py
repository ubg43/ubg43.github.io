from pathlib import Path
import html
import json
import re
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date

INDEX=Path('index.html')
LEGACY=Path('legacy-index.html')
REGISTRY=Path('.github/game-registry.json')
START='<!-- TRENDING-GAMES-START -->'
END='<!-- TRENDING-GAMES-END -->'
TARGET=1100
ZONES='https://raw.githubusercontent.com/gn-math/assets/main/zones.json'
HTML_ROOT='https://raw.githubusercontent.com/gn-math/html/main'
COVER_ROOT='https://raw.githubusercontent.com/gn-math/covers/main'

RULES={
'Action':['action','shooter','combat','battle','fight','war','zombie','ninja','stickman','assassin','gun','sniper','strike','rush','arena','brawler','fighter','hero'],
'Adventure':['adventure','quest','platform','dungeon','maze','escape','explore','survival','island','parkour','treasure','mystery'],
'Arcade':['arcade','flappy','runner','run','jump','brick','ball','bubble','match','pinball','snake','pong','breakout','stack','tap'],
'Puzzle':['puzzle','logic','sudoku','2048','mahjong','word','memory','connect','block','brain','sort','merge','numbers','crossword','jigsaw'],
'Racing':['racing','race','drift','car','cars','motor','bike','bmx','kart','traffic','drive','rally','formula','truck','rider'],
'Sports':['football','soccer','basketball','baseball','golf','tennis','hockey','volleyball','bowling','pool','sports','skate','ski','boxing','wrestling','cricket'],
'Strategy':['strategy','tower','defense','defence','battle','td','idle','tycoon','manager','kingdom','chess','checkers','warcraft','empire','tactics'],
'Simulation':['simulator','simulation','farming','farm','restaurant','cooking','shop','business','city','hotel','airport','life','house','doctor','hospital','school','job'],
'Casual':['clicker','idle','dress','makeup','color','drawing','quiz','trivia','fun','cute','music','piano','matching','decorate']}
MP_WORDS=['2 player','2-player','2p','local multiplayer','local co op','local co-op','same device','player 1','player 2','player one','player two','two players','two-player']
MP_TITLES=['supreme duelist','basket random','soccer random','boxing random','volley random','rooftop snipers','get on top','stick duel','battle wheels','4 in a row','four in a row','12 mini battles','2 3 4 player']

def norm(s): return re.sub(r'[^a-z0-9]+',' ',str(s or '').lower()).strip()
def strip(s): return html.unescape(re.sub(r'<[^>]+>','',s or '')).strip()
def get_json(url):
    req=urllib.request.Request(url,headers={'User-Agent':'ubg43-game-builder/2.0'})
    with urllib.request.urlopen(req,timeout=30) as r: return json.loads(r.read().decode('utf-8'))
def game_url(z): return str(z.get('url','')).replace('{HTML_URL}',HTML_ROOT).replace('//main/','//main/') if '{HTML_URL}' in str(z.get('url','')) else str(z.get('url',''))
def cover_url(z): return str(z.get('cover','')).replace('{COVER_URL}',COVER_ROOT) if '{COVER_URL}' in str(z.get('cover','')) else str(z.get('cover',''))
def extract_titles(text): return {norm(strip(x)) for x in re.findall(r'<h3[^>]*>(.*?)</h3>',text,re.I|re.S) if norm(strip(x))}
def card_attrs(text):
    out=[]
    for m in re.finditer(r'<div class="game-card"([^>]*)>.*?<h3>(.*?)</h3>.*?</div>',text,re.I|re.S):
        a=m.group(1); title=strip(m.group(2)); key=norm(title)
        if key: out.append((key,title,a))
    return out

def probe(url,kind):
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'ubg43-game-builder/2.0'})
        with urllib.request.urlopen(req,timeout=8) as r:
            if not 200<=r.status<400:return False
            b=r.read(512); ct=(r.headers.get('Content-Type') or '').lower()
            if kind=='image': return bool(b) and ('image/' in ct or re.search(r'\.(png|jpe?g|webp|gif)(\?|$)',url,re.I))
            return b'<html' in b.lower() or b'<!doctype' in b.lower() or 'text/html' in ct or 'xhtml' in ct
    except Exception:return False

def page_text(url):
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'ubg43-game-builder/2.0'})
        with urllib.request.urlopen(req,timeout=8) as r:return r.read(120000).decode('utf-8','ignore').lower()
    except Exception:return ''

def local_mp(name,text=''):
    t=(text or '').lower(); n=norm(name)
    return any(x in t for x in MP_WORDS) or any(x in n for x in MP_TITLES) or any(x in n for x in ['2 player','2-player','two player','2 3 4 player'])

def category(name,is_local=False):
    if is_local:return 'Multiplayer'
    n=norm(name); best='Casual'; score=0
    for cat,words in RULES.items():
        s=sum(3 if n==norm(w) else 2 if f' {norm(w)} ' in f' {n} ' else 1 for w in words if norm(w) in n)
        if s>score: score=s; best=cat
    return best

def add_attrs(attrs,extra):
    attrs=re.sub(r'\sdata-(?:category|new-since|local-multiplayer)="[^"]*"','',attrs)
    return attrs+extra

def render_card(name,url,cover,local,new_since=None,seed=False):
    a=' data-local-multiplayer="true"' if local else ''
    a+=f' data-category="{html.escape(category(name,local),quote=True)}"'
    if new_since:a+=f' data-new-since="{html.escape(new_since,quote=True)}"'
    if seed:a+=' data-trending-seed="true"'
    return f'  <div class="game-card"{a} onclick="openGame(\'{html.escape(url,quote=True)}\')">\n    <img loading="lazy" src="{html.escape(cover,quote=True)}" alt="{html.escape(name,quote=True)}" referrerpolicy="no-referrer">\n    <h3>{html.escape(name)}</h3>\n  </div>'

def inject_index(index):
    css=r'''
<style id="smart-game-ui">
.search-icon{opacity:1!important;visibility:visible!important}
.search-clear,.category-close{font-family:Arial,sans-serif;line-height:1;display:inline-flex;align-items:center;justify-content:center;text-align:center}
.featured-section{padding:20px 22px 4px}.featured-section.is-hidden{display:none}.featured-header{display:flex;align-items:end;justify-content:space-between;gap:12px;margin:0 0 12px}.featured-title{margin:0;color:#fff;font-size:21px;font-weight:850;text-shadow:0 2px 6px rgba(0,0,0,.24)}.featured-subtitle{margin:0;color:rgba(255,255,255,.68);font-size:12px;font-weight:650}.featured-grid{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:13px}.featured-grid .game-card{min-width:0}.card-badges{position:absolute;left:8px;top:8px;z-index:3;display:flex;gap:5px;flex-wrap:wrap}.card-badge{padding:4px 7px;border-radius:999px;background:rgba(9,28,64,.86);color:#fff;font-size:10px;font-weight:850;letter-spacing:.02em;box-shadow:0 3px 9px rgba(0,0,0,.22);backdrop-filter:blur(5px)}.card-badge.new{background:#0f6b4a}.card-badge.trending{background:#245fb7}.game-card.has-trending{box-shadow:0 7px 20px rgba(38,102,198,.22)}
@media(max-width:1200px){.featured-grid{grid-template-columns:repeat(5,minmax(0,1fr))}}@media(max-width:900px){.featured-grid{grid-template-columns:repeat(4,minmax(0,1fr))}}@media(max-width:700px){.featured-grid{grid-template-columns:repeat(3,minmax(0,1fr))}.featured-section{padding-left:14px;padding-right:14px}}@media(max-width:570px){.featured-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.featured-header{align-items:flex-start;flex-direction:column}}
</style>'''
    if 'id="smart-game-ui"' not in index:index=index.replace('</head>',css+'\n</head>',1)
    blocks='''
    <section class="featured-section" id="trendingSection"><div class="featured-header"><div><h2 class="featured-title">Trending Now</h2><p class="featured-subtitle">Automatically ranked from recent play activity</p></div></div><div class="featured-grid" id="trendingGrid"></div></section>
    <section class="featured-section" id="newGamesSection"><div class="featured-header"><div><h2 class="featured-title">New Games</h2><p class="featured-subtitle">Recently added games, updated automatically</p></div></div><div class="featured-grid" id="newGamesGrid"></div></section>'''
    if 'id="trendingSection"' not in index:index=index.replace('    <div class="game-grid" id="gameGrid">',blocks+'\n    <div class="game-grid" id="gameGrid">',1)
    start=index.find('  <script>'); end=index.rfind('  </script>')
    if start<0 or end<start: raise SystemExit('main script block not found')
    js=r'''  <script>
  function openGame(url){if(!url)return;const tab=window.open('about:blank','_blank');if(!tab)return;const safe=String(url).replace(/&/g,'&amp;').replace(/"/g,'&quot;');tab.document.write('<!doctype html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Google Docs</title><style>html,body{margin:0;width:100%;height:100%;overflow:hidden;background:#000}iframe{width:100%;height:100%;border:0}</style></head><body><iframe src="'+safe+'" allow="fullscreen;autoplay;gamepad;clipboard-read;clipboard-write" allowfullscreen></iframe></body></html>');tab.document.close();}
  const searchBar=document.getElementById('searchBar'),searchResults=document.getElementById('searchResults'),searchClear=document.getElementById('searchClear'),gameGrid=document.getElementById('gameGrid'),loadingCard=document.getElementById('loadingCard'),randomButton=document.getElementById('randomGameButton'),reportButton=document.getElementById('reportGameButton');
  const norm=s=>(s||'').toString().toLowerCase().replace(/[^a-z0-9]+/g,' ').trim();
  const RULES={"Action":["action","shooter","combat","battle","fight","war","zombie","ninja","stickman","assassin","gun","sniper","strike","rush","arena","brawler","fighter","hero"],"Adventure":["adventure","quest","platform","dungeon","maze","escape","explore","survival","island","parkour","treasure","mystery"],"Arcade":["arcade","flappy","runner","run","jump","brick","ball","bubble","match","pinball","snake","pong","breakout","stack","tap"],"Puzzle":["puzzle","logic","sudoku","2048","mahjong","word","memory","connect","block","brain","sort","merge","numbers","crossword","jigsaw"],"Racing":["racing","race","drift","car","cars","motor","bike","bmx","kart","traffic","drive","rally","formula","truck","rider"],"Sports":["football","soccer","basketball","baseball","golf","tennis","hockey","volleyball","bowling","pool","sports","skate","ski","boxing","wrestling","cricket"],"Strategy":["strategy","tower","defense","defence","battle","td","idle","tycoon","manager","kingdom","chess","checkers","warcraft","empire","tactics"],"Simulation":["simulator","simulation","farming","farm","restaurant","cooking","shop","business","city","hotel","airport","life","house","doctor","hospital","school","job"],"Casual":["clicker","idle","dress","makeup","color","drawing","quiz","trivia","fun","cute","music","piano","matching","decorate"]};
  const MPWORDS=["2 player","2-player","2p","local multiplayer","local co op","local co-op","same device","player 1","player 2","player one","player two","two players","two-player"];const MPTITLES=["supreme duelist","basket random","soccer random","boxing random","volley random","rooftop snipers","get on top","stick duel","battle wheels","4 in a row","four in a row","12 mini battles","2 3 4 player"];
  function games(){return [...gameGrid.querySelectorAll(':scope > .game-card')].map(card=>{const img=card.querySelector('img');return {card,title:(card.querySelector('h3')?.textContent||img?.alt||'Game').trim(),image:img?.getAttribute('src')||img?.currentSrc||'',key:norm((card.querySelector('h3')?.textContent||img?.alt||'Game'))+'|'+(img?.getAttribute('src')||''),category:card.dataset.category||inferCategory((card.querySelector('h3')?.textContent||''),card),new:isNew(card)}}).filter(g=>g.title)}
  function inferCategory(title,card){if(card?.dataset.localMultiplayer==='true')return 'Multiplayer';const t=norm(title);let best='Casual',score=0;for(const [c,ws] of Object.entries(RULES)){const s=ws.reduce((n,w)=>n+(t.includes(norm(w))?1:0),0);if(s>score){score=s;best=c}}return best}
  function isNew(card){const s=card.dataset.newSince;if(!s)return false;const d=Date.parse(s);return Number.isNaN(d)?false:(Date.now()-d)<1000*60*60*24*45}
  function tags(card){let b=card.querySelector('.card-badges');if(!b){b=document.createElement('div');b.className='card-badges';card.appendChild(b)}return b}
  function clearBadges(card){const b=card.querySelector('.card-badges');if(b)b.remove();card.classList.remove('has-trending')}
  function decorate(card,trend){clearBadges(card);const b=tags(card);if(isNew(card)){const x=document.createElement('span');x.className='card-badge new';x.textContent='NEW';b.appendChild(x)}if(trend.has(gameKey(card))){const x=document.createElement('span');x.className='card-badge trending';x.textContent='TRENDING';b.appendChild(x);card.classList.add('has-trending')}}
  function gameKey(card){const img=card.querySelector('img');return norm((card.querySelector('h3')?.textContent||img?.alt||'Game'))+'|'+(img?.getAttribute('src')||img?.currentSrc||'')}
  const TLOG='ubg_trending_play_log_v2',TCACHE='ubg_trending_cache_v2',PLAY='ubg_play_history_v4',SEARCH='ubg_search_history_v3';
  function read(k,f){try{return JSON.parse(localStorage.getItem(k)||JSON.stringify(f))||f}catch(_){return f}}function write(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(_){} }
  function recordPlay(g){if(!g?.title)return;const h=read(PLAY,{}),x=h[g.key]||{title:g.title,image:g.image,plays:0,last:0};x.plays++;x.last=Date.now();x.title=g.title;x.image=g.image;h[g.key]=x;write(PLAY,h);recordTrend(g)}
  function recordTrend(g){const h=read(TLOG,{}),k=gameKey(g.card||g);h[k]=h[k]||[];h[k].push(Date.now());const cut=Date.now()-90*864e5;Object.keys(h).forEach(k=>{h[k]=(h[k]||[]).filter(t=>t>=cut).slice(-100);if(!h[k].length)delete h[k]});write(TLOG,h);write(TCACHE,{at:0,keys:[]})}
  function trendSet(){const gs=games(),h=read(TLOG,{}),cut=Date.now()-3*864e5;const ranked=gs.map(g=>{const hits=(h[g.key]||[]).filter(t=>t>=cut);let s=0;hits.forEach(t=>s+=Math.exp(-(Date.now()-t)/864e5));return {g,s,last:Math.max(0,...hits)}}).filter(x=>x.s>0).sort((a,b)=>b.s-a.s||b.last-a.last);let chosen=ranked.slice(0,18).map(x=>x.g);if(chosen.length<18){const seed=gs.filter(g=>g.card.dataset.trendingSeed==='true');for(const g of seed)if(!chosen.some(x=>x.key===g.key)){chosen.push(g);if(chosen.length>=18)break}}write(TCACHE,{at:Date.now(),keys:chosen.map(x=>x.key)});return new Set(chosen.map(x=>x.key))}
  function trendSetCached(){const c=read(TCACHE,{});return c.at&&Date.now()-c.at<600000&&Array.isArray(c.keys)?new Set(c.keys):trendSet()}
  function newGames(){return games().filter(g=>g.new).sort((a,b)=>((Date.parse(b.card.dataset.newSince)||0)-(Date.parse(a.card.dataset.newSince)||0)||a.title.localeCompare(b.title)))}
  function cloneCard(g,trend){const c=g.card.cloneNode(true);c.removeAttribute('onclick');const b=c.querySelector('.card-badges');if(b)b.remove();decorate(c,trend);c.addEventListener('click',()=>{recordPlay(g);g.card.click()});return c}
  function renderFeatured(){const trend=trendSetCached(),tg=document.getElementById('trendingGrid'),ng=document.getElementById('newGamesGrid');if(!tg||!ng)return;tg.innerHTML='';const gs=games();const ranked=gs.filter(g=>trend.has(g.key));let lim=window.innerWidth<=570?6:window.innerWidth<=700?9:window.innerWidth<=900?12:window.innerWidth<=1200?15:18;ranked.slice(0,lim).forEach(g=>tg.appendChild(cloneCard(g,trend)));ng.innerHTML='';newGames().slice(0,18).forEach(g=>ng.appendChild(cloneCard(g,trend)));document.getElementById('trendingSection')?.classList.toggle('is-hidden',searchBar.value.trim().length>0||activeCat!=='All Games');document.getElementById('newGamesSection')?.classList.toggle('is-hidden',searchBar.value.trim().length>0||activeCat!=='All Games')}
  function categoryFor(g){return g.card.dataset.category||inferCategory(g.title,g.card)}
  let activeCat='All Games';
  function renderCategories(){const list=document.getElementById('categoryList'),sidebar=document.getElementById('categorySidebar'),overlay=document.getElementById('categoryOverlay');if(!list||!sidebar||!overlay)return;const gs=games(),trend=trendSetCached(),counts={"All Games":gs.length,Trending:trend.size,"New Games":gs.filter(g=>g.new).length};Object.keys(RULES).forEach(c=>counts[c]=gs.filter(g=>categoryFor(g)===c).length);counts.Multiplayer=gs.filter(g=>categoryFor(g)==='Multiplayer').length;const cats=['All Games','Trending','New Games',...Object.keys(RULES).slice(0,8),'Multiplayer','Casual'];const unique=[...new Set(cats)];list.innerHTML='';unique.forEach(c=>{const b=document.createElement('button');b.type='button';b.className='category-item'+(c===activeCat?' is-active':'')+(c==='Trending'?' is-trending':'');b.innerHTML='<span class="category-item-main"><span class="category-dot"></span><span class="category-name"></span></span><span class="category-count"></span>';b.querySelector('.category-name').textContent=c;b.querySelector('.category-count').textContent=String(counts[c]||0);b.onclick=()=>{activeCat=c;applyFilters();renderCategories();document.getElementById('categorySidebar')?.classList.remove('is-open');document.getElementById('categoryOverlay')?.classList.remove('is-open');if(overlay)overlay.hidden=true;document.body.classList.remove('category-locked')};list.appendChild(b)})}
  function applyFilters(){const q=searchBar.value.trim(),gs=games(),trend=trendSetCached();gs.forEach(g=>{let show=activeCat==='All Games'||(activeCat==='Trending'?trend.has(g.key):activeCat==='New Games'?g.new:categoryFor(g)===activeCat);if(q)show=show&&norm(g.title).includes(norm(q));g.card.style.display=show?'':'none';decorate(g.card,trend)});renderFeatured();}
  function rank(t,q){const a=norm(t),b=norm(q);if(!b)return 99;if(a===b)return 0;if(a.startsWith(b))return 1;if(a.includes(b))return 2;const bw=b.split(' ').filter(Boolean);const aw=a.split(' ');return bw.length&&bw.every(x=>aw.some(y=>y.startsWith(x)||y.includes(x)))?3:99}
  function matched(q){return games().map(g=>({...g,score:rank(g.title,q)})).filter(g=>g.score<99).sort((a,b)=>a.score-b.score||a.title.localeCompare(b.title))}
  function closeSearch(){searchResults.classList.remove('is-open');searchBar.setAttribute('aria-expanded','false')}function openSearch(){searchResults.classList.add('is-open');searchBar.setAttribute('aria-expanded','true')}
  function suggestions(q){searchResults.innerHTML='';if(!q){closeSearch();return}const top=matched(q).slice(0,5);if(!top.length){searchResults.innerHTML='<div class="search-empty">No matching games yet</div>';openSearch();return}top.forEach(g=>{const b=document.createElement('button');b.type='button';b.className='search-result';b.innerHTML='<img loading="lazy" alt=""><span class="search-result-copy"><span class="search-result-title"></span><span class="search-result-label">Play game</span></span>';const i=b.querySelector('img');i.src=g.image;i.alt=g.title;b.querySelector('.search-result-title').textContent=g.title;b.onclick=()=>{searchBar.value=g.title;searchClear.style.display='inline-flex';closeSearch();recordPlay(g);g.card.click();refreshRecommendations(g.title)};searchResults.appendChild(b)});openSearch()}
  function similarity(a,b){const A=new Set(norm(a).split(' ').filter(x=>x.length>1)),B=new Set(norm(b).split(' ').filter(x=>x.length>1));if(!A.size||!B.size)return 0;let n=0;A.forEach(x=>B.has(x)&&n++);return n/Math.sqrt(A.size*B.size)}
  function recordSearch(q){q=norm(q);if(!q)return;const h=read(SEARCH,{}),x=h[q]||{count:0,last:0};x.count++;x.last=Date.now();h[q]=x;write(SEARCH,h)}
  function refreshRecommendations(q){const sec=document.getElementById('searchRecommendations'),grid=document.getElementById('searchRecommendationsGrid');if(!sec||!grid)return;if(!q){sec.classList.remove('is-visible');grid.innerHTML='';return}const gs=games(),plays=read(PLAY,{}),searches=read(SEARCH,{});const candidates=gs.map(g=>{let s=similarity(g.title,q)*.38;Object.values(searches).forEach(x=>s+=similarity(g.title,x.q||'')*(x.count||0)*.16);Object.values(plays).forEach(x=>s+=similarity(g.title,x.title||'')*Math.min(5,x.plays||1)*.09);if(categoryFor(g)===Object.values(plays).map(x=>categoryFor({title:x.title,card:{dataset:{}}}))[0])s+=.03;if(trendSetCached().has(g.key))s+=.04;return {...g,s}}).filter(g=>rank(g.title,q)>=99).sort((a,b)=>b.s-a.s||a.title.localeCompare(b.title)).slice(0,24);grid.innerHTML='';candidates.forEach(g=>{const b=document.createElement('button');b.type='button';b.className='search-recommendation';b.title=g.title;const i=document.createElement('img');i.loading='lazy';i.src=g.image;i.alt=g.title;const s=document.createElement('span');s.textContent=g.title;b.append(i,s);b.onclick=()=>{recordPlay(g);g.card.click();refreshRecommendations(q)};grid.appendChild(b)});sec.querySelector('.search-recommendations-subtitle').textContent='Similar to your search and recent games';sec.classList.add('is-visible')}
  searchBar.addEventListener('input',()=>{const q=searchBar.value.trim();searchClear.style.display=q?'inline-flex':'none';suggestions(q);clearTimeout(window.__srchTimer);window.__srchTimer=setTimeout(()=>{if(q.length>=2)recordSearch(q);refreshRecommendations(q);applyFilters()},300)});searchBar.addEventListener('focus',()=>{if(searchBar.value.trim())suggestions(searchBar.value.trim())});searchBar.addEventListener('keydown',e=>{if(e.key==='Escape')closeSearch();if(e.key==='Enter'){const a=searchResults.querySelector('.search-result.is-active');if(a){e.preventDefault();a.click()}}});searchClear.addEventListener('click',()=>{searchBar.value='';searchClear.style.display='none';closeSearch();activeCat='All Games';applyFilters();searchBar.focus()});document.addEventListener('click',e=>{if(!e.target.closest('.search-shell'))closeSearch()});
  let audioContext=null;function clickSound(){try{audioContext=audioContext||new(window.AudioContext||window.webkitAudioContext)();const n=audioContext.currentTime,m=audioContext.createGain();m.gain.setValueAtTime(.0001,n);m.gain.exponentialRampToValueAtTime(.05,n+.01);m.gain.exponentialRampToValueAtTime(.0001,n+.12);m.connect(audioContext.destination);[620,880].forEach((f,i)=>{const o=audioContext.createOscillator();const g=audioContext.createGain();o.frequency.value=f;g.gain.value=.03;o.connect(g);g.connect(audioContext.destination);o.start(n+i*.03);o.stop(n+.13+i*.03)})}catch(_){} }
  document.addEventListener('click',e=>{if(e.target.closest('button,.game-card'))clickSound()},true);document.addEventListener('click',e=>{const c=e.target.closest('#gameGrid > .game-card');if(c){const g=games().find(x=>x.card===c);if(g)recordPlay(g)}},true);
  const toggle=document.getElementById('categoryToggle'),close=document.getElementById('categoryClose'),side=document.getElementById('categorySidebar'),overlay=document.getElementById('categoryOverlay');function openCats(){side.classList.add('is-open');overlay.hidden=false;requestAnimationFrame(()=>overlay.classList.add('is-open'));side.setAttribute('aria-hidden','false');toggle.setAttribute('aria-expanded','true');document.body.classList.add('category-locked');renderCategories()}function closeCats(){side.classList.remove('is-open');overlay.classList.remove('is-open');side.setAttribute('aria-hidden','true');toggle.setAttribute('aria-expanded','false');document.body.classList.remove('category-locked');setTimeout(()=>{overlay.hidden=true},220)}toggle?.addEventListener('click',openCats);close?.addEventListener('click',closeCats);overlay?.addEventListener('click',closeCats);document.addEventListener('keydown',e=>{if(e.key==='Escape'&&side?.classList.contains('is-open'))closeCats()});
  async function loadLegacy(){try{const custom=[...gameGrid.children].filter(x=>x.classList.contains('game-card'));const r=await fetch('legacy-index.html',{cache:'no-store'});if(!r.ok)throw new Error();const d=new DOMParser().parseFromString(await r.text(),'text/html'),src=d.querySelector('#gameGrid');if(!src)throw new Error();const cards=[...src.querySelectorAll(':scope > .game-card')];gameGrid.innerHTML='';cards.forEach(c=>gameGrid.appendChild(document.importNode(c,true)));custom.forEach(c=>gameGrid.appendChild(c));loadingCard.style.display='none';applyFilters()}catch(_){loadingCard.className='error-card';loadingCard.textContent='The game library could not be loaded right now. Refresh the page to try again.'}}
  randomButton?.addEventListener('click',()=>{const pool=games().filter(g=>g.card.style.display!=='none');if(pool.length)pool[Math.floor(Math.random()*pool.length)].card.click()});reportButton?.addEventListener('click',()=>{location.href='mailto:ubg423@gmail.com?subject=UBG%20Problem%20%2F%20Game%20Suggestion'});
  let resizeTimer=0;window.addEventListener('resize',()=>{clearTimeout(resizeTimer);resizeTimer=setTimeout(()=>{applyFilters()},140)});new MutationObserver(()=>{if(gameGrid.children.length)applyFilters()}).observe(gameGrid,{childList:true});loadLegacy();
  </script>'''
    return index[:start]+js+index[end+len('  </script>'):]

def main():
    index=INDEX.read_text(encoding='utf-8')
    legacy=LEGACY.read_text(encoding='utf-8') if LEGACY.exists() else ''
    today=date.today().isoformat()
    old_registry={}
    if REGISTRY.exists():
        try:old_registry=json.loads(REGISTRY.read_text(encoding='utf-8'))
        except Exception:old_registry={}
    existing=extract_titles(legacy)|extract_titles(index)
    existing_cards=card_attrs(legacy)
    if not old_registry:
        old_registry={k:{'first_seen':None} for k in existing}
    changed_legacy=legacy
    for key,title,attrs in existing_cards:
        if key not in old_registry:
            old_registry[key]={'first_seen':today}
            if 'data-new-since=' not in attrs:
                newa=add_attrs(attrs,f' data-new-since="{today}"')
                changed_legacy=changed_legacy.replace(f'<div class="game-card"{attrs}>',f'<div class="game-card"{newa}>',1)
    zones=get_json(ZONES)
    byname={norm(strip(str(z.get('name','')))):z for z in zones if int(z.get('id',-1))>=0 and norm(strip(str(z.get('name',''))))}
    forced=[]
    for w in ['Granny',"Five Nights at Freddy's"]:
        if norm(w) in byname:forced.append(byname[norm(w)])
    candidates=forced+[z for z in zones if int(z.get('id',-1))>=0 and norm(strip(str(z.get('name','')))) not in existing and z not in forced]
    seen=set(existing); candidates2=[]
    for z in candidates:
        name=strip(str(z.get('name','')));k=norm(name);u=game_url(z);c=cover_url(z)
        if not name or not u.startswith(('http://','https://')) or not c.startswith(('http://','https://')) or k in seen:continue
        if k.startswith('suggest games'):continue
        seen.add(k);candidates2.append((name,u,c))
        if len(candidates2)>=1450:break
    verified=[]
    with ThreadPoolExecutor(max_workers=56) as ex:
        futs={ex.submit(lambda x:(probe(x[1],'html') and probe(x[2],'image')),it):it for it in candidates2}
        for f in as_completed(futs):
            it=futs[f]
            try:
                if f.result():verified.append(it)
            except Exception:pass
    vmap={norm(x[0]):x for x in verified}
    for w in ['Granny',"Five Nights at Freddy's"]:
        if norm(w) in byname and norm(w) not in vmap and norm(w) not in existing:raise SystemExit(f'{w} failed page/image verification')
    old_auto=[]
    if START in changed_legacy and END in changed_legacy:
        s,e=changed_legacy.index(START),changed_legacy.index(END)
        old_auto=card_attrs(changed_legacy[s:e])
    auto_keys={x[0] for x in old_auto}
    # Keep the previous generated library and only fill it to TARGET with newly verified games.
    keep=[]
    for key,title,attrs in old_auto:
        im=re.search(r'<img[^>]+src="([^"]+)"',changed_legacy[changed_legacy.find(f'<h3>{title}</h3>')-500:changed_legacy.find(f'<h3>{title}</h3>')+20] if f'<h3>{title}</h3>' in changed_legacy else '')
        url=re.search(r'onclick="openGame\(\'([^\']+)\'\)"',attrs)
        # safer parse from full card below
    pattern=re.compile(r'<div class="game-card"(?P<a>[^>]*)>\s*<img[^>]+src="(?P<img>[^"]+)"[^>]*>\s*<h3>(?P<t>.*?)</h3>\s*</div>',re.I|re.S)
    if START in changed_legacy and END in changed_legacy:
        s,e=changed_legacy.index(START),changed_legacy.index(END)
        segment=changed_legacy[s:e]
        for m in pattern.finditer(segment):
            a=m.group('a');name=strip(m.group('t'));src=m.group('img');onclick=re.search(r'onclick="openGame\(\'([^\']+)\'\)"',a)
            if onclick:keep.append((name,onclick.group(1),src,'true' in a and 'data-local-multiplayer' in a,old_registry.get(norm(name),{}).get('first_seen')))
    need=max(0,TARGET-len(keep));new=verified[:need]
    combined=keep.copy()
    if new:
        # Inspect enough pages to verify local-multiplayer classification on the finished library.
        flags={}
        with ThreadPoolExecutor(max_workers=40) as ex:
            futs={ex.submit(page_text,u):(n,u,c) for n,u,c in new}
            for f in as_completed(futs):
                n,u,c=futs[f];flags[norm(n)]=local_mp(n,f.result())
        combined += [(n,u,c,flags.get(norm(n),False),today) for n,u,c in new]
    if len(combined)<1000:raise SystemExit(f'Only {len(combined)} verified games available; refusing incomplete library')
    # Re-check/identify local multiplayer over the complete auto library, preserving prior verified flags.
    local_count=sum(1 for x in combined if x[3])
    if local_count<100:raise SystemExit(f'Only {local_count} same-device multiplayer games verified')
    cards=[]
    for i,(n,u,c,local,first_seen) in enumerate(combined):
        fs=first_seen or old_registry.get(norm(n),{}).get('first_seen') or today
        old_registry.setdefault(norm(n),{'first_seen':fs})
        cards.append(render_card(n,u,c,local,fs,seed=i<18))
    block=START+'\n'+'\n'.join(cards)+'\n'+END
    if START in changed_legacy and END in changed_legacy:
        a,b=changed_legacy.index(START),changed_legacy.index(END)+len(END);changed_legacy=changed_legacy[:a]+block+changed_legacy[b:]
    else:
        raise SystemExit('game marker anchors not found')
    # Patch the homepage UI/JS every run so manual game additions are automatically categorized too.
    index=inject_index(index)
    LEGACY.write_text(changed_legacy,encoding='utf-8');INDEX.write_text(index,encoding='utf-8');REGISTRY.parent.mkdir(parents=True,exist_ok=True);REGISTRY.write_text(json.dumps(old_registry,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(f'FINAL VERIFIED BUILD: {len(combined)} games; {local_count} same-device multiplayer; Granny and FNAF included; runtime categories, trending, new-game tags and personalized recommendations enabled.')

if __name__=='__main__':main()
