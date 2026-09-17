from pathlib import Path
import re

INDEX=Path('index.html')
LEGACY=Path('legacy-index.html')
FILES=[INDEX,LEGACY]

STYLE='''<style id="ubg43-runtime-stability-style">\n#status{display:none!important}\n</style>'''
BAD_OBSERVER='new MutationObserver(()=>normalize()).observe(document.body,{childList:true,subtree:true});'


def patch(text, fallback=''):
    text=text.replace(BAD_OBSERVER,'')
    text=re.sub(r'new MutationObserver\(\(\)=>normalize\(\)\)\.observe\(document\.body,\{childList:true,subtree:true\}\);','',text)
    text=text.replace('Building your game library…','').replace('Building your game library...','')
    # Re-add a safe game grid from the companion HTML file if any previous cleanup removed it.
    if not re.search(r'id=["\']gameGrid["\']',text,re.I) and fallback:
        fm=re.search(r'<div\s+id=["\']gameGrid["\'][^>]*>.*?</div>',fallback,re.I|re.S)
        mm=re.search(r'</main>',text,re.I)
        if fm and mm:
            text=text[:mm.start()]+fm.group(0)+'\n'+text[mm.start():]
    text=re.sub(r'\s*<style id="ubg43-runtime-stability-style">.*?</style>\s*','\n',text,count=1,flags=re.S)
    pos=text.lower().rfind('</head>')
    if pos!=-1:text=text[:pos]+STYLE+'\n'+text[pos:]
    return text

index_original=INDEX.read_text(encoding='utf-8') if INDEX.exists() else ''
legacy_original=LEGACY.read_text(encoding='utf-8') if LEGACY.exists() else ''

for path in FILES:
    if not path.exists():
        continue
    src=path.read_text(encoding='utf-8')
    fallback=legacy_original if path==INDEX else index_original
    path.write_text(patch(src,fallback),encoding='utf-8')
    print('RUNTIME STABILITY FIX:',path)
