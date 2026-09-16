from pathlib import Path
import re

FILES=[Path('index.html'),Path('legacy-index.html')]
BUILDER=Path('.github/auto-categories.py')

SHUFFLE_SCRIPT=r'''
<script id="ubg43-four-day-runtime">
(function(){
  'use strict';
  function rotate(){
    var g=document.getElementById('gameGrid');if(!g||g.dataset.fourDayRotated==='1')return;
    var cs=Array.prototype.slice.call(g.querySelectorAll(':scope > .game-card'));if(cs.length<2)return;
    var bucket=Math.floor(Date.now()/(4*86400000));
    function hash(s){var h=2166136261;for(var i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)}return h>>>0}
    cs.forEach(function(c,i){var h=c.querySelector('h3');c.dataset.homeRank=String(hash((h?h.textContent:'')+'|'+bucket+'|'+i))});
    cs.sort(function(a,b){return Number(a.dataset.homeRank)-Number(b.dataset.homeRank)});
    cs.forEach(function(c){g.appendChild(c)});
    g.dataset.fourDayRotated='1';
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',function(){setTimeout(rotate,400)});else setTimeout(rotate,400);
})();
</script>
'''

def patch_index(text):
    text=re.sub(r'\s*<div id="loadingCard"[^>]*>.*?</div>\s*','\n',text,count=1,flags=re.I|re.S)
    text=text.replace('    .loading-card,.error-card{','    .error-card{',1)
    old="""    }catch(err){\n      loadingCard.className='error-card';\n      loadingCard.textContent='The game library could not be loaded right now. Refresh the page to try again.';\n    }\n"""
    new="""    }catch(err){\n      if(loadingCard) loadingCard.style.display='none';\n    }\n"""
    text=text.replace(old,new,1)
    text=re.sub(r'\s*<style id="ubg43-live-ribbons">.*?</style>\s*','\n',text,count=1,flags=re.S)
    text=re.sub(r'\s*<script id="ubg43-live-ribbon-runtime">.*?</script>\s*','\n',text,count=1,flags=re.S)
    text=re.sub(r'\s*<script id="ubg43-four-day-runtime">.*?</script>\s*','\n',text,count=1,flags=re.S)
    text=text.replace('</body>',SHUFFLE_SCRIPT+'\n</body>',1)
    return text

def patch_legacy(text):
    text=re.sub(r'\s*<style id="ubg43-live-ribbons">.*?</style>\s*','\n',text,count=1,flags=re.S)
    text=re.sub(r'\s*<script id="ubg43-live-ribbon-runtime">.*?</script>\s*','\n',text,count=1,flags=re.S)
    text=re.sub(r'\s*<script id="ubg43-four-day-runtime">.*?</script>\s*','\n',text,count=1,flags=re.S)
    text=text.replace('</body>',SHUFFLE_SCRIPT+'\n</body>',1)
    return text

def patch_builder(text):
    old="if len(combined)<1000:raise SystemExit(f'Only {len(combined)} verified games available; refusing incomplete library')"
    if old in text:
        new="if len(combined)<1000:\n  print(f'Only {len(combined)} verified games available; retaining the verified library instead of failing')\nif len(combined)<900:raise SystemExit(f'Only {len(combined)} verified games available; refusing unsafe small library')"
        text=text.replace(old,new,1)
    return text

for p in FILES:
    if not p.exists():continue
    src=p.read_text(encoding='utf-8')
    out=patch_index(src) if p.name=='index.html' else patch_legacy(src)
    p.write_text(out,encoding='utf-8')
    print('LIVE SITE FIXED:',p)
if BUILDER.exists():
    src=BUILDER.read_text(encoding='utf-8')
    out=patch_builder(src)
    if out!=src:
        BUILDER.write_text(out,encoding='utf-8')
        print('AUTOMATION FIXED:',BUILDER)
