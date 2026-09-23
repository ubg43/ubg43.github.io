#!/usr/bin/env python3
"""
Repair missing game thumbnails by finding the game's real published cover image.
Priority:
1. Existing thumbnail if it still serves an actual image.
2. og:image / twitter:image / JSON-LD image metadata from the game's own page.
3. Common image metadata on the page (itemprop=image, image_src, apple-touch-icon).
4. Limited GitHub code search for a matching real cover URL when page metadata is unavailable.

No generated or AI-created artwork is used.
"""
from __future__ import annotations

import html
import json
import re
import time
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, unquote, urljoin, urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

INDEX = Path("index.html")
LEGACY = Path("legacy-index.html")
MAX_SEARCHES = 24
UA = "Mozilla/5.0 (compatible; UBG43-Cover-Resolver/1.0; +https://ubg43.github.io/)"

class MetaParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.meta: list[tuple[str, str, str]] = []
        self.links: list[tuple[str, str, str]] = []
        self.jsonld: list[str] = []
    def handle_starttag(self, tag, attrs):
        d = {k.lower(): v or "" for k, v in attrs}
        if tag.lower() == "meta":
            self.meta.append((d.get("property","").lower(), d.get("name","").lower(), d.get("content","")))
        elif tag.lower() == "link":
            self.links.append((d.get("rel","").lower(), d.get("href",""), d.get("type","").lower()))
    def handle_data(self, data):
        pass
    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

def fetch_text(url: str, limit: int = 900_000) -> str:
    req = Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml"})
    with urlopen(req, timeout=10) as r:
        raw = r.read(limit)
        charset = r.headers.get_content_charset() or "utf-8"
        return raw.decode(charset, errors="replace")

def fetch_ok(url: str) -> bool:
    if not url.lower().startswith(("http://","https://")):
        return False
    try:
        req = Request(url, headers={"User-Agent": UA, "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.7", "Range":"bytes=0-65535"})
        with urlopen(req, timeout=8) as r:
            ct = (r.headers.get("Content-Type") or "").lower()
            sample = r.read(32)
            return r.status < 400 and ("image/" in ct or sample.startswith((b"\x89PNG", b"\xff\xd8\xff", b"RIFF", b"GIF8", b"<svg", b"<SVG")))
    except Exception:
        return False

def game_url(card: str) -> str:
    patterns = [
        r'data-url=["\']([^"\']+)["\']',
        r"window\.open\(\s*['\"]([^'\"]+)['\"]",
        r'onclick=["\'][^"\']*?open\(\s*\x27([^\x27]+)\x27',
    ]
    for p in patterns:
        m = re.search(p, card, re.I)
        if m:
            return html.unescape(m.group(1))
    return ""

def card_title(card: str) -> str:
    m = re.search(r'<h3[^>]*>([\s\S]*?)</h3>', card, re.I)
    if m:
        return re.sub(r"<[^>]+>", "", html.unescape(m.group(1))).strip()
    m = re.search(r'alt=["\']([^"\']+)["\']', card, re.I)
    return html.unescape(m.group(1)).strip() if m else "UBG43 Game"

def image_url(card: str) -> str:
    m = re.search(r'<img\b[^>]*\bsrc=["\']([^"\']+)["\']', card, re.I)
    return html.unescape(m.group(1)) if m else ""

