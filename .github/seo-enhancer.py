from pathlib import Path
import re

FILES = [Path('index.html'), Path('legacy-index.html')]
SITE = 'https://ubg43.github.io/'
TITLE = 'Google Docs'
DESCRIPTION = (
    'UBG43 is a fast unblocked games site with 1000+ games, searchable game titles, '
    'automatic categories, new games, trending games and personalized recommendations.'
)

HEAD_MARKER = 'ubg43-seo-enhanced'

SEO_HEAD = r'''<!-- ubg43-seo-enhanced -->
<link rel="canonical" href="https://ubg43.github.io/">
<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
<meta name="description" content="UBG43 is a fast unblocked games site with 1000+ games, searchable game titles, automatic categories, new games, trending games and personalized recommendations.">
<meta property="og:type" content="website">
<meta property="og:site_name" content="UBG43">
<meta property="og:title" content="Google Docs">
<meta property="og:description" content="Play 1000+ unblocked games with fast search, automatic categories, new games, trending games and personalized recommendations.">
<meta property="og:url" content="https://ubg43.github.io/">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="Google Docs">
<meta name="twitter:description" content="Play 1000+ unblocked games with fast search, automatic categories, new games and trending picks.">
<script type="application/ld+json">
{
  "@context":"https://schema.org",
  "@type":"WebSite",
  "name":"UBG43",
  "alternateName":"UBG43 Unblocked Games",
  "url":"https://ubg43.github.io/",
  "description":"UBG43 is a fast unblocked games site with 1000+ games, searchable game titles, automatic categories, new games, trending games and personalized recommendations.",
  "publisher":{
    "@type":"Organization",
    "name":"UBG43",
    "url":"https://ubg43.github.io/"
  }
}
</script>'''


def patch(text: str) -> str:
    text = re.sub(r'\s*<!-- ubg43-seo-enhanced -->.*?</script>\s*', '\n', text, count=1, flags=re.I | re.S)
    text = re.sub(r'<title>.*?</title>', f'<title>{TITLE}</title>', text, count=1, flags=re.I | re.S)
    text = re.sub(
        r'<meta\s+name=["\']description["\']\s+content=["\'][^"\']*["\']\s*/?>',
        '<meta name="description" content="' + DESCRIPTION + '">',
        text,
        count=1,
        flags=re.I,
    )
    pos = text.lower().find('</head>')
    if pos != -1:
        text = text[:pos] + SEO_HEAD + '\n' + text[pos:]
    return text

for path in FILES:
    if path.exists():
        path.write_text(patch(path.read_text(encoding='utf-8')), encoding='utf-8')
        print('SEO ENHANCED:', path)
