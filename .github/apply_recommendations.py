from pathlib import Path

path = Path('index.html')
html = path.read_text(encoding='utf-8')

if '/* Personalized recommendation carousel */' in html:
    print('already installed')
    raise SystemExit(0)

marker = '  loadLegacyGames();'
if marker not in html:
    raise SystemExit('loadLegacyGames marker not found')

css = '''
<style id="personalized-recommendation-style">
  .search-recommendations-header{align-items:center;position:relative}
  .recommendation-arrow{width:36px;height:36px;flex:0 0 36px;border:1px solid rgba(255,255,255,.35);border-radius:10px;background:rgba(0,73,190,.72);color:#fff;display:inline-flex;align-items:center;justify-content:center;cursor:pointer;font-size:22px;line-height:1;box-shadow:0 5px 15px rgba(0,15,55,.2);transition:transform .16s ease,background .16s ease,box-shadow .16s ease}
  .recommendation-arrow:hover:not(:disabled){transform:translateX(2px) scale(1.06);background:rgba(0,83,213,.9);box-shadow:0 8px 19px rgba(0,15,55,.28)}
  .recommendation-arrow:active:not(:disabled){transform:translateX(1px) scale(.97)}
  .recommendation-arrow:disabled{opacity:.42;cursor:default}
  .recommendation-arrow.is-hidden{display:none}
  #searchRecommendationsGrid.recommendation-track{display:flex;overflow:hidden;gap:13px;width:100%;grid-template-columns:none}
  #searchRecommendationsGrid.recommendation-track .search-recommendation{flex:0 0 calc((100% - 39px)/4);min-width:0;transition:transform .22s ease,box-shadow .18s ease;will-change:transform}
  #searchRecommendationsGrid.recommendation-track .search-recommendation.is-shifted{transform:translateX(calc(-100% - 13px));}
  @media(max-width:900px){#searchRecommendationsGrid.recommendation-track .search-recommendation{flex-basis:calc((100% - 26px)/3)}.recommendation-arrow{width:34px;height:34px;flex-basis:34px}}
  @media(max-width:570px){#searchRecommendationsGrid.recommendation-track .search-recommendation{flex-basis:calc((100% - 13px)/2)}}
</style>
'''

