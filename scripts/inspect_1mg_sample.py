import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

html = open(r"C:\Users\RISHABH\Desktop\Pediatric_Medicine_India\raw_pages\samples\1mg_sample.html", encoding="utf-8").read()


def ctx(pattern, width=260, limit=3):
    for i, m in enumerate(re.finditer(pattern, html)):
        if i >= limit:
            break
        s = max(0, m.start() - width // 3)
        print("  ..." + html[s : s + width].replace("\n", " ") + "...")
    print()


print("[bought recently]")
ctx(r'bought recently"', 360)
print("[price blocks]")
ctx(r'"price":"', 300)
print("[rating]")
ctx(r'(?i)"rating[^"]*":', 240)
print("[salt_composition]")
ctx(r'"salt_composition":\{', 420, 1)
print("[pack / unit]")
ctx(r'bottle of 60 ml', 300, 2)
print("[window state keys]")
for m in re.finditer(r"window\.__[A-Z_]+__\s*=", html):
    print("  ", m.group(0))
print("[drug id / sku]")
ctx(r'(?i)"(sku_id|drug_id|id)":\s*"?\d{5,8}', 160, 3)
