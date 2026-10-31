import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = r"C:\Users\RISHABH\Desktop\Pediatric_Medicine_India\raw_pages\samples"

html = open(BASE + r"\PharmEasy_sample.html", encoding="utf-8").read()
data = json.loads(re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S).group(1))
pd = data["props"]["pageProps"]["productDetails"]
for k in ("ratingDetails", "pastPurchasedDetails", "labelDetails", "compositions", "productAvailabilityFlags"):
    print(k, "=>", json.dumps(pd.get(k), ensure_ascii=False)[:700])
print("pageProps similarItemsBoughtData:", json.dumps(data["props"]["pageProps"].get("similarItemsBoughtData"), ensure_ascii=False)[:300])

html = open(BASE + r"\Apollo_sample.html", encoding="utf-8").read()
blocks = re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S)
drug = json.loads(blocks[0])
main = drug.get("mainEntity", {})
print()
print("Apollo Drug keys:", list(main.keys()))
for k in ("manufacturer", "offers", "activeIngredient", "dosageForm", "administrationRoute", "drugClass", "nonProprietaryName", "availableStrength", "packaging", "isProprietary"):
    if k in main:
        print("  ", k, "=>", json.dumps(main[k], ensure_ascii=False)[:400])
for pat in [r'"price":38\.5[^}]{0,200}', r'"mrp[^"]*":[^,]{1,30}', r'(?i)"manufacturer[^"]*":\{[^}]{0,150}', r'(?i)"packSize[^"]*":[^,]{0,40}', r'(?i)"(?:unit|pack)(?:Size|Label|Qty)[^"]*":[^,]{0,40}', r'(?i)"productUrl[^"]*":[^,]{0,80}']:
    print(f"  {pat[:40]:42s}", re.findall(pat, html)[:3])
m = re.search(r'"price":38\.5', html)
if m:
    print("  price ctx:", html[max(0, m.start() - 400) : m.end() + 200].replace("\n", " "))
