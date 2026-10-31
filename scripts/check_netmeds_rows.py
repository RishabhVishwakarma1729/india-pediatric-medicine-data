import json
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
rows = [json.loads(l) for l in open(r"C:\Users\RISHABH\Desktop\Pediatric_Medicine_India\raw_pages\products_Netmeds.jsonl", encoding="utf-8")]
for r in rows[:28]:
    print(f"{str(r.get('name'))[:48]:48s} mrp={r.get('mrp')} sale={r.get('sale_price')} pack={r.get('pack')} err={r.get('error')} fam={r.get('brand_family')}")
print([r["url"] for r in rows if not r.get("mrp")][:3])
