#!/usr/bin/env python3
from __future__ import annotations
import html
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

MARKER = "<!-- UBG43 300-game expansion v1 -->"
LEGACY = Path("legacy-index.html")
INDEX = Path("index.html")
TARGET = 300
TIMEOUT = 12
WORKERS = 32

SOURCES = [
    {
        "repo": "selenite-cc/selenite-old",
        "branch": "main",
        "patterns": [re.compile(r"^[^/]+/index\.html$", re.I)],
        "exclude_dirs": {
            "404","ad","about","backgrounds","changelog","credits","contact",
            "error","games","index","search","settings","support","tools"
        },
    },
    {
        "repo": "Prollhouse2/gamesite",
        "branch": "main",
        "patterns": [
            re.compile(r"^g/[^/]+/index\.html$", re.I),
            re.compile(r"^g/[^/]+/[^/]+\.html$", re.I),
        ],
        "exclude_dirs": {"__macosx","about","apps","bookmarks","chat","error","ai","emulator"},
    },
    {
        "repo": "Nintendoboi222/games",
        "branch": "main",
        "patterns": [
            re.compile(r"^[^/]+/index\.html$", re.I),
            re.compile(r"^[^/]+/[^/]+/index\.html$", re.I),
        ],
        "exclude_dirs": {"404","components","docs","index","about"},
    },
    {
        "repo": "MonkeyGG2/monkeygg2.github.io",
        "branch": "main",
        "patterns": [
            re.compile(r"^games/[^/]+/index\.html$", re.I),
        ],
        "exclude_dirs": {"404","about","index","settings","proxy"},
    },
]

GAME_SIGNALS = (
    "<canvas", "<iframe", "<script", "phaser", "pixi", "construct", "unity",
    "godot", "playcanvas", "keydown", "keyup", "pointerdown", "touchstart",
    "requestanimationframe", "gamepad", "javascript game", "gamecontainer",
    "unityloader", "wasm"
)
BAD_TEXT = (
    "404 not found", "page not found", "access denied", "forbidden",
    "service unavailable", "this page could not be found",
    "maintenance page", "under construction"
)
BAD_TITLE = {"", "untitled", "index", "404", "error", "not found", "home", "dashboard"}
EXCLUDED_TITLES = (
    "five nights at epstein", "five nights at last breath", "five nights at shrek",
    "suggest games", "[!]"
)

def norm(value: str) -> str:
    value = html.unescape(str(value or ""))
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()

def title_from_path(path: str) -> str:
    parts = path.split("/")
    if parts[-1].lower() in {"index.html", "index.htm"} and len(parts) >= 2:
        base = parts[-2]
    else:
        base = re.sub(r"\.(html?|htm)$", "", parts[-1], flags=re.I)
    base = re.sub(r"[-_]+", " ", base)
    return re.sub(r"\s+", " ", base).strip().title()

def request(url: str, max_bytes: int = 60000):
    req = Request(url, headers={
        "User-Agent": "UBG43-300-Game-Importer/1.0",
        "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
    })
    with urlopen(req, timeout=TIMEOUT) as r:
        return int(r.status), (r.headers.get("Content-Type") or "").lower(), r.read(max_bytes)

def fetch_tree(source):
    url = f"https://api.github.com/repos/{source['repo']}/git/trees/{source['branch']}?recursive=1"
    status, ctype, body = request(url, 2000000)
    if status >= 400:
        raise RuntimeError(f"GitHub tree HTTP {status} for {source['repo']}")
    data = json.loads(body.decode("utf-8", "ignore"))
    return [x["path"] for x in data.get("tree", []) if x.get("type") == "blob"]

def usable_path(source, path: str) -> bool:
    if not any(p.search(path) for p in source["patterns"]):
        return False
    low_parts = [p.lower() for p in path.split("/")]
    if any(p in source["exclude_dirs"] for p in low_parts):
        return False
    if "__macosx" in low_parts or "/." in path:
        return False
    return True

