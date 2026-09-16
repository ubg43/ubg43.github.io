from pathlib import Path
import re

FILES = [Path('index.html'), Path('legacy-index.html')]

# Replace the old about:blank + iframe game opener with a direct navigation opener.
DIRECT_PLAY = """function play(g){
  try{if(typeof recordTrend==='function')recordTrend(g)}catch(_){ }
  const url=String(g&&g.url||'').trim();
  if(!url)return;
  const w=window.open(url,'_blank','noopener,noreferrer');
  if(!w)window.location.href=url;
}
"""

# Inline cards created by the automated builders call openGame('URL'). Make those
# handlers direct too, so there is no iframe layer left anywhere in the card path.
INLINE = re.compile(r"onclick=\"openGame\(\s*'([^']+)'\s*\)\"", re.I)
INLINE_DQ = re.compile(r'onclick=\"openGame\(\s*\"([^\"]+)\"\s*\)\"', re.I)

for p in FILES:
    if not p.exists():
        continue
    text = p.read_text(encoding='utf-8')
    original = text

    # Catch the generated legacy play() implementation, including the large
    # about:blank document.write iframe wrapper.
    text, n = re.subn(
        r'function play\(g\)\{.*?\nfunction recordTrend\(g\)',
        DIRECT_PLAY + 'function recordTrend(g)',
        text,
        count=1,
        flags=re.S,
    )

    # Normalize static/expanded cards away from openGame() inline handlers.
    text = INLINE.sub(lambda m: 'onclick="window.open(\'' + m.group(1).replace("'", '%27') + '\',\'_blank\')"', text)
    text = INLINE_DQ.sub(lambda m: 'onclick="window.open(\'' + m.group(1).replace("'", '%27') + '\',\'_blank\')"', text)

    # Safety check: the repaired page must not contain the old iframe launcher.
    if 'window.open(\'about:blank\'' in text or '<iframe src="\'+u+\'"' in text:
        raise SystemExit(f'Launch fix failed to remove iframe opener from {p}')

    if text != original:
        p.write_text(text, encoding='utf-8')
        print(f'GAME LAUNCH FIX: repaired {p}')
    else:
        print(f'GAME LAUNCH FIX: no legacy iframe launcher found in {p}')
