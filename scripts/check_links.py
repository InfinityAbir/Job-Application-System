"""Wake up and check your live demo links before an interview (free hosts sleep and load slowly).

Reads profile/links.txt (one URL per line, # for comments); falls back to profile/links.example.txt.

python scripts/check_links.py
"""
import time
import urllib.request
from pathlib import Path

PROFILE = Path(__file__).resolve().parent.parent / "profile"
src = PROFILE / "links.txt"
if not src.exists():
    src = PROFILE / "links.example.txt"
LINKS = [l.strip() for l in src.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
print(f"checking {len(LINKS)} links from {src.name}")

for url in LINKS:
    start = time.time()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=90) as r:
            print(f"OK   {r.status}  {time.time() - start:5.1f}s  {url}")
    except Exception as e:
        print(f"FAIL {type(e).__name__}  {time.time() - start:5.1f}s  {url}  {e}")
