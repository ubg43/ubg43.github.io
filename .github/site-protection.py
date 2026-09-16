from pathlib import Path
import re

FILES = [Path('index.html'), Path('legacy-index.html')]
MARKER = 'ubg43-site-protection'

CSS = r'''<style id="ubg43-site-protection-style">
.ubg43-protection-note{margin:0 20px 18px;padding:10px 14px;border:1px solid rgba(255,255,255,.12);border-radius:12px;background:rgba(255,255,255,.055);color:rgba(255,255,255,.60);font-size:11px;text-align:center}
.ubg43-protection-note strong{color:rgba(255,255,255,.82)}
.ubg43-protected-image{user-select:none;-webkit-user-drag:none}
@media(max-width:600px){.ubg43-protection-note{margin:0 14px 16px}}
</style>'''

JS = r'''<script id="ubg43-site-protection-runtime">(()=>{
'use strict';
const NOTE='UBG43 — original site content. Please do not copy, mirror, or redistribute this site without permission.';
function protect(){
  document.querySelectorAll('.game-card img').forEach(img=>{img.classList.add('ubg43-protected-image');img.setAttribute('draggable','false')});
  const footer=document.querySelector('footer');
  if(footer && !footer.querySelector('.ubg43-protection-note')){
    const n=document.createElement('div');n.className='ubg43-protection-note';n.innerHTML='<strong>© '+new Date().getFullYear()+' UBG43</strong> · '+NOTE;
    footer.prepend(n);
  }
}
// Discourage direct image saving without disabling right-click, text selection, search, or accessibility.
document.addEventListener('dragstart',e=>{if(e.target.closest('.ubg43-protected-image'))e.preventDefault()},true);
document.addEventListener('contextmenu',e=>{if(e.target.closest('.ubg43-protected-image'))e.preventDefault()},true);
// Add a lightweight attribution when copying text from UBG43 game cards/hero content.
document.addEventListener('copy',e=>{
  const sel=window.getSelection(); if(!sel||!sel.rangeCount)return;
  const node=sel.anchorNode&&sel.anchorNode.parentElement; if(!node)return;
  if(!node.closest('.game-card,.hero,.hero-copy'))return;
  const text=sel.toString().trim(); if(!text)return;
  e.clipboardData?.setData('text/plain',text+'\n\nSource: UBG43 — https://ubg43.github.io/');
  if(e.clipboardData)e.preventDefault();
},true);
// Prevent other pages from silently embedding UBG43 as a frame.
try{if(window.top!==window.self)window.top.location.href=window.location.href}catch(_){}
new MutationObserver(protect).observe(document.body,{childList:true,subtree:true});
setTimeout(protect,80);setTimeout(protect,500);setTimeout(protect,1500);
})();</script>'''

def patch(text: str) -> str:
    if MARKER in text:
        return text
    pos=text.lower().rfind('</head>')
    if pos!=-1:
        text=text[:pos]+CSS+'\n'+text[pos:]
    pos=text.lower().rfind('</body>')
    if pos!=-1:
        text=text[:pos]+JS+'\n'+text[pos:]
    return text

for path in FILES:
    if path.exists():
        path.write_text(patch(path.read_text(encoding='utf-8')),encoding='utf-8')
        print('SITE PROTECTION:',path)