def parse_candidate(source, path):
    raw_url = f"https://raw.githubusercontent.com/{source['repo']}/{source['branch']}/{path}"
    try:
        status, ctype, body = request(raw_url, 70000)
        if not (200 <= status < 400):
            return None
        if len(body) < 300:
            return None
        lower = body.decode("utf-8", "ignore").lower()
        if any(b in lower[:50000] for b in BAD_TEXT):
            return None
        title_match = re.search(r"<title[^>]*>([\s\S]*?)</title>", lower, re.I)
        title = html.unescape(re.sub(r"<[^>]+>", " ", title_match.group(1) if title_match else "")).strip()
        title = re.sub(r"\s+", " ", title)
        if not title or norm(title) in BAD_TITLE:
            title = title_from_path(path)
        title = re.sub(r"\s*[|—–-]\s*(unblocked|games?|html5|play online|game hub).*?$", "", title, flags=re.I).strip()
        ntitle = norm(title)
        if len(ntitle) < 3 or ntitle in BAD_TITLE:
            return None
        if any(x in ntitle for x in EXCLUDED_TITLES):
            return None
        signal_count = sum(1 for s in GAME_SIGNALS if s in lower[:60000])
        if signal_count < 1:
            # Accept self-contained game documents that use modules/custom elements
            # but still include a clear game container or player shell.
            if not any(x in lower[:60000] for x in ("<body", "<main", "<div", "javascript")):
                return None

        og = re.search(r'<meta[^>]+(?:property|name)=["\']og:image["\'][^>]+content=["\']([^"\']+)', lower, re.I)
        image = html.unescape(og.group(1).strip()) if og else ""
        return {"repo": source["repo"], "branch": source["branch"], "path": path, "url": raw_url, "title": title, "image": image}
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError):
        return None

def build_image_map(source, paths):
    by_dir = {}
    for p in paths:
        low = p.lower()
        if not re.search(r"\.(png|jpe?g|webp|gif)$", low):
            continue
        parts = p.split("/")
        if source["repo"] == "selenite-cc/selenite-old":
            if len(parts) < 2:
                continue
            game_dir = parts[0]
        elif source["repo"] == "Prollhouse2/gamesite":
            if len(parts) < 3 or parts[0].lower() != "g":
                continue
            game_dir = "/".join(parts[:2])
        elif source["repo"] == "Nintendoboi222/games":
            if len(parts) < 2:
                continue
            game_dir = "/".join(parts[:2])
        else:
            if len(parts) < 3 or parts[0].lower() != "games":
                continue
            game_dir = "/".join(parts[:2])
        by_dir.setdefault(game_dir, []).append(p)
    return by_dir

def choose_image(candidate, image_map):
    if candidate["image"] and candidate["image"].startswith("http"):
        return candidate["image"]
    path = candidate["path"]
    parts = path.split("/")
    if candidate["repo"] == "selenite-cc/selenite-old":
        key = parts[0]
    elif candidate["repo"] == "Prollhouse2/gamesite":
        key = "/".join(parts[:2])
    elif candidate["repo"] == "Nintendoboi222/games":
        key = "/".join(parts[:2])
    else:
        key = "/".join(parts[:2])
    imgs = image_map.get(key, [])
    preferred = re.compile(r"(cover|thumb|thumbnail|icon|logo|preview|screenshot|image)", re.I)
    imgs = sorted(imgs, key=lambda p: (0 if preferred.search(p.split("/")[-1]) else 1, len(p)))
    if imgs:
        return f"https://raw.githubusercontent.com/{candidate['repo']}/{candidate['branch']}/{imgs[0]}"
    return "https://raw.githubusercontent.com/ubg43/ubg43.github.io/main/Docs.ico"

def category(title: str) -> str:
    n = norm(title)
    rules = {
        "Horror": ("horror","fnaf","freddy","granny","scary","nightmare","terror","creepy"),
        "Racing": ("racing","race","drift","car","truck","bike","moto","rally","drive","kart","traffic"),
        "Sports": ("football","soccer","basket","basketball","golf","tennis","hockey","bowling","sports","pool"),
        "Puzzle": ("puzzle","2048","sudoku","word","maze","memory","chess","connect","match","sort","block"),
        "Strategy": ("strategy","tower","defense","defence","war","kingdom","idle","tycoon","manager"),
        "Fighting": ("fight","fighter","boxing","brawl","duel","wrestle","combat"),
        "Platformer": ("platform","mario","sonic","vex","jump","obby"),
        "Arcade": ("arcade","runner","flappy","snake","pong","breakout","ball","clicker"),
        "Adventure": ("adventure","quest","dungeon","escape","explore","island","mystery"),
        "Simulation": ("simulator","simulation","farming","farm","cooking","restaurant","city","life"),
        "Multiplayer": ("multiplayer","2 player","2p",".io","io"),
    }
    for cat, words in rules.items():
        if any(w in n for w in words):
            return cat
    return "Casual"

