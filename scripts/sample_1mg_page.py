import json
import os
import re

import requests

H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36", "Accept-Language": "en-IN,en;q=0.9"}
url = "https://www.1mg.com/drugs/dolopar-250-suspension-228130"
r = requests.get(url, headers=H, timeout=40)
print("status", r.status_code, "bytes", len(r.text))
os.makedirs(r"C:\Users\RISHABH\Desktop\Pediatric_Medicine_India\raw_pages\samples", exist_ok=True)
with open(r"C:\Users\RISHABH\Desktop\Pediatric_Medicine_India\raw_pages\samples\1mg_sample.html", "w", encoding="utf-8") as fh:
    fh.write(r.text)
html = r.text
blocks = re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S)
print("json-ld blocks:", len(blocks))
for b in blocks:
    try:
        data = json.loads(b)
    except Exception:
        print("  unparsable block", b[:100])
        continue
    print(json.dumps(data, indent=1)[:1500])
for pat in [r"MRP[^<]{0,60}", r"Marketer[^<]{0,80}", r"Manufacturer[^<]{0,80}", r"[0-9,]+ (?:ratings|reviews)", r"bottle of [^<]{0,40}", r"Pack Size[^<]{0,50}", r"bought[^<]{0,60}", r"(?i)bestseller[^<]{0,40}", r"Composition[^<]{0,120}"]:
    m = re.findall(pat, html)
    print(pat, "->", m[:4])
