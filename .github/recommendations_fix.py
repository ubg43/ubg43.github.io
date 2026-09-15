from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

# Disable the older random recommendation renderer so the personalized system is the single source of truth.
start=s.find('  function renderRecommendations(query){')
if start < 0:
    raise SystemExit('old renderRecommendations not found')
end=s.find('\n\n  searchBar.addEventListener', start)
if end < 0:
    raise SystemExit('searchBar listener anchor not found')
s=s[:start] + '  function renderRecommendations(query){}' + s[end:]

# Replace the old personalized carousel style with a real two-row horizontal track and bidirectional controls.
style_start=s.find('<style id="personalized-recommendation-style">')
if style_start < 0:
    raise SystemExit('recommendation style not found')
style_end=s.find('</style>', style_start)
if style_end < 0:
    raise SystemExit('recommendation style end not found')
new_style='''<style id="personalized-recommendation-style">\n  .search-recommendations-header{align-items:center;position:relative}\n  .recommendation-controls{display:flex;align-items:center;gap:7px}\n  .recommendation-arrow{width:34px;height:34px;flex:0 0 34px;border:1px solid rgba(255,255,255,.34);border-radius:10px;background:rgba(0,54,150,.84);color:#fff;display:inline-flex;align-items:center;justify-content:center;cursor:pointer;font-size:20px;line-height:1;box-shadow:0 5px 15px rgba(0,15,55,.2);transition:transform .16s ease,background .16s ease,box-shadow .16s ease,opacity .16s ease}\n  .recommendation-arrow:hover:not(:disabled){transform:translateY(-1px) scale(1.05);background:rgba(0,64,170,.95);box-shadow:0 8px 19px rgba(0,15,55,.28)}\n  .recommendation-arrow:active:not(:disabled){transform:scale(.96)}\n  .recommendation-arrow:disabled{opacity:.35;cursor:default}\n  .recommendation-track{display:grid!important;grid-template-rows:repeat(2,minmax(0,1fr));grid-auto-flow:column;grid-auto-columns:calc((100% - 39px)/4);grid-template-columns:none!important;gap:13px;overflow-x:auto;overflow-y:hidden;width:100%;scroll-behavior:smooth;scrollbar-width:none;padding:2px 2px 5px}\n  .recommendation-track::-webkit-scrollbar{display:none}\n  .recommendation-track .search-recommendation{width:100%;min-width:0;height:100%}\n  @media(max-width:900px){.recommendation-track{grid-auto-columns:calc((100% - 26px)/3)}.recommendation-arrow{width:32px;height:32px;flex-basis:32px}}\n  @media(max-width:570px){.recommendation-track{grid-auto-columns:calc((100% - 13px)/2)}.recommendation-arrow{width:31px;height:31px;flex-basis:31px}}\n</style>'''
s=s[:style_start] + new_style + s[style_end+8:]

# Replace the previous personalized IIFE entirely.
iife_start=s.find('  /* Personalized recommendation carousel */')
if iife_start < 0:
    raise SystemExit('personalized IIFE start not found')
iife_end=s.find('\n  </script>', iife_start)
if iife_end < 0:
    raise SystemExit('script end not found')