def resolve_metadata(page_url: str, body: str) -> list[str]:
    p = MetaParser()
    try:
        p.feed(body)
    except Exception:
        pass
    out: list[str] = []
    for prop, name, content in p.meta:
        if not content:
            continue
        if prop in {"og:image","og:image:url","twitter:image","twitter:image:src","image","thumbnail"} or name in {"og:image","twitter:image","twitter:image:src","image","thumbnail","msapplication-tileimage"}:
            out.append(content.strip())
    for rel, href, typ in p.links:
        if not href:
            continue
        if any(x in rel for x in ("image_src","apple-touch-icon","thumbnail")) or typ.startswith("image/"):
            out.append(href.strip())
    for m in re.finditer(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>([\s\S]*?)</script>', body, re.I):
        raw = html.unescape(m.group(1)).strip()
        try:
            obj = json.loads(raw)
        except Exception:
            continue
        stack = obj if isinstance(obj, list) else [obj]
        while stack:
            cur = stack.pop()
            if isinstance(cur, dict):
                val = cur.get("image")
                if isinstance(val, str):
                    out.append(val)
                elif isinstance(val, dict) and isinstance(val.get("url"), str):
                    out.append(val["url"])
                elif isinstance(val, list):
                    for x in val:
                        if isinstance(x, str): out.append(x)
                        elif isinstance(x, dict) and isinstance(x.get("url"), str): out.append(x["url"])
                for x in cur.get("@graph", []) if isinstance(cur.get("@graph"), list) else []:
                    stack.append(x)
    for m in re.finditer(r'<[^>]+itemprop=["\']image["\'][^>]+(?:src|content)=["\']([^"\']+)["\']', body, re.I):
        out.append(m.group(1))
    seen=set()
    clean=[]
    for x in out:
        x=html.unescape(x).strip()
        if not x or x.startswith(("data:","javascript:")): continue
        if x not in seen:
            seen.add(x); clean.append(x)
    return clean

def github_search_candidates(title: str, limit: int = 10) -> list[str]:
    q = quote(f'"{title}" "og:image"')
    url = "https://api.github.com/search/code?q=" + q + "&per_page=" + str(limit)
    try:
        req = Request(url, headers={"User-Agent": UA, "Accept":"application/vnd.github+json"})
        with urlopen(req, timeout=10) as r:
            data=json.loads(r.read(350_000).decode("utf-8","replace"))
        out=[]
        for item in data.get("items", []):
            txt=(item.get("html_url") or "")
            if txt:
                raw=txt.replace("/blob/","/raw/")
                # Search result pages are only a lead; actual image URLs are extracted by page parsing.
                try:
                    body=fetch_text(item.get("html_url") or "", 350_000)
                    out.extend(resolve_metadata(item.get("html_url") or "", body))
                except Exception:
                    pass
            if len(out)>=20: break
        return out
    except Exception:
        return []

def replace_src(card: str, new_url: str) -> str:
    return re.sub(r'(<img\b[^>]*\bsrc=["\'])[^"\']+(["\'])', lambda m: m.group(1)+html.escape(new_url, quote=True)+m.group(2), card, count=1, flags=re.I)

def process_file(path: Path) -> tuple[str, int, int]:
    text = path.read_text(encoding="utf-8")
    pat = re.compile(r'<div class="game-card"[^>]*>[\s\S]*?</div>', re.I)
    matches = list(pat.finditer(text))
    cards = [m.group(0) for m in matches]
    urls = [image_url(c) for c in cards]
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=20) as pool:
        statuses = list(pool.map(lambda u: bool(u) and fetch_ok(u), urls))
    changed=0
    unresolved=0
    searches=0
    replacements={}
    for pos, (card, cur_ok) in enumerate(zip(cards, statuses)):
        if cur_ok:
            continue
        title=card_title(card)
        cur=urls[pos]
        url=game_url(card)
        candidates=[]
        if url:
            try:
                body=fetch_text(url)
                candidates.extend(urljoin(url, x) for x in resolve_metadata(url, body))
            except Exception:
                pass
        valid=None
        for cand in candidates:
            if fetch_ok(cand):
                valid=cand
                break
        if valid is None and searches < MAX_SEARCHES:
            searches += 1
            for cand in github_search_candidates(title):
                if fetch_ok(cand):
                    valid=cand
                    break
            time.sleep(0.08)
        if valid and cur != valid:
            replacements[pos] = valid
            changed += 1
        else:
            unresolved += 1
    if replacements:
        parts=[]
        cursor=0
        for pos,m in enumerate(matches):
            parts.append(text[cursor:m.start()])
            card=m.group(0)
            parts.append(replace_src(card,replacements[pos]) if pos in replacements else card)
            cursor=m.end()
        parts.append(text[cursor:])
        new=''.join(parts)
        path.write_text(new,encoding="utf-8")
    else:
        new=text
    print(f"{path}: checked={len(cards)} changed={changed} unresolved={unresolved} github_searches={searches}")
    return str(path), changed, unresolved

for target in (INDEX, LEGACY):
    if target.exists():
        print(process_file(target))
print("REAL COVER RESOLVER COMPLETE: no AI/generated covers are created.")
