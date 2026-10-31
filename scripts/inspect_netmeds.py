import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
html = open(r"C:\Users\RISHABH\Desktop\Pediatric_Medicine_India\raw_pages\samples\Netmeds_sample.html", encoding="utf-8").read()
blocks = re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S)
drug = json.loads(blocks[1])
d = drug[0] if isinstance(drug, list) else drug
print("Drug LD keys:", list(d.keys()))
for k in ("offers", "manufacturer", "activeIngredient", "dosageForm", "aggregateRating", "category"):
    if k in d:
        print(" ", k, "=>", json.dumps(d[k], ensure_ascii=False)[:350])


def ctx(pat, before=120, after=260, limit=2):
    for i, m in enumerate(re.finditer(pat, html)):
        if i >= limit:
            break
        print("   ..." + html[max(0, m.start() - before) : m.end() + after].replace("\n", " ") + "...")


for pat in [r'"manufacturer":', r'"manufacturername"', r'"manufacturer_name"', r'"mrp":80\.3', r'"rating_count"', r'"generic', r'"composition', r'"salt']:
    print("[%s]" % pat)
    ctx(pat)
