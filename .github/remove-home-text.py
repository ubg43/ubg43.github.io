from pathlib import Path
import re

FILES=[Path('index.html'),Path('legacy-index.html')]
STYLE='''<style id="ubg43-home-text-cleanup-style">\n.hero-copy p,.hero-copy .hero-stat,#status{display:none!important}\n</style>'''
SCRIPT='''<script id="ubg43-home-text-cleanup-runtime">(()=>{\n'use strict';\nfunction clean(){\n  document.querySelectorAll('.hero-copy p,.hero-copy .hero-stat,#status').forEach(el=>{el.style.display='none';});\n}\nclean();\nsetTimeout(clean,100);\nsetTimeout(clean,500);\nsetTimeout(clean,1200);\n})();</script>'''

def patch(text):
    text=re.sub(r'\s*<style id="ubg43-home-text-cleanup-style">.*?</style>\s*','\n',text,count=1,flags=re.S)
    text=re.sub(r'\s*<script id="ubg43-home-text-cleanup-runtime">.*?</script>\s*','\n',text,count=1,flags=re.S)
    # Remove the text itself without touching surrounding markup, so the game grid cannot be damaged.
    text=text.replace('Building your game library…','').replace('Building your game library...','')
    text=text.replace('1000+ games, quick search, automatic categories, fresh releases and personalized picks — all in one place.','')
    text=text.replace('1000+ games • new games every day • personalized recommendations','')
    pos=text.lower().rfind('</head>')
    if pos!=-1:text=text[:pos]+STYLE+'\n'+text[pos:]
    pos=text.lower().rfind('</body>')
    if pos!=-1:text=text[:pos]+SCRIPT+'\n'+text[pos:]
    return text

for p in FILES:
    if p.exists():
        p.write_text(patch(p.read_text(encoding='utf-8')),encoding='utf-8')
        print('HOME TEXT CLEANUP:',p)
