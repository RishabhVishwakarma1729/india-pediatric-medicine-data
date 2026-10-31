import csv
import json
import os
import re
import sys

import requests

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36", "Accept-Language": "en-IN,en;q=0.9"}
BASE = r"C:\Users\RISHABH\Desktop\Pediatric_Medicine_India\raw_pages"

cands = []
with open(BASE + r"\candidate_urls.csv", encoding="utf-8") as fh:
    for rec in csv.DictReader(fh):
        if rec["site"] == "Netmeds":
            cands.append(rec["url"])
print("Netmeds candidates so far:", len(cands))
for u in cands[:12]:
    print("  ", u)
pick = next((u for u in cands if re.search(r"(calpol|crocin|augmentin|taxim|azithral|zifi|meftal|dolo|ascoril)", u, re.I)), cands[0])
print("sample:", pick)
r = requests.get(pick, headers=H, timeout=45)
html = r.content.decode("utf-8", errors="replace")
print("status", r.status_code, "bytes", len(html))
with open(BASE + r"\samples\Netmeds_sample.html", "w", encoding="utf-8") as fh:
    fh.write(html)
blocks = re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S)
print("json-ld blocks:", len(blocks))
for b in blocks[:4]:
    try:
        print(json.dumps(json.loads(b), ensure_ascii=False)[:1100])
    except Exception:
        print("  unparsable", b[:100])
for pat in [r'(?i)"mrp"[^,]{0,30}', r'(?i)manufacturer[^<"]{0,80}', r'(?i)"pack_?size[^,]{0,50}', r'(?i)bought[^<"]{0,60}', r'(?i)\d+\s*(?:ratings|reviews)', r'(?i)bestseller[^<"]{0,30}', r'(?i)"rating[^,]{0,40}', r'(?i)"composition[^,]{0,80}', r'(?i)"dosage_form[^,]{0,40}']:
    print(f"  {pat[:34]:36s}", re.findall(pat, html)[:3])
