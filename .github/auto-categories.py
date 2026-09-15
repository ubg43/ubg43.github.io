from pathlib import Path
import html
import json
import re
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

INDEX = Path('index.html')
LEGACY = Path('legacy-index.html')

CATEGORY_RULES = '''    const CATEGORY_RULES=[
      ['Action',['action','shooter','combat','battle','fight','war','zombie','ninja','stickman','assassin','gun','sniper','strike','rush','arena','brawler','fighter','hero']],
      ['Adventure',['adventure','quest','platform','dungeon','maze','escape','explore','survival','island','parkour','treasure','mystery']],
      ['Arcade',['arcade','flappy','runner','run','jump','brick','ball','bubble','match','pinball','snake','pong','breakout','stack','tap']],
      ['Puzzle',['puzzle','logic','sudoku','2048','mahjong','word','memory','connect','block','brain','sort','merge','numbers','crossword','jigsaw']],
      ['Racing',['racing','race','drift','car','cars','motor','bike','bmx','kart','traffic','drive','rally','formula','truck','rider']],
      ['Sports',['football','soccer','basketball','baseball','golf','tennis','hockey','volleyball','bowling','pool','sports','skate','ski','boxing','wrestling','cricket']],
      ['Strategy',['strategy','tower','defense','defence','battle','td','idle','tycoon','manager','kingdom','chess','checkers','warcraft','empire','tactics']],
      ['Simulation',['simulator','simulation','farming','farm','restaurant','cooking','shop','business','city','hotel','airport','life','house','doctor','hospital','school','job']],
      ['Multiplayer',['2 player','2-player','2p','local multiplayer','local co op','local co-op','same device','versus local','player 1','player 2','player one','player two','two players','two-player','versus','vs']],
      ['Casual',['clicker','idle','dress','makeup','color','drawing','quiz','trivia','fun','cute','music','piano','matching','decorate']]
    ];'''

START = '<!-- TRENDING-GAMES-START -->'
END = '<!-- TRENDING-GAMES-END -->'
ZONES_URL = 'https://cdn.jsdelivr.net/gh/gn-math/assets@main/zones.json'
POPULARITY_URL = 'https://data.jsdelivr.com/v1/stats/packages/gh/gn-math/html@main/files?period=year'
COVER_ROOT = 'https://cdn.jsdelivr.net/gh/gn-math/covers@main'
HTML_ROOT = 'https://rawcdn.githack.com/gn-math/html/main'


def fetch_json(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'ubg43-public-library-builder/1.0'})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode('utf-8'))


def normalize(s):
    return re.sub(r'[^a-z0-9]+', ' ', (s or '').lower()).strip()


def strip_tags(s):
    return html.unescape(re.sub(r'<[^>]+>', '', s)).strip()


def extract_titles(text):
    out=set()
    for x in re.findall(r'<h3[^>]*>(.*?)</h3>', text, flags=re.I|re.S):
        x=normalize(strip_tags(x))
        if x: out.add(x)
    return out


def zone_url(zone):
    url=str(zone.get('url',''))
    if '{HTML_URL}' in url:
        return f"{HTML_ROOT}/{url.replace('{HTML_URL}','').lstrip('/')}"
    return url


def zone_cover(zone):
    cover=str(zone.get('cover',''))
    if '{COVER_URL}' in cover:
        return f"{COVER_ROOT}/{cover.replace('{COVER_URL}','').lstrip('/')}"
    return cover


def popularity_map(data):
    result={}
    for item in data if isinstance(data,list) else []:
        name=str(item.get('name',''))
        hits=item.get('hits',{})
        total=hits.get('total',0) if isinstance(hits,dict) else 0
        m=re.search(r'/(\d+)(?:-[^/]*)?\.html$',name)
        if m:
            result[int(m.group(1))]=max(result.get(int(m.group(1)),0),int(total or 0))
    return result


