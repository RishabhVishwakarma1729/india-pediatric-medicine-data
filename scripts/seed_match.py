"""Match the 1mg candidate URLs against the seed list of common pediatric brands and print a summary."""
import csv
import re
from collections import Counter

SEED = {
    "Paracetamol": r"(calpol|crocin|dolo|pacimol|paracetamol)",
    "Ibuprofen+Paracetamol": r"(ibugesic|brufen|combiflam|ibuprofen)",
    "Mefenamic+Paracetamol": r"(meftal)",
    "Amoxicillin+Clavulanate": r"(augmentin|clavam|moxikind-cv|mox-cv|amoxycillin-and-clav)",
    "Amoxicillin": r"(novamox|mox-\d|amoxil|amoxicillin)",
    "Cefixime": r"(taxim-o|zifi|cefix|cefixime)",
    "Cefpodoxime": r"(cepodem|doxcef|cefpodoxime)",
    "Cefuroxime": r"(ceftum|zocef|cefuroxime)",
    "Azithromycin": r"(azithral|azee|zithromax|azithromycin)",
    "Cough/cold": r"(ascoril|alex-|grilinctus|benadryl|chericof|tusq|ambroxol)",
    "Antihistamine": r"(cetzine|okacet|levocet|xyzal|montair|montek|cetirizine|levocetirizine)",
    "Antiemetic": r"(emeset|ondem|domstal|vomistop|ondansetron|domperidone)",
    "ORS/Zinc/probiotic": r"(electral|zinconia|z-d|econorm|sporlac|ors-|zinc)",
    "Laxative/antispasmodic": r"(duphalac|looz|lactulose|cyclopam)",
    "Anthelmintic": r"(zentel|bandy|albendazole)",
    "Bronchodilator": r"(asthalin|salbutamol)",
    "Appetite/vitamin": r"(practin|zincovit|cyproheptadine)",
}
FORM = re.compile(r"(syrup|suspension|susp|sachet|granule|dry-syrup)", re.I)

counts = Counter()
rows = []
with open(r"C:\Users\RISHABH\Desktop\Pediatric_Medicine_India\raw_pages\candidate_urls.csv", encoding="utf-8") as fh:
    for rec in csv.DictReader(fh):
        if rec["site"] != "1mg":
            continue
        slug = rec["url"].rsplit("/", 1)[-1]
        if not FORM.search(slug):
            continue
        for group, pat in SEED.items():
            if re.search(pat, slug, re.I):
                counts[group] += 1
                rows.append((group, rec["url"]))
                break
print("1mg formulation URLs matching a seed group:", len(rows))
for group, n in counts.most_common():
    print(f"  {group:26s} {n}")
print()
for group in ("Paracetamol", "Amoxicillin+Clavulanate", "Mefenamic+Paracetamol"):
    print(group)
    for g, u in [r for r in rows if r[0] == group][:6]:
        print("   ", u)
with open(r"C:\Users\RISHABH\Desktop\Pediatric_Medicine_India\raw_pages\seed_urls_1mg.csv", "w", newline="", encoding="utf-8") as out:
    w = csv.writer(out)
    w.writerow(["group", "url"])
    w.writerows(rows)
