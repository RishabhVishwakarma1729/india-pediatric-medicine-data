import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, r"C:\Users\RISHABH\Desktop\Pediatric_Medicine_India\scripts")
import fetch_products as fp

S = r"C:\Users\RISHABH\Desktop\Pediatric_Medicine_India\raw_pages\samples"
for fn in ("Netmeds_sample.html", "netmeds_chericof.html", "netmeds_benadryl_nodrug.html"):
    out = fp.parse_netmeds(open(f"{S}\\{fn}", encoding="utf-8").read())
    print("=" * 50, fn)
    for k in ("name", "manufacturer", "composition", "mrp", "sale_price", "pack", "rating_count", "price_valid_until", "available", "error"):
        print(f"  {k:18s} {out.get(k)}")
