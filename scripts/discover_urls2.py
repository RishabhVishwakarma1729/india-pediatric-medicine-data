"""Second-level sitemap discovery for PharmEasy and Apollo, plus the remaining Netmeds product sitemaps.

Reads only sitemap files listed in each site's robots.txt hierarchy. Output: raw_pages/candidate_urls2.csv (site, url).
One request every 1.5 s.
"""
import csv
import re
import time

import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept-Language": "en-IN,en;q=0.9",
}
OUT = r"C:\Users\RISHABH\Desktop\Pediatric_Medicine_India\raw_pages\candidate_urls2.csv"
FORM = re.compile(r"(syrup|suspension|susp|sachet|granule|dry-syrup|oral-drops|drops)", re.I)
SEED = re.compile(
    r"(calpol|crocin|dolo|pacimol|meftal|ibugesic|brufen|combiflam|augmentin|clavam|moxikind|mox-|novamox|taxim|zifi|cefix|cepodem|doxcef|ceftum|zocef|"
    r"azithral|azee|zithromax|ascoril|alex|grilinctus|benadryl|chericof|tusq|cetzine|okacet|levocet|xyzal|montair|montek|emeset|ondem|domstal|vomistop|"
    r"electral|zinconia|z-d|econorm|sporlac|duphalac|looz|zentel|bandy|asthalin|practin|cyclopam|zincovit|ors)",
    re.I,
)


def get(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=60)
    except Exception as exc:
        print("ERROR", url, type(exc).__name__, flush=True)
        return None
    if r.status_code != 200:
        print("status", r.status_code, url, flush=True)
        return None
    return r.text


def locs_of(text):
    return re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", text or "")


def keep(url):
    slug = url.rsplit("/", 1)[-1]
    return bool(FORM.search(slug) or SEED.search(slug))


rows = 0
with open(OUT, "w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh)
    writer.writerow(["site", "url"])

    for site, parents in {
        "PharmEasy": ["https://pharmeasy.in/sitemaps/sitemap-prescription-medicines.xml", "https://pharmeasy.in/sitemaps/sitemap-otc-products.xml"],
        "Apollo": ["https://www.apollopharmacy.in/sitemap/sitemap-pharma-rx.xml", "https://www.apollopharmacy.in/sitemap/sitemap-pharma-otc.xml"],
    }.items():
        children = []
        for p in parents:
            children += locs_of(get(p))
            time.sleep(1.5)
        print(site, "child sitemaps:", len(children), flush=True)
        site_kept = 0
        for child in children:
            text = get(child)
            time.sleep(1.5)
            if text is None:
                continue
            urls = locs_of(text)
            kept = [u for u in urls if keep(u)]
            for u in kept:
                writer.writerow([site, u])
            site_kept += len(kept)
            print(f"{site:10s} {child.rsplit('/', 1)[-1][:40]:40s} urls={len(urls):6d} kept={len(kept):5d}", flush=True)
        print(f"== {site}: kept {site_kept}", flush=True)
        rows += site_kept

    root = get("https://www.netmeds.com/sitemap.xml")
    time.sleep(1.5)
    product_maps = [u for u in locs_of(root) if "/sitemap/products/" in u]
    done = set(f"https://www.netmeds.com/sitemap/products/{i}/page.sitemap.xml" for i in range(1, 15))
    todo = [u for u in product_maps if u not in done]
    print("Netmeds product sitemaps total:", len(product_maps), "to fetch:", len(todo), flush=True)
    site_kept = 0
    for n, child in enumerate(todo, start=1):
        text = get(child)
        time.sleep(1.5)
        if text is None:
            continue
        kept = [u for u in locs_of(text) if keep(u)]
        for u in kept:
            writer.writerow(["Netmeds", u])
        site_kept += len(kept)
        if n % 20 == 0:
            print(f"Netmeds {n}/{len(todo)} kept so far {site_kept}", flush=True)
    print(f"== Netmeds: kept {site_kept}", flush=True)
    rows += site_kept
print("TOTAL kept", rows, flush=True)