new_iife=r'''  /* Personalized recommendation carousel */
  (function(){
    const recSection=document.getElementById('searchRecommendations');
    const recGrid=document.getElementById('searchRecommendationsGrid');
    const gameGridEl=document.getElementById('gameGrid');
    const searchInput=document.getElementById('searchBar');
    const recHeader=recSection?.querySelector('.search-recommendations-header');
    if(!recSection||!recGrid||!gameGridEl||!searchInput||!recHeader)return;

    const PLAY_KEY='ubg_play_history_v2';
    const SEARCH_KEY='ubg_search_history_v1';
    const LIMIT=100;
    const STOP=new Set(['the','and','for','with','game','games','play','new','online','3d','io','html','html5','a']);
    const norm=s=>(s||'').toString().toLowerCase().replace(/[^a-z0-9\s]/g,' ').replace(/\s+/g,' ').trim();
    const tokens=s=>norm(s).split(' ').filter(x=>x.length>1&&!STOP.has(x));
    const key=g=>norm(g.title)+'|'+(g.image||'');

    function read(keyName){try{return JSON.parse(localStorage.getItem(keyName)||'{}')||{};}catch(_){return {};}}
    function write(keyName,value){try{localStorage.setItem(keyName,JSON.stringify(value));}catch(_){} }
    function games(){
      return Array.from(gameGridEl.querySelectorAll(':scope > .game-card')).map(card=>{
        const img=card.querySelector('img');
        return {card,title:(card.querySelector('h3')?.textContent||img?.alt||'Game').trim(),image:img?.currentSrc||img?.src||''};
      }).filter(g=>g.title).map(g=>({...g,key:key(g)}));
    }
    function overlap(a,b){
      const A=new Set(tokens(a)),B=new Set(tokens(b));
      if(!A.size||!B.size)return 0;
      let hit=0;A.forEach(x=>{if(B.has(x))hit++;});
      return hit/Math.sqrt(A.size*B.size);
    }
    function recordSearch(query){
      const q=norm(query);if(!q)return;
      const h=read(SEARCH_KEY);const item=h[q]||{count:0,last:0,tokens:tokens(q)};
      item.count++;item.last=Date.now();item.tokens=tokens(q);h[q]=item;
      const entries=Object.entries(h).sort((a,b)=>(b[1].last||0)-(a[1].last||0)).slice(0,50);
      write(SEARCH_KEY,Object.fromEntries(entries));
    }
    function recordPlay(game){
      if(!game?.title)return;
      const h=read(PLAY_KEY);const k=game.key;const item=h[k]||{title:game.title,image:game.image,plays:0,lastPlayed:0,tokens:tokens(game.title)};
      item.title=game.title;item.image=game.image;item.plays++;item.lastPlayed=Date.now();item.tokens=tokens(game.title);h[k]=item;
      const entries=Object.entries(h).sort((a,b)=>(b[1].lastPlayed||0)-(a[1].lastPlayed||0)).slice(0,LIMIT);
      write(PLAY_KEY,Object.fromEntries(entries));
    }

    let page=0,pageCount=1,currentItems=[];
    function visibleCount(){return window.innerWidth<=570?2:(window.innerWidth<=900?3:4);}
    function pageSize(){return visibleCount()*2;}
    function buildControls(){
      if(recHeader.querySelector('.recommendation-controls'))return;
      const wrap=document.createElement('div');wrap.className='recommendation-controls';
      const left=document.createElement('button');left.type='button';left.className='recommendation-arrow';left.id='recommendationPrev';left.setAttribute('aria-label','Previous recommendations');left.textContent='←';
      const right=document.createElement('button');right.type='button';right.className='recommendation-arrow';right.id='recommendationNext';right.setAttribute('aria-label','More recommendations');right.textContent='→';
      wrap.append(left,right);recHeader.appendChild(wrap);
      left.addEventListener('click',()=>goToPage(page-1));
      right.addEventListener('click',()=>goToPage(page+1));
    }
    function paintControls(){
      const prev=document.getElementById('recommendationPrev'),next=document.getElementById('recommendationNext');
      if(!prev||!next)return;
      prev.disabled=page<=0;next.disabled=page>=pageCount-1;
      const enough=currentItems.length>pageSize();
      prev.style.display=enough?'inline-flex':'none';next.style.display=enough?'inline-flex':'none';
    }
    function goToPage(target){
      page=Math.max(0,Math.min(pageCount-1,target));
      recGrid.scrollTo({left:page*recGrid.clientWidth,behavior:'smooth'});
      paintControls();
    }
    function score(game,query,plays,searches){
      const qScore=overlap(game.title,query);
      let playScore=0,recentScore=0;
      const playEntries=Object.values(plays);
      const totalPlays=playEntries.reduce((n,x)=>n+(x.plays||0),0);
      if(totalPlays){
        let raw=0;
        playEntries.forEach(item=>{raw+=overlap(game.title,item.title)*Math.sqrt(item.plays||0);});
        playScore=Math.min(1,raw/Math.max(1,totalPlays));
        let recent=0;
        playEntries.forEach(item=>{const sim=overlap(game.title,item.title);if(sim){const age=(Date.now()-(item.lastPlayed||0))/86400000;recent+=sim*(item.plays||0)*Math.exp(-Math.max(0,age)/21);}});
        recentScore=Math.min(1,recent/Math.max(1,totalPlays));
      }
      let searchScore=0;
      const searchEntries=Object.values(searches);
      const totalSearches=searchEntries.reduce((n,x)=>n+(x.count||0),0);
      if(totalSearches){
        let raw=0;searchEntries.forEach(item=>raw+=overlap(game.title,(item.tokens||[]).join(' '))*(item.count||0));
        searchScore=Math.min(1,raw/Math.max(1,totalSearches));
      }
      const alreadyPlayed=plays[game.key]?.plays||0;
      const exploration=1/Math.sqrt(1+alreadyPlayed);
      return qScore*.28+playScore*.34+searchScore*.23+recentScore*.10+exploration*.05;
    }
    function render(query){
      const gs=games();
      if(!query||!gs.length){recSection.classList.remove('is-visible');recGrid.innerHTML='';currentItems=[];page=0;pageCount=1;paintControls();return;}
      buildControls();
      const plays=read(PLAY_KEY),searches=read(SEARCH_KEY);
      currentItems=gs.map(g=>({...g,score:score(g,query,plays,searches),played:!!plays[g.key]})).sort((a,b)=>b.score-a.score||a.title.localeCompare(b.title));
      const topKeys=new Set((typeof matched==='function'?matched(query):[]).slice(0,5).map(g=>key(g)));
      const filtered=currentItems.filter(g=>!topKeys.has(g.key));
      currentItems=filtered.length?filtered:currentItems.filter(g=>!topKeys.has(g.key)).slice(0,1);
      recGrid.innerHTML='';
      currentItems.slice(0,32).forEach(game=>{
        const button=document.createElement('button');button.type='button';button.className='search-recommendation';
        const img=document.createElement('img');img.loading='lazy';img.src=game.image;img.alt=game.title;
        const span=document.createElement('span');span.textContent=game.title;button.append(img,span);
        button.addEventListener('click',()=>{clickSound();game.card.click();recordPlay(game);});
        recGrid.appendChild(button);
      });
      page=0;pageCount=Math.max(1,Math.ceil(currentItems.length/pageSize()));
      recGrid.scrollLeft=0;recSection.classList.add('is-visible');paintControls();
    }

    document.addEventListener('click',event=>{
      const card=event.target.closest('#gameGrid > .game-card');
      if(card){
        const game=games().find(g=>g.card===card);if(game)recordPlay(game);
      }
    },true);
    let lastQuery='';let timer=0;
    const refresh=()=>{
      const q=searchInput.value.trim();
      if(q===lastQuery){paintControls();return;}
      lastQuery=q;
      if(q)recordSearch(q);
      render(q);
    };
    searchInput.addEventListener('input',()=>{lastQuery='';clearTimeout(timer);timer=setTimeout(refresh,80);});
    searchInput.addEventListener('change',refresh);
    window.addEventListener('resize',()=>{const old=page;page=0;pageCount=Math.max(1,Math.ceil(currentItems.length/pageSize()));goToPage(Math.min(old,pageCount-1));});
    new MutationObserver(()=>{if(searchInput.value.trim())render(searchInput.value.trim());}).observe(gameGridEl,{childList:true});
    refresh();
  })();
'''
s=s[:iife_start]+new_iife+s[iife_end:]
p.write_text(s,encoding='utf-8')
