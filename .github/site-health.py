from pathlib import Path
# Health checks cover the stable homepage, strict game admission automation, duplicate protection, and live UI safeguards.
import html,re,sys

INDEX=Path('index.html'); LEGACY=Path('legacy-index.html')
TITLE_RE=re.compile(r'<h3[^>]*>(.*?)</h3>',re.I|re.S)
CARD_RE=re.compile(r'<(?:div|article)\s+class="game-card"(?=\s|>)',re.I)
URL_RE=re.compile(r"openGame\(\s*['\"]([^'\"]+)['\"]",re.I)

def clean(s):
    return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>','',s or ''))).strip()

def titles(text): return [clean(x) for x in TITLE_RE.findall(text) if clean(x)]
def urls(text):
    decoded=html.unescape(text)
    return [x.strip() for x in URL_RE.findall(decoded) if x.strip()]
def dupes(items):
    seen=set(); out=set()
    for x in items:
        k=x.casefold()
        if k in seen: out.add(k)
        seen.add(k)
    return sorted(out)

errors=[]
if not INDEX.exists(): errors.append('index.html is missing')
if not LEGACY.exists(): errors.append('legacy-index.html is missing')
if errors:
    print('HEALTH CHECK FAILED');print('\n'.join(errors));sys.exit(1)
idx=INDEX.read_text(encoding='utf-8'); leg=LEGACY.read_text(encoding='utf-8')
required=['id="gameGrid"','id="searchBar"','id="categoryToggle"','id="randomGameButton"','id="reportGameButton"','You may also like','Play games instantly with UBG43!','1000+ games','v3-carousel','v3-ribbon','zones.json','legacy-index.html','function openGame','rel="canonical"']
for needle in required:
    if needle not in idx: errors.append(f'index.html missing {needle}')
for bad in ['id="loadingCard"','Loading games...','new MutationObserver(()=>normalize()).observe(document.body,{childList:true,subtree:true})','window.open(\'about:blank\'']:
    if bad in idx: errors.append(f'unwanted runtime marker remains: {bad}')
leg_titles=titles(leg); leg_urls=urls(leg)
if len(leg_urls)<300: errors.append(f'legacy-index.html contains only {len(leg_urls)} game links')
if dupes(leg_titles): errors.append(f'legacy-index.html has duplicate titles: {dupes(leg_titles)[:8]}')
if dupes(leg_urls): errors.append(f'legacy-index.html has duplicate URLs: {dupes(leg_urls)[:8]}')
for i,card in enumerate(re.findall(r'<div\s+class="game-card"[^>]*>.*?</div>\s*(?=<div\s+class="game-card"|</div>\s*<footer|$)',leg,re.I|re.S),1):
    head=card.split('>',1)[0]
    if 'data-category=' not in head: errors.append(f'legacy card {i} is missing data-category')
    if re.search(r'<img\b[^>]*\bsrc\s*=',card,re.I) is None: errors.append(f'legacy card {i} is missing an image src')
print('SITE HEALTH')
print(f'- index.html: {len(CARD_RE.findall(idx))} static cards; stable runtime catalogue enabled')
print(f'- legacy-index.html: {len(CARD_RE.findall(leg))} static cards; {len(set(leg_urls))} unique game links')
print('- search, categories, recommendations, carousels and direct game launching are present')
if errors:
    print('HEALTH CHECK FAILED');
    for e in errors: print('ERROR:',e)
    sys.exit(1)
print('HEALTH CHECK PASSED')