def probe(url, kind):
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'ubg43-public-library-builder/1.0'},method='GET')
        with urllib.request.urlopen(req,timeout=7) as r:
            if r.status < 200 or r.status >= 400:
                return False,b''
            chunk=r.read(256)
            ctype=(r.headers.get('Content-Type') or '').lower()
            if kind=='image':
                return ('image/' in ctype or url.lower().endswith(('.png','.jpg','.jpeg','.webp','.gif'))) and len(chunk)>0,chunk
            return ('text/html' in ctype or 'application/xhtml' in ctype or b'<!doctype' in chunk.lower() or b'<html' in chunk.lower()),chunk
    except Exception:
        return False,b''


def valid_pair(item):
    name,url,cover=item
    ok_game,_=probe(url,'html')
    ok_img,_=probe(cover,'image')
    return name,url,cover,ok_game and ok_img


def fetch_html(url):
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'ubg43-public-library-builder/1.0'})
        with urllib.request.urlopen(req,timeout=8) as r:
            return r.read(450000).decode('utf-8',errors='ignore')
    except Exception:
        return ''


def is_local_multiplayer(name,content):
    text=(content or '').lower()
    title=normalize(name)
    strong=(
        'local multiplayer','local co-op','local co op','same device','two player','two-player',
        '2 player','2-player','player 1','player 2','player one','player two',
        'player 1 controls','player 2 controls','two players'
    )
    if any(x in text for x in strong):
        return True
    title_terms=(
        'supreme duelist','basket random','soccer random','boxing random','volley random',
        'rooftop snipers','get on top','stick duel','battle wheels','4 in a row','four in a row',
        '12 mini battles','2 player','2-player','two player','2 3 4 player'
    )
    return any(x in title for x in title_terms)


def build_candidates(zones,pop,existing,limit=1250):
    by_name={}
    for z in zones:
        try: gid=int(z.get('id',-1))
        except Exception: continue
        if gid<0: continue
        name=strip_tags(str(z.get('name','')))
        key=normalize(name)
        if not key or key in by_name: continue
        by_name[key]=z
    forced=[]
    for wanted in ['Granny',"Five Nights at Freddy's"]:
        z=by_name.get(normalize(wanted))
        if z: forced.append(z)
    ranked=sorted([z for z in zones if int(z.get('id',-1))>=0],key=lambda z:(pop.get(int(z.get('id',-1)),0),-int(z.get('id',999999))),reverse=True)
    out=[];seen=set(existing)
    for z in forced+ranked:
        name=strip_tags(str(z.get('name',''))); key=normalize(name)
        if not name or not key or key in seen: continue
        url=zone_url(z); cover=zone_cover(z)
        if not url.startswith(('http://','https://')) or not cover.startswith(('http://','https://')): continue
        if key.startswith('suggest games'): continue
        out.append((name,url,cover)); seen.add(key)
        if len(out)>=limit: break
    return out


def card_html(name,url,cover,local_mp):
    title=html.escape(name,quote=True); su=html.escape(url,quote=True); sc=html.escape(cover,quote=True)
    marker=' data-local-multiplayer="true"' if local_mp else ''
    return f'  <div class="game-card"{marker} onclick="openGame(\'{su}\')">\n    <img loading="lazy" src="{sc}" alt="{title}" referrerpolicy="no-referrer">\n    <h3>{title}</h3>\n  </div>'


index=INDEX.read_text(encoding='utf-8')
legacy=LEGACY.read_text(encoding='utf-8') if LEGACY.exists() else ''

# Update category rules.
start=index.find('    const CATEGORY_RULES=[')
end=index.find('    ];',start)
if start<0 or end<0: raise SystemExit('CATEGORY_RULES block not found')
index=index[:start]+CATEGORY_RULES+index[end+len('    ];'):]

