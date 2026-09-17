from pathlib import Path
import re

FILES=[Path('index.html'),Path('legacy-index.html')]

STYLE='''<style id="ubg43-runtime-stability-style">\n/* Prevent runaway layout observers from locking the page while preserving buttons, search and game cards. */\n#status{display:none!important}\n</style>'''

# The previous hotfix installed a body-wide MutationObserver that called normalize(),
# while normalize() itself changed the DOM. That feedback loop can lock the browser.
BAD_OBSERVER='new MutationObserver(()=>normalize()).observe(document.body,{childList:true,subtree:true});'

# Remove the observer and keep all other runtime behaviour intact.
def patch(text):
    text=text.replace(BAD_OBSERVER,'')
    # Remove any older copy of the same observer with harmless whitespace differences.
    text=re.sub(r'new MutationObserver\(\(\)=>normalize\(\)\)\.observe\(document\.body,\{childList:true,subtree:true\}\);','',text)
    text=re.sub(r'\s*<style id="ubg43-runtime-stability-style">.*?</style>\s*','\n',text,count=1,flags=re.S)
    pos=text.lower().rfind('</head>')
    if pos!=-1:text=text[:pos]+STYLE+'\n'+text[pos:]
    return text

for p in FILES:
    if p.exists():
        text=patch(p.read_text(encoding='utf-8'))
        p.write_text(text,encoding='utf-8')
        print('RUNTIME STABILITY FIX:',p)