block = r'''

  /* Personalized recommendation carousel */
  (function(){
    const recSection=document.getElementById('searchRecommendations');
    const recGrid=document.getElementById('searchRecommendationsGrid');
    const gameGridEl=document.getElementById('gameGrid');
    const searchInput=document.getElementById('searchBar');
    if(!recSection||!recGrid||!gameGridEl||!searchInput)return;

    const HISTORY_KEY='ubg_play_history_v2';
    const HISTORY_LIMIT=80;
    const normalizeText=s=>(s||'').toString().toLowerCase().replace(/[^a-z0-9\s]/g,' ').replace(/\s+/g,' ').trim();
    const stopWords=new Set(['the','and','for','with','game','games','play','new','online','3d','io','html','html5']);
    const tokens=s=>normalizeText(s).split(' ').filter(w=>w.length>1&&!stopWords.has(w));
    const gameKey=g=>normalizeText(g.title)+'|'+g.image;

    function readHistory(){try{return JSON.parse(localStorage.getItem(HISTORY_KEY)||'{}')||{};}catch(_){return {};}}
    function writeHistory(history){try{localStorage.setItem(HISTORY_KEY,JSON.stringify(history));}catch(_){}
    }
    function recordGame(game){
      if(!game||!game.title)return;
      const history=readHistory(); const key=gameKey(game);
      const item=history[key]||{title:game.title,image:game.image,plays:0,lastPlayed:0,tokens:tokens(game.title)};
      item.title=game.title; item.image=game.image; item.tokens=tokens(game.title); item.plays+=1; item.lastPlayed=Date.now(); history[key]=item;
      const keys=Object.keys(history).sort((a,b)=>(history[b].lastPlayed||0)-(history[a].lastPlayed||0)).slice(0,HISTORY_LIMIT);
      const trimmed={}; keys.forEach(k=>trimmed[k]=history[k]); writeHistory(trimmed);
    }
    function scrape(){
      return Array.from(gameGridEl.querySelectorAll(':scope > .game-card')).map((card,index)=>({
        card,index,title:(card.querySelector('h3')?.textContent||card.querySelector('img')?.alt||'Game').trim(),image:card.querySelector('img')?.currentSrc||card.querySelector('img')?.src||''
      })).filter(g=>g.title).map(g=>({...g,key:gameKey(g)}));
    }
    function overlap(a,b){
      const A=new Set(tokens(a)),B=new Set(tokens(b)); if(!A.size||!B.size)return 0; let hit=0; A.forEach(x=>{if(B.has(x))hit++;}); return hit/Math.sqrt(A.size*B.size);
    }
    function daysSince(ts){return ts?Math.max(0,(Date.now()-ts)/86400000):999;}
    function scoreCandidate(game,query,history,maxPlays){
      const played=Object.values(history), total=played.reduce((n,x)=>n+(x.plays||0),0), qSim=query?overlap(game.title,query):0;
      const weights={}; played.forEach(item=>{const w=Math.sqrt(item.plays||0); (item.tokens||tokens(item.title)).forEach(t=>weights[t]=(weights[t]||0)+w);});
      const gameTokens=tokens(game.title); let affinityRaw=0; gameTokens.forEach(t=>affinityRaw+=weights[t]||0);
      const maxWeight=Math.max(1,...Object.values(weights));
      const taste=total?Math.min(1,affinityRaw/(maxWeight*Math.max(1,gameTokens.length))):0;
      let recentRaw=0; played.forEach(item=>{const sim=overlap(game.title,item.title); if(sim>0)recentRaw+=sim*(item.plays||0)*Math.exp(-daysSince(item.lastPlayed)/14);});
      const recent=total?Math.min(1,recentRaw/Math.max(1,total)):0;
      const plays=history[game.key]?.plays||0;
      const popularity=maxPlays?Math.log1p(plays)/Math.log1p(maxPlays):0;
      const exploration=1/Math.sqrt(1+plays);
      if(!played.length)return qSim*.60+exploration*.25+popularity*.15;
      return taste*.38+qSim*.25+recent*.22+popularity*.10+exploration*.05;
    }

    let offset=0, items=[];
    function ensureArrow(){
      const header=recSection.querySelector('.search-recommendations-header'); if(!header)return;
      if(document.getElementById('recommendationNext'))return;
      const next=document.createElement('button'); next.type='button'; next.id='recommendationNext'; next.className='recommendation-arrow'; next.setAttribute('aria-label','Show more recommendations'); next.innerHTML='<span aria-hidden="true">→</span>';
      header.appendChild(next);
      next.addEventListener('click',()=>{offset=Math.min(Math.max(0,items.length-visibleCount()),offset+visibleCount()); paint();});
    }
    function visibleCount(){return window.innerWidth<=570?2:(window.innerWidth<=900?3:4);}
    function paint(){
      const cards=[...recGrid.children], visible=visibleCount();
      cards.forEach((card,i)=>card.classList.toggle('is-shifted',i<offset));
      const next=document.getElementById('recommendationNext');
      if(next){next.disabled=offset>=Math.max(0,items.length-visible); next.classList.toggle('is-hidden',items.length<=visible);}
    }
    function renderPersonalized(query){
      const games=scrape();
      if(!query||!games.length){recSection.classList.remove('is-visible');recGrid.innerHTML='';items=[];offset=0;return;}
      ensureArrow();
      const history=readHistory(), playedKeys=new Set(Object.keys(history));
      const top=new Set((typeof matched==='function'?matched(query):[]).slice(0,5).map(x=>gameKey(x)));
      const maxPlays=Math.max(1,...Object.values(history).map(x=>x.plays||0));
      items=games.filter(g=>!top.has(g.key)).map(g=>({...g,score:scoreCandidate(g,query,history,maxPlays),played:playedKeys.has(g.key)})).sort((a,b)=>b.score-a.score||a.title.localeCompare(b.title));
      recGrid.innerHTML=''; offset=0;
      items.slice(0,20).forEach(game=>{
        const button=document.createElement('button'); button.type='button'; button.className='search-recommendation';
        const img=document.createElement('img'); img.loading='lazy'; img.src=game.image; img.alt=game.title;
        const span=document.createElement('span'); span.textContent=game.title; button.append(img,span);
        button.addEventListener('click',()=>game.card.click()); recGrid.appendChild(button);
      });
      recSection.classList.add('is-visible'); paint();
    }

    document.addEventListener('click',event=>{
      const card=event.target.closest('#gameGrid > .game-card');
      if(card){const game=scrape().find(g=>g.card===card); if(game)recordGame(game);}
    },true);
    let last='';
    const refresh=()=>{const q=searchInput.value.trim(); if(q===last)return; last=q; renderPersonalized(q);};
    searchInput.addEventListener('input',()=>{last='';setTimeout(refresh,0);});
    searchInput.addEventListener('change',()=>{last='';refresh();});
    window.addEventListener('resize',()=>{if(items.length)paint();});
    new MutationObserver(()=>{if(searchInput.value.trim())renderPersonalized(searchInput.value.trim());}).observe(gameGridEl,{childList:true});
    refresh();
  })();
'''

html = html.replace('</head>', css + '</head>', 1)
html = html.replace(marker, marker + block, 1)
path.write_text(html, encoding='utf-8')
print('recommendation carousel patch applied')
