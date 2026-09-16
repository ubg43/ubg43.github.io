from pathlib import Path
import re

FILES = [Path('index.html'), Path('legacy-index.html')]

DIRECT_PLAY = """function play(g){
  try{if(typeof recordTrend==='function')recordTrend(g)}catch(_){ }
  const url=String(g&&g.url||'').trim();
  if(!url)return;
  const w=window.open(url,'_blank','noopener,noreferrer');
  if(!w)window.location.href=url;
}
"""

DIRECT_GLOBAL = r'''<script id="ubg43-direct-launch-runtime">
(()=>{
  'use strict';
  const openDirect=url=>{url=String(url||'').trim();if(!url)return;const w=window.open(url,'_blank','noopener,noreferrer');if(!w)window.location.href=url};
  window.openGame=openDirect;
  document.addEventListener('click',e=>{
    const card=e.target.closest('.game-card');
    if(!card)return;
    const a=card.getAttribute('onclick')||'';
    const m=a.match(/openGame\(\s*['\"]([^'\"]+)['\"]/i);
    if(!m)return;
    e.preventDefault();
    e.stopImmediatePropagation();
    openDirect(m[1]);
  },true);
})();
</script>'''

INLINE = re.compile(r"onclick=\"openGame\(\s*(['\"])(.*?)\1(?:\s*,[^)]*)?\)\"", re.I)

for p in FILES:
    if not p.exists():
        continue
    text = p.read_text(encoding='utf-8')
    original = text

    # Main index: replace the old about:blank -> iframe play() implementation.
    text, _ = re.subn(
        r'function play\(g\)\{.*?\nfunction recordTrend\(g\)',
        DIRECT_PLAY + 'function recordTrend(g)',
        text,
        count=1,
        flags=re.S,
    )

    def inline_replace(m):
        url = m.group(2).replace("'", '%27')
        return 'onclick="window.open(\'' + url + '\',\'_blank\')"'
    text = INLINE.sub(inline_replace, text)

    text = re.sub(r'\s*<script id="ubg43-direct-launch-runtime">.*?</script>\s*', '\n', text, count=1, flags=re.S)
    pos = text.lower().rfind('</body>')
    if pos >= 0:
        text = text[:pos] + '\n' + DIRECT_GLOBAL + '\n' + text[pos:]
    else:
        text += '\n' + DIRECT_GLOBAL

    # The live homepage must be completely free of the old wrapper. legacy-index
    # is parsed only as a card catalogue by index.html, so its old inert source
    # scripts do not execute in the live page.
    if p.name == 'index.html' and re.search(r"window\.open\(\s*['\"]about:blank['\"]", text, re.I):
        raise SystemExit('Live index still contains the old about:blank launcher')
    if 'ubg43-direct-launch-runtime' not in text:
        raise SystemExit(f'Direct launch runtime missing from {p}')

    if text != original:
        p.write_text(text, encoding='utf-8')
        print(f'GAME LAUNCH FIX: repaired {p}')
    else:
        print(f'GAME LAUNCH FIX: already repaired {p}')
