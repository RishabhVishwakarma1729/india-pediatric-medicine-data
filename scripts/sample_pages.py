import csv
import json
import os
import re
import sys
import time

import requests

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36", "Accept-Language": "en-IN,en;q=0.9"}
BASE = r"C:\Users\RISHABH\Desktop\Pediatric_Medicine_India\raw_pages"
os.makedirs(BASE + r"\samples", exist_ok=True)

urls = {}
with open(BASE + r"\candidate_urls2.csv", encoding="utf-8") as fh:
    for rec in csv.DictReader(fh):
        if rec["site"] in ("PharmEasy", "Apollo") and "calpol" in rec["url"].lower() and ("susp" in rec["url"].lower() or "syrup" in rec["url"].lower()):
            urls.setdefault(rec["site"], []).append(rec["url"])
for site in urls:
    print(site, "calpol candidates:", len(urls[site]))
    for u in urls[site][:5]:
        print("   ", u)

for site, lst in urls.items():
    url = lst[0]
    time.sleep(2)
    r = requests.get(url, headers=H, timeout=40)
    html = r.content.decode("utf-8", errors="replace")
    path = BASE + rf"\samples\{site}_sample.html"
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(html)
    print("=" * 70)
    print(site, url, "status", r.status_code, "bytes", len(html))
    blocks = re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S)
    print("json-ld blocks:", len(blocks))
    for b in blocks[:3]:
        try:
            print(json.dumps(json.loads(b), ensure_ascii=False)[:900])
        except Exception:
            print("  unparsable", b[:120])
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if m:
        data = json.loads(m.group(1))
        print("__NEXT_DATA__ top keys:", list(data.keys()))
        props = data.get("props", {}).get("pageProps", {})
        print("pageProps keys:", list(props.keys())[:20])
        prod = props.get("productDetails") or props.get("data") or {}
        print(json.dumps(prod, ensure_ascii=False)[:1500])
    for pat in [r"(?i)bought[^<\"]{0,60}", r"(?i)bestseller[^<\"]{0,40}", r"(?i)\d[\d,.]*\s*(?:ratings|reviews)[^<\"]{0,20}", r"(?i)last \d+ days[^<\"]{0,40}"]:
        print(pat, "->", re.findall(pat, html)[:4])
