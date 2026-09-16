from pathlib import Path
import re

FILES=[Path('index.html'),Path('legacy-index.html')]
TITLE='UBG43 - 1000+ Unblocked Games'
DESCRIPTION='UBG43 - play 1000+ unblocked games online with fast search, game categories, trending games, new releases and personalized recommendations.'
REPORT_URL='https://forms.gle/zXYtnxwXhGvXmBrq9'

CSS=r'''<style id="ubg43-hotfix-style">
.search-shell input[type="search"]::-webkit-search-cancel-button,.search-shell input[type="search"]::-webkit-search-decoration{-webkit-appearance:none;appearance:none;display:none}
.search-shell input[type="search"]::-moz-search-cancel-button{display:none}
.search-shell input{padding-right:48px!important}
.search-clear{right:8px!important;top:50%!important;transform:translateY(-50%)!important;width:32px!important;height:32px!important;margin:0!important;display:none;align-items:center;justify-content:center;line-height:1!important;border-radius:9px!important;font-size:22px!important;font-weight:800!important;background:transparent!important;color:#64748b!important;z-index:10}
.search-clear:hover{background:#eef3fb!important;color:#0f2d66!important}.search-clear:active{transform:translateY(-50%) scale(.91)!important}
body{overflow-x:hidden!important}.site-header{position:sticky!important;top:0!important;z-index:1000!important}
.hero,.hero-copy{color:#fff!important;position:relative!important;z-index:2!important}.hero h1,.hero-copy h1,.hero p,.hero-copy p,.hero-copy .hero-stat{color:inherit!important}
.hero-copy p{color:rgba(255,255,255,.78)!important}.hero-copy .hero-stat{color:#fff!important}
.v3-strip{position:relative!important;width:100%!important;display:block!important;clear:both!important;box-sizing:border-box!important;padding:14px 22px 6px!important;z-index:2!important}
.v3-head{display:flex!important;align-items:flex-end!important;justify-content:space-between!important;gap:12px!important;margin:0 0 10px!important}.v3-title{color:#fff!important}.v3-sub{color:rgba(255,255,255,.68)!important}
.v3-carousel{display:grid!important;grid-template-rows:repeat(2,minmax(0,1fr))!important;grid-auto-flow:column!important;grid-auto-columns:clamp(170px,15.8vw,250px)!important;gap:12px!important;align-items:stretch!important;overflow-x:auto!important;overflow-y:hidden!important;width:100%!important;min-height:216px!important;padding:4px 4px 8px!important;scrollbar-width:none!important;overscroll-behavior-x:contain!important;touch-action:pan-x!important;scroll-snap-type:x proximity!important}
.v3-carousel::-webkit-scrollbar{display:none}.v3-carousel .game-card{display:block!important;width:auto!important;min-width:0!important;height:auto!important;min-height:0!important;margin:0!important;overflow:hidden!important;scroll-snap-align:start!important;background:#fff!important;color:#17213a!important}
.v3-carousel .game-card img{display:block!important;width:100%!important;height:108px!important;object-fit:cover!important}.v3-carousel .game-card h3{margin:9px 8px 12px!important;font-size:12px!important;color:#17213a!important;text-align:center!important}
.v3-carousel .v3-done{min-width:170px!important;min-height:100%!important;box-sizing:border-box!important}
.v3-ribbon-wrap{position:absolute!important;left:8px!important;top:8px!important;z-index:20!important;display:flex!important;flex-direction:column!important;align-items:flex-start!important;gap:4px!important;pointer-events:none!important}
.v3-ribbon{height:22px!important;min-height:22px!important;padding:0 9px!important;display:inline-flex!important;align-items:center!important;justify-content:center!important;border-radius:6px 8px 8px 6px!important;font:900 9px/1 Arial,sans-serif!important;letter-spacing:.055em!important;box-shadow:0 4px 10px #0003!important;white-space:nowrap!important;position:relative!important}
.v3-ribbon.new{background:#e52525!important;color:#ffe600!important}.v3-ribbon.trending{background:#ffe600!important;color:#c51f1f!important}
.card-ribbons{display:none!important}
.game-card{position:relative!important;isolation:isolate!important;backface-visibility:hidden!important;-webkit-backface-visibility:hidden!important;transform:translateZ(0)!important;will-change:transform,box-shadow!important;transition:transform .16s ease,box-shadow .16s ease,filter .16s ease!important}
@media (hover:hover){.game-card:hover{transform:translate3d(0,-4px,0)!important;box-shadow:0 15px 30px #00132d44!important;filter:saturate(1.035)}.game-card:hover img{filter:brightness(1.03)!important}.game-card:active{transform:translate3d(0,-1px,0) scale(.988)!important}}
button,.action,.cat-btn,.v3-arrow,.category-item,.search-result,.result{transition:transform .14s ease,box-shadow .16s ease,background-color .16s ease,filter .16s ease!important}
@media(hover:hover){button:hover,.action:hover,.cat-btn:hover,.v3-arrow:hover,.category-item:hover{filter:brightness(1.06)!important;box-shadow:0 9px 20px #001b5a2c!important}}
button:active,.action:active,.cat-btn:active,.v3-arrow:active,.category-item:active,.search-result:active,.result:active{transform:translateY(1px) scale(.975)!important}
button:focus-visible,.action:focus-visible,.cat-btn:focus-visible,.v3-arrow:focus-visible,.category-item:focus-visible,.search-result:focus-visible{outline:3px solid #ffffff80!important;outline-offset:2px!important}
#status{display:block!important;margin:0 20px 2px!important;padding:0 0 6px!important;color:#ffffff9c!important;font-size:12px!important;font-weight:750!important;min-height:22px}
.search-page{margin:0 22px 6px;padding:16px 18px;border:1px solid rgba(255,255,255,.12);border-radius:16px;background:linear-gradient(135deg,rgba(255,255,255,.08),rgba(37,109,255,.08));box-shadow:0 10px 28px rgba(0,0,0,.14)}
.search-page h2{margin:0;color:#fff;font-size:24px;font-weight:900}.search-page p{margin:5px 0 0;color:rgba(255,255,255,.70);font-size:13px}
body.ubg43-search-active .hero-copy,body.ubg43-search-active .hero{display:none!important}
@media(max-width:600px){.v3-strip{padding-left:14px!important;padding-right:14px!important}.v3-carousel{grid-auto-columns:calc((100vw - 40px)/2)!important;min-height:210px!important}#status{margin-left:14px!important;margin-right:14px!important}.search-page{margin-left:14px!important;margin-right:14px!important}}
</style>'''

