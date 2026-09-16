from pathlib import Path
from datetime import date
import html,re

INDEX=Path('index.html')
LEGACY=Path('legacy-index.html')
TODAY=date.today().isoformat()
GAMES=[
    {
        'title':'Undertale Sans Fight',
        'url':'https://jcw87.github.io/c2-sans-fight/',
        'image':'undertale-thumbnails/sans-fight.svg',
        'category':'Horror',
    },
    {
        'title':"Undertale Flowey's Time Machine",
        'url':'https://crumblingstatue.github.io/FloweysTimeMachine/',
        'image':'undertale-thumbnails/floweys-time-machine.svg',
        'category':'Horror',
    },
    {
        'title':'Undertale Text Generator',
        'url':'https://ruyili.ca/greetings-human/',
        'image':'undertale-thumbnails/text-generator.svg',
        'category':'Casual',
    },
]

def extract_grid(text):
    m=re.search(r'<div\b[^>]*class="game-grid"[^>]*>',text,re.I)
    if not m:return None
    start=m.start();pos=m.end();depth=1
    tag_re=re.compile(r'<div\b[^>]*>|</div>',re.I)
    for t in tag_re.finditer(text,pos):
        if t.group(0).lower().startswith('<div'):depth+=1
        else:
            depth-=1
            if depth==0:return start,t.end(),text[m.end():t.start()],text[m.start():m.end()],text[t.start():t.end()]
    return None

def has_title(text,title):
    return re.search(r'<h3[^>]*>\s*'+re.escape(title)+r'\s*</h3>',text,re.I) is not None

def card(g):
    return f'''  <div class="game-card" data-category="{html.escape(g['category'],quote=True)}" data-new-since="{TODAY}" data-collection="undertale" onclick="openGame('{html.escape(g['url'],quote=True)}')">\n    <img loading="lazy" src="{html.escape(g['image'],quote=True)}" alt="{html.escape(g['title'],quote=True)}" referrerpolicy="no-referrer">\n    <h3>{html.escape(g['title'])}</h3>\n  </div>'''

def add_games(text):
    info=extract_grid(text)
    if not info:return text
    start,end,body,opening,closing=info
    additions=[card(g) for g in GAMES if not has_title(text,g['title'])]
    if not additions:return text
    return text[:end-len(closing)] if False else text[:start]+opening+'\n'+body.rstrip()+'\n'+'\n'.join(additions)+'\n'+closing+text[end:]

for path in (INDEX,LEGACY):
    if path.exists():
        original=path.read_text(encoding='utf-8')
        updated=add_games(original)
        path.write_text(updated,encoding='utf-8')
        print(f'Undertale collection updated: {path} ({sum(1 for g in GAMES if not has_title(original,g["title"]))} possible additions)')

print('UNDERTALE GAMES: Sans Fight, Flowey\'s Time Machine, and Text Generator are enforced automatically; they use the site\'s existing about:blank openGame wrapper.')
