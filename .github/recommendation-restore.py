from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')

start=s.find('  /* Personalized recommendation carousel */')
if start<0: raise SystemExit('recommendation block not found')
end=s.find('\n  </script>',start)
if end<0: raise SystemExit('script end not found')

block=r'''  /* Personalized recommendation carousel */
  (function(){
    const recSection=document.getElementById('searchRecommendations');
    const recGrid=document.getElementById('searchRecommendationsGrid');
    const gameGridEl=document.getElementById('gameGrid');
    const searchInput=document.getElementById('searchBar');
    const recHeader=recSection?.querySelector('.search-recommendations-header');
    if(!recSection||!recGrid||!gameGridEl||!searchInput||!recHeader)return;

    const PLAY_KEY='ubg_play_history_v3';
    const SEARCH_KEY='ubg_search_history_v2';
    const MAX_ITEMS=32;
    const STOP=new Set(['the','and','for','with','game','games','play','new','online','3d','io','html','html5','a','of','to','in','on','my','free']);
    const norm=s=>(s||'').toString().toLowerCase().replace(/[^a-z0-9\s]/g,' ').replace(/\s+/g,' ').trim();
    const tokens=s=>norm(s).split(' ').filter(x=>x.length>1&&!STOP.has(x));
    const key=g=>norm(g.title)+'|'+(g.image||'');
    const read=(k,f)=>{try{return JSON.parse(localStorage.getItem(k)||JSON.stringify(f))||f}catch(_){return f}};
    const write=(k,v)=>{try{localStorage.setItem(k,JSON.stringify(v))}catch(_){}};
    function games(){return Array.from(gameGridEl.querySelectorAll(':scope > .game-card')).map(card=>{const img=card.querySelector('img');return {card,title:(card.querySelector('h3')?.textContent||img?.alt||'Game').trim(),image:img?.currentSrc||img?.src||''}}).filter(g=>g.title).map(g=>({...g,key:key(g)}));}
    function similarity(a,b){const A=new Set(tokens(a)),B=new Set(tokens(b));if(!A.size||!B.size)return 0;let hit=0;A.forEach(t=>{if(B.has(t))hit++});return hit/Math.sqrt(A.size*B.size);}
    function recordSearch(q){q=norm(q);if(!q)return;const h=read(SEARCH_KEY,{});const x=h[q]||{count:0,last:0};x.count++;x.last=Date.now();h[q]=x;const ordered=Object.entries(h).sort((a,b)=>(b[1].last||0)-(a[1].last||0)).slice(0,80);write(SEARCH_KEY,Object.fromEntries(ordered));}
    function recordPlay(g){if(!g?.title)return;const h=read(PLAY_KEY,{});const x=h[g.key]||{title:g.title,image:g.image,plays:0,lastPlayed:0};x.title=g.title;x.image=g.image;x.plays++;x.lastPlayed=Date.now();h[g.key]=x;const ordered=Object.entries(h).sort((a,b)=>(b[1].lastPlayed||0)-(a[1].lastPlayed||0)).slice(0,120);write(PLAY_KEY,Object.fromEntries(ordered));}

    let page=0;
    function cols(){return window.innerWidth<=570?2:window.innerWidth<=900?3:4;}
    function pageSize(){return cols()*2;}
    function pages(){return Math.max(1,Math.ceil(currentItems.length/pageSize()));}
    let currentItems=[];

    function ensureControls(){
      if(recHeader.querySelector('.recommendation-controls'))return;
      const controls=document.createElement('div');controls.className='recommendation-controls';
      const prev=document.createElement('button');prev.type='button';prev.className='recommendation-arrow';prev.setAttribute('aria-label','Previous recommendations');prev.textContent='←';
      const next=document.createElement('button');next.type='button';next.className='recommendation-arrow';next.setAttribute('aria-label','Next recommendations');next.textContent='→';
      controls.append(prev,next);recHeader.appendChild(controls);
      prev.addEventListener('click',()=>go(page-1));next.addEventListener('click',()=>go(page+1));
    }
    function updateControls(){
      const controls=recHeader.querySelector('.recommendation-controls');
      if(!controls)return;
      const prev=controls.children[0],next=controls.children[1];
      const total=pages();
      prev.disabled=page<=0;next.disabled=page>=total-1;
      controls.hidden=currentItems.length<=pageSize();
    }
    function go(target){page=Math.max(0,Math.min(pages()-1,target));recGrid.scrollTo({left:page*recGrid.clientWidth,behavior:'smooth'});updateControls();}

    function recommendationScore(g,query,plays,searches){
      const q=norm(query);
      const querySim=similarity(g.title,q);
      let playAffinity=0,recentAffinity=0;
      const pv=Object.values(plays);
      const totalPlays=pv.reduce((n,x)=>n+(x.plays||0),0);
      if(totalPlays){
        let weighted=0,recent=0;
        pv.forEach(item=>{
          const sim=similarity(g.title,item.title);
          if(!sim)return;
          const p=Math.max(1,item.plays||1);
          weighted+=sim*Math.sqrt(p);
          const age=Math.max(0,(Date.now()-(item.lastPlayed||0))/86400000);
          recent+=sim*p*Math.exp(-age/14);
        });
        playAffinity=Math.min(1,weighted/Math.sqrt(totalPlays));
        recentAffinity=Math.min(1,recent/Math.max(1,totalPlays));
      }
      let searchAffinity=0;
      const sv=Object.values(searches);
      const totalSearches=sv.reduce((n,x)=>n+(x.count||0),0);
      if(totalSearches){
        let weighted=0;
        sv.forEach(item=>weighted+=similarity(g.title,item.query||'')*(item.count||0));
        searchAffinity=Math.min(1,weighted/totalSearches);
      }
      const already=plays[g.key]?.plays||0;
      const freshness=already?1/Math.sqrt(already+1):1;
      // Search intent gets priority, then durable play taste and recent play taste.
      return querySim*.30 + searchAffinity*.25 + playAffinity*.25 + recentAffinity*.15 + freshness*.05;
    }

    function render(query){
      const gs=games();
      if(!query||!gs.length){recSection.classList.remove('is-visible');recGrid.innerHTML='';currentItems=[];page=0;updateControls();return;}
      ensureControls();
      const plays=read(PLAY_KEY,{}),searches=read(SEARCH_KEY,{});
      const exact=typeof matched==='function'?matched(query):[];
      const exactKeys=new Set(exact.slice(0,8).map(g=>key(g)));
      currentItems=gs.map(g=>({...g,score:recommendationScore(g,query,plays,searches)}))
        .filter(g=>!exactKeys.has(g.key))
        .sort((a,b)=>b.score-a.score||a.title.localeCompare(b.title))
        .slice(0,MAX_ITEMS);
      // When a broad query would otherwise leave too little, add best non-exact candidates.
      if(currentItems.length<Math.min(12,gs.length)){
        const extras=gs.map(g=>({...g,score:recommendationScore(g,query,plays,searches)})).filter(g=>!currentItems.some(x=>x.key===g.key)).sort((a,b)=>b.score-a.score||a.title.localeCompare(b.title));
        currentItems=currentItems.concat(extras).slice(0,MAX_ITEMS);
      }
      recGrid.innerHTML='';
      currentItems.forEach(game=>{
        const button=document.createElement('button');button.type='button';button.className='search-recommendation';button.title=game.title;
        const img=document.createElement('img');img.loading='lazy';img.src=game.image;img.alt=game.title;
        const span=document.createElement('span');span.textContent=game.title;button.append(img,span);
        button.addEventListener('click',()=>{clickSound();recordPlay(game);game.card.click();});
        recGrid.appendChild(button);
      });
      page=0;recGrid.scrollLeft=0;recSection.classList.add('is-visible');updateControls();
    }

    document.addEventListener('click',e=>{const card=e.target.closest('#gameGrid > .game-card');if(card){const game=games().find(g=>g.card===card);if(game)recordPlay(game);}},true);
    let lastQuery='',timer=0;
    const refresh=()=>{const q=searchInput.value.trim();if(q===lastQuery){updateControls();return;}lastQuery=q;if(q)recordSearch(q);render(q);};
    searchInput.addEventListener('input',()=>{lastQuery='';clearTimeout(timer);timer=setTimeout(refresh,120);});
    searchInput.addEventListener('change',refresh);
    window.addEventListener('resize',()=>{page=0;updateControls();});
    new MutationObserver(()=>{if(searchInput.value.trim())render(searchInput.value.trim());}).observe(gameGridEl,{childList:true});
    setTimeout(refresh,150);
  })();
'''
s=s[:start]+block+s[end:]
p.write_text(s,encoding='utf-8')
