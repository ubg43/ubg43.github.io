from pathlib import Path
import html,re,random

INDEX=Path('index.html')
LEGACY=Path('legacy-index.html')

CATEGORIES=['Action','Adventure','Horror','Multiplayer','Fighting','Survival','Platformer','Racing','Sports','Puzzle','Arcade','Strategy','Simulation','Casual','Anime','Rhythm & Music','Card & Board','io']
RULES={
'Horror':['horror','scary','scare','creepy','haunted','ghost','ghoul','evil','nightmare','backrooms','fnaf','five nights','granny','slenderman','creepypasta','escape the ayuwoki','dead by','vampire','monster'],
'Fighting':['fighting','fighter','duel','duelist','boxing','wrestling','brawl','brawler','beat em up','kung fu','karate','ninja','samurai','street fighter','mortal kombat'],
'Survival':['survival','survive','craft','crafting','island survival','hunger','waves','last stand','apocalypse','zombie survival','forest survival'],
'Platformer':['platformer','platform','obby','parkour','jump n run','super mario','mario','sonic','metroid','geometry dash','run and jump'],
'Anime':['anime','naruto','dragon ball','goku','one piece','bleach','demon slayer','jujutsu','my hero','pokemon','pokémon','sword art online','anime battle'],
'Rhythm & Music':['rhythm','music','piano','guitar','drum','dance','dj','beat','song','karaoke','osu'],
'Card & Board':['card','cards','solitaire','poker','blackjack','checkers','chess','mahjong','uno','domino','board','connect 4','4 in a row'],
'io':['.io',' io','io game','agar','slither','krunker','shell shockers','paper io','diep io','hole io','moomoo'],
'Action':['action','shooter','combat','battle','fight','war','assassin','gun','sniper','strike','rush','arena','brawler','fighter','hero'],
'Adventure':['adventure','quest','dungeon','maze','escape','explore','island','treasure','mystery','story'],
'Arcade':['arcade','flappy','runner','run','brick','ball','bubble','match','pinball','snake','pong','breakout','stack','tap'],
'Puzzle':['puzzle','logic','sudoku','2048','word','memory','connect','block','brain','sort','merge','numbers','crossword','jigsaw'],
'Racing':['racing','race','drift','car','cars','motor','bike','bmx','kart','traffic','drive','rally','formula','truck','rider'],
'Sports':['football','soccer','basketball','baseball','golf','tennis','hockey','volleyball','bowling','pool','sports','skate','ski','boxing','wrestling','cricket'],
'Strategy':['strategy','tower','defense','defence','td','tycoon','manager','kingdom','chess','checkers','empire','tactics'],
'Simulation':['simulator','simulation','farming','farm','restaurant','cooking','shop','business','city','hotel','airport','life','house','doctor','hospital','school','job'],
'Casual':['clicker','dress','makeup','color','drawing','quiz','trivia','fun','cute','matching','decorate']}

def norm(s): return re.sub(r'[^a-z0-9]+',' ',str(s or '').lower()).strip()
def title_from_card(card):
 m=re.search(r'<h3[^>]*>(.*?)</h3>',card,re.I|re.S)
 return html.unescape(re.sub(r'<[^>]+>','',m.group(1))).strip() if m else ''
def classify(title,attrs):
 t=norm(title)
 if 'data-local-multiplayer="true"' in attrs: return 'Multiplayer'
 for cat in ['Horror','Anime','Fighting','Survival','Platformer','Rhythm & Music','Card & Board','io']:
  if any(norm(w) in t for w in RULES[cat]): return cat
 best='Casual';score=0
 for cat in ['Action','Adventure','Arcade','Puzzle','Racing','Sports','Strategy','Simulation','Casual']:
  s=sum(1 for w in RULES[cat] if norm(w) in t)
  if s>score: score=s;best=cat
 return best

