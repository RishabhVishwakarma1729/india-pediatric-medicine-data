"""Stream each site's public product sitemaps and keep only URLs whose slug names a target formulation.

Only sitemap.xml files listed in robots.txt are read. Output: raw_pages/candidate_urls.csv (site, url).
Polite: one request every 1.5 s, no parallelism.
"""
import csv
import re
import time

import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept-Language": "en-IN,en;q=0.9",
}
OUT = r"C:\Users\RISHABH\Desktop\Pediatric_Medicine_India\raw_pages\candidate_urls.csv"

FORM = re.compile(r"(syrup|suspension|susp|sachet|granule|dry-syrup|oral-drops|drops)", re.I)

SITEMAPS = {
    "1mg": [f"https://www.1mg.com/sitemap_drugs_{i}.xml" for i in range(1, 26)],
    "PharmEasy": [
        "https://pharmeasy.in/sitemaps/sitemap-prescription-medicines.xml",
        "https://pharmeasy.in/sitemaps/sitemap-otc-products.xml",
    ],
    "Netmeds": [f"https://www.netmeds.com/sitemap/products/{i}/page.sitemap.xml" for i in range(1, 15)],
    "Apollo": [
        "https://www.apollopharmacy.in/sitemap/sitemap-pharma-rx.xml",
        "https://www.apollopharmacy.in/sitemap/sitemap-pharma-otc.xml",
    ],
}

total = 0
with open(OUT, "w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh)
    writer.writerow(["site", "url"])
    for site, urls in SITEMAPS.items():
        kept_site = 0
        for sm in urls:
            try:
                r = requests.get(sm, headers=HEADERS, timeout=60)
            except Exception as exc:
                print(site, sm, "ERROR", type(exc).__name__, flush=True)
                time.sleep(1.5)
                continue
            if r.status_code != 200:
                print(site, sm, "status", r.status_code, flush=True)
                time.sleep(1.5)
                continue
            locs = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", r.text)
            kept = [u for u in locs if FORM.search(u.rsplit("/", 1)[-1])]
            for u in kept:
                writer.writerow([site, u])
            kept_site += len(kept)
            print(f"{site:10s} {sm.rsplit('/', 1)[-1]:38s} urls={len(locs):6d} kept={len(kept):5d}", flush=True)
            del r, locs, kept
            time.sleep(1.5)
        print(f"== {site}: kept {kept_site}", flush=True)
        total += kept_site
print("TOTAL kept", total, flush=True)
