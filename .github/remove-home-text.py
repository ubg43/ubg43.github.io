from pathlib import Path
import re

FILES=[Path('index.html'),Path('legacy-index.html')]
STYLE='''<style id="ubg43-home-text-cleanup-style">\n/* Remove the extra library status/marketing lines while keeping the game library itself intact. */\n.hero-copy p,.hero-copy .hero-stat,#status{display:none!important}\n</style>'''
SCRIPT='''<script id="ubg43-home-text-cleanup-runtime">(()=>{\n'use strict';\nfunction clean(){\n  document.querySelectorAll('.hero-copy p,.hero-copy .hero-stat,#status').forEach(el=>el.remove());\n}\nclean();\nsetTimeout(clean,50);\nsetTimeout(clean,250);\nsetTimeout(clean,1000);\n})();</script>'''

def patch(text):
    text=re.sub(r'\s*<style id="ubg43-home-text-cleanup-style">.*?</style>\s*','\n',text,count=1,flags=re.S)
    text=re.sub(r'\s*<script id="ubg43-home-text-cleanup-runtime">.*?</script>\s*','\n',text,count=1,flags=re.S)
    # Remove the generated hero description/stat from source HTML where present.
    text=re.sub(r'<p>1000\+ games, quick search, automatic categories, fresh releases and personalized picks — all in one place\.</p>','',text,flags=re.I)
    text=re.sub(r'<span class="hero-stat">1000\+ games • new games every day • personalized recommendations</span>','',text,flags=re.I)
    # Remove the visible build-status element from source HTML.
    text=re.sub(r'<div id="status"[^>]*>\s*Building your game library[.…]*\s*</div>','',text,flags=re.I)
    text=text.replace('Building your game library…','').replace('Building your game library...','')
    pos=text.lower().rfind('</head>')
    if pos!=-1:text=text[:pos]+STYLE+'\n'+text[pos:]
    pos=text.lower().rfind('</body>')
    if pos!=-1:text=text[:pos]+SCRIPT+'\n'+text[pos:]
    return text

for p in FILES:
    if p.exists():
        p.write_text(patch(p.read_text(encoding='utf-8')),encoding='utf-8')
        print('HOME TEXT CLEANUP:',p)
