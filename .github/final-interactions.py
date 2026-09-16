from pathlib import Path
import re

FILES=[Path('index.html'),Path('legacy-index.html')]
REPORT_URL='https://forms.gle/zXYtnxwXhGvXmBrq9'

CSS=r'''<style id="ubg43-final-interactions-style">
.search-page{margin:0 22px 10px;padding:18px 20px;border:1px solid rgba(255,255,255,.14);border-radius:16px;background:linear-gradient(135deg,rgba(255,255,255,.09),rgba(37,109,255,.10));box-shadow:0 12px 30px rgba(0,0,0,.16)}
.search-page h2{margin:0;color:#fff;font-size:24px;font-weight:900}.search-page p{margin:6px 0 0;color:rgba(255,255,255,.72);font-size:13px;line-height:1.45}
body.ubg43-search-active .hero,body.ubg43-search-active .hero-copy{display:none!important}
body.ubg43-search-active #gameGrid{scroll-margin-top:90px}
@media(max-width:600px){.search-page{margin-left:14px;margin-right:14px;padding:15px 16px}}
</style>'''

JS=r'''<script id="ubg43-final-interactions-runtime">(()=>{
'use strict';
const $=id=>document.getElementById(id),grid=$('gameGrid'),search=$('searchBar'),clear=$('searchClear'),status=$('status');
if(!grid||!search)return;
const norm=s=>String(s||'').toLowerCase().replace(/[^a-z0-9]+/g,' ').trim();
let searchMode=false;
function cards(){return [...grid.querySelectorAll(':scope > .game-card')]}
function title(c){return (c.querySelector('h3')?.textContent||c.querySelector('img')?.alt||'Game').trim()}
function syncStatus(){if(!status)return;const q=norm(search.value);const n=cards().filter(c=>getComputedStyle(c).display!=='none').length;status.textContent=searchMode?(n?`Showing ${n} matching game${n===1?'':'s'}`:'No games matched your search.'):`${cards().length} games loaded`}
function orderSearch(){if(!searchMode)return;const main=grid.closest('main')||document.querySelector('main')||document.body,p=$('ubg43SearchPage'),r=$('v3Recommendations'),t=$('v3Trending'),n=$('v3New');if(p)main.insertBefore(p,grid);if(r){r.style.display='block';r.classList.remove('is-hidden');main.insertBefore(r,grid.nextSibling)}if(t)main.insertBefore(t,r?r.nextSibling:grid.nextSibling);if(n)main.insertBefore(n,t?t.nextSibling:(r?r.nextSibling:grid.nextSibling))}
function removeSearchPage(){const p=$('ubg43SearchPage');if(p)p.remove()}
function clearSearch(){searchMode=false;document.body.classList.remove('ubg43-search-active');cards().forEach(c=>c.style.display='');removeSearchPage();const r=$('v3Recommendations');if(r)r.remove();syncStatus();window.scrollTo({top:0,behavior:'smooth'})}
function showSearch(q){q=norm(q);if(!q){clearSearch();return}searchMode=true;document.body.classList.add('ubg43-search-active');let p=$('ubg43SearchPage');if(!p){p=document.createElement('section');p.id='ubg43SearchPage';p.className='search-page';(grid.closest('main')||grid.parentNode).insertBefore(p,grid)}const hits=cards().filter(c=>norm(title(c)).includes(q));cards().forEach(c=>{c.style.display=hits.includes(c)?'':'none'});p.innerHTML=`<h2>Search results</h2><p>Showing ${hits.length} game${hits.length===1?'':'s'} for “${String(q).replace(/[&<>]/g,'')}”. New Games and Trending Now stay available below.</p>`;const r=$('v3Recommendations');if(r){r.style.display='block';r.classList.remove('is-hidden')}orderSearch();syncStatus();p.scrollIntoView({behavior:'smooth',block:'start'})}
if(report=$('reportGameButton'))report.addEventListener('click',e=>{e.preventDefault();e.stopImmediatePropagation();window.location.href='https://forms.gle/zXYtnxwXhGvXmBrq9'},true);
search.addEventListener('input',()=>{setTimeout(()=>{if(!norm(search.value))clearSearch();else if(!searchMode){cards().forEach(c=>c.style.display='');const r=$('v3Recommendations');if(r)r.style.display='none'}syncStatus()},35)});
search.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();e.stopImmediatePropagation();showSearch(search.value)}else if(e.key==='Escape'){e.preventDefault();e.stopImmediatePropagation();search.value='';if(clear)clear.style.display='none';clearSearch()}},true);
if(clear)clear.addEventListener('click',e=>{e.preventDefault();e.stopImmediatePropagation();search.value='';clearSearch();search.focus()},true);
new MutationObserver(()=>{if(searchMode){orderSearch();syncStatus()}}).observe(document.body,{childList:true,subtree:true});
setTimeout(syncStatus,80);setTimeout(syncStatus,400);setTimeout(syncStatus,1200);
})();</script>'''

def patch(text):
    text=re.sub(r'\s*<style id="ubg43-final-interactions-style">.*?</style>\s*','\n',text,count=1,flags=re.S)
    text=re.sub(r'\s*<script id="ubg43-final-interactions-runtime">.*?</script>\s*','\n',text,count=1,flags=re.S)
    pos=text.lower().rfind('</head>');text=text[:pos]+CSS+'\n'+text[pos:] if pos!=-1 else CSS+text
    pos=text.lower().rfind('</body>');text=text[:pos]+JS+'\n'+text[pos:] if pos!=-1 else text+JS
    return text

for p in FILES:
    if p.exists():
        p.write_text(patch(p.read_text(encoding='utf-8')),encoding='utf-8')
        print('FINAL INTERACTIONS:',p)
