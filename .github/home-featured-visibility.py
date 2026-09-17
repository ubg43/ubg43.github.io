from pathlib import Path

FILES = [Path('index.html'), Path('legacy-index.html')]

STYLE = '''<style id="ubg43-home-featured-visibility">
/* Keep the homepage focused on the main game library. Featured rails return in search mode. */
#v3Trending,#v3New{display:none!important}
body.ubg43-search-active #v3Trending,body.ubg43-search-active #v3New{display:block!important}
</style>'''

for path in FILES:
    if not path.exists():
        continue
    text = path.read_text(encoding='utf-8')
    marker_start = '<style id="ubg43-home-featured-visibility">'
    marker_end = '</style>'
    if marker_start in text:
        start = text.index(marker_start)
        end = text.index(marker_end, start) + len(marker_end)
        text = text[:start] + STYLE + text[end:]
    else:
        pos = text.lower().rfind('</head>')
        text = text[:pos] + STYLE + '\n' + text[pos:] if pos != -1 else STYLE + text
    path.write_text(text, encoding='utf-8')
    print('HOME FEATURED VISIBILITY:', path)
