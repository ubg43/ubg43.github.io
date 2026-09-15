from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

# Slightly deepen the blue palette without changing layout or non-blue UI.
replacements={
    '--blue:#004dcc;':'--blue:#0047bd;',
    '--blue-deep:#003ea8;':'--blue-deep:#003a96;',
    'background:#0849b6;':'background:#0744ab;',
    'background:#063f9f;':'background:#063a92;',
    'background:rgba(0,58,160,.80);':'background:rgba(0,54,150,.84);',
    'background:rgba(0,68,182,.93);':'background:rgba(0,64,170,.95);',
    'background:linear-gradient(180deg,#061734 0%,#0b2350 100%);':'background:linear-gradient(180deg,#05142f 0%,#092047 100%);',
}
for old,new in replacements.items():
    if old not in s:
        raise SystemExit(f'missing expected color: {old}')
    s=s.replace(old,new,1)

# Ensure the old decorative splash is gone from the live homepage markup/styles.
s=s.replace('      <div class="mc-text">Lil croak was here!</div>\n','',1)
s=s.replace('    .mc-text{font-family:"Pixelify Sans",sans-serif;font-optical-sizing:auto;font-weight:400;font-style:normal;color:#ffff00;display:inline-block;position:absolute;left:1070px;top:35px;white-space:nowrap;text-shadow:1px 1px 0 #000;transform:rotate(-15deg);animation:splash 1.2s infinite ease-in-out}\n','',1)

# Add Trending as the first real category.
old_categories="    const categories=['All Games',...CATEGORY_RULES.map(x=>x[0])];"
new_categories="    const categories=['All Games','Trending',...CATEGORY_RULES.map(x=>x[0])];"
if old_categories not in s:
    raise SystemExit('categories declaration not found')
s=s.replace(old_categories,new_categories,1)

# Add a three-day local trending log and cache immediately after active category state.
needle="    let active='All Games';\n\n    const normalize="
insert="""    let active='All Games';\n\n    const TRENDING_LOG_KEY='ubg_trending_play_log_v1';\n    const TRENDING_CACHE_KEY='ubg_trending_cache_v1';\n    const THREE_DAYS=3*24*60*60*1000;\n    const MAX_TRENDING=25;\n    const normalize=s=>(s||'').toLowerCase().replace(/[^a-z0-9]+/g,' ').trim();\n    const gameKey=(title,image='')=>normalize(title)+'|'+image;\n    function readJSON(key,fallback){try{return JSON.parse(localStorage.getItem(key)||JSON.stringify(fallback));}catch(_){return fallback;}}\n    function writeJSON(key,value){try{localStorage.setItem(key,JSON.stringify(value));}catch(_){} }\n    function pruneTrendLog(log){\n      const cutoff=Date.now()-90*24*60*60*1000;\n      Object.keys(log).forEach(k=>{log[k]=(log[k]||[]).filter(ts=>Number(ts)>=cutoff).slice(-80);if(!log[k].length)delete log[k];});\n      return log;\n    }\n    function recordTrendingPlay(game){\n      if(!game||!game.title)return;\n      const log=pruneTrendLog(readJSON(TRENDING_LOG_KEY,{}));\n      const key=gameKey(game.title,game.image);\n      log[key]=log[key]||[];\n      log[key].push(Date.now());\n      writeJSON(TRENDING_LOG_KEY,pruneTrendLog(log));\n    }\n    function trendingKeys(){\n      const slot=Math.floor(Date.now()/THREE_DAYS);\n      const cached=readJSON(TRENDING_CACHE_KEY,{});\n      if(cached.slot===slot&&Array.isArray(cached.keys))return new Set(cached.keys.slice(0,MAX_TRENDING));\n      const gs=games();\n      const log=pruneTrendLog(readJSON(TRENDING_LOG_KEY,{}));\n      writeJSON(TRENDING_LOG_KEY,log);\n      const cutoff=Date.now()-THREE_DAYS;\n      const ranked=gs.map(g=>({g,n:(log[gameKey(g.title,document.querySelector('#gameGrid img')?.src)]||[]).filter(ts=>Number(ts)>=cutoff).length,last:Math.max(0,...(log[gameKey(g.title,document.querySelector('#gameGrid img')?.src)]||[]))}));\n      ranked.sort((a,b)=>b.n-a.n||b.last-a.last||a.g.title.localeCompare(b.g.title));\n      const keys=ranked.filter(x=>x.n>0).slice(0,MAX_TRENDING).map(x=>gameKey(x.g.title,x.g.card.querySelector('img')?.currentSrc||x.g.card.querySelector('img')?.src||''));\n      writeJSON(TRENDING_CACHE_KEY,{slot,keys});\n      return new Set(keys);\n    }\n\n    const normalize="""
# The inserted normalize is intentionally replaced below with the original normalize declaration.
if needle not in s:
    raise SystemExit('active category marker not found')
