from pathlib import Path
import re

FILES=[Path('index.html'),Path('legacy-index.html')]
DESCRIPTION='UBG43 - play 1000+ unblocked games online with fast search, game categories, trending games, new releases and personalized recommendations.'
TITLE='UBG43 - 1000+ Unblocked Games'

CSS=r'''<style id="ubg43-hotfix-style">
.v3-carousel{cursor:grab;overscroll-behavior-x:contain;touch-action:pan-x}.v3-carousel:active{cursor:grabbing}
.category-item{user-select:none}.category-item.is-active{background:rgba(37,109,255,.25)!important;border-color:rgba(83,148,255,.4)!important}
</style>'''

JS=r'''<script id="ubg43-hotfix-runtime">(()=>{
'use strict';
const $=id=>document.getElementById(id);
const grid=$('gameGrid');if(!grid)return;
const norm=s=>String(s||'').toLowerCase().replace(/[^a-z0-9]+/g,' ').trim();
const cards=()=>[...grid.querySelectorAll(':scope > .game-card')];
const info=c=>{const h=c.querySelector('h3'),i=c.querySelector('img');return{title:(h?.textContent||i?.alt||'Game').trim(),category:c.dataset.category||'Other',isNew:!!c.dataset.newSince||c.dataset.new==='1'}};
let active='All Games';let renderTimer=0;
function trendKeys(){try{const h=JSON.parse(localStorage.getItem('ubg43_v3_plays')||'{}');return new Set(cards().map(c=>{const g=info(c),k=norm(g.title)+'|'+(c.querySelector('img')?.getAttribute('src')||'');const x=h[k]||{};return{key:k,score:(x.plays||0)+((Date.now()-(x.last||0)<259200000)?2:0)}}).sort((a,b)=>b.score-a.score).slice(0,24).map(x=>x.key))}catch(_){return new Set()}}
function key(c){const g=info(c);return norm(g.title)+'|'+(c.querySelector('img')?.getAttribute('src')||'')}
function categoryMatch(c){const g=info(c),tr=trendKeys();return active==='All Games'||(active==='New Games'&&g.isNew)||(active==='Trending'&&tr.has(key(c)))||g.category===active}
function apply(){const q=norm($('searchBar')?.value||'');cards().forEach(c=>{const title=norm(info(c).title);c.style.display=(!q||title.includes(q))&&categoryMatch(c)?'':'none'});renderCategories()}
function closeSide(){const side=$('categorySidebar')||$('sidebar'),overlay=$('categoryOverlay')||$('overlay');if(side)side.classList.remove('is-open','open');if(overlay){overlay.classList.remove('is-open');overlay.classList.add('hidden');overlay.hidden=true}}
function openSide(){const side=$('categorySidebar')||$('sidebar'),overlay=$('categoryOverlay')||$('overlay');if(side)side.classList.add(side.id==='sidebar'?'open':'is-open');if(overlay){overlay.hidden=false;overlay.classList.remove('hidden');overlay.classList.add('is-open')}}
function renderCategories(){const list=$('categoryList')||$('catList');if(!list)return;const gs=cards(),set=new Set(['Action','Adventure','Horror','Multiplayer','Fighting','Survival','Platformer','Racing','Sports','Puzzle','Arcade','Strategy','Simulation','Casual','Anime','Rhythm & Music','Card & Board','io']);gs.forEach(c=>set.add(info(c).category));const cats=['All Games','New Games','Trending',...Array.from(set).sort()];list.innerHTML='';const tr=trendKeys();cats.forEach(cat=>{const b=document.createElement('button');b.type='button';b.className='category-item'+(active===cat?' is-active':'');b.innerHTML='<span class="category-item-main"><span class="category-dot"></span><span class="category-name"></span></span><span class="category-count"></span>';b.querySelector('.category-name').textContent=cat;let n=gs.length;if(cat==='New Games')n=gs.filter(c=>info(c).isNew).length;else if(cat==='Trending')n=tr.size;else if(cat!=='All Games')n=gs.filter(c=>info(c).category===cat).length;b.querySelector('.category-count').textContent=String(n);b.addEventListener('click',()=>{active=cat;closeSide();apply();setTimeout(()=>grid.scrollIntoView({behavior:'smooth',block:'start'}),20)});list.appendChild(b)})}
function wireCategories(){const toggle=$('categoryToggle'),close=$('categoryClose'),overlay=$('categoryOverlay')||$('overlay');if(toggle){toggle.addEventListener('click',e=>{e.preventDefault();openSide();renderCategories()})}if(close)close.addEventListener('click',e=>{e.preventDefault();closeSide()});if(overlay)overlay.addEventListener('click',closeSide);document.addEventListener('keydown',e=>{if(e.key==='Escape')closeSide()});const s=$('searchBar');if(s){s.addEventListener('input',()=>setTimeout(apply,0));s.addEventListener('change',()=>setTimeout(apply,0))}renderCategories()}
function wheel(c){c.addEventListener('wheel',e=>{if(Math.abs(e.deltaY)>Math.abs(e.deltaX)){e.preventDefault();c.scrollLeft+=e.deltaY}}, {passive:false})}
function wireScroll(){document.querySelectorAll('.v3-carousel').forEach(wheel)}
function init(){wireCategories();wireScroll();new MutationObserver(()=>{clearTimeout(renderTimer);renderTimer=setTimeout(()=>{renderCategories();wireScroll();apply()},80)}).observe(grid,{childList:true});apply();wireScroll()}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();</script>'''

def patch(text):
    text=re.sub(r'<title>.*?</title>',f'<title>{TITLE}</title>',text,count=1,flags=re.I|re.S)
    meta=f'<meta name="description" content="{DESCRIPTION}">'
    if re.search(r'<meta\s+name="description"\s+content="[^"]*"\s*/?>',text,re.I):
        text=re.sub(r'<meta\s+name="description"\s+content="[^"]*"\s*/?>',meta,text,count=1,flags=re.I)
    else:
        text=text.replace('</head>',meta+'\n</head>',1)
    text=re.sub(r'\s*<style id="ubg43-hotfix-style">.*?</style>\s*','\n',text,count=1,flags=re.S)
    text=re.sub(r'\s*<script id="ubg43-hotfix-runtime">.*?</script>\s*','\n',text,count=1,flags=re.S)
    pos=text.lower().rfind('</head>');text=text[:pos]+CSS+'\n'+text[pos:] if pos!=-1 else CSS+text
    pos=text.lower().rfind('</body>');text=text[:pos]+JS+'\n'+text[pos:] if pos!=-1 else text+JS
    return text

for p in FILES:
    if p.exists():
        src=p.read_text(encoding='utf-8');p.write_text(patch(src),encoding='utf-8');print('UBG43 HOTFIX:',p)
