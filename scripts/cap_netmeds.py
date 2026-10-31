import csv
from collections import Counter

P = r"C:\Users\RISHABH\Desktop\Pediatric_Medicine_India\raw_pages\crawl_set.csv"
rows = list(csv.DictReader(open(P, encoding="utf-8")))
seen = Counter()
kept = []
for r in rows:
    if r["site"] == "Netmeds":
        seen[r["brand_family"]] += 1
        if seen[r["brand_family"]] > 3:
            continue
    kept.append(r)
with open(P, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["site", "group", "brand_family", "url", "slug"])
    w.writeheader()
    w.writerows(kept)
print("rows:", len(rows), "->", len(kept), "| Netmeds:", sum(1 for r in kept if r["site"] == "Netmeds"))
