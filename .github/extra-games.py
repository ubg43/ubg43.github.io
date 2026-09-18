from pathlib import Path
import html, json, re, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from game_validator import validate_candidate

INDEX = Path('index.html')
LEGACY = Path('legacy-index.html')
ZONES_URL = 'https://raw.githubusercontent.com/gn-math/assets/main/zones.json'
HTML_ROOT = 'https://raw.githubusercontent.com/gn-math/html/main'
COVER_ROOT = 'https://raw.githubusercontent.com/gn-math/covers/main'
TARGET_NEW = 150

PREFERRED = [
    'minecraft','bloons','fireboy','watergirl','papas','duck life','wheely','learn to fly',
    'red ball','super fighter','stickman','bob the robber','worlds hardest game','run 3',
    'cut the rope','fruit ninja','angry birds','action turnip','bad ice cream','sugar sugar',
    'drift','driving','sniper','zombie','ninja','soccer','football','basketball','boxing',
    'tennis','golf','racing','car','bike','motor','hockey','volleyball','pool','geometry',
    'vex','ovo','fnf','friday night','sprunki','sonic','mario','pokemon','naruto',
    'dragon ball','tower defense','strategy','horror','fnaf','granny','five nights'
]
BAD_WORDS = ['suggest games', 'discord gg', 'unavailable', 'test game', 'demo only']


def req(url, timeout=12):
    return urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':'ubg43-extra-game-builder/2.1'}), timeout=timeout)


def get_json(url):
    return json.loads(req(url, 30).read().decode('utf-8'))


def norm(s):
    return re.sub(r'[^a-z0-9]+', ' ', str(s or '').lower()).strip()


def strip_html(s):
    return html.unescape(re.sub(r'<[^>]+>', '', s or '')).strip()


def extract_titles(text):
    return {norm(strip_html(x)) for x in re.findall(r'<h3[^>]*>(.*?)</h3>', text, re.I | re.S) if norm(strip_html(x))}


def game_url(z):
    return str(z.get('url', '')).replace('{HTML_URL}', HTML_ROOT)


def cover_url(z):
    return str(z.get('cover', '')).replace('{COVER_URL}', COVER_ROOT)


def good_candidate(z):
    name = str(z.get('name', '')).strip(); url = game_url(z); cover = cover_url(z); n = norm(name)
    if not name or not url.startswith('https://') or not cover.startswith('https://'):
        return False
    if any(x in n for x in BAD_WORDS):
        return False
    if 'github.com/gn-math/html' not in url and 'raw.githubusercontent.com/gn-math/html' not in url:
        return False
    return True


def probe(z):
    return z if validate_candidate(str(z.get('name','')), game_url(z), cover_url(z)) else None


def score(z, index):
    n = norm(z.get('name', ''))
    hits = sum(1 for w in PREFERRED if w in n)
    return (-hits, index)


def grid_info(text):
    m = re.search(r'<div\b[^>]*class="game-grid"[^>]*>', text, re.I)
    if not m: return None
    start, pos, depth = m.start(), m.end(), 1
    tag_re = re.compile(r'<div\b[^>]*>|</div>', re.I)
    for t in tag_re.finditer(text, pos):
        if t.group(0).lower().startswith('<div'): depth += 1
        else:
            depth -= 1
            if depth == 0:
                return start, t.end(), text[m.end():t.start()], text[m.start():m.end()], text[t.start():t.end()]
    return None


def card(z):
    name = html.escape(str(z['name']).strip()); url = html.escape(game_url(z), quote=True); cover = html.escape(cover_url(z), quote=True)
    return f'''  <div class="game-card" data-new-since="{date.today().isoformat()}" data-source="gn-math-verified" onclick="openGame('{url}')">\n    <img loading="lazy" src="{cover}" alt="{name}" referrerpolicy="no-referrer">\n    <h3>{name}</h3>\n  </div>'''


def add_cards(text, additions):
    info = grid_info(text)
    if not info or not additions: return text
    start, end, body, opening, closing = info
    return text[:start] + opening + '\n' + body.rstrip() + '\n' + '\n'.join(card(z) for z in additions) + '\n' + closing + text[end:]


texts = [p.read_text(encoding='utf-8') for p in (INDEX, LEGACY) if p.exists()]
existing_text = '\n'.join(texts)
existing_titles = extract_titles(existing_text)
existing_extra_count = len(re.findall(r'data-source="gn-math-verified"', existing_text))
needed = max(0, TARGET_NEW - existing_extra_count)

if needed == 0:
    print(f'EXTRA GAMES: already have at least {TARGET_NEW} verified expansion games; nothing to add.')
    raise SystemExit(0)

zones = [z for z in get_json(ZONES_URL) if good_candidate(z)]
seen_names = set(existing_titles)
seen_urls = set()
for _text in texts:
    for _u in re.findall(r'onclick="openGame\\([\\\']([^\\\']+)', _text, re.I):
        seen_urls.add(_u.split('#',1)[0].rstrip('/'))
candidates = []
for i, z in enumerate(zones):
    n = norm(z.get('name', '')); u = game_url(z).split('#',1)[0].rstrip('/')
    if not n or n in seen_names or not u or u in seen_urls: continue
    seen_names.add(n); seen_urls.add(u); candidates.append((i, z))
candidates.sort(key=lambda iz: score(iz[1], iz[0]))

verified = []
with ThreadPoolExecutor(max_workers=24) as ex:
    futures = [ex.submit(probe, z) for _, z in candidates[:1200]]
    for fut in as_completed(futures):
        z = fut.result()
        if z:
            verified.append(z)
            if len(verified) >= needed * 2:
                break

final = []; used_names = set(existing_titles); used_urls = set(seen_urls)
for z in sorted(verified, key=lambda z: norm(z.get('name', ''))):
    n = norm(z.get('name', '')); u = game_url(z).split('#',1)[0].rstrip('/')
    if n in used_names or u in used_urls: continue
    used_names.add(n); used_urls.add(u); final.append(z)
    if len(final) >= needed: break

if len(final) < needed:
    print(f'Only {len(final)} verified new games found in this pass; adding the available verified games and continuing (needed {needed}).')
if not final:
    raise SystemExit('No new verified expansion games available in this pass; leaving the existing library unchanged.')

for p in (INDEX, LEGACY):
    if p.exists():
        original = p.read_text(encoding='utf-8')
        p.write_text(add_cards(original, final), encoding='utf-8')

print(f'EXTRA GAMES: added {len(final)} verified HTML5 games with matching cover images; total automated expansion now at least {existing_extra_count + len(final)}.')
# Trigger note: this file is intentionally touched so the first scheduled expansion runs immediately.
