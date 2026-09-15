from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
needle="""    function render(query){\n      const gs=games();\n      if(!query||!gs.length){recSection.classList.remove('is-visible');recGrid.innerHTML='';currentItems=[];page=0;updateControls();return;}\n      ensureControls();"""
replacement="""    function render(query){\n      const gs=games();\n      recGrid.classList.add('recommendation-track');\n      if(!query||!gs.length){recSection.classList.remove('is-visible');recGrid.classList.remove('recommendation-track');recGrid.innerHTML='';currentItems=[];page=0;updateControls();return;}\n      ensureControls();"""
if needle not in s: raise SystemExit('recommendation render anchor not found')
s=s.replace(needle,replacement,1)
old="""    let lastQuery='',timer=0;\n    const refresh=()=>{const q=searchInput.value.trim();if(q===lastQuery){updateControls();return;}lastQuery=q;if(q)recordSearch(q);render(q);};\n    searchInput.addEventListener('input',()=>{lastQuery='';clearTimeout(timer);timer=setTimeout(refresh,120);});"""
new="""    let lastQuery='',timer=0;\n    const refresh=()=>{const q=searchInput.value.trim();if(q===lastQuery){updateControls();return;}lastQuery=q;if(q.length>=2)recordSearch(q);render(q);};\n    searchInput.addEventListener('input',()=>{lastQuery='';clearTimeout(timer);timer=setTimeout(refresh,280);});"""
if old not in s: raise SystemExit('search refresh anchor not found')
s=s.replace(old,new,1)
old_resize="""    window.addEventListener('resize',()=>{page=0;updateControls();});"""
new_resize="""    let resizeTimer=0;\n    window.addEventListener('resize',()=>{clearTimeout(resizeTimer);resizeTimer=setTimeout(()=>{page=0;recGrid.scrollLeft=0;updateControls();},120);});"""
if old_resize not in s: raise SystemExit('resize anchor not found')
s=s.replace(old_resize,new_resize,1)
p.write_text(s,encoding='utf-8')
