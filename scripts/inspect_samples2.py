import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = r"C:\Users\RISHABH\Desktop\Pediatric_Medicine_India\raw_pages\samples"

# ---------------- PharmEasy
html = open(BASE + r"\PharmEasy_sample.html", encoding="utf-8").read()
data = json.loads(re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S).group(1))
pd = data["props"]["pageProps"]["productDetails"]
print("PharmEasy productDetails scalar fields:")
for k, v in pd.items():
    if isinstance(v, (str, int, float, bool)) or v is None:
        print(f"  {k:28s} {str(v)[:90]}")
print("  nested keys:", [k for k, v in pd.items() if isinstance(v, (dict, list))])
for k in ("salePrice", "mrp", "price", "priceDetails", "productPrice", "ratingsCount"):
    if k in pd:
        print("  >>", k, json.dumps(pd[k], ensure_ascii=False)[:300])
for m in list(re.finditer(r"Bought 2 lakh\+ users", html))[:1]:
    print("  context:", html[max(0, m.start() - 250) : m.end() + 120].replace("\n", " "))

# ---------------- Apollo
html = open(BASE + r"\Apollo_sample.html", encoding="utf-8").read()
print()
print("Apollo")
m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
print("  __NEXT_DATA__:", bool(m))
for pat in [r'"manufacturer[^"]*":"[^"]{2,60}"', r'"mrp":[\d.]+', r'"price":[\d.]+', r'"specialPrice":[\d.]+', r'"packSize[^"]*":"?[^",]{1,40}', r'"sku":"[^"]+"', r'"productName":"[^"]+"', r'"formulation[^"]*":"[^"]+"', r'"dosage[^"]*":"[^"]+"', r'(?i)recently purchased[^<"]{0,60}', r'(?i)[\d,]+\+? (?:people|customers|users)[^<"]{0,50}', r'"rating[^"]*":[\d.]+', r'"reviewCount":[\d]+', r'"ratingValue":[\d.]+']:
    print(f"  {pat[:46]:48s}", re.findall(pat, html)[:4])
for m in list(re.finditer(r"RecentlyPurchase", html))[:2]:
    print("  ctx:", html[m.start() : m.start() + 260].replace("\n", " "))
