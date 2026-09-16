from pathlib import Path
import re

FILES=[Path('index.html'),Path('legacy-index.html')]
TITLE='UBG43 - 1000+ Unblocked Games'
DESCRIPTION='UBG43 - play 1000+ unblocked games online with fast search, game categories, trending games, new releases and personalized recommendations.'

CSS=r'''<style id="ubg43-hotfix-style">
/* Search: one clear control, perfectly centered, with the browser's native X disabled. */
.search-shell input[type="search"]::-webkit-search-cancel-button,.search-shell input[type="search"]::-webkit-search-decoration{-webkit-appearance:none;appearance:none;display:none}
.search-shell input[type="search"]::-moz-search-cancel-button{display:none}
.search-shell{isolation:isolate}
.search-shell input{padding-right:48px!important}
.search-clear{right:8px!important;top:50%!important;transform:translateY(-50%)!important;width:32px!important;height:32px!important;margin:0!important;display:none;align-items:center;justify-content:center;line-height:1!important;border-radius:9px!important;font-size:22px!important;font-weight:800!important;background:transparent!important;color:#64748b!important;z-index:5;transition:background .16s ease,color .16s ease,transform .12s ease,box-shadow .16s ease!important}
.search-clear:hover{background:#eef3fb!important;color:#0f2d66!important;box-shadow:0 4px 12px #001b5a22!important;transform:translateY(-50%)!important}
.search-clear:active{transform:translateY(-50%) scale(.91)!important}
.search-shell:focus-within input{box-shadow:0 0 0 3px #ffffff33,0 12px 28px #001b5a3d!important}

/* Accurate result count. */
#status{display:block!important;margin:0 20px 2px!important;padding:0 0 6px!important;color:#ffffff9c!important;font-size:12px!important;font-weight:750!important;min-height:22px}

/* Keep cards stable while still giving them a polished lift. */
.game-card{position:relative;isolation:isolate;contain:paint;backface-visibility:hidden;-webkit-backface-visibility:hidden;transform:translateZ(0);will-change:transform,box-shadow;transition:transform .18s cubic-bezier(.2,.75,.25,1),box-shadow .18s ease,filter .18s ease!important}
.game-card img{backface-visibility:hidden;-webkit-backface-visibility:hidden;transform:translateZ(0);transition:transform .22s cubic-bezier(.2,.75,.25,1),filter .22s ease!important}
.game-card h3{position:relative;z-index:2}
@media (hover:hover){.game-card:hover{transform:translate3d(0,-5px,0)!important;box-shadow:0 18px 34px #00132d4d,0 0 0 1px #ffffff20!important;filter:saturate(1.04)}.game-card:hover img{transform:translateZ(0) scale(1.035);filter:brightness(1.035)}.v3-carousel .game-card:hover{transform:translate3d(0,-4px,0)!important}.game-card:active{transform:translate3d(0,-1px,0) scale(.988)!important}}

/* Small, stable ribbons. Hide the older oversized chevrons and let the V3 ribbons be the single source of truth. */
.card-ribbons{display:none!important}
.v3-ribbon-wrap{position:absolute!important;left:8px!important;top:8px!important;z-index:7!important;display:flex!important;flex-direction:column!important;align-items:flex-start!important;gap:4px!important;pointer-events:none!important;transform:translateZ(0)!important}
.v3-ribbon{height:22px!important;min-height:22px!important;padding:0 9px!important;display:inline-flex!important;align-items:center!important;justify-content:center!important;border-radius:6px 8px 8px 6px!important;font:900 9px/1 Arial,sans-serif!important;letter-spacing:.055em!important;box-shadow:0 4px 10px #0003!important;white-space:nowrap!important;position:relative!important;transform:translateZ(0)!important}
.v3-ribbon.new{background:#e52525!important;color:#ffe600!important}.v3-ribbon.trending{background:#ffe600!important;color:#c51f1f!important}
.v3-ribbon.new::after,.v3-ribbon.trending::after{content:"";position:absolute;right:-5px;top:0;border-top:11px solid transparent;border-bottom:11px solid transparent;border-left:5px solid currentColor;opacity:.12;pointer-events:none}

/* Carousels should never flash, jump or reflow on hover. */
.v3-carousel{cursor:grab;overscroll-behavior-x:contain;touch-action:pan-x;scrollbar-width:none}
.v3-carousel:active{cursor:grabbing}
.v3-carousel .game-card{min-width:0;height:100%;overflow:hidden}
.v3-carousel .game-card,.v3-carousel .game-card img,.v3-ribbon-wrap{will-change:transform}
.v3-done{user-select:none}

/* Buttons and controls: hover glow + real press feedback + keyboard focus. */
button,.action,.cat-btn,.v3-arrow,.category-item,.search-result,.result{transition:transform .14s ease,box-shadow .16s ease,background-color .16s ease,border-color .16s ease,filter .16s ease!important}
@media (hover:hover){button:hover,.action:hover,.cat-btn:hover,.v3-arrow:hover,.category-item:hover{filter:brightness(1.06);box-shadow:0 9px 20px #001b5a2c!important}}
button:active,.action:active,.cat-btn:active,.v3-arrow:active,.category-item:active,.search-result:active,.result:active{transform:translateY(1px) scale(.975)!important;filter:brightness(.98)}
button:focus-visible,.action:focus-visible,.cat-btn:focus-visible,.v3-arrow:focus-visible,.category-item:focus-visible,.search-result:focus-visible{outline:3px solid #ffffff80!important;outline-offset:2px!important}
.v3-arrow:disabled{transform:none!important;box-shadow:none!important;filter:none!important}

/* Search suggestions also feel clickable without causing layout shifts. */
.search-result:hover,.result:hover{transform:translateX(2px)!important}

/* Mobile spacing for the count pill/label. */
@media(max-width:600px){#status{margin-left:14px!important;margin-right:14px!important}}
</style>'''