def patch_cards(text):
 matches=list(re.finditer(r'<div\b[^>]*class="game-card"[^>]*>',text,re.I))
 if not matches:return text
 out=[];last=0
 for m in matches:
  start=m.start(); end=text.find('</div>',m.end())
  if end<0: continue
  end+=6; card=text[start:end]; title=title_from_card(card)
  if not title: continue
  attrs=m.group(0); cat=classify(title,attrs)
  if 'data-category=' in attrs: new_open=re.sub(r'\sdata-category="[^"]*"',f' data-category="{html.escape(cat,quote=True)}"',attrs,1)
  else: new_open=attrs.replace('class="game-card"',f'class="game-card" data-category="{html.escape(cat,quote=True)}"',1)
  out.append(text[last:start]);out.append(new_open+card[len(attrs):]);last=end
 out.append(text[last:]);return ''.join(out)

def extract_grid(text):
 m=re.search(r'<div\b[^>]*class="game-grid"[^>]*>',text,re.I)
 if not m:return None
 start=m.start();pos=m.end();depth=1;tag_re=re.compile(r'<div\b[^>]*>|</div>',re.I)
 for t in tag_re.finditer(text,pos):
  if t.group(0).lower().startswith('<div'):depth+=1
  else:
   depth-=1
   if depth==0:return start,t.end(),text[m.end():t.start()],text[m.start():m.end()],text[t.start():t.end()]
 return None

def reorder_grid(text):
 info=extract_grid(text)
 if not info:return text
 start,end,body,opening,closing=info
 cards=re.findall(r'<div\b[^>]*class="game-card"[^>]*>.*?</div>',body,re.I|re.S)
 if len(cards)<8:return text
 buckets={c:[] for c in CATEGORIES}
 for c in cards:
  cm=re.search(r'data-category="([^"]+)"',c,re.I);cat=html.unescape(cm.group(1)) if cm else 'Casual';buckets.setdefault(cat,[]).append(c)
 for cat,items in buckets.items(): random.Random('ubg43-home-'+cat).shuffle(items)
 pools=[buckets[c] for c in CATEGORIES if buckets.get(c)];ordered=[]
 while pools:
  for p in pools:
   if p: ordered.append(p.pop())
  pools=[p for p in pools if p]
 return text[:start]+opening+'\n'+'\n'.join(ordered)+'\n'+closing+text[end:]

def inject_runtime(text):
 marker='id="expanded-category-runtime"'
 if marker in text:return text
 js='''\n<script id="expanded-category-runtime">\n(function(){\n const categories=['All Games','Action','Adventure','Horror','Multiplayer','Fighting','Survival','Platformer','Racing','Sports','Puzzle','Arcade','Strategy','Simulation','Casual','Anime','Rhythm & Music','Card & Board','io'];\n const list=document.querySelector('.category-list'),grid=document.getElementById('gameGrid'); if(!list||!grid)return;\n const cards=()=>[...grid.querySelectorAll(':scope > .game-card')];\n function render(){const all=cards();list.innerHTML=categories.map(cat=>{const n=cat==='All Games'?all.length:all.filter(c=>(c.dataset.category||'Casual')===cat).length;return '<button class="category-item" type="button" data-expanded-category="'+cat.replace(/"/g,'&quot;')+'"><span class="category-item-main"><span class="category-dot"></span><span class="category-name">'+cat+'</span></span><span class="category-count">'+n+'</span></button>'}).join('');list.querySelectorAll('[data-expanded-category]').forEach(btn=>btn.addEventListener('click',()=>{const cat=btn.dataset.expandedCategory;list.querySelectorAll('.category-item').forEach(x=>x.classList.toggle('is-active',x===btn));cards().forEach(card=>{card.hidden=cat!=='All Games'&&(card.dataset.category||'Casual')!==cat});grid.scrollIntoView({behavior:'smooth',block:'start'})}));const first=list.querySelector('.category-item');if(first)first.classList.add('is-active')}\n render();\n})();\n</script>\n'''
 return text.replace('</body>',js+'</body>',1) if '</body>' in text else text+js

for p in [LEGACY,INDEX]:
 if p.exists():
  text=p.read_text(encoding='utf-8');text=patch_cards(text);text=reorder_grid(text);text=inject_runtime(text);p.write_text(text,encoding='utf-8')
print('Expanded categories + homepage category-interleave applied.')
