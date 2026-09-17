from pathlib import Path
import re

INDEX=Path('index.html')
LEGACY=Path('legacy-index.html')
FILES=[INDEX,LEGACY]
BACKUPS={
    INDEX: Path('/tmp/ubg43-index-original.html'),
    LEGACY: Path('/tmp/ubg43-legacy-original.html'),
}

STYLE='''<style id="ubg43-runtime-stability-style">\n#status{display:none!important}\n.hero-copy p,.hero-copy .hero-stat{display:none!important}\n#v3Trending,#v3New{display:none!important}\nbody.ubg43-search-active #v3Trending,body.ubg43-search-active #v3New{display:block!important}\n</style>'''
BAD_OBSERVER='new MutationObserver(()=>normalize()).observe(document.body,{childList:true,subtree:true});'


def has_grid(text):
    return bool(re.search(r'id=["\']gameGrid["\']', text, re.I))


def patch(text):
    text=text.replace(BAD_OBSERVER,'')
    text=re.sub(r'new MutationObserver\(\(\)=>normalize\(\)\)\.observe\(document\.body,\{childList:true,subtree:true\}\);','',text)
    text=text.replace('Building your game library…','').replace('Building your game library...','')
    text=text.replace('1000+ games, quick search, automatic categories, fresh releases and personalized picks — all in one place.','')
    text=text.replace('1000+ games • new games every day • personalized recommendations','')
    text=re.sub(r'\s*<style id="ubg43-runtime-stability-style">.*?</style>\s*','\n',text,count=1,flags=re.S)
    pos=text.lower().rfind('</head>')
    if pos!=-1:text=text[:pos]+STYLE+'\n'+text[pos:]
    return text

for path in FILES:
    if not path.exists():
        continue
    src=path.read_text(encoding='utf-8')
    # Several layout scripts operate on both files. If one accidentally removes the core grid,
    # restore that file from the exact checkout copy made before the repair pipeline ran.
    backup=BACKUPS[path]
    if not has_grid(src) and backup.exists():
        restored=backup.read_text(encoding='utf-8')
        if has_grid(restored):
            src=restored
            print('RUNTIME STABILITY: restored',path,'from checkout backup')
    path.write_text(patch(src),encoding='utf-8')
    print('RUNTIME STABILITY FIX:',path)