s=s.replace(needle,insert,1)
s=s.replace("    const normalize=    const normalize=", "    const normalize=",1)

# The helper above needs the exact image when calculating the game key; replace the ranking function with a safer version.
start="    function trendingKeys(){"
end="    function openSidebar(){"
if start not in s or end not in s:
    raise SystemExit('trending function anchors not found')
oldblock=s[s.index(start):s.index(end)]
newblock="""    function trendingKeys(){\n      const slot=Math.floor(Date.now()/THREE_DAYS);\n      const cached=readJSON(TRENDING_CACHE_KEY,{});\n      if(cached.slot===slot&&Array.isArray(cached.keys))return new Set(cached.keys.slice(0,MAX_TRENDING));\n      const gs=games();\n      const log=pruneTrendLog(readJSON(TRENDING_LOG_KEY,{}));\n      writeJSON(TRENDING_LOG_KEY,log);\n      const cutoff=Date.now()-THREE_DAYS;\n      const ranked=gs.map(g=>{\n        const key=gameKey(g.title,g.card.querySelector('img')?.currentSrc||g.card.querySelector('img')?.src||'');\n        const hits=(log[key]||[]).filter(ts=>Number(ts)>=cutoff);\n        return {g,n:hits.length,last:Math.max(0,...hits)};\n      }).filter(x=>x.n>0);\n      ranked.sort((a,b)=>b.n-a.n||b.last-a.last||a.g.title.localeCompare(b.g.title));\n      const keys=ranked.slice(0,MAX_TRENDING).map(x=>gameKey(x.g.title,x.g.card.querySelector('img')?.currentSrc||x.g.card.querySelector('img')?.src||''));\n      writeJSON(TRENDING_CACHE_KEY,{slot,keys});\n      return new Set(keys);\n    }\n    function openSidebar(){"""
s=s[:s.index(start)]+newblock+s[s.index(end)+len(end):]

