from pathlib import Path
import re
from html import unescape

FILES=[Path('legacy-index.html'),Path('index.html')]
CARD=re.compile(r'<div\s+class="game-card"[^>]*>.*?</div>\s*(?=<div\s+class="game-card"|</(?:div|footer|main|body|html)>)',re.I|re.S)
TITLE=re.compile(r'<h3[^>]*>(.*?)</h3>',re.I|re.S)
URL=re.compile(r"openGame\(\s*['\"]([^'\"]+)['\"]",re.I)

def clean(s):
    return re.sub(r'\s+',' ',unescape(re.sub(r'<[^>]+>','',s))).strip().casefold()

for p in FILES:
    if not p.exists(): continue
    text=p.read_text(encoding='utf-8')
    seen_titles=set();seen_urls=set();removed=0
    out=[];pos=0
    for m in CARD.finditer(text):
        out.append(text[pos:m.start()])
        card=m.group(0)
        tm=TITLE.search(card);um=URL.search(card)
        title=clean(tm.group(1)) if tm else ''
        url=um.group(1).strip() if um else ''
        duplicate=(title and title in seen_titles) or (url and url in seen_urls)
        if duplicate:
            removed+=1
        else:
            if title:seen_titles.add(title)
            if url:seen_urls.add(url)
            out.append(card)
        pos=m.end()
    out.append(text[pos:])
    new=''.join(out)
    if new!=text:
        p.write_text(new,encoding='utf-8')
    print(f'DEDUPE {p}: removed {removed}, kept {len(seen_titles)} unique titled games')
