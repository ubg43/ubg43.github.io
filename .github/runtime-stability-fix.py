from pathlib import Path
import re

FILES=[Path('index.html'),Path('legacy-index.html')]

STYLE='''<style id="ubg43-runtime-stability-style">\n/* Keep the page responsive: hide transient status text and never run the runaway layout observer. */\n#status{display:none!important}\n</style>'''
BAD_OBSERVER='new MutationObserver(()=>normalize()).observe(document.body,{childList:true,subtree:true});'


def extract_grid(html):
    m=re.search(r'(<div\s+id=["\']gameGrid["\'][^>]*>)(.*?)(</div>\s*</main>)',html,re.I|re.S)
    return m.group(0) if m else ''


def patch(text, fallback=''):
    text=text.replace(BAD_OBSERVER,'')
    text=re.sub(r'new MutationObserver\(\(\)=>normalize\(\)\)\.observe\(document\.body,\{childList:true,subtree:true\}\);','',text)
    text=text.replace('Building your game library…','').replace('Building your game library...','')
    # Never allow the cleanup pass to leave the main game grid missing.
    if not re.search(r'id=["\']gameGrid["\']',text,re.I) and fallback:
        fm=re.search(r'<div\s+id=["\']gameGrid["\'][^>]*>.*?</div>',fallback,re.I|re.S)
        mm=re.search(r'</main>',text,re.I)
        if fm and mm:
            text=text[:mm.start()]+fm.group(0)+'\n'+text[mm.start():]
    text=re.sub(r'\s*<style id="ubg43-runtime-stability-style">.*?</style>\s*','\n',text,count=1,flags=re.S)
    pos=text.lower().rfind('</head>')
    if pos!=-1:text=text[:pos]+STYLE+'\n'+text[pos:]
    return text

for p in FILES:
    if not p.exists():
        continue
    fallback=p.read_text(encoding='utf-8')
    # Work from the same file contents at build time; if a later regex ever removes the grid,
    # the current repair pass still has a safe fallback for the next page copy operation.
    text=patch(fallback)
    p.write_text(text,encoding='utf-8')
    print('RUNTIME STABILITY FIX:',p)