def card(candidate, image):
    safe_title = html.escape(candidate["title"], quote=True)
    safe_url = html.escape(candidate["url"], quote=True)
    safe_img = html.escape(image, quote=True)
    return (
        f'<div class="game-card" data-category="{html.escape(category(candidate["title"]))}" '
        f'data-new-since="2026-09-23" data-source="ubg43-300-expansion" '
        f'onclick="window.open(\'{safe_url}\',\'_blank\')">\n'
        f'  <img loading="lazy" src="{safe_img}" alt="{safe_title}" referrerpolicy="no-referrer">\n'
        f'  <h3>{safe_title}</h3>\n'
        f'</div>'
    )

def main():
    if not LEGACY.exists() or not INDEX.exists():
        raise SystemExit("legacy-index.html or index.html missing")
    legacy = LEGACY.read_text(encoding="utf-8")
    index = INDEX.read_text(encoding="utf-8")
    if MARKER in legacy:
        print("300-game expansion already present; nothing to do.")
        return

    existing_html = legacy + "\n" + index
    existing_titles = set(norm(x) for x in re.findall(r"<h3[^>]*>([\s\S]*?)</h3>", existing_html, re.I))
    existing_urls = set(re.findall(r"(?:openGame\(|window\.open\()\s*[\'\"](https?://[^\'\"\s]+)", existing_html, re.I))
    candidates = []

    for source in SOURCES:
        paths = fetch_tree(source)
        source["paths"] = paths
        source["image_map"] = build_image_map(source, paths)
        valid_paths = [p for p in paths if usable_path(source, p)]
        print(f"{source['repo']}: {len(valid_paths)} candidate HTML paths")
        candidates.extend((source, p) for p in valid_paths)

    # De-duplicate source paths before fetching.
    seen_paths = set()
    unique_candidates = []
    for source, path in candidates:
        key = source["repo"] + "::" + path
        if key not in seen_paths:
            seen_paths.add(key)
            unique_candidates.append((source, path))

    validated = []
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        future_map = {pool.submit(parse_candidate, source, path): (source, path) for source, path in unique_candidates}
        for f in as_completed(future_map):
            item = f.result()
            if item:
                validated.append(item)

    # Prefer games with an explicit og:image, then stable source ordering.
    validated.sort(key=lambda x: (0 if x["image"].startswith("http") else 1, norm(x["title"]), x["repo"], x["path"]))

    selected = []
    selected_titles = set(existing_titles)
    selected_urls = set(existing_urls)
    near = lambda s: norm(s)

    for c in validated:
        tn = near(c["title"])
        if tn in selected_titles or c["url"] in selected_urls:
            continue
        # Avoid near-exact duplicates such as "Geometry Dash" vs "Geometry Dash Lite".
        duplicate = False
        for old in list(selected_titles)[-800:]:
            if tn == old:
                duplicate = True
                break
        if duplicate:
            continue
        selected.append(c)
        selected_titles.add(tn)
        selected_urls.add(c["url"])
        if len(selected) >= TARGET:
            break

    if len(selected) < TARGET:
        raise SystemExit(f"Only {len(selected)} validated, non-duplicate games were found; refusing a partial expansion.")

    cards = []
    for c in selected:
        cards.append(card(c, choose_image(c, next(s["image_map"] for s in SOURCES if s["repo"] == c["repo"]))))

    # Put the new cards at the front of legacy so they become available immediately,
    # while keeping the existing library untouched below them.
    marker_block = MARKER + "\n" + "\n".join(cards) + "\n" + MARKER + "\n"
    pos = legacy.lower().rfind("</div>")
    if pos < 0:
        raise SystemExit("Could not locate the end of the legacy game-card grid.")
    legacy = legacy[:pos] + marker_block + legacy[pos:]

    LEGACY.write_text(legacy, encoding="utf-8")
    print(f"UBG43 300-game expansion added {len(selected)} validated, non-duplicate games.")
    print("Game URLs use raw.githubusercontent.com so the UBG43 about:blank/ad-filter player can process them.")
    print(json.dumps([{"title": c["title"], "url": c["url"]} for c in selected[:25]], indent=2))

if __name__ == "__main__":
    main()
