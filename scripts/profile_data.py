import glob
import json
import sys

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
rows = []
for f in glob.glob(r"C:\Users\RISHABH\Desktop\Pediatric_Medicine_India\raw_pages\products_*.jsonl"):
    for line in open(f, encoding="utf-8"):
        rows.append(json.loads(line))
df = pd.DataFrame(rows)
print("total rows:", len(df))
print(df.groupby("site").agg(rows=("url", "count"), ok=("status", lambda s: (s == 200).sum())))
ok = df[(df["status"] == 200) & df["name"].notna()]
print("\nusable (200 + name):", len(ok))
print(ok.groupby("site").agg(rows=("url", "count"), with_mrp=("mrp", lambda s: s.notna().sum()), with_mfr=("manufacturer", lambda s: s.notna().sum())))
print("\nstatus counts by site:")
print(df.groupby(["site", "status"]).size())
m = ok[ok["site"] == "1mg"]
print("\n1mg 'bought recently' present:", m["demand_n"].notna().sum(), "of", len(m))
print(m["demand_n"].describe())
print(m.sort_values("demand_n", ascending=False)[["name", "brand_family", "demand_text", "mrp", "pack"]].head(15).to_string())
pe = ok[ok["site"] == "PharmEasy"]
print("\nPharmEasy ratings present:", pe["demand_n"].notna().sum(), "of", len(pe))
print(pe.sort_values("demand_n", ascending=False)[["name", "demand_text", "mrp"]].head(8).to_string())
print("\nPharmEasy page_updated min/max:", pe["page_updated"].min(), pe["page_updated"].max())
print("\n1mg rating_raw non-empty:", (m["rating_raw"].fillna("{}") != "{}").sum())
print(m[m["rating_raw"].fillna("{}") != "{}"][["name", "rating_raw"]].head(5).to_string())
