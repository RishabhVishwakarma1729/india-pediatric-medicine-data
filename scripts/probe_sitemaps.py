"""Read the Sitemap lines from each robots.txt and peek at the sitemap indexes (allowed, public discovery routes)."""
import re
import time

import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept-Language": "en-IN,en;q=0.9",
}

ROBOTS = {
    "1mg": "https://www.1mg.com/robots.txt",
    "PharmEasy": "https://pharmeasy.in/robots.txt",
    "Netmeds": "https://www.netmeds.com/robots.txt",
    "Apollo": "https://www.apollopharmacy.in/robots.txt",
}

for name, url in ROBOTS.items():
    print("=" * 70)
    print(name)
    robots = requests.get(url, headers=HEADERS, timeout=25).text
    sitemaps = re.findall(r"(?i)^sitemap:\s*(\S+)", robots, flags=re.M)
    print("  sitemap lines:", sitemaps)
    for sm in sitemaps[:3]:
        time.sleep(1.5)
        try:
            r = requests.get(sm, headers=HEADERS, timeout=40)
        except Exception as exc:
            print("   ", sm, "ERROR", exc)
            continue
        locs = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", r.text)
        print("   ", sm, "status", r.status_code, "bytes", len(r.text), "locs", len(locs))
        for loc in locs[:25]:
            print("      ", loc)
    time.sleep(1.5)
