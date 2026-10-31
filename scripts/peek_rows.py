import sys

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
P = r"C:\Users\RISHABH\Desktop\Pediatric_Medicine_India\India_Pediatric_Liquid_Medicines_Oct2026.xlsx"
s1 = pd.read_excel(P, sheet_name="1_Most_Sold_High_Demand")
s2 = pd.read_excel(P, sheet_name="2_Most_Pediatric_Relevant")
print("--- SHEET 1, row 3 (Calpol) ---")
r = s1[s1["Brand family"] == "Calpol"].iloc[0]
for k, v in r.items():
    print(f"  {k:48s} {str(v)[:150]}")
print("\n--- SHEET 2, first Level-2 row ---")
r = s2[s2["Relevance level (India NLEM 2022)"] == 2].iloc[0]
for k, v in r.items():
    print(f"  {k:48s} {str(v)[:150]}")
print("\nSheet 2 rows per level:", s2["Relevance level (India NLEM 2022)"].value_counts().sort_index().to_dict())
print("Sheet 2 molecule groups:", s2["Molecule group"].value_counts().to_dict())
cov = pd.read_excel(P, sheet_name="Coverage_and_gaps", header=None)
print("\n--- Coverage sheet ---")
print(cov.fillna("").to_string(index=False, header=False)[:2200])
