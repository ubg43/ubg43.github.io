from pathlib import Path
import html
import json
import re
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
      ['Multiplayer',['2 player','2-player','2p','local multiplayer','local co op','local co-op','same device','versus local','player 1','player 2','player one','player two','two players','two-player']],
      ['Online Multiplayer',['multiplayer','online multiplayer','io','agar','slither','online','versus','vs','co-op','coop']],
      ['Casual',['clicker','idle','dress','makeup','color','drawing','quiz','trivia','fun','cute','music','piano','matching','decorate']]
    ];'''

START = '<!-- TRENDING-GAMES-START -->'
END = '<!-- TRENDING-GAMES-END -->'
ZONES_URL = 'https://cdn.jsdelivr.net/gh/gn-math/assets@main/zones.json'
POPULARITY_URL = 'https://data.jsdelivr.com/v1/stats/packages/gh/gn-math/html@main/files?period=year'
COVER_ROOT = 'https://cdn.jsdelivr.net/gh/gn-math/covers@main'
HTML_ROOT = 'https://rawcdn.githack.com/gn-math/html/main'


def fetch_json(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'ubg43-library-updater/1.0'})
    with urllib.request.urlopen(req, timeout=35) as r:
        return json.loads(r.read().decode('utf-8'))


def normalize(s):
    return re.sub(r'[^a-z0-9]+', ' ', (s or '').lower()).strip()


def extract_titles(text):
    return {normalize(x) for x in re.findall(r'<h3[^>]*>(.*?)</h3>', text, flags=re.I | re.S) if normalize(x)}


def strip_tags(s):
    return html.unescape(re.sub(r'<[^>]+>', '', s)).strip()


def zone_url(zone):
    url = str(zone.get('url', ''))
    if '{HTML_URL}' in url:
        suffix = url.replace('{HTML_URL}', '').lstrip('/')
        return f'{HTML_ROOT}/{suffix}'
    return url


def zone_cover(zone):
    cover = str(zone.get('cover', ''))
    if '{COVER_URL}' in cover:
        suffix = cover.replace('{COVER_URL}', '').lstrip('/')
        return f'{COVER_ROOT}/{suffix}'
    return cover


def popularity_map(data):
    out = {}
    for item in data if isinstance(data, list) else []:
        name = str(item.get('name', ''))
        hits = item.get('hits', {})
        total = hits.get('total', 0) if isinstance(hits, dict) else 0
        m = re.search(r'/(\d+)(?:-[^/]*)?\.html$', name)
        if m:
            out[int(m.group(1))] = max(out.get(int(m.group(1)), 0), int(total or 0))
    return out


def fetch_html(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'ubg43-library-updater/1.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.read(300000).decode('utf-8', errors='ignore')
    except Exception:
        return ''


def is_local_multiplayer(name, content):
    text = (content or '').lower()
    n = normalize(name)
    strong = [
        'local multiplayer', 'local co-op', 'local co op', 'same device',
        'player 1', 'player 2', 'player one', 'player two',
        '2 player', '2-player', 'two players', 'two-player',
        'player 1 controls', 'player 2 controls',
    ]
    if any(x in text for x in strong):
        return True
    # Well-known local same-device game titles.
    local_title_terms = [
        'supreme duelist', 'boxing random', 'basket random', 'get on top',
        'rooftop snipers', 'stick duel', 'battle wheels', 'party',
    ]
    return any(x in n for x in local_title_terms)


def build_cards(zones, pop, existing, limit=1200):
    by_name = {}
    for z in zones:
        name = strip_tags(str(z.get('name', '')))
        if not name or int(z.get('id', -999999)) < 0:
            continue
        key = normalize(name)
        if key and key not in by_name:
            by_name[key] = z

    forced = []
    for wanted in ['Granny', "Five Nights at Freddy's"]:
        z = by_name.get(normalize(wanted))
        if z:
            forced.append(z)

    ranked = sorted(
        [z for z in zones if int(z.get('id', -999999)) >= 0],
        key=lambda z: (pop.get(int(z.get('id', -999999)), 0), -int(z.get('id', 999999))),
        reverse=True,
    )

    chosen = []
    seen = set(existing)
    for z in forced + ranked:
        name = strip_tags(str(z.get('name', '')))
        key = normalize(name)
        if not name or not key or key in seen:
            continue
        url = zone_url(z)
        cover = zone_cover(z)
        if not url.startswith(('http://', 'https://')) or not cover.startswith(('http://', 'https://')):
            continue
        if key.startswith('suggest games'):
            continue
        chosen.append((name, url, cover))
        seen.add(key)
        if len(chosen) >= limit:
            break
    return chosen


def card_html(item):
    name, url, cover, local_mp = item
    title = html.escape(name, quote=True)
    safe_url = html.escape(url, quote=True)
    safe_cover = html.escape(cover, quote=True)
    attr = ' data-local-multiplayer="true"' if local_mp else ''
    return (
        f'  <div class="game-card"{attr} onclick="openGame(\'{safe_url}\')">\n'
        f'    <img loading="lazy" src="{safe_cover}" alt="{title}" referrerpolicy="no-referrer">\n'
        f'    <h3>{title}</h3>\n'
        f'  </div>'
    )


index = INDEX.read_text(encoding='utf-8')
legacy = LEGACY.read_text(encoding='utf-8') if LEGACY.exists() else ''

# Replace the category rule block in the current homepage regardless of its older version.
start = index.find('    const CATEGORY_RULES=[')
end = index.find('    ];', start)
if start < 0 or end < 0:
    raise SystemExit('CATEGORY_RULES block not found')
index = index[:start] + CATEGORY_RULES + index[end + len('    ];'):]

# Use the current homepage's actual categoryFor function shape.
pattern = re.compile(r"    function categoryFor\(title\)\{.*?\n    \}", re.S)
match = pattern.search(index)
if not match:
    raise SystemExit('categoryFor function not found')
new_cat = """    function categoryFor(title,card){\n      if(card?.dataset.localMultiplayer==='true')return 'Multiplayer';\n      const text=normalize(title);\n      let best='Casual',bestScore=0;\n      CATEGORY_RULES.forEach(([name,words])=>{\n        let score=0;\n        words.forEach(word=>{\n          const w=normalize(word);\n          if(!w)return;\n          if(text===w)score+=4;\n          else if((` ${text} `).includes(` ${w} `))score+=3;\n          else if(text.includes(w))score+=1;\n        });\n        if(score>bestScore){best=name;bestScore=score;}\n      });\n      return best;\n    }"""
index = index[:match.start()] + new_cat + index[match.end():]
index = index.replace('counts[categoryFor(g.title)]++;', 'counts[categoryFor(g.title,g.card)]++;', 1)
index = index.replace('categoryFor(g.title)===c', 'categoryFor(g.title,g.card)===c', 1)

existing = extract_titles(legacy) | extract_titles(index)
zones = fetch_json(ZONES_URL)
pop = popularity_map(fetch_json(POPULARITY_URL))
base_cards = build_cards(zones, pop, existing, limit=1200)
if len(base_cards) < 1000:
    raise SystemExit(f'Only found {len(base_cards)} new eligible games; refusing to publish fewer than 1000 new games')

local_flags = {}
with ThreadPoolExecutor(max_workers=32) as pool:
    futures = {pool.submit(fetch_html, url): (name, url) for name, url, _ in base_cards}
    for fut in as_completed(futures):
        name, url = futures[fut]
        local_flags[normalize(name)] = is_local_multiplayer(name, fut.result())

items = [(name, url, cover, bool(local_flags.get(normalize(name), False))) for name, url, cover in base_cards]
local_count = sum(1 for x in items if x[3])
if local_count < 100:
    raise SystemExit(f'Only verified {local_count} same-device multiplayer games; refusing to publish a misleading 100-game category')

names = {normalize(x[0]) for x in items}
for wanted in ['Granny', "Five Nights at Freddy's"]:
    if normalize(wanted) not in names:
        raise SystemExit(f'{wanted} was not included')

# New games belong in legacy-index.html because index.html imports and rebuilds its game grid from that file.
new_block = START + '\n' + '\n'.join(card_html(x) for x in items) + '\n' + END
if START in legacy and END in legacy:
    a, b = legacy.index(START), legacy.index(END) + len(END)
    legacy = legacy[:a] + new_block + legacy[b:]
else:
    anchor = '\n\t\t</div>\n\t\t<footer>'
    if anchor not in legacy:
        anchor = '\n\t</div>\n\t<footer>'
    if anchor not in legacy:
        raise SystemExit('legacy game-grid/footer anchor not found')
    legacy = legacy.replace(anchor, '\n' + new_block + anchor, 1)

INDEX.write_text(index, encoding='utf-8')
LEGACY.write_text(legacy, encoding='utf-8')
print(f'Published {len(items)} new games, including Granny and FNAF, with {local_count} verified same-device multiplayer games.')
