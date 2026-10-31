"""Pick the crawl set: named, nationally known pediatric brands only. Writes raw_pages/crawl_set.csv and prints per-site counts."""
import csv
import re
import sys
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = r"C:\Users\RISHABH\Desktop\Pediatric_Medicine_India\raw_pages"

# brand token -> (brand family, molecule group hint)
BRANDS = {
    "calpol": "Calpol", "crocin": "Crocin", "dolo-?(125|250|paed|kid)": "Dolo", "pacimol": "Pacimol", "febrex": "Febrex Plus",
    "ibugesic": "Ibugesic Plus", "brufen": "Brufen", "meftal": "Meftal-P",
    "augmentin": "Augmentin Duo", "clavam": "Clavam", "moxikind": "Moxikind-CV", "megaclav": "Megaclav", "bactoclav": "Bactoclav", "novamox": "Novamox", "wymox": "Wymox",
    "taxim-?o": "Taxim-O", "zifi": "Zifi", "cefix(?!ime)": "Cefix", "mahacef": "Mahacef", "cepodem": "Cepodem", "doxcef": "Doxcef", "cefakind": "Cefakind",
    "ceftum": "Ceftum", "zocef": "Zocef", "azithral": "Azithral", "azee": "Azee", "zithromax": "Zithromax", "aziwok": "Aziwok",
    "ascoril": "Ascoril", "alex-": "Alex", "grilinctus": "Grilinctus", "benadryl": "Benadryl", "chericof": "Chericof", "tusq": "Tusq", "corex": "Corex", "honitus": "Honitus",
    "cetzine": "Cetzine", "okacet": "Okacet", "alerid": "Alerid", "levocet": "Levocet", "xyzal": "Xyzal", "montair": "Montair", "montek": "Montek",
    "emeset": "Emeset", "ondem": "Ondem", "domstal": "Domstal", "vomistop": "Vomistop",
    "electral": "Electral", "orsl": "ORSL", "enerzal": "Enerzal", "zinconia": "Zinconia", "z-d-": "Z&D", "zincovit": "Zincovit",
    "econorm": "Econorm", "sporlac": "Sporlac", "bifilac": "Bifilac",
    "duphalac": "Duphalac", "looz": "Looz", "cremaffin": "Cremaffin", "cyclopam": "Cyclopam",
    "zentel": "Zentel", "bandy": "Bandy", "asthalin": "Asthalin", "ventorlin": "Ventorlin", "practin": "Practin", "dexorange": "Dexorange",
}
PATS = [(re.compile(r"(?<![a-z])" + tok, re.I), fam) for tok, fam in BRANDS.items()]

rows = []
with open(BASE + r"\master_candidates.csv", encoding="utf-8") as fh:
    for rec in csv.DictReader(fh):
        slug = rec["slug"]
        for pat, fam in PATS:
            if pat.search(slug):
                rec["brand_family"] = fam
                rows.append(rec)
                break
print("named-brand rows:", len(rows))
tab = defaultdict(Counter)
for r in rows:
    tab[r["brand_family"]][r["site"]] += 1
sites = ["1mg", "PharmEasy", "Netmeds", "Apollo"]
print(f"{'brand family':18s}" + "".join(f"{s:>11s}" for s in sites))
for fam in sorted(tab):
    print(f"{fam:18s}" + "".join(f"{tab[fam][s]:>11d}" for s in sites))
print(f"{'TOTAL':18s}" + "".join(f"{sum(tab[f][s] for f in tab):>11d}" for s in sites))
with open(BASE + r"\crawl_set.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["site", "group", "brand_family", "url", "slug"])
    w.writeheader()
    for r in rows:
        w.writerow({k: r[k] for k in ("site", "group", "brand_family", "url", "slug")})
