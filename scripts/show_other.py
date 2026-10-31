import sys

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
df = pd.read_csv(r"C:\Users\RISHABH\Desktop\Pediatric_Medicine_India\raw_pages\dataset_clean.csv", encoding="utf-8-sig")
o = df[df["molecule_key"] == "Other (not mapped)"]
for _, r in o.iterrows():
    print(f"{r['site']:9s} {str(r['name'])[:55]:55s} | {str(r['composition'])[:70]}")
print()
c = df[df["molecule_key"] == "Cefixime"]
print("cefixime rows with pediatric label:", (c["pediatric_label"] == "Yes").sum(), "of", len(c), "| by site:", c["site"].value_counts().to_dict())
print(c["brand_family"].value_counts().head(8).to_dict())
