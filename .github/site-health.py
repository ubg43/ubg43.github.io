from pathlib import Path
import re
import sys
from html import unescape

FILES = [Path('index.html'), Path('legacy-index.html')]
MIN_CARDS = 1000
required = ['openGame(', 'id="gameGrid"', 'id="searchBar"']
card_re = re.compile(r'<div\s+class="game-card"(?=\s|>)', re.I)
title_re = re.compile(r'<h3[^>]*>(.*?)</h3>', re.I | re.S)
img_re = re.compile(r'<img\b[^>]*>', re.I | re.S)
url_re = re.compile(r"openGame\(['\"]([^'\"]+)['\"]\)", re.I)

def clean(s):
    return re.sub(r'\s+', ' ', unescape(re.sub(r'<[^>]+>', '', s))).strip()

def unique(items):
    return len(set(x.strip() for x in items if x.strip()))

errors = []
stats = []

for path in FILES:
    if not path.exists():
        errors.append(f'{path} is missing')
        continue
    text = path.read_text(encoding='utf-8')
    cards = card_re.findall(text)
    titles = [clean(x) for x in title_re.findall(text)]
    urls = url_re.findall(text)
    imgs = img_re.findall(text)
    title_keys = [t.casefold() for t in titles if t]
    url_keys = [u.strip() for u in urls if u.strip()]
    dup_titles = sorted({x for x in title_keys if title_keys.count(x) > 1})
    dup_urls = sorted({x for x in url_keys if url_keys.count(x) > 1})
    missing_images = sum('src=' not in tag.lower() for tag in imgs)
    if len(cards) < MIN_CARDS:
        errors.append(f'{path}: only {len(cards)} game cards (expected at least {MIN_CARDS})')
    if dup_titles:
        errors.append(f'{path}: duplicate game titles: {dup_titles[:8]}')
    if dup_urls:
        errors.append(f'{path}: duplicate game URLs: {dup_urls[:8]}')
    if missing_images:
        errors.append(f'{path}: {missing_images} image tags are missing src')
    for needle in required:
        if needle not in text:
            errors.append(f'{path}: required UI marker missing: {needle}')
    if 'Loading games...' in text or 'id="loadingCard"' in text:
        errors.append(f'{path}: obsolete loading placeholder is still present')
    stats.append((path, len(cards), unique(urls), len(imgs)))

print('SITE HEALTH')
for path, cards, urls, imgs in stats:
    print(f'- {path}: {cards} game cards, {urls} unique game URLs, {imgs} images')

if errors:
    print('HEALTH CHECK FAILED')
    for e in errors:
        print('ERROR:', e)
    sys.exit(1)
print('HEALTH CHECK PASSED: game count, UI hooks, duplicate checks, images, and loading-placeholder removal are clean.')
