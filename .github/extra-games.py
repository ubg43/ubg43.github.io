from pathlib import Path
import html, json, re, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date

INDEX = Path('index.html')
LEGACY = Path('legacy-index.html')
ZONES_URL = 'https://raw.githubusercontent.com/gn-math/assets/main/zones.json'
HTML_ROOT = 'https://raw.githubusercontent.com/gn-math/html/main'
COVER_ROOT = 'https://raw.githubusercontent.com/gn-math/covers/main'
TARGET_NEW = 150

# Prefer recognizable/popular-style titles first, then fall back to other verified entries.
PREFERRED = [
    'minecraft','bloons','fireboy','watergirl','papas','duck life','wheely','learn to fly',
    'red ball','super fighter','stickman','bob the robber','worlds hardest game','run 3',
    'cut the rope','fruit ninja','angry birds','action turnip','bad ice cream','sugar sugar',
    'drift','driving','sniper','zombie','ninja','soccer','football','basketball','boxing',
    'tennis','golf','racing','car','bike','motor','football','hockey','volleyball','pool',
    'geometry','vex','ovo','fnf','friday night','sprunki','sonic','mario','pokemon','naruto',
    'dragon ball','tower defense','strategy','horror','fnaf','granny','five nights'
]

BAD_WORDS = ['suggest games', 'discord.gg/', 'unavailable', 'test game', 'demo only']


def req(url, timeout=12):
    r = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':'ubg43-extra-game-builder/1.0'}), timeout=timeout)
    return r


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
    name = str(z.get('name', '')).strip()
    url = game_url(z)
    cover = cover_url(z)
    n = norm(name)
    if not name or not url.startswith('https://') or not cover.startswith('https://'):
        return False
    if any(x in n for x in BAD_WORDS):
        return False
    if not ('github.com/gn-math/html' in url or 'raw.githubusercontent.com/gn-math/html' in url):
        return False
    return True


def probe(z):
    name = str(z.get('name', '')).strip()
    page = game_url(z)
    cover = cover_url(z)
    try:
        rp = req(page, 8)
        body = rp.read(800)
        ct = (rp.headers.get('Content-Type') or '').lower()
        page_ok = 200 <= rp.status < 400 and (b'<html' in body.lower() or b'<!doctype' in body.lower() or 'html' in ct)
        ri = req(cover, 8)
        ib = ri.read(32)
        ict = (ri.headers.get('Content-Type') or '').lower()
        image_ok = 200 <= ri.status < 400 and bool(ib) and ('image/' in ict or re.search(r'\.(png|jpe?g|webp|gif)(\?|$)', cover, re.I))
        return z if page_ok and image_ok else None
    except Exception:
        return None


def score(z, index):
    n = norm(z.get('name', ''))
    hits = sum(1 for w in PREFERRED if w in n)
    # Keep earlier catalogue entries reasonably high while avoiding dependence on exact IDs.
    return (-hits, index)


def grid_info(text):
    m = re.search(r'<div\b[^>]*class="game-grid"[^>]*>', text, re.I)
    if not m:
        return None
    start = m.start(); pos = m.end(); depth = 1
    tag_re = re.compile(r'<div\b[^>]*>|</div>', re.I)
    for t in tag_re.finditer(text, pos):
        if t.group(0).lower().startswith('<div'):
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                return start, t.end(), text[m.end():t.start()], text[m.start():m.end()], text[t.start():t.end()]
    return None


def has_title(text, title):
    return norm(title) in extract_titles(text)


def card(z):
    name = html.escape(str(z['name']).strip())
    url = html.escape(game_url(z), quote=True)
    cover = html.escape(cover_url(z), quote=True)
    return f'''  <div class="game-card" data-new-since="{date.today().isoformat()}" data-source="gn-math-verified" onclick="openGame('{url}')">\n    <img loading="lazy" src="{cover}" alt="{name}" referrerpolicy="no-referrer">\n    <h3>{name}</h3>\n  </div>'''


def add_cards(text, additions):
    if not additions:
        return text
    info = grid_info(text)
    if not info:
        return text
    start, end, body, opening, closing = info
    cards = '\n'.join(card(z) for z in additions)
    return text[:start] + opening + '\n' + body.rstrip() + '\n' + cards + '\n' + closing + text[end:]


existing_text = ''
for p in (INDEX, LEGACY):
    if p.exists():
        existing_text += '\n' + p.read_text(encoding='utf-8')
existing_titles = extract_titles(existing_text)

zones = [z for z in get_json(ZONES_URL) if good_candidate(z)]
# De-duplicate catalogue entries by normalized name and URL.
seen = set(); candidates = []
for i, z in enumerate(zones):
    key = (norm(z.get('name', '')), game_url(z))
    if not key[0] or key[0] in existing_titles or key in seen:
        continue
    seen.add(key)
    candidates.append((i, z))

candidates.sort(key=lambda iz: score(iz[1], iz[0]))

verified = []
with ThreadPoolExecutor(max_workers=24) as ex:
    futures = [ex.submit(probe, z) for _, z in candidates[:900]]
    for fut in as_completed(futures):
        z = fut.result()
        if z:
            verified.append(z)
            if len(verified) >= TARGET_NEW:
                break

if len(verified) < TARGET_NEW:
    raise SystemExit(f'Only {len(verified)} verified new games found; refusing a partial build.')

# Stabilize the resulting set so repeated workflow runs are deterministic and deduplicated.
final = []
used = set(existing_titles)
for z in sorted(verified, key=lambda z: norm(z.get('name', ''))):
    n = norm(z.get('name', ''))
    if n in used:
        continue
    used.add(n); final.append(z)
    if len(final) >= TARGET_NEW:
        break

if len(final) < TARGET_NEW:
    raise SystemExit(f'Deduplication left only {len(final)} new games; refusing a partial build.')

for path in (INDEX, LEGACY):
    if path.exists():
        original = path.read_text(encoding='utf-8')
        updated = add_cards(original, final)
        path.write_text(updated, encoding='utf-8')

print(f'EXTRA GAMES: added {len(final)} new verified HTML5 games with matching cover images; duplicates excluded.')
