"""Fetch the remaining 1mg product sitemaps (drugs 26-78 and otc 1-59) and keep formulation or seed-brand URLs."""
import csv
import re
import time

import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept-Language": "en-IN,en;q=0.9",
}
OUT = r"C:\Users\RISHABH\Desktop\Pediatric_Medicine_India\raw_pages\candidate_urls_1mg_rest.csv"
FORM = re.compile(r"(syrup|suspension|susp|sachet|granule|dry-syrup|oral-drops|drops)", re.I)
SEED = re.compile(
    r"(calpol|crocin|dolo|pacimol|meftal|ibugesic|brufen|combiflam|augmentin|clavam|moxikind|mox-|novamox|taxim|zifi|cefix|cepodem|doxcef|ceftum|zocef|"
    r"azithral|azee|zithromax|ascoril|alex|grilinctus|benadryl|chericof|tusq|cetzine|okacet|levocet|xyzal|montair|montek|emeset|ondem|domstal|vomistop|"
    r"electral|zinconia|z-d|econorm|sporlac|duphalac|looz|zentel|bandy|asthalin|practin|cyclopam|zincovit)",
    re.I,
)

files = [f"https://www.1mg.com/sitemap_drugs_{i}.xml" for i in range(26, 79)] + [f"https://www.1mg.com/sitemap_otc_{i}.xml" for i in range(1, 60)]
total = 0
with open(OUT, "w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh)
    writer.writerow(["site", "url"])
    for n, sm in enumerate(files, start=1):
        try:
            r = requests.get(sm, headers=HEADERS, timeout=60)
        except Exception as exc:
            print("ERROR", sm, type(exc).__name__, flush=True)
            time.sleep(1.5)
            continue
        if r.status_code != 200:
            print("status", r.status_code, sm, flush=True)
            time.sleep(1.5)
            continue
        locs = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", r.text)
        kept = [u for u in locs if FORM.search(u.rsplit("/", 1)[-1]) or SEED.search(u.rsplit("/", 1)[-1])]
        for u in kept:
            writer.writerow(["1mg", u])
        total += len(kept)
        if n % 10 == 0 or n == len(files):
            print(f"{n}/{len(files)} {sm.rsplit('/', 1)[-1]} urls={len(locs)} kept={len(kept)} running_total={total}", flush=True)
        time.sleep(1.5)
print("TOTAL kept", total, flush=True)
