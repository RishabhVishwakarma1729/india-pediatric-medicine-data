import re
import sys

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
df = pd.read_csv(r"C:\Users\RISHABH\Desktop\Pediatric_Medicine_India\raw_pages\dataset_clean.csv", encoding="utf-8-sig")
EXPECT = {
    "Paracetamol": r"paracetamol|acetaminophen", "Cefixime": r"cefixime", "Amoxicillin + Clavulanic acid": r"clav", "Amoxicillin": r"amox", "Azithromycin": r"azithro",
    "Lactulose": r"lactulose", "Probiotic": r"lactobac|bacillus|saccharomyces|lactic|probiotic|streptococ", "Cefpodoxime": r"cefpodoxime", "Levocetirizine": r"levocetirizine|levocet",
    "Salbutamol": r"salbutamol|albuterol", "Albendazole": r"albendazole", "Ondansetron": r"ondansetron", "Cetirizine": r"cetirizine", "Domperidone": r"domperidone",
    "Ibuprofen + Paracetamol": r"ibuprofen", "Mefenamic acid + Paracetamol": r"mefenamic", "Oral rehydration salts": r"sodium|glucose|dextrose|rehydrat|ors", "Cefuroxime": r"cefuroxime",
    "Montelukast + Levocetirizine": r"montelukast", "Ibuprofen": r"ibuprofen",
}
bad_total = 0
for key, pat in EXPECT.items():
    sub = df[df["molecule_key"] == key]
    txt = (sub["composition"].fillna("") + " " + sub["name"].fillna("")).str.lower()
    ok = txt.str.contains(pat, regex=True)
    nbad = int((~ok).sum())
    bad_total += nbad
    print(f"{key:34s} rows={len(sub):4d} mismatch={nbad}")
    for _, r in sub[~ok].head(4).iterrows():
        print(f"      ? {r['site']:9s} {str(r['name'])[:60]:60s} | {str(r['composition'])[:50]}")
print("total mismatches:", bad_total)
