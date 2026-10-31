import json
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, r"C:\Users\RISHABH\Desktop\Pediatric_Medicine_India\scripts")
import fetch_products as fp

S = r"C:\Users\RISHABH\Desktop\Pediatric_Medicine_India\raw_pages\samples"
for site, fn in (("1mg", "1mg_sample.html"), ("PharmEasy", "PharmEasy_sample.html"), ("Apollo", "Apollo_sample.html"), ("Netmeds", "Netmeds_sample.html")):
    html = open(f"{S}\\{fn}", encoding="utf-8").read()
    out = fp.PARSERS[site](html)
    print("=" * 60)
    print(site)
    for k, v in out.items():
        print(f"  {k:18s} {str(v)[:110]}")