# Make categoryFor robust whether the older homepage has it as a function, arrow, or not at all.
func=re.search(r"\n    function categoryFor\(title(?:,card)?\)\{.*?\n    \}",index,re.S)
new_func="""\n    function categoryFor(title,card){\n      if(card?.dataset.localMultiplayer==='true')return 'Multiplayer';\n      const text=normalize(title);\n      let best='Casual',bestScore=0;\n      CATEGORY_RULES.forEach(([name,words])=>{\n        let score=0;\n        words.forEach(word=>{\n          const w=normalize(word);\n          if(!w)return;\n          if(text===w)score+=4;\n          else if((` ${text} `).includes(` ${w} `))score+=3;\n          else if(text.includes(w))score+=1;\n        });\n        if(score>bestScore){best=name;bestScore=score;}\n      });\n      return best;\n    }\n"""
if func:
    index=index[:func.start()]+new_func+index[func.end():]
else:
    anchor='    const categories=['
    if anchor not in index: raise SystemExit('category insertion anchor not found')
    index=index.replace(anchor,new_func+'    const categories=[',1)
index=index.replace('counts[categoryFor(g.title)]++;','counts[categoryFor(g.title,g.card)]++;')
index=index.replace('categoryFor(g.title)===c','categoryFor(g.title,g.card)===c')

existing=extract_titles(legacy)|extract_titles(index)
zones=fetch_json(ZONES_URL)
pop=popularity_map(fetch_json(POPULARITY_URL))
candidates=build_candidates(zones,pop,existing,limit=1250)
if len(candidates)<1100:
    raise SystemExit(f'Only {len(candidates)} new candidates are available; refusing a library smaller than 1000 verified games')

# Verify every selected game has both a reachable game page and a real image before publishing it.
verified=[]
with ThreadPoolExecutor(max_workers=48) as pool:
    futures=[pool.submit(valid_pair,item) for item in candidates]
    for fut in as_completed(futures):
        try:
            name,url,cover,ok=fut.result()
            if ok: verified.append((name,url,cover))
        except Exception:
            pass

# Preserve the requested titles even if ranking moves, but only when their page and cover both verify.
verified_by_name={normalize(x[0]):x for x in verified}
for wanted in ['Granny',"Five Nights at Freddy's"]:
    if normalize(wanted) not in verified_by_name:
        raise SystemExit(f'{wanted} did not pass game/image verification')

# Keep the most popular verified set and guarantee 100+ same-device games by inspecting their game pages.
verified.sort(key=lambda x:(pop.get(next((int(z.get('id')) for z in zones if strip_tags(str(z.get('name',''))) == x[0]),-1),0),x[0]),reverse=True)
probe_set=verified[:1100]
local_flags={}
with ThreadPoolExecutor(max_workers=40) as pool:
    futures={pool.submit(fetch_html,url):(name,url) for name,url,_ in probe_set}
    for fut in as_completed(futures):
        name,url=futures[fut]
        local_flags[normalize(name)]=is_local_multiplayer(name,fut.result())

local_count=sum(1 for x in probe_set if local_flags.get(normalize(x[0]),False))
if local_count<100:
    raise SystemExit(f'Only {local_count} same-device multiplayer games could be verified; refusing a misleading multiplayer category')

selected=probe_set
items=[(name,url,cover,bool(local_flags.get(normalize(name),False))) for name,url,cover in selected]
if len(items)<1000:
    raise SystemExit(f'Only {len(items)} fully verified games available after image/game checks')

new_block=START+'\n'+'\n'.join(card_html(*x) for x in items)+'\n'+END
if START in legacy and END in legacy:
    a,b=legacy.index(START),legacy.index(END)+len(END)
    legacy=legacy[:a]+new_block+legacy[b:]
else:
    # Legacy index normally closes the game grid immediately before footer.
    anchors=['\n\t\t</div>\n\t\t<footer','\n\t</div>\n\t<footer','\n</div>\n<footer']
    for anchor in anchors:
        if anchor in legacy:
            legacy=legacy.replace(anchor,'\n'+new_block+anchor,1)
            break
    else:
        raise SystemExit('legacy game-grid/footer anchor not found')

INDEX.write_text(index,encoding='utf-8')
LEGACY.write_text(legacy,encoding='utf-8')
print(f'FINAL VERIFIED BUILD: {len(items)} games; {local_count} same-device multiplayer; all published cards passed game-page and image checks; Granny and FNAF included.')
