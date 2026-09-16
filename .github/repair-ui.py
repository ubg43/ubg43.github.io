from pathlib import Path
import re

FILES = [Path('index.html'), Path('legacy-index.html')]
MARKER = '<!-- UBGR43-UI-REPAIR-V1 -->'
SCRIPT = r'''<script id="ubg43-ui-repair">
(function(){
  'use strict';
  function $(id){return document.getElementById(id)}
  function cards(){var grid=$('gameGrid');return grid?Array.prototype.slice.call(grid.querySelectorAll('.game-card')):[]}
  function norm(s){return String(s||'').toLowerCase().replace(/[^a-z0-9]+/g,' ').trim()}
  function title(card){var h=card&&card.querySelector('h3');return h?(h.textContent||'').trim():'Game'}
  function img(card){var i=card&&card.querySelector('img');return i?i.getAttribute('src')||'':''}
  function url(card){
    var a=card&&card.getAttribute('onclick')||'';
    var m=a.match(/openGame\(\s*['\"]([^'\"]+)['\"]\s*\)/);
    return m?m[1]:'';
  }
  window.openGame=function(u){
    if(!u)return false;
    var w=window.open('about:blank','_blank');
    if(!w){window.location.href=u;return false;}
    var esc=String(u).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/"/g,'&quot;');
    w.document.open();
    w.document.write('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Google Docs</title><style>html,body{margin:0;width:100%;height:100%;overflow:hidden;background:#000}iframe{display:block;width:100%;height:100%;border:0}</style></head><body><iframe src="'+esc+'" allow="fullscreen;autoplay;gamepad;clipboard-read;clipboard-write" allowfullscreen></iframe></body></html>');
    w.document.close();
    return false;
  };
  function hideLoading(){var l=$('loadingCard');if(l)l.style.display='none'}
  function showLoading(){var l=$('loadingCard');if(l)l.style.display='block'}
  function setupSearch(){
    var input=$('searchBar'), clear=$('searchClear'), results=$('searchResults');
    if(!input)return;
    function render(){
      var q=norm(input.value), all=cards(), hits=[];
      all.forEach(function(c){var t=norm(title(c));if(!q||t.indexOf(q)!==-1)hits.push(c)});
      if(clear)clear.style.display=input.value?'inline-flex':'none';
      if(results){
        results.innerHTML='';
        if(q){
          results.classList.add('is-open');results.hidden=false;
          if(!hits.length){results.innerHTML='<div class="search-empty">No games found</div>';}
          else hits.slice(0,8).forEach(function(c){
            var b=document.createElement('button');b.type='button';b.className='search-result';
            var im=document.createElement('img');im.src=img(c);im.alt='';im.loading='lazy';
            var copy=document.createElement('span');copy.className='search-result-copy';
            var name=document.createElement('span');name.className='search-result-title';name.textContent=title(c);
            copy.appendChild(name);b.appendChild(im);b.appendChild(copy);
            b.addEventListener('click',function(){window.openGame(url(c));results.classList.remove('is-open');results.hidden=true;});
            results.appendChild(b);
          });
        }else{results.classList.remove('is-open');results.hidden=true;}
      }
      all.forEach(function(c){c.style.display=!q||norm(title(c)).indexOf(q)!==-1?'':'none'});
      if(input.value){try{localStorage.setItem('ubg43_last_search',input.value)}catch(e){}}
    }
    input.addEventListener('input',render);input.addEventListener('search',render);
    input.addEventListener('keydown',function(e){if(e.key==='Escape'){input.value='';render();input.blur()}});
    if(clear)clear.addEventListener('click',function(){input.value='';render();input.focus()});
    document.addEventListener('click',function(e){if(results&& !input.contains(e.target) && !results.contains(e.target)){results.classList.remove('is-open');results.hidden=true}});
    render();
  }
  function setupButtons(){
    var random=$('randomGameButton'), report=$('reportGameButton');
    if(random)random.addEventListener('click',function(){var cs=cards().filter(function(c){return c.offsetParent!==null});if(cs.length)window.openGame(url(cs[Math.floor(Math.random()*cs.length)]));});
    if(report)report.addEventListener('click',function(){window.location.href='mailto:ubg43@proton.me?subject=Game%20report%20or%20suggestion';});
  }
  function setupCategories(){
    var toggle=$('categoryToggle'), side=$('categorySidebar'), overlay=$('categoryOverlay'), close=$('categoryClose'), list=$('categoryList');
    if(!side||!list)return;
    var cats={};cards().forEach(function(c){var k=c.dataset.category||'Other';cats[k]=(cats[k]||0)+1});
    list.innerHTML='';Object.keys(cats).sort().forEach(function(k){var b=document.createElement('button');b.type='button';b.className='category-item';b.innerHTML='<span class="category-item-main"><span class="category-dot"></span><span class="category-name"></span></span><span class="category-count"></span>';b.querySelector('.category-name').textContent=k;b.querySelector('.category-count').textContent=cats[k];b.addEventListener('click',function(){cards().forEach(function(c){c.style.display=(k==='Other'||(c.dataset.category||'Other')===k)?'':'none'});side.classList.remove('is-open');side.setAttribute('aria-hidden','true');if(overlay){overlay.classList.remove('is-open');overlay.hidden=true}});list.appendChild(b)});
    function open(){side.classList.add('is-open');side.setAttribute('aria-hidden','false');if(overlay){overlay.hidden=false;requestAnimationFrame(function(){overlay.classList.add('is-open')})}}
    function shut(){side.classList.remove('is-open');side.setAttribute('aria-hidden','true');if(overlay){overlay.classList.remove('is-open');setTimeout(function(){overlay.hidden=true},200)}}
    if(toggle)toggle.addEventListener('click',open);if(close)close.addEventListener('click',shut);if(overlay)overlay.addEventListener('click',shut);document.addEventListener('keydown',function(e){if(e.key==='Escape')shut()});
  }
  function boot(){hideLoading();setupSearch();setupButtons();setupCategories();cards().forEach(function(c){c.addEventListener('click',function(){var u=url(c);if(u)window.openGame(u);},false)});}
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot);else boot();
})();
</script>'''

for p in FILES:
    if not p.exists():
        continue
    text = p.read_text(encoding='utf-8')
    if MARKER in text:
        continue
    inject = '\n' + MARKER + '\n' + SCRIPT + '\n'
    if '</body>' in text.lower():
        pos = text.lower().rfind('</body>')
        text = text[:pos] + inject + text[pos:]
    else:
        text += inject
    p.write_text(text, encoding='utf-8')
    print(f'REPAIRED UI: {p}')
