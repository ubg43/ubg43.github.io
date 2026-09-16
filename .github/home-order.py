from pathlib import Path
import re, random
from datetime import datetime, timezone

INDEX = Path('index.html')
LEGACY = Path('legacy-index.html')

def extract_grid(text):
    m = re.search(r'<div\b[^>]*class="game-grid"[^>]*>', text, re.I)
    if not m:
        return None
    start = m.start()
    pos = m.end()
    depth = 1
    tag_re = re.compile(r'<div\b[^>]*>|</div>', re.I)
    for t in tag_re.finditer(text, pos):
        if t.group(0).lower().startswith('<div'):
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                return start, t.end(), text[m.end():t.start()], text[m.start():m.end()], text[t.start():t.end()]
    return None

def shuffle_page(text, seed):
    info = extract_grid(text)
    if not info:
        return text
    start, end, body, opening, closing = info
    cards = re.findall(r'<div\b[^>]*class="game-card"[^>]*>.*?</div>', body, re.I | re.S)
    if len(cards) < 8:
        return text
    rng = random.Random(f'ubg43-home-rotation-{seed}')
    rng.shuffle(cards)
    return text[:start] + opening + '\n' + '\n'.join(cards) + '\n' + closing + text[end:]

# UTC day buckets advance every four days, so the same build is stable within a bucket,
# but the homepage gets a genuinely new order at the next rotation. New games are naturally
# included in the same shuffle the moment they are added, without any manual code changes.
today = datetime.now(timezone.utc).date()
seed = today.toordinal() // 4

for path in (INDEX, LEGACY):
    if path.exists():
        original = path.read_text(encoding='utf-8')
        updated = shuffle_page(original, seed)
        path.write_text(updated, encoding='utf-8')

print(f'HOME ORDER: four-day rotation bucket={seed}; all current and newly added games shuffled automatically.')
