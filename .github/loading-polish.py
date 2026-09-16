from pathlib import Path
import re

INDEX = Path('index.html')

# The game library is rendered directly in index.html, so there is no reason
# to show a loading placeholder before the cards. Keep this automation step
# idempotent so future maintenance runs never put the loader back.
index = INDEX.read_text(encoding='utf-8')
index = re.sub(r'\s*<div id="loadingCard"[^>]*>.*?</div>\s*', '\n', index, count=1, flags=re.I | re.S)
index = re.sub(r'\s*<style id="loading-polish-style">.*?</style>\s*', '\n', index, count=1, flags=re.I | re.S)
INDEX.write_text(index, encoding='utf-8')
print('LOADING POLISH: removed obsolete loading placeholder; games are rendered directly from the page.')
