from pathlib import Path
import html,re,random

INDEX=Path('index.html')
LEGACY=Path('legacy-index.html')

CATEGORIES=[
    'Action','Adventure','Horror','Multiplayer','Fighting','Survival','Platformer',
    'Racing','Sports','Puzzle','Arcade','Strategy','Simulation','Casual',
    'Anime','Rhythm & Music','Card & Board','io'
]

RULES={
    'Horror':['horror','scary','scare','creepy','haunted','ghost','ghoul','evil','nightmare','backrooms','fnaf','five nights','granny','slenderman','creepypasta','escape the ayuwoki','dead by','zombie','vampire','monster'],
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
    'Casual':['clicker','dress','makeup','color','drawing','quiz','trivia','fun','cute','matching','decorate'],
}

MP_LOCAL=['data-local-multiplayer="true"']

def norm(s):
    return re.sub(r'[^a-z0-9]+',' ',str(s or '').lower()).strip()

def title_from_card(card):
    m=re.search(r'<h3[^>]*>(.*?)</h3>',card,re.I|re.S)
    return html.unescape(re.sub(r'<[^>]+>','',m.group(1))).strip() if m else ''

def classify(title,attrs):
    t=norm(title)
    if any(x in attrs for x in MP_LOCAL):
        return 'Multiplayer'
    for cat in ['Horror','Anime','Fighting','Survival','Platformer','Rhythm & Music','Card & Board','io']:
        if any(norm(w) in t for w in RULES[cat]):
            return cat
    best='Casual';score=0
    for cat in ['Action','Adventure','Arcade','Puzzle','Racing','Sports','Strategy','Simulation','Casual']:
        s=sum(1 for w in RULES[cat] if norm(w) in t)
        if s>score:
            score=s;best=cat
    return best

def patch_cards(text):
    def repl(m):
        card=m.group(0)
        attrs_m=re.search(r'<div\b([^>]*)class="game-card"([^>]*)>',card,re.I|re.S)
        if not attrs_m:
            return card
        attrs=(attrs_m.group(1) or '')+(attrs_m.group(2) or '')
        title=title_from_card(card)
        if not title:
            return card
        cat=classify(title,attrs)
        if 'data-category=' in attrs:
            card=re.sub(r'\sdata-category="[^"]*"',f' data-category="{html.escape(cat,quote=True)}"',card,count=1)
        else:
            card=card.replace('class="game-card"',f'class="game-card" data-category="{html.escape(cat,quote=True)}"',1)
        return card
    return re.sub(r'<div\b[^>]*class="game-card"[^>]*>.*?</div>',repl,text,flags=re.I|re.S)

def reorder_grid(text):
    def grid_repl(m):
        opening,body,closing=m.group(1),m.group(2),m.group(3)
        cards=re.findall(r'<div\b[^>]*class="game-card"[^>]*>.*?</div>',body,re.I|re.S)
        if len(cards)<8:
            return m.group(0)
        buckets={c:[] for c in CATEGORIES}
        for c in cards:
            attrs_m=re.search(r'<div\b([^>]*)class="game-card"([^>]*)>',c,re.I|re.S)
            attrs=(attrs_m.group(1) or '')+(attrs_m.group(2) or '') if attrs_m else ''
            cm=re.search(r'data-category="([^"]+)"',attrs,re.I)
            cat=html.unescape(cm.group(1)) if cm else 'Casual'
            buckets.setdefault(cat,[]).append(c)
        # Deterministic shuffle inside each category, then interleave categories so the home page
        # has a curated-looking variety instead of mirroring the upstream/source order.
        for cat,items in buckets.items():
            rng=random.Random('ubg43-home-'+cat)
            rng.shuffle(items)
        pools=[buckets[c] for c in CATEGORIES if buckets.get(c)]
        ordered=[]
        idx=0
        while pools:
            active=[]
            for p in pools:
                if p:
                    active.append(p.pop())
            ordered.extend(active)
            pools=[p for p in pools if p]
            idx+=1
        return opening+'\n'+'\n'.join(ordered)+'\n'+closing
    return re.sub(r'(<div\b[^>]*class="game-grid"[^>]*>)(.*?)(</div>)',grid_repl,text,count=1,flags=re.I|re.S)

def inject_runtime(text):
    marker='id="expanded-category-runtime"'
    if marker not in text:
        js='''\n<script id="expanded-category-runtime">\n(function(){\n  const categories=['All Games','Action','Adventure','Horror','Multiplayer','Fighting','Survival','Platformer','Racing','Sports','Puzzle','Arcade','Strategy','Simulation','Casual','Anime','Rhythm & Music','Card & Board','io'];\n  const list=document.querySelector('.category-list');\n  const grid=document.getElementById('gameGrid');\n  if(!list||!grid)return;\n  function cards(){return [...grid.querySelectorAll(':scope > .game-card')];}\n  function render(){\n    const all=cards();\n    list.innerHTML=categories.map(cat=>{\n      const count=cat==='All Games'?all.length:all.filter(c=>(c.dataset.category||'Casual')===cat).length;\n      return '<button class="category-item" type="button" data-expanded-category="'+cat.replace(/"/g,'&quot;')+'"><span class="category-item-main"><span class="category-dot"></span><span class="category-name">'+cat+'</span></span><span class="category-count">'+count+'</span></button>';\n    }).join('');\n    list.querySelectorAll('[data-expanded-category]').forEach(btn=>btn.addEventListener('click',()=>{\n      const cat=btn.dataset.expandedCategory;\n      list.querySelectorAll('.category-item').forEach(x=>x.classList.toggle('is-active',x===btn));\n      cards().forEach(card=>{card.hidden=cat!=='All Games'&&(card.dataset.category||'Casual')!==cat});\n      grid.scrollIntoView({behavior:'smooth',block:'start'});\n    }));\n    const first=list.querySelector('.category-item'); if(first)first.classList.add('is-active');\n  }\n  render();\n})();\n</script>\n'''
        text=text.replace('</body>',js+'</body>',1) if '</body>' in text else text+js
    return text

def process(path):
    text=path.read_text(encoding='utf-8')
    text=patch_cards(text)
    text=reorder_grid(text)
    text=inject_runtime(text)
    path.write_text(text,encoding='utf-8')

for p in [LEGACY,INDEX]:
    if p.exists():
        process(p)

print('EXPANDED CATEGORIES: Horror, Multiplayer, Fighting, Survival, Platformer, Anime, Rhythm & Music, Card & Board, io plus existing categories; homepage reordered with deterministic category interleave.')
