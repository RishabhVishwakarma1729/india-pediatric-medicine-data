import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
for line in open(r"C:\Users\RISHABH\Desktop\Pediatric_Medicine_India\raw_pages\products_Apollo.jsonl", encoding="utf-8"):
    j = json.loads(line)
    if j.get("name") and "kidzo" in j["name"].lower():
        print({k: j.get(k) for k in ("name", "url", "mrp", "sale_price", "available", "manufacturer", "dosage_form", "retrieved_utc")})
# distribution of Apollo mrp vs sale_price mismatches
import statistics
bad = []
for line in open(r"C:\Users\RISHABH\Desktop\Pediatric_Medicine_India\raw_pages\products_Apollo.jsonl", encoding="utf-8"):
    j = json.loads(line)
    m, s = j.get("mrp"), j.get("sale_price")
    if m and s and (m > 4 * s or s > 4 * m):
        bad.append((j["name"], m, s))
print("Apollo rows where mrp and offer price differ >4x:", len(bad))
for b in bad[:8]:
    print("  ", b)