JS=r'''<script id="ubg43-hotfix-runtime">(()=>{
'use strict';
const $=id=>document.getElementById(id),grid=$('gameGrid');if(!grid)return;
const search=$('searchBar'),clear=$('searchClear'),status=$('status'),report=$('reportGameButton');
const norm=s=>String(s||'').toLowerCase().replace(/[^a-z0-9]+/g,' ').trim();
function allCards(){return [...grid.querySelectorAll(':scope > .game-card')]}
function visibleCards(){return allCards().filter(c=>getComputedStyle(c).display!=='none'&&c.getAttribute('aria-hidden')!=='true')}
function syncStatus(){if(!status)return;const q=norm(search?.value||'');const v=visibleCards().length;status.textContent=q?(v?`Showing ${v} matching game${v===1?'':'s'}`:'No games matched your search.'):`${allCards().length} games loaded`}
function directUrl(c){const a=c.getAttribute('onclick')||'';let m=a.match(/openGame\(\s*['"]([^'"]+)['"]/);if(m)return m[1];m=a.match(/window\.open\(\s*['"]([^'"]+)['"]/);return m?m[1]:''}
function launch(c,e){const u=directUrl(c);if(!u)return;e.preventDefault();e.stopImmediatePropagation();const w=window.open(u,'_blank','noopener,noreferrer');if(!w)location.href=u}
document.addEventListener('click',e=>{const c=e.target.closest('.game-card');if(c&&c.closest('#gameGrid'))launch(c,e)},true);
function moveLayout(){const header=document.querySelector('.site-header')||document.querySelector('header');if(header&&header.parentNode===document.body&&document.body.firstElementChild!==header)document.body.insertBefore(header,document.body.firstElementChild);const hero=document.querySelector('.hero')||document.getElementById('v3Hero');const main=grid.closest('main')||document.querySelector('main')||document.body;if(hero&&hero.parentNode!==main)main.insertBefore(hero,main.firstChild);['v3Trending','v3New','v3Recommendations'].forEach(id=>{const s=$(id);if(!s)return;s.style.display=s.classList.contains('is-hidden')?'none':'block';if(s.parentNode!==main)main.insertBefore(s,grid)});document.querySelectorAll('section.featured').forEach(s=>s.remove())}
function badge(c,text,kind){let w=c.querySelector('.v3-ribbon-wrap');if(!w){w=document.createElement('div');w.className='v3-ribbon-wrap';c.appendChild(w)}if([...w.children].some(x=>x.textContent===text))return;const b=document.createElement('span');b.className='v3-ribbon '+kind;b.textContent=text;w.appendChild(b)}
function normalizeRail(id,kind){const rail=$(id);if(!rail)return;const car=rail.querySelector('.v3-carousel');if(!car)return;car.style.display='grid';car.style.gridTemplateRows='repeat(2,minmax(0,1fr))';car.style.gridAutoFlow='column';car.style.gridAutoColumns=innerWidth<600?'calc((100vw - 40px)/2)':'clamp(170px,15.8vw,250px)';car.style.gap='12px';car.style.overflowX='auto';car.style.overflowY='hidden';car.style.minHeight='216px';car.querySelectorAll('.game-card').forEach(c=>{c.style.display='block';c.style.width='auto';c.style.minWidth='0';c.style.height='auto';c.style.margin='0';if(kind==='new')badge(c,'NEW','new');if(kind==='trend')badge(c,'TRENDING','trending')});let done=car.querySelector('.v3-done');if(!done){done=document.createElement('div');done.className='v3-done';done.innerHTML='<span>That’s all for now ✨<small>More games are added automatically.</small></span>';car.appendChild(done)}}
function normalize(){moveLayout();decorateLegacy();normalizeRail('v3Trending','trend');normalizeRail('v3New','new');normalizeRail('v3Recommendations','recommend');syncStatus()}
function decorateLegacy(){allCards().forEach(c=>{const old=c.querySelector('.card-ribbons');const v=c.querySelector('.v3-ribbon-wrap');if(old)old.remove();if(v)return;const isNew=c.dataset.new==='1'||!!c.dataset.newSince;const isTrend=c.dataset.seed==='1';if(isNew)badge(c,'NEW','new');if(isTrend)badge(c,'TRENDING','trending')})}
function showSearchPage(q){q=norm(q);if(!q){clearSearch();return}document.body.classList.add('ubg43-search-active');let panel=$('ubg43SearchPage');if(!panel){panel=document.createElement('section');panel.id='ubg43SearchPage';panel.className='search-page';const anchor=document.querySelector('.v3Trending')||grid;anchor.parentNode.insertBefore(panel,anchor)}const hits=allCards().filter(c=>norm(c.querySelector('h3')?.textContent||c.querySelector('img')?.alt||'').includes(q));allCards().forEach(c=>c.style.display=hits.includes(c)?'block':'none');panel.innerHTML=`<h2>Search results</h2><p>Showing ${hits.length} game${hits.length===1?'':'s'} for “${q.replace(/[&<>]/g,'')}”. Trending and New Games stay available below.</p>`;const rec=$('v3Recommendations');if(rec){rec.style.display='block';rec.classList.remove('is-hidden')}syncStatus();panel.scrollIntoView({behavior:'smooth',block:'start'});}
function clearSearch(){allCards().forEach(c=>c.style.display='');document.body.classList.remove('ubg43-search-active');$('ubg43SearchPage')?.remove();const rec=$('v3Recommendations');if(rec)rec.remove();syncStatus()}
if(report)report.addEventListener('click',e=>{e.preventDefault();e.stopImmediatePropagation();window.location.href=REPORT_URL},true);
if(search){search.addEventListener('input',()=>{setTimeout(()=>{if(!norm(search.value))clearSearch();else{allCards().forEach(c=>c.style.display='');document.body.classList.remove('ubg43-search-active');$('ubg43SearchPage')?.remove();const rec=$('v3Recommendations');if(rec)rec.remove()}syncStatus()},40)});search.addEventListener('change',()=>setTimeout(syncStatus,30));search.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();e.stopImmediatePropagation();setTimeout(()=>showSearchPage(search.value),45)}if(e.key==='Escape'){e.preventDefault();search.value='';clearSearch()}} ,true)}
if(clear)clear.addEventListener('click',()=>setTimeout(clearSearch,40),true);
new MutationObserver(()=>normalize()).observe(document.body,{childList:true,subtree:true});
window.addEventListener('resize',()=>{normalizeRail('v3Trending','trend');normalizeRail('v3New','new');normalizeRail('v3Recommendations','recommend')});
setTimeout(normalize,50);setTimeout(normalize,400);setTimeout(normalize,1200);setTimeout(normalize,2500);
})();</script>'''