# Replace category render/filter logic with Trending support.
old_render="""    function render(){\n      const gs=games();\n      const counts=Object.fromEntries(categories.map(c=>[c,0]));\n      gs.forEach(g=>counts[categoryFor(g.title)]++);\n      list.innerHTML='';\n      categories.forEach(c=>{\n        const btn=document.createElement('button');btn.type='button';btn.className='category-item'+(active===c?' is-active':'');\n        btn.innerHTML='<span class=\"category-item-main\"><span class=\"category-dot\" aria-hidden=\"true\"></span><span class=\"category-name\"></span></span><span class=\"category-count\"></span>';\n        btn.querySelector('.category-name').textContent=c;btn.querySelector('.category-count').textContent=String(c==='All Games'?gs.length:counts[c]);\n        btn.addEventListener('click',()=>{active=c;gs.forEach(g=>{const match=c==='All Games'||categoryFor(g.title)===c;g.card.style.display=match?'':'none';});list.querySelectorAll('.category-item').forEach(x=>x.classList.remove('is-active'));btn.classList.add('is-active');});\n        list.appendChild(btn);\n      });\n    }\n"""
new_render="""    function render(){\n      const gs=games();\n      const trend=trendingKeys();\n      const counts=Object.fromEntries(categories.map(c=>[c,0]));\n      gs.forEach(g=>{counts[categoryFor(g.title)]++;});\n      counts.Trending=trend.size;\n      list.innerHTML='';\n      categories.forEach(c=>{\n        const btn=document.createElement('button');btn.type='button';btn.className='category-item'+(active===c?' is-active':'')+(c==='Trending'?' is-trending':'');\n        btn.innerHTML='<span class=\"category-item-main\"><span class=\"category-dot\" aria-hidden=\"true\"></span><span class=\"category-name\"></span></span><span class=\"category-count\"></span>';\n        btn.querySelector('.category-name').textContent=c;\n        btn.querySelector('.category-count').textContent=String(c==='All Games'?gs.length:counts[c]);\n        btn.addEventListener('click',()=>{\n          active=c;\n          const nowTrend=trendingKeys();\n          gs.forEach(g=>{\n            const key=gameKey(g.title,g.card.querySelector('img')?.currentSrc||g.card.querySelector('img')?.src||'');\n            const match=c==='All Games'||(c==='Trending'?nowTrend.has(key):categoryFor(g.title)===c);\n            g.card.style.display=match?'':'none';\n          });\n          list.querySelectorAll('.category-item').forEach(x=>x.classList.remove('is-active'));btn.classList.add('is-active');\n        });\n        list.appendChild(btn);\n      });\n    }\n"""
if old_render not in s:
    raise SystemExit('old render block not found')
s=s.replace(old_render,new_render,1)

# Record plays for the current three-day trending window.
needle2="    toggle.addEventListener('click',()=>sidebar.classList.contains('is-open')?closeSidebar():openSidebar());"
listener="""    document.addEventListener('click',event=>{\n      const card=event.target.closest('#gameGrid > .game-card');\n      if(card){\n        const img=card.querySelector('img');\n        recordTrendingPlay({title:(card.querySelector('h3')?.textContent||img?.alt||'Game').trim(),image:img?.currentSrc||img?.src||''});\n      }\n    },true);\n    window.addEventListener('storage',event=>{if(event.key===TRENDING_CACHE_KEY||event.key===TRENDING_LOG_KEY)render();});\n\n    toggle.addEventListener('click',()=>sidebar.classList.contains('is-open')?closeSidebar():openSidebar());"""
if needle2 not in s:
    raise SystemExit('toggle listener marker not found')
s=s.replace(needle2,listener,1)

# Make the Trending row subtly special while keeping the same visual language.
trend_css="""\n    .category-item.is-trending .category-dot{background:#5a9bff;box-shadow:0 0 0 4px rgba(90,155,255,.14),0 0 12px rgba(90,155,255,.18)}\n    .category-item.is-trending.is-active{background:rgba(28,94,205,.29);border-color:rgba(83,148,255,.42)}\n"""
if '.category-item.is-trending' not in s:
    s=s.replace('    body.category-locked{overflow:hidden}\n',trend_css+'    body.category-locked{overflow:hidden}\n',1)

# Remove the old splash keyframes and responsive references now that the message is gone.
s=s.replace("    @keyframes splash {\n      0% { transform: rotate(-15deg) scale(0.95) translateY(0px); }\n      25% { transform: rotate(-15deg) scale(1.15) translateY(0px); }\n      50% { transform: rotate(-15deg) scale(0.95) translateY(0px); }\n      75% { transform: rotate(-15deg) scale(1.2) translateY(0px); }\n      100% { transform: rotate(-15deg) scale(0.95) translateY(0px); }\n    }\n\n",'',1)
s=s.replace('.mc-text{font-size:14px}', '', 1)
s=s.replace('.mc-text{order:3;margin-left:auto;margin-right:4px}', '', 1)
s=s.replace('.mc-text{display:none}', '', 1)

p.write_text(s,encoding='utf-8')
