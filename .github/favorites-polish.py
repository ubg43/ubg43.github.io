from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

old='.search-clear{position:absolute;right:7px;top:50%;transform:translateY(-50%);display:none;width:30px;height:30px;border:0;border-radius:8px;background:transparent;color:#69758a;cursor:pointer;font-size:19px;font-weight:800;line-height:1;z-index:2;transition:transform .15s ease,background .15s ease}'
new='.search-clear{position:absolute;right:7px;top:50%;transform:translateY(-50%);display:none;width:30px;height:30px;padding:0;border:0;border-radius:8px;background:transparent;color:#69758a;cursor:pointer;font-size:19px;font-weight:800;line-height:1;z-index:2;transition:transform .15s ease,background .15s ease;align-items:center;justify-content:center;text-align:center}'
if old not in s: raise SystemExit('search clear style anchor not found')
s=s.replace(old,new,1)
s=s.replace("searchClear.style.display=query?'block':'none';","searchClear.style.display=query?'flex':'none';",1)
s=s.replace("searchClear.style.display='block';","searchClear.style.display='flex';",1)
icon='.search-icon{position:absolute;left:15px;top:50%;width:16px;height:16px;transform:translateY(-58%);border:2px solid #6c7890;border-radius:50%;pointer-events:none}'
if icon in s and '.search-shell:focus-within .search-icon' not in s:
    s=s.replace(icon,icon+'\n    .search-shell:focus-within .search-icon{opacity:1;visibility:visible}',1)
cat='.category-toggle{height:38px;display:inline-flex;'
if cat in s and '.category-toggle{margin-left:auto;height:38px' not in s:
    s=s.replace(cat,'.category-toggle{margin-left:auto;height:38px;display:inline-flex;',1)
close='.category-close{width:34px;height:34px;border:1px solid rgba(255,255,255,.2);border-radius:10px;background:rgba(255,255,255,.06);color:#fff;font-size:25px;line-height:1;cursor:pointer;transition:background .15s ease,transform .15s ease}'
close_new='.category-close{width:34px;height:34px;padding:0;border:1px solid rgba(255,255,255,.2);border-radius:10px;background:rgba(255,255,255,.06);color:#fff;font-size:25px;line-height:1;cursor:pointer;display:inline-flex;align-items:center;justify-content:center;text-align:center;transition:background .15s ease,transform .15s ease}'
if close not in s: raise SystemExit('category close style anchor not found')
s=s.replace(close,close_new,1)
s=s.replace('@media(max-width:830px){.category-toggle-label{display:none}.category-toggle{width:42px;padding:0}.header-actions{margin-left:auto}}','@media(max-width:830px){.category-toggle-label{display:none}.category-toggle{width:42px;padding:0;margin-left:auto}.header-actions{margin-left:0}}',1)
s=s.replace('@media(max-width:570px){.category-toggle{width:100%;height:38px}.header-actions{margin-left:0}}','@media(max-width:570px){.category-toggle{width:42px;height:38px;margin-left:auto}.header-actions{margin-left:0}}',1)
# Fix the two-row recommendation carousel class mismatch.
if "recGrid.classList.add('recommendation-track')" not in s:
    anchor="      recGrid.innerHTML='';"
    if anchor not in s: raise SystemExit('recommendation render anchor not found')
    s=s.replace(anchor,anchor+"\n      recGrid.classList.add('recommendation-track');",1)

p.write_text(s,encoding='utf-8')
