import re
import sys

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
P = r"C:\Users\RISHABH\Desktop\Pediatric_Medicine_India\India_Pediatric_Liquid_Medicines_Oct2026.xlsx"
xl = pd.ExcelFile(P)
print("sheets:", xl.sheet_names)
for sn in ("1_Most_Sold_High_Demand", "2_Most_Pediatric_Relevant", "All_data"):
    d = xl.parse(sn)
    url_col = [c for c in d.columns if "URL" in c][0]
    print("=" * 70)
    print(sn, d.shape)
    print("  empty URL cells :", int(d[url_col].isna().sum()))
    print("  non-http URLs   :", int((~d[url_col].astype(str).str.startswith("http")).sum()))
    print("  duplicate URLs  :", int(d.duplicated(subset=[url_col, "Platform"]).sum()))
    print("  'nan' text cells:", int(d.astype(str).apply(lambda s: s.str.fullmatch("nan")).sum().sum()))
    print("  MRP missing     :", int(d["MRP (Rs)"].isna().sum()), "| MRP min/max:", d["MRP (Rs)"].min(), d["MRP (Rs)"].max())
    print("  formulation     :", d["Formulation"].value_counts().to_dict())
    print("  platforms       :", d["Platform"].value_counts().to_dict())

a = xl.parse("All_data")
print("\n=== MRP consistency: same brand, same pack volume, same strength across platforms ===")


def ml(p):
    m = re.search(r"(\d+(?:\.\d+)?)\s*ml", str(p), re.I)
    return float(m.group(1)) if m else None


def strength(t):
    m = re.search(r"(\d+(?:\.\d+)?)\s*(?:mg|mcg|gm|g)", str(t), re.I)
    return m.group(1) if m else None


a["ml"] = a["Pack size"].apply(ml)
a["key_name"] = a["Brand family"].where(~a["Brand family"].astype(str).str.contains("other brand"))
a["strength_in_name"] = a["Product"].str.extract(r"(\d{2,4})\s*(?:mg|ml|\b)")[0]
sub = a[a["key_name"].notna() & a["ml"].notna() & a["strength_in_name"].notna()].copy()
g = sub.groupby(["key_name", "strength_in_name", "ml"])
agree = disagree = 0
rows = []
for k, d in g:
    if d["Platform"].nunique() >= 2:
        spread = d["MRP (Rs)"].max() - d["MRP (Rs)"].min()
        if spread < 0.5:
            agree += 1
        else:
            disagree += 1
            rows.append((k, d[["Platform", "Product", "MRP (Rs)"]].values.tolist()))
print("groups on >=2 platforms with MRP within Rs 0.5:", agree, "| differing by >= Rs 0.5:", disagree)
for k, v in rows[:8]:
    print("  ", k)
    for x in v:
        print("      ", x)
print("\n=== MRP outliers (> Rs 1000) ===")
print(a[a["MRP (Rs)"] > 1000][["Platform", "Product", "MRP (Rs)", "Pack size"]].to_string(index=False))
print("\n=== Calpol rows ===")
print(a[a["Product"].str.lower().str.contains("calpol")][["Platform", "Product", "MRP (Rs)", "Pack size", "Platform demand signal"]].to_string(index=False))

s1 = xl.parse("1_Most_Sold_High_Demand")
print("\n=== Sheet 1 top rows ===")
print(s1[["Rank (brand)", "Brand family", "Platform", "Product (as listed)", "MRP (Rs)", "Pack size (as listed)", "Platform demand signal (verbatim)"]].head(12).to_string(index=False))
s2 = xl.parse("2_Most_Pediatric_Relevant")
print("\n=== Sheet 2 top rows ===")
print(s2[["Relevance rank", "Relevance level (India NLEM 2022)", "Molecule group", "Platform", "Product (as listed)", "MRP (Rs)"]].head(10).to_string(index=False))
print("\nrelevance level counts:", s2["Relevance level (India NLEM 2022)"].value_counts().sort_index().to_dict())
