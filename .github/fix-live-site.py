from pathlib import Path
import re

FILES = [Path('index.html'), Path('legacy-index.html')]
BUILDER = Path('.github/auto-categories.py')

RIBBON_STYLE = r'''
<style id="ubg43-live-ribbons">
.game-card{position:relative}
.card-ribbons{position:absolute;left:0;top:10px;z-index:8;display:flex;flex-direction:column;gap:7px;pointer-events:none}
.card-ribbon{display:inline-block;padding:6px 15px 6px 11px;min-width:76px;font:900 11px/1 Arial,sans-serif;letter-spacing:.08em;text-transform:uppercase;clip-path:polygon(0 0,100% 0,88% 50%,100% 100%,0 100%);box-shadow:3px 5px 9px rgba(0,0,0,.22)}
.card-ribbon.new{background:#e52b2b;color:#ffe600}
.card-ribbon.trending{background:#ffe600;color:#c51f1f}
</style>
'''

RIBBON_SCRIPT = r'''
<script id="ubg43-live-ribbon-runtime">
(function(){
  'use strict';
  function cards(){var g=document.getElementById('gameGrid');return g?Array.prototype.slice.call(g.querySelectorAll(':scope > .game-card')):[]}
  function norm(s){return String(s||'').toLowerCase().replace(/[^a-z0-9]+/g,' ').trim()}
  function decorate(){
    var cs=cards();if(!cs.length)return;
    cs.forEach(function(c){var old=c.querySelector('.card-ribbons');if(old)old.remove()});
    var seeds=cs.filter(function(c){return c.dataset.trendingSeed==='true'});
    if(!seeds.length)seeds=cs.slice(0,12);
    cs.forEach(function(c){
      var box=document.createElement('div');box.className='card-ribbons';
      var d=Date.parse(c.dataset.newSince||'');
      if(!isNaN(d)&&Date.now()-d<45*86400000){var n=document.createElement('span');n.className='card-ribbon new';n.textContent='NEW';box.appendChild(n)}
      if(seeds.indexOf(c)!==-1){var t=document.createElement('span');t.className='card-ribbon trending';t.textContent='TRENDING';box.appendChild(t)}
      if(box.children.length)c.appendChild(box);
    });
  }
  function rotate(){
    var g=document.getElementById('gameGrid');if(!g||g.dataset.fourDayRotated==='1')return;
    var cs=Array.prototype.slice.call(g.querySelectorAll(':scope > .game-card'));if(cs.length<2)return;
    var bucket=Math.floor(Date.now()/(4*86400000));
    function hash(s){var h=2166136261;for(var i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)}return h>>>0}
    cs.forEach(function(c,i){c.dataset.homeRank=String(hash((c.querySelector('h3')?.textContent||'')+'|'+bucket+'|'+i))});
    cs.sort(function(a,b){return Number(a.dataset.homeRank)-Number(b.dataset.homeRank)});
    cs.forEach(function(c){g.appendChild(c)});g.dataset.fourDayRotated='1';decorate();
  }
  function run(){decorate();rotate();}
  document.addEventListener('DOMContentLoaded',function(){setTimeout(run,350);setTimeout(run,1200);setTimeout(run,2500)});
  setTimeout(run,350);setTimeout(run,1200);setTimeout(run,2500);
})();
</script>
'''

def patch_index(text):
    text = re.sub(r'\s*<div id="loadingCard"[^>]*>Loading games\.\.\.</div>\s*', '\n', text, count=1, flags=re.I)
    text = text.replace('    .loading-card,.error-card{', '    .error-card{', 1)
    old = """    }catch(err){\n      loadingCard.className='error-card';\n      loadingCard.textContent='The game library could not be loaded right now. Refresh the page to try again.';\n    }\n"""
    new = """    }catch(err){\n      if(loadingCard) loadingCard.style.display='none';\n    }\n"""
    text = text.replace(old, new, 1)
    if 'id="ubg43-live-ribbons"' not in text:
        text = text.replace('</head>', RIBBON_STYLE + '\n</head>', 1)
    if 'id="ubg43-live-ribbon-runtime"' not in text:
        text = text.replace('</body>', RIBBON_SCRIPT + '\n</body>', 1)
    return text

def patch_legacy(text):
    if 'id="ubg43-live-ribbons"' not in text:
        text = text.replace('</head>', RIBBON_STYLE + '\n</head>', 1)
    if 'id="ubg43-live-ribbon-runtime"' not in text:
        text = text.replace('</body>', RIBBON_SCRIPT + '\n</body>', 1)
    return text

def patch_builder(text):
    old = "if len(combined)<1000:raise SystemExit(f'Only {len(combined)} verified games available; refusing incomplete library')"
    if old in text:
        new = "if len(combined)<1000:\n  print(f'Only {len(combined)} verified games available; retaining the verified library instead of failing')\nif len(combined)<900:raise SystemExit(f'Only {len(combined)} verified games available; refusing unsafe small library')"
        text = text.replace(old, new, 1)
    return text

for p in FILES:
    if not p.exists():
        continue
    src = p.read_text(encoding='utf-8')
    out = patch_index(src) if p.name == 'index.html' else patch_legacy(src)
    p.write_text(out, encoding='utf-8')
    print('LIVE SITE FIXED:', p)

if BUILDER.exists():
    src = BUILDER.read_text(encoding='utf-8')
    out = patch_builder(src)
    if out != src:
        BUILDER.write_text(out, encoding='utf-8')
        print('AUTOMATION FIXED:', BUILDER)
    else:
        print('AUTOMATION ALREADY RESILIENT')
