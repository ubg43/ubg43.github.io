from pathlib import Path
import re

INDEX = Path("index.html")

if not INDEX.exists():
    raise SystemExit("index.html missing")

text = INDEX.read_text(encoding="utf-8")

# Normalize older rules that explicitly forced the homepage rails to stay visible.
text = re.sub(
    r"\.ubg43-searching\s+\.ubg43-home-secondary\s*\{\s*display\s*:\s*(?:block|none)\s*!?important?\s*\}",
    ".ubg43-searching .ubg43-home-secondary{display:none!important}",
    text,
    flags=re.I,
)
text = re.sub(
    r"\.ubg43-searching\s+#trendingSection\s*,\s*\.ubg43-searching\s+#newSection\s*\{\s*display\s*:\s*(?:block|none)\s*!important\s*\}",
    ".ubg43-searching #trendingSection,.ubg43-searching #newSection{display:none!important}",
    text,
    flags=re.I,
)

style = """<style id="ubg43-search-rail-visibility">
/* Search mode hides homepage rails. A selected category hides them too; All Games restores them. */
.ubg43-searching .ubg43-home-secondary,
.ubg43-searching #trendingSection,
.ubg43-searching #newSection,
.ubg43-category-view #trendingSection,
.ubg43-category-view #newSection{display:none!important}
</style>"""

text = re.sub(
    r'<style[^>]*id=["\']ubg43-search-rail-visibility["\'][^>]*>.*?</style>\s*',
    "",
    text,
    count=1,
    flags=re.I | re.S,
)

pos = text.lower().rfind("</head>")
if pos < 0:
    raise SystemExit("head end marker not found")

text = text[:pos] + style + "\n" + text[pos:]

required = [
    'id="searchBar"',
    'id="trendingSection"',
    'id="newSection"',
    "ubg43-search-rail-visibility",
    ".ubg43-searching #trendingSection",
    ".ubg43-searching #newSection",
]
missing = [x for x in required if x not in text]
if missing:
    raise SystemExit("Search rail visibility validation failed: " + ", ".join(missing))

INDEX.write_text(text, encoding="utf-8")
print("UBG43 search rail visibility: Trending Now and New Games are hidden while searching and restored automatically when search is cleared.")
