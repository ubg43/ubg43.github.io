from pathlib import Path

p = Path('index.html')
if not p.exists():
    raise SystemExit('index.html missing')

s = p.read_text(encoding='utf-8')

old = "function renderGrid(){if(!state.cards.size){grid.innerHTML='';state.games.forEach(g=>{const c=cardFor(g);state.cards.set(gameKey(g),c);grid.append(c)})}applyFilters()}"
new = "function renderGrid(){const frag=document.createDocumentFragment();state.games.forEach(g=>{const k=gameKey(g);if(!state.cards.has(k))state.cards.set(k,cardFor(g));frag.appendChild(state.cards.get(k))});grid.append(frag);applyFilters()}"
if old not in s:
    raise SystemExit('renderGrid target not found')
s = s.replace(old, new, 1)

old = "img.loading=mini?'lazy':'eager'"
if old not in s:
    raise SystemExit('image loading target not found')
s = s.replace(old, "img.loading='lazy'", 1)

old = "function applyFilters(){const q=normalize(state.query);let visible=0;state.games.forEach(g=>{const c=state.cards.get(gameKey(g));if(!c)return;const ok=matches(g)&&(!q||normalize(g.title).includes(q));c.style.display=ok?'':'none';if(ok)visible++;decorate(c,g)});status.textContent=`${visible} of ${state.games.length} games shown`;renderCategories()}"
new = "function applyFilters(){const q=normalize(state.query);let visible=0;state.games.forEach(g=>{const c=state.cards.get(gameKey(g));if(!c)return;const ok=matches(g)&&(!q||normalize(g.title).includes(q));c.style.display=ok?'':'none';if(ok)visible++});status.textContent=`${visible} of ${state.games.length} games shown`}"
if old not in s:
    raise SystemExit('applyFilters target not found')
s = s.replace(old, new, 1)

p.write_text(s, encoding='utf-8')
print('STABLE RUNTIME HOTFIX: applied')
