"""Combine candidate URLs from all sitemap passes, keep pediatric-relevant liquids/sachets/granules, tag a molecule group."""
import csv
import os
import re
import sys
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = r"C:\Users\RISHABH\Desktop\Pediatric_Medicine_India\raw_pages"

FORM = re.compile(r"(syrup|suspension|susp|dry-syrup|sachet|granule|oral-liquid|oral-solution|powder-for-oral|readymix|ready-mix|rediuse|redimix)", re.I)
EXCLUDE = re.compile(r"(eye|ear-|-ear|nasal|nose|ointment|cream|gel|lotion|shampoo|soap|spray|inhaler|injection|tablet|capsule|vaginal|mouth-?wash|gargle|ayur|herbal|himalaya|dabur|baidyanath|hamdard|patanjali|kesari|ashwagandha|tonic-for-adult|adult)", re.I)

GROUPS = [
    ("Paracetamol", r"(calpol|crocin|dolo-?\d|dolopar|pacimol|pyrigesic|febrex|paracetamol|paracip|pyrimol|fepanil)"),
    ("Ibuprofen+Paracetamol", r"(ibugesic|brufen|ibuprofen|combiflam|ibuprofen-and-paracetamol)"),
    ("Mefenamic acid+Paracetamol", r"(meftal|mefenamic)"),
    ("Amoxicillin+Clavulanate", r"(augmentin|clavam|moxikind-cv|-cv-|amoxycillin-?(and|\+)?-?clav|amoxicillin-?(and|\+)?-?clav|clavulan|megaclav|mox-cv|novamox-cv|bactoclav|moxclav)"),
    ("Amoxicillin", r"(novamox|amoxil|mox-\d|amoxycillin|amoxicillin|wymox|amoxyclav)"),
    ("Cefixime", r"(taxim-?o|zifi|cefix|cefixime|mahacef|ximacef|cefolac|zoxim)"),
    ("Cefpodoxime", r"(cepodem|doxcef|cefpodoxime|podoxime|cefakind|zocef-?o)"),
    ("Cefuroxime", r"(ceftum|zocef|cefuroxime|cefoprox)"),
    ("Cefadroxil/Cefaclor", r"(cefadroxil|cefaclor|kefadroxil|droxyl)"),
    ("Azithromycin", r"(azithral|azee|zithromax|azithromycin|azibact|aziwok)"),
    ("Cough/cold", r"(ascoril|alex-|alex\b|grilinctus|benadryl|chericof|tusq|ambroxol|levosalbutamol|dextromethorphan|terbutaline|corex|phensedyl|cofsils|honitus)"),
    ("Antihistamine", r"(cetzine|okacet|alerid|levocet|xyzal|montair|montek|cetirizine|levocetirizine|montelukast|chlorpheniramine|cheston)"),
    ("Antiemetic", r"(emeset|ondem|ondansetron|domstal|domperidone|vomistop|vomikind|perinorm)"),
    ("ORS/Zinc", r"(electral|\bors\b|ors-|zinc|z-d|zinconia|rehydrat|enerzal|zincovit)"),
    ("Probiotic", r"(econorm|sporlac|lactobacillus|saccharomyces|probiotic|bifilac|ultralevure|enterogermina)"),
    ("Laxative/antispasmodic", r"(duphalac|lactulose|looz|cremaffin|cyclopam|dicyclomine|colicaid|meftal-spas)"),
    ("Anthelmintic", r"(zentel|bandy|albendazole|mebendazole|vermox|pyrantel)"),
    ("Bronchodilator", r"(asthalin|salbutamol|ventorlin)"),
    ("Appetite/vitamin/iron", r"(practin|cyproheptadine|zincovit|multivitamin|ferrous|feronia|orofer|tonoferon|dexorange|maxirich|vitamin|calcium|shelcal|cod-liver)"),
    ("Cotrimoxazole/other anti-infective", r"(septran|cotrimoxazole|co-trimoxazole|metronidazole|metrogyl|flagyl|nitazoxanide|nizonide|clarithromycin|erythromycin|cloxacillin)"),
]
GROUPS = [(g, re.compile(p, re.I)) for g, p in GROUPS]


def load(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


rows = []
for name in ("candidate_urls.csv", "candidate_urls_1mg_rest.csv", "candidate_urls2.csv"):
    rows += load(os.path.join(BASE, name))
print("raw candidate rows:", len(rows))

seen = set()
out = []
for rec in rows:
    url = rec["url"].strip()
    if url in seen:
        continue
    seen.add(url)
    slug = url.rsplit("/", 1)[-1]
    if not FORM.search(slug) or EXCLUDE.search(slug):
        continue
    for group, pat in GROUPS:
        if pat.search(slug):
            out.append({"site": rec["site"], "group": group, "url": url, "slug": slug})
            break

print("after formulation + group filter:", len(out))
tab = defaultdict(Counter)
for r in out:
    tab[r["group"]][r["site"]] += 1
sites = ["1mg", "PharmEasy", "Netmeds", "Apollo"]
print(f"{'group':36s}" + "".join(f"{s:>11s}" for s in sites))
for group, _ in GROUPS:
    print(f"{group:36s}" + "".join(f"{tab[group][s]:>11d}" for s in sites))
print(f"{'TOTAL':36s}" + "".join(f"{sum(tab[g][s] for g in tab):>11d}" for s in sites))

with open(os.path.join(BASE, "master_candidates.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["site", "group", "url", "slug"])
    w.writeheader()
    w.writerows(out)
