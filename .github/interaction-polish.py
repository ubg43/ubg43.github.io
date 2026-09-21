from pathlib import Path
import re

INDEX = Path('index.html')
TITLE = 'UBG43 - 1000+ Unblocked Games'
MARKER = '<!-- UBG43 interaction polish v2 -->'
STYLE_ID = 'ubg43-interaction-polish-style'
SCRIPT_ID = 'ubg43-interaction-polish-runtime'

if not INDEX.exists():
    raise SystemExit('index.html missing')

text = INDEX.read_text(encoding='utf-8')

# Restore the proper browser title after the legacy finalizer's compatibility title.
text = re.sub(r'<title>[^<]*</title>', f'<title>{TITLE}</title>', text, count=1, flags=re.I)

# Keep Trending Now and New Games visible on the homepage and in search mode.
text = text.replace('.ubg43-home-secondary{display:none}', '.ubg43-home-secondary{display:block}')
text = text.replace('.ubg43-searching .ubg43-home-secondary{display:none}', '.ubg43-searching .ubg43-home-secondary{display:block}')

style = f'''<style id="{STYLE_ID}">
/* UBG43 interaction polish v2 */
.search-clear{{
  position:absolute !important;
  right:8px !important;
  top:50% !important;
  width:38px !important;
  height:38px !important;
  transform:translateY(-50%) !important;
  padding:0 !important;
  margin:0 !important;
  display:none;
  align-items:center !important;
  justify-content:center !important;
  line-height:0 !important;
  text-align:center !important;
  text-indent:0 !important;
  border:0 !important;
  box-sizing:border-box !important;
  font-size:21px !important;
  font-weight:800 !important;
}}
.search-clear:hover{{background:#eef3fb;color:#12356d}}
.search-shell .results{{pointer-events:auto}}
</style>'''

text = re.sub(
    rf'<style[^>]*id=["\']{re.escape(STYLE_ID)}["\'][^>]*>.*?</style>\s*',
    '',
    text,
    count=1,
    flags=re.I | re.S,
)
text = text.replace('</head>', f'{style}\n</head>', 1)

runtime = f'''<script id="{SCRIPT_ID}">
(()=>{{
'use strict';
const shell=document.querySelector('.search-shell');
const search=document.getElementById('searchBar');
const results=document.getElementById('searchResults');
const closeSearchUi=()=>{{
  if(results)results.classList.remove('open');
  if(search)search.blur();
}};
document.addEventListener('pointerdown',e=>{{
  if(shell && !shell.contains(e.target))closeSearchUi();
}},{{capture:true}});
document.addEventListener('click',e=>{{
  if(shell && !shell.contains(e.target))closeSearchUi();
}},{{capture:true}});
window.addEventListener('scroll',()=>{{
  if(results)results.classList.remove('open');
}},{{passive:true}});
}})();
</script>'''

text = re.sub(
    rf'<script[^>]*id=["\']{re.escape(SCRIPT_ID)}["\'][^>]*>.*?</script>\s*',
    '',
    text,
    count=1,
    flags=re.I | re.S,
)
body_pos = text.lower().rfind('</body>')
if body_pos < 0:
    raise SystemExit('body end marker not found')
text = text[:body_pos] + runtime + '\n' + text[body_pos:]

# Keep the NEW/TRENDING badge system present and styled.
required = ['.ubg43-badge.new', '.ubg43-badge.trending', 'function isTrending', 'function setSearchMode', f'id="{SCRIPT_ID}"', f'id="{STYLE_ID}"']
missing = [x for x in required if x not in text]
if missing:
    raise SystemExit('Interaction polish validation failed: ' + ', '.join(missing))

INDEX.write_text(text, encoding='utf-8')
print('UBG43 interaction polish applied: outside-click search close, centered clear button, correct title, homepage rails visible on home and search, and NEW/TRENDING badges preserved.')
