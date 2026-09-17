from pathlib import Path
import re

FILES=[Path('index.html'),Path('legacy-index.html')]
STYLE='''<style id="ubg43-home-text-cleanup-style">\n.hero-copy p,.hero-copy .hero-stat{display:none!important}\n</style>'''
SCRIPT='''<script id="ubg43-home-text-cleanup-runtime">(()=>{\n'use strict';\nconst BAD=['Building your game library...'];\nfunction clean(){\n  document.querySelectorAll('.hero-copy p,.hero-copy .hero-stat').forEach(el=>el.remove());\n  const root=document.body;if(!root)return;\n  const w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);\n  const hit=[];let n;while(n=w.nextNode()){if(BAD.includes((n.nodeValue||'').trim()))hit.push(n)}\n  hit.forEach(n=>{const el=n.parentElement;if(el&&el!==root)el.remove()});\n}\nclean();\nnew MutationObserver(clean).observe(document.body,{childList:true,subtree:true});\nsetTimeout(clean,50);setTimeout(clean,250);setTimeout(clean,1000);\n})();</script>'''

def patch(text):
    text=re.sub(r'\\s*<style id="ubg43-home-text-cleanup-style">.*?</style>\\s*','\\n',text,count=1,flags=re.S)
    text=re.sub(r'\\s*<script id="ubg43-home-text-cleanup-runtime">.*?</script>\\s*','\\n',text,count=1,flags=re.S)
    # Remove the generated hero description/stat from source HTML where present.
    text=re.sub(r'<p>1000\+ games, quick search, automatic categories, fresh releases and personalized picks — all in one place\.</p>','',text,flags=re.I)
    text=re.sub(r'<span class="hero-stat">1000\+ games • new games every day • personalized recommendations</span>','',text,flags=re.I)
    # Remove the old loading sentence anywhere it exists as literal HTML.
    text=re.sub(r'<[^>]*>\\s*Building your game library\.\.\.\\s*</[^>]+>','',text,flags=re.I)
    pos=text.lower().rfind('</head>')
    if pos!=-1:text=text[:pos]+STYLE+'\\n'+text[pos:]
    pos=text.lower().rfind('</body>')
    if pos!=-1:text=text[:pos]+SCRIPT+'\\n'+text[pos:]
    return text

for p in FILES:
    if p.exists():
        p.write_text(patch(p.read_text(encoding='utf-8')),encoding='utf-8')
        print('HOME TEXT CLEANUP:',p)
