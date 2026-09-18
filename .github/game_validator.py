from __future__ import annotations
import html
import re
import urllib.request
from urllib.error import HTTPError, URLError

BAD_TITLE_WORDS = (
    '404', 'not found', 'page not found', 'error', 'access denied',
    'forbidden', 'service unavailable', 'suggest games', 'login',
    'sign in', 'repository', 'readme'
)
GAME_SIGNALS = (
    '<canvas', '<iframe', '<script', 'phaser', 'pixi', 'construct',
    'unity', 'godot', 'playcanvas', 'keydown', 'keyup', 'pointerdown',
    'pointerup', 'touchstart', 'touchend', 'requestanimationframe',
    'gamepad', 'javascript game'
)
def norm(value: str) -> str:
    return re.sub(r'[^a-z0-9]+', ' ', str(value or '').lower()).strip()

def fetch(url: str, limit: int, timeout: int = 10):
    req = urllib.request.Request(url, headers={'User-Agent': 'UBG43-Game-Validator/1.0'})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        if not (200 <= resp.status < 400):
            raise ValueError(f'HTTP {resp.status}')
        return resp.status, resp.headers, resp.read(limit)

def validate_game_page(name: str, url: str) -> bool:
    if not url.startswith('https://'):
        return False
    if 'raw.githubusercontent.com/gn-math/html/' not in url:
        return False
    try:
        status, headers, body = fetch(url, 16000, 10)
        ctype = (headers.get('Content-Type') or '').lower()
        text = body.decode('utf-8', 'ignore').lower()
        if status >= 400 or len(body) < 180:
            return False
        if 'html' not in ctype and b'<html' not in body.lower() and b'<!doctype' not in body.lower():
            return False
        title_match = re.search(r'<title[^>]*>(.*?)</title>', text, re.I | re.S)
        page_title = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', title_match.group(1) if title_match else ''))).strip()
        if page_title and any(word == page_title.lower().strip() for word in BAD_TITLE_WORDS):
            return False
        head = text[:12000]
        if any(marker in head for marker in ('suggest games', 'this page could not be found', '404 not found', 'access denied')):
            return False
        signal_count = sum(1 for marker in GAME_SIGNALS if marker in head)
        return signal_count >= 2
    except (HTTPError, URLError, TimeoutError, ValueError, OSError):
        return False

def validate_cover(url: str) -> bool:
    if not url.startswith('https://'):
        return False
    try:
        status, headers, body = fetch(url, 1024, 10)
        ctype = (headers.get('Content-Type') or '').lower()
        return 200 <= status < 400 and bool(body) and (
            'image/' in ctype or re.search(r'\.(png|jpe?g|webp|gif)(\?|$)', url, re.I)
        )
    except (HTTPError, URLError, TimeoutError, ValueError, OSError):
        return False

def validate_candidate(name: str, url: str, cover: str) -> bool:
    clean = norm(name)
    if len(clean) < 2 or clean in {'game', 'html', 'index'}:
        return False
    return validate_game_page(name, url) and validate_cover(cover)
