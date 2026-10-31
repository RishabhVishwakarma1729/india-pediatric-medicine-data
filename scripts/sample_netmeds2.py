import re
import sys
import time

import requests

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36", "Accept-Language": "en-IN,en;q=0.9"}
OUTD = r"C:\Users\RISHABH\Desktop\Pediatric_Medicine_India\raw_pages\samples"
URLS = {
    "netmeds_chericof": "https://www.netmeds.com/product/chericof-12-cherry-flavour-oral-suspension-60ml-lui3ut-8273401",
    "netmeds_benadryl_nodrug": None,
}
import csv

cands = [r["url"] for r in csv.DictReader(open(r"C:\Users\RISHABH\Desktop\Pediatric_Medicine_India\raw_pages\crawl_set.csv", encoding="utf-8")) if r["site"] == "Netmeds" and r["brand_family"] == "Benadryl"]
URLS["netmeds_benadryl_nodrug"] = cands[0]
for name, url in URLS.items():
    r = requests.get(url, headers=H, timeout=60)
    html = r.content.decode("utf-8", errors="replace")
    open(f"{OUTD}\\{name}.html", "w", encoding="utf-8").write(html)
    print("=" * 60)
    print(name, url, r.status_code, len(html))
    lds = re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S)
    print("ld+json blocks:", [re.search(r'"@type":\s*"(\w+)"', b).group(1) if re.search(r'"@type":\s*"(\w+)"', b) else '?' for b in lds])
    for pat in [r'"mrp":[\d.]+', r'"marked":[\d.]+', r'"effective":[\d.]+', r'"price":\{[^}]{0,120}\}', r'"packsize":"?[\d.]+', r'(?i)mrp[^<"]{0,30}', r'"rating_count":\d+', r'"manufacturername":"[^"]*"', r'"genericnamewithdosage":"[^"]*"']:
        print(f"  {pat[:34]:36s}", re.findall(pat, html)[:3])
    time.sleep(11)