JS=r'''<script id="ubg43-hotfix-runtime">(()=>{
'use strict';
const $=id=>document.getElementById(id),grid=$('gameGrid');if(!grid)return;
const search=$('searchBar'),clear=$('searchClear'),status=$('status');
function visibleCards(){return [...grid.querySelectorAll(':scope > .game-card')].filter(c=>getComputedStyle(c).display!=='none' && c.getAttribute('aria-hidden')!=='true')}
function allCards(){return [...grid.querySelectorAll(':scope > .game-card')]}
function norm(s){return String(s||'').toLowerCase().replace(/[^a-z0-9]+/g,' ').trim()}
function titleOf(c){return (c.querySelector('h3')?.textContent||c.querySelector('img')?.alt||'Game').trim()}
function syncStatus(){if(!status)return;const q=norm(search?.value||'');const visible=visibleCards().length;const total=allCards().length;if(q){status.textContent=visible===0?'No games matched your search.':`Showing ${visible} matching game${visible===1?'':'s'}`}
else{status.textContent=`${total} games loaded`}}
function refreshSearch(){try{search?.dispatchEvent(new Event('input',{bubbles:true}))}catch(_){}setTimeout(syncStatus,40);setTimeout(syncStatus,220)}
if(search){search.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();e.stopPropagation();refreshSearch();setTimeout(()=>grid.scrollIntoView({behavior:'smooth',block:'start'}),70)}},true);search.addEventListener('input',()=>setTimeout(syncStatus,20));search.addEventListener('change',()=>setTimeout(syncStatus,20))}
if(clear){clear.addEventListener('click',e=>{e.preventDefault();e.stopPropagation();setTimeout(syncStatus,30)},true)}

/* The V3 cards get their small ribbons; this also repairs cards produced by the older builder. */
function decorateRibbons(){allCards().forEach(c=>{
  const hasV3=c.querySelector('.v3-ribbon-wrap');
  const old=c.querySelector('.card-ribbons');
  if(hasV3)return;
  const labels=[...c.querySelectorAll('.card-ribbons .ribbon')].map(x=>String(x.textContent||'').trim().toUpperCase());
  const isNew=c.dataset.new==='1'||c.dataset.newSince||labels.includes('NEW');
  const isTrending=c.dataset.seed==='1'||labels.includes('TRENDING');
  if(!isNew&&!isTrending)return;
  const wrap=document.createElement('div');wrap.className='v3-ribbon-wrap';
  if(isNew){const s=document.createElement('span');s.className='v3-ribbon new';s.textContent='NEW';wrap.appendChild(s)}
  if(isTrending){const s=document.createElement('span');s.className='v3-ribbon trending';s.textContent='TRENDING';wrap.appendChild(s)}
  c.appendChild(wrap);
  if(old)old.remove();
})}

/* Prevent the legacy iframe opener from winning the click race. */
function extractUrl(card){const a=card.getAttribute('onclick')||'',m=a.match(/openGame\(\s*['"]([^'"]+)['"](?:\s*,[^)]*)?\)/);return m?m[1]:''}
function directOpen(url){if(!url)return;const w=window.open(url,'_blank','noopener,noreferrer');if(!w)window.location.href=url}
document.addEventListener('click',e=>{const card=e.target.closest('#gameGrid > .game-card');if(!card)return;const u=extractUrl(card);if(!u)return;e.preventDefault();e.stopImmediatePropagation();directOpen(u)},true);

/* Keep the load count truthful as the runtime library changes. */
new MutationObserver(()=>{decorateRibbons();setTimeout(syncStatus,20)}).observe(grid,{childList:true});
setTimeout(()=>{decorateRibbons();syncStatus()},250);
setTimeout(()=>{decorateRibbons();syncStatus()},1000);
})();</script>'''


