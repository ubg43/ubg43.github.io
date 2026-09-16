from pathlib import Path
import re
import sys
from html import unescape

INDEX=Path('index.html')
LEGACY=Path('legacy-index.html')
CARD_RE=re.compile(r'<div\s+class="game-card"(?=\s|>)',re.I)
TITLE_RE=re.compile(r'<h3[^>]*>(.*?)</h3>',re.I|re.S)
URL_RE=re.compile(r"openGame\(['\"]([^'\"]+)['\"]",re.I)


def clean(s):
    return re.sub(r'\s+',' ',unescape(re.sub(r'<[^>]+>','',s))).strip()

def cards_in(text):
    return len(CARD_RE.findall(text))

def titles_in(text):
    return [clean(x) for x in TITLE_RE.findall(text) if clean(x)]

def urls_in(text):
    return [x.strip() for x in URL_RE.findall(text) if x.strip()]

def dupes(items):
    seen=set();out=set()
    for x in items:
        k=x.casefold() if hasattr(x,'casefold') else x
        if k in seen: out.add(k)
        seen.add(k)
    return sorted(out)

errors=[]
if not INDEX.exists():errors.append('index.html is missing')
if not LEGACY.exists():errors.append('legacy-index.html is missing')
if errors:
    print('HEALTH CHECK FAILED');print('\n'.join(errors));sys.exit(1)

idx=INDEX.read_text(encoding='utf-8')
leg=LEGACY.read_text(encoding='utf-8')

# The homepage is runtime-built from legacy-index.html + GN-Math zones.json, so static card count is not the health criterion.
required=['id="gameGrid"','id="searchBar"','id="categoryToggle"','id="randomGameButton"','id="reportGameButton"','You may also like','Play games instantly with UBG43!','1000+ games','v3-carousel','v3-ribbon']
for needle in required:
    if needle not in idx:errors.append(f'index.html missing {needle}')
for bad in ['id="loadingCard"','Loading games...']:
    if bad in idx or bad in leg:errors.append(f'obsolete loader marker remains: {bad}')
if 'zones.json' not in idx:errors.append('index.html no longer references the automatic GN-Math catalogue')
if 'legacy-index.html' not in idx:errors.append('index.html no longer references the legacy library')
if 'openGameDirect' not in idx and 'function openGame' not in idx:errors.append('no game-launch runtime found')

leg_titles=titles_in(leg)
leg_urls=urls_in(leg)
if len(leg_urls)<300:errors.append(f'legacy-index.html contains only {len(leg_urls)} game links')
if dupes(leg_titles):errors.append(f'legacy-index.html has duplicate titles: {dupes(leg_titles)[:8]}')
if dupes(leg_urls):errors.append(f'legacy-index.html has duplicate URLs: {dupes(leg_urls)[:8]}')

# Every legacy card must have a category and image; this keeps the category browser reliable.
legacy_cards=re.findall(r'<div\s+class="game-card"[^>]*>.*?</div>\s*(?=<div\s+class="game-card"|</div>\s*<footer|$)',leg,re.I|re.S)
for i,card in enumerate(legacy_cards,1):
    head=card.split('>',1)[0]
    if 'data-category=' not in head:errors.append(f'legacy card {i} is missing data-category')
    if re.search(r'<img\b[^>]*\bsrc\s*=',card,re.I) is None:errors.append(f'legacy card {i} is missing an image src')

print('SITE HEALTH')
print(f'- index.html: {cards_in(idx)} static cards; runtime catalogue + legacy library enabled')
print(f'- legacy-index.html: {cards_in(leg)} static cards; {len(set(leg_urls))} unique game links')
print('- recommendation runtime, two-row horizontal carousels, category filtering and direct game launching are present')
if errors:
    print('HEALTH CHECK FAILED')
    for e in errors:print('ERROR:',e)
    sys.exit(1)
print('HEALTH CHECK PASSED')
