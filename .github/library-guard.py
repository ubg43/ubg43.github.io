from pathlib import Path
import re
from html import unescape
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

FILES = (Path('legacy-index.html'), Path('index.html'))
CARD = re.compile(r'<(?P<tag>div|article)\b[^>]*class=["\'][^"\']*\bgame-card\b[^"\']*["\'][^>]*>.*?</(?P=tag)>\s*(?=<(?:div|article)\b[^>]*class=["\'][^"\']*\bgame-card\b|</(?:div|footer|main|body|html)>|<!--)', re.I | re.S)
TITLE = re.compile(r'<h3[^>]*>(.*?)</h3>', re.I | re.S)
URL = re.compile(r"openGame\(\s*['\"]([^'\"]+)", re.I)
HREF = re.compile(r'href=["\']([^"\']+)["\']', re.I)
IMAGE = re.compile(r'<img\b[^>]*src=["\']([^"\']+)["\']', re.I)
BLOCKED = ('[!] comments', 'suggest games', 'd4c9vfywyu', '1 date danger', 'game loading')

def normalize_title(value):
    return re.sub(r'[^a-z0-9]+', ' ', unescape(re.sub(r'<[^>]+>', '', str(value or ''))).lower()).strip()

def normalize_url(value):
    raw = str(value or '').strip()
    if not raw:
        return ''
    try:
        p = urlsplit(raw)
        if p.scheme.lower() not in ('http', 'https') or not p.netloc:
            return re.sub(r'#.*$', '', raw).rstrip('/').lower()
        query = [(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True)
                 if not k.lower().startswith('utm_') and k.lower() not in {'fbclid', 'gclid', 'ref', 'referrer'}]
        path = re.sub(r'/+', '/', p.path or '/')
        if path != '/':
            path = path.rstrip('/')
        return urlunsplit((p.scheme.lower(), p.netloc.lower(), path, urlencode(sorted(query)), '')).rstrip('/')
    except Exception:
        return re.sub(r'#.*$', '', raw).rstrip('/').lower()

def card_info(card):
    tm = TITLE.search(card)
    um = URL.search(card) or HREF.search(card)
    im = IMAGE.search(card)
    return (
        normalize_title(tm.group(1) if tm else ''),
        normalize_url(um.group(1) if um else ''),
        (im.group(1).strip() if im else '')
    )

def dedupe_text(text):
    seen_titles, seen_urls = set(), set()
    out, pos, removed = [], 0, 0
    for m in CARD.finditer(text):
        out.append(text[pos:m.start()])
        card = m.group(0)
        title, url, image = card_info(card)
        invalid = not title or not url or not image or any(x in title for x in BLOCKED)
        duplicate = title in seen_titles or url in seen_urls
        if invalid or duplicate:
            removed += 1
        else:
            seen_titles.add(title)
            seen_urls.add(url)
            out.append(card)
        pos = m.end()
    out.append(text[pos:])
    return ''.join(out), removed, len(seen_titles), len(seen_urls)

def guard_file(path):
    if not path.exists():
        return
    old = path.read_text(encoding='utf-8')
    new, removed, titles, urls = dedupe_text(old)
    if new != old:
        path.write_text(new, encoding='utf-8')
    print(f'LIBRARY GUARD {path}: removed {removed}; kept {titles} unique titles / {urls} unique URLs')

def validate_file(path):
    problems = []
    if not path.exists():
        return problems
    text = path.read_text(encoding='utf-8')
    seen_titles, seen_urls = set(), set()
    for number, match in enumerate(CARD.finditer(text), 1):
        title, url, image = card_info(match.group(0))
        if not title or not url or not image:
            problems.append(f'{path}: card {number} missing title, URL, or image')
            continue
        if title in seen_titles:
            problems.append(f'{path}: duplicate title {title}')
        if url in seen_urls:
            problems.append(f'{path}: duplicate URL {url}')
        seen_titles.add(title)
        seen_urls.add(url)
    return problems

def main():
    import sys
    if '--check' in sys.argv:
        problems = []
        for path in FILES:
            problems.extend(validate_file(path))
        if problems:
            print('LIBRARY GUARD FAILED')
            print('\n'.join(problems[:50]))
            raise SystemExit(1)
        print('LIBRARY GUARD PASSED: no duplicate game titles/URLs; every retained card has a title, URL, and image.')
        return
    for path in FILES:
        guard_file(path)
    print('LIBRARY GUARD COMPLETE')

if __name__ == '__main__':
    main()
