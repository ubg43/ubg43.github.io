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

# Inline cards created by older builders may pass a second title argument.
INLINE = re.compile(r"onclick=\"openGame\(\s*(['\"])(.*?)\1(?:\s*,[^)]*)?\)\"", re.I)

for p in FILES:
    if not p.exists():
        continue
    text = p.read_text(encoding='utf-8')
    original = text

    # Replace the generated legacy play() implementation, including the old
    # about:blank -> iframe wrapper, wherever that implementation exists.
    text, _ = re.subn(
        r'function play\(g\)\{.*?\nfunction recordTrend\(g\)',
        DIRECT_PLAY + 'function recordTrend(g)',
        text,
        count=1,
        flags=re.S,
    )

    # Replace inline openGame handlers with ordinary direct window.open calls.
    def inline_replace(m):
        url = m.group(2).replace("'", '%27')
        return 'onclick="window.open(\'' + url + '\',\'_blank\')"'
    text = INLINE.sub(inline_replace, text)

    # Install the final direct opener after every other page script.
    text = re.sub(r'\s*<script id="ubg43-direct-launch-runtime">.*?</script>\s*', '\n', text, count=1, flags=re.S)
    pos = text.lower().rfind('</body>')
    if pos >= 0:
        text = text[:pos] + '\n' + DIRECT_GLOBAL + '\n' + text[pos:]
    else:
        text += '\n' + DIRECT_GLOBAL

    # Do not fail just because some hidden/legacy source contains an iframe in
    # unrelated content. The visible launch path is explicitly direct now.
    visible_launcher_bad = bool(re.search(r"window\.open\(\s*['\"]about:blank['\"]", text, re.I))
    direct_marker = 'ubg43-direct-launch-runtime' in text
    if visible_launcher_bad or not direct_marker:
        raise SystemExit(f'Direct launch repair validation failed for {p}')

    if text != original:
        p.write_text(text, encoding='utf-8')
        print(f'GAME LAUNCH FIX: repaired {p}')
    else:
        print(f'GAME LAUNCH FIX: already repaired {p}')
