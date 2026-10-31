import re
from collections import Counter

import requests

H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"}
text = requests.get("https://www.1mg.com/sitemap.xml", headers=H, timeout=40).text
locs = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", text)
prefix = Counter(re.sub(r"_?\d+\.xml$", "", u.rsplit("/", 1)[-1]) for u in locs)
print(len(locs), "sitemap files")
for k, v in prefix.most_common():
    print(f"  {k:40s} {v}")
