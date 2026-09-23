#!/usr/bin/env python3
from __future__ import annotations
import html, re, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

LEGACY=Path("legacy-index.html"); INDEX=Path("index.html")
TIMEOUT=12; MAX_BYTES=70000; WORKERS=32
SIGNALS=("<canvas","<iframe","<script","phaser","pixi","construct","unity","godot","playcanvas","keydown","keyup","pointerdown","touchstart","requestanimationframe","gamepad","javascript game")
BAD_PAGE=("404 not found","page not found","access denied","forbidden","service unavailable","this site can't be reached","this page could not be found")

def clean(v):
    return re.sub(r"\s+"," ",re.sub(r"<[^>]+>","",html.unescape(v or ""))).strip()

def extract_games(text):
    out=[]
    for m in re.finditer(r'<div\s+class="game-card"[^>]*>[\s\S]*?</div>',text,re.I):
        card=m.group(0); tm=re.search(r"<h3[^>]*>([\s\S]*?)</h3>",card,re.I)
        um=re.search(r"openGame\(\s*['\"]([^'\"]+)",card,re.I) or re.search(r"window\.open\(\s*['\"]([^'\"]+)",card,re.I)
        if tm and um:
            out.append((clean(tm.group(1)),html.unescape(um.group(1).strip())))
    return out

def check(item):
    title,url=item
    if not url.startswith("https://"): return title,url,False,"non-HTTPS URL"
    try:
        req=Request(url,headers={"User-Agent":"UBG43-Full-Game-Health/1.0","Accept":"text/html,application/xhtml+xml,*/*;q=0.8"})
        with urlopen(req,timeout=TIMEOUT) as r:
            body=r.read(MAX_BYTES); status=int(r.status); ctype=(r.headers.get("Content-Type") or "").lower()
        text=body.decode("utf-8","ignore").lower(); head=text[:50000]
        if not (200<=status<400): return title,url,False,f"HTTP {status}"
        if len(body)<120: return title,url,False,f"response too small ({len(body)} bytes)"
        if "text/html" not in ctype and b"<html" not in body.lower() and b"<!doctype" not in body.lower():
            return title,url,False,f"not HTML ({ctype or 'unknown'})"
        if any(x in head for x in BAD_PAGE): return title,url,False,"error page detected"
        signals=sum(1 for x in SIGNALS if x in head)
        if "raw.githubusercontent.com/gn-math/html/" in url:
            return title,url,True,""
        if signals<1 and len(body)<600:
            # Small launcher pages (for example a "Click to Play" wrapper) are
            # valid when they point to another HTTPS game page.
            hrefs=re.findall(r'href=["\'](https://[^"\']+)["\']', text, re.I)
            if hrefs and any("play" in h.lower() or "game" in h.lower() for h in hrefs):
                return title,url,True,""
            return title,url,False,"no recognizable game signal"
        return title,url,True,""
    except HTTPError as e: return title,url,False,f"HTTP {e.code}"
    except (URLError,TimeoutError,OSError,ValueError) as e: return title,url,False,str(e)[:180]

all_games=extract_games(INDEX.read_text(encoding="utf-8"))+extract_games(LEGACY.read_text(encoding="utf-8"))
seen=set(); unique=[]
for title,url in all_games:
    key=url.split("#",1)[0].rstrip("/")
    if key not in seen: seen.add(key); unique.append((title,url))

results=[]
with ThreadPoolExecutor(max_workers=WORKERS) as pool:
    futures=[pool.submit(check,x) for x in unique]
    for f in as_completed(futures): results.append(f.result())

bad=sorted((x for x in results if not x[2]),key=lambda x:x[0].casefold())
print("FULL GAME LINK HEALTH")
print(f"- unique game URLs checked: {len(results)}")
print(f"- healthy endpoints: {len(results)-len(bad)}")
print(f"- failing/suspicious endpoints: {len(bad)}")
for title,url,_,reason in bad: print(f"FAIL\t{title}\t{reason}\t{url}")
if bad: sys.exit(1)
print("FULL GAME LINK HEALTH PASSED")