def patch(text):
    old="const rows=zones.filter(x=>Number(x.id)>=0).slice(0,1400);for(const x of rows){const url=String(x.url||'').replace('{HTML_URL}','https://raw.githubusercontent.com/gn-math/html/main');const image=String(x.cover||'').replace('{COVER_URL}','https://raw.githubusercontent.com/gn-math/covers/main');addGame({name:x.name,url,image,text:x.name,new:true,seed:all.length<18},seen)}"
    new="const rows=zones.filter(x=>Number(x.id)>=0&&x.url&&x.cover).slice(0,1400);for(let p=0;p<rows.length;p+=24){await Promise.all(rows.slice(p,p+24).map(async x=>{const url=String(x.url||'').replace('{HTML_URL}','https://raw.githubusercontent.com/gn-math/html/main');const image=String(x.cover||'').replace('{COVER_URL}','https://raw.githubusercontent.com/gn-math/covers/main');let ok=false;try{let r=await fetch(url,{method:'HEAD',cache:'force-cache',redirect:'follow'});ok=r.ok;if(!ok&&r.status===405){r=await fetch(url,{cache:'force-cache',redirect:'follow'});ok=r.ok}}catch(_){}if(ok)addGame({name:x.name,url,image,text:x.name,new:true,seed:all.length<18},seen)}))}"
    text=text.replace(old,new,1)
    text=re.sub(r'\s*<style id="ubg43-hotfix-style">.*?</style>\s*','\n',text,count=1,flags=re.S)
    text=re.sub(r'\s*<script id="ubg43-hotfix-runtime">.*?</script>\s*','\n',text,count=1,flags=re.S)
    text=re.sub(r'\s*<script id="ubg43-runtime-game-safety">.*?</script>\s*','\n',text,count=1,flags=re.S)
    text=re.sub(r'<title>.*?</title>',f'<title>{TITLE}</title>',text,count=1,flags=re.I|re.S)
    meta=f'<meta name="description" content="{DESCRIPTION}">'
    if re.search(r'<meta\s+name="description"\s+content="[^"]*"\s*/?>',text,re.I):text=re.sub(r'<meta\s+name="description"\s+content="[^"]*"\s*/?>',meta,text,count=1,flags=re.I)
    else:text=text.replace('</head>',meta+'\n</head>',1)
    text=re.sub(r'\s*<section\s+class="featured">\s*<h2>Trending Now</h2>\s*<div[^>]+id="trendingStrip"[^>]*>.*?</div>\s*</section>\s*','\n',text,count=1,flags=re.I|re.S)
    text=re.sub(r'\s*<section\s+class="featured">\s*<h2>New Games</h2>\s*<div[^>]+id="newStrip"[^>]*>.*?</div>\s*</section>\s*','\n',text,count=1,flags=re.I|re.S)
    text=re.sub(r'\s*<section\s+id="v3Trending"[^>]*>.*?</section>\s*','\n',text,count=1,flags=re.I|re.S)
    text=re.sub(r'\s*<section\s+id="v3New"[^>]*>.*?</section>\s*','\n',text,count=1,flags=re.I|re.S)
    pos=text.lower().rfind('</head>');text=text[:pos]+CSS+'\n'+text[pos:] if pos!=-1 else CSS+text
    pos=text.lower().rfind('</body>');text=text[:pos]+JS+'\n'+text[pos:] if pos!=-1 else text+JS
    return text

for p in FILES:
    if p.exists():
        src=p.read_text(encoding='utf-8')
        p.write_text(patch(src),encoding='utf-8')
        print('UBG43 HOTFIX:',p)