def patch(text):
    # Verify GN-Math candidates before they become visible cards, preserving the current dynamic loader architecture.
    old="const rows=zones.filter(x=>Number(x.id)>=0).slice(0,1400);for(const x of rows){const url=String(x.url||'').replace('{HTML_URL}','https://raw.githubusercontent.com/gn-math/html/main');const image=String(x.cover||'').replace('{COVER_URL}','https://raw.githubusercontent.com/gn-math/covers/main');addGame({name:x.name,url,image,text:x.name,new:true,seed:all.length<18},seen)}"
    new="const rows=zones.filter(x=>Number(x.id)>=0&&x.url&&x.cover).slice(0,1400);for(let p=0;p<rows.length;p+=24){await Promise.all(rows.slice(p,p+24).map(async x=>{const url=String(x.url||'').replace('{HTML_URL}','https://raw.githubusercontent.com/gn-math/html/main');const image=String(x.cover||'').replace('{COVER_URL}','https://raw.githubusercontent.com/gn-math/covers/main');let ok=false;try{let r=await fetch(url,{method:'HEAD',cache:'force-cache',redirect:'follow'});ok=r.ok;if(!ok&&r.status===405){r=await fetch(url,{cache:'force-cache',redirect:'follow'});ok=r.ok}}catch(_){}if(ok)addGame({name:x.name,url,image,text:x.name,new:true,seed:all.length<18},seen)}))}"
    text=text.replace(old,new,1)
    # Remove this layer from a previous run before inserting the final version, making the workflow idempotent.
    text=re.sub(r'\s*<style id="ubg43-hotfix-style">.*?</style>\s*','\n',text,count=1,flags=re.S)
    text=re.sub(r'\s*<script id="ubg43-hotfix-runtime">.*?</script>\s*','\n',text,count=1,flags=re.S)
    text=re.sub(r'\s*<script id="ubg43-runtime-game-safety">.*?</script>\s*','\n',text,count=1,flags=re.S)
    text=re.sub(r'<title>.*?</title>',f'<title>{TITLE}</title>',text,count=1,flags=re.I|re.S)
    meta=f'<meta name="description" content="{DESCRIPTION}">'
    if re.search(r'<meta\s+name="description"\s+content="[^"]*"\s*/?>',text,re.I):text=re.sub(r'<meta\s+name="description"\s+content="[^"]*"\s*/?>',meta,text,count=1,flags=re.I)
    else:text=text.replace('</head>',meta+'\n</head>',1)
    # Remove the old empty featured rails if they survived into a generated copy.
    text=re.sub(r'\s*<section\s+class="featured">\s*<h2>Trending Now</h2>\s*<div[^>]+id="trendingStrip"[^>]*>.*?</div>\s*</section>\s*','\n',text,count=1,flags=re.I|re.S)
    text=re.sub(r'\s*<section\s+class="featured">\s*<h2>New Games</h2>\s*<div[^>]+id="newStrip"[^>]*>.*?</div>\s*</section>\s*','\n',text,count=1,flags=re.I|re.S)
    pos=text.lower().rfind('</head>');text=text[:pos]+CSS+'\n'+text[pos:] if pos!=-1 else CSS+text
    pos=text.lower().rfind('</body>');text=text[:pos]+JS+'\n'+text[pos:] if pos!=-1 else text+JS
    return text

for p in FILES:
    if p.exists():
        src=p.read_text(encoding='utf-8')
        p.write_text(patch(src),encoding='utf-8')
        print('UBG43 HOTFIX:',p)
