"""Extract Pharmarack brand-sales rows (Rs mn, Jun/Jul 2026) from the BOBCAPS 13-Aug-2026 report for the target brands."""
import csv
import re
import sys

from pypdf import PdfReader

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
# Download first: https://www.barodaetrade.com/Reports/Pharmaceuticals-SectorUpdate13Aug26-Research.pdf
PDF = r"C:\Users\RISHABH\Desktop\Pediatric_Medicine_India\raw_pages\evidence_docs\BOBCAPS_Pharma_Update_13Aug2026.pdf"
OUT = r"C:\Users\RISHABH\Desktop\Pediatric_Medicine_India\raw_pages\pharmarack_brand_rows.csv"
TARGETS = ["CALPOL", "CROCIN", "DOLO", "MEFTAL", "AUGMENTIN", "CLAVAM", "TAXIM O", "TAXIM", "ZIFI", "AZEE", "AZITHRAL", "ASCORIL", "ALEX", "GRILINCTUS", "BENADRYL", "CETZINE", "ONDEM", "EMESET", "DOMSTAL",
           "ELECTRAL", "ECONORM", "DUPHALAC", "ZENTEL", "ASTHALIN", "PRACTIN", "MONTAIR", "LEVOCET", "XYZAL", "CEFTUM", "ZOCEF", "CEFIX", "CEPODEM", "DOXCEF", "MOXIKIND", "MEGACLAV", "NOVAMOX", "ZINCOVIT", "SPORLAC", "BIFILAC", "LOOZ", "CREMAFFIN", "CYCLOPAM", "TUSQ", "COREX", "CHERICOF", "MONTEK", "ALERID", "OKACET", "T BACT"]
reader = PdfReader(PDF)
rows = []
for pno, pg in enumerate(reader.pages, start=1):
    flat = re.sub(r"\s+", " ", pg.extract_text() or "")
    # a row looks like: "<CORPORATE>* <rank> <BRAND> <jun> <jul>"
    for m in re.finditer(r"([A-Z][A-Z\.'&\- ]{2,24}?)\*?\s(\d{1,2})\s([A-Z][A-Z0-9 \-\+\.&/]{1,26}?)\s(\d+(?:\.\d+)?)\s(\d+(?:\.\d+)?)(?=\s[A-Z]|\s|$)", flat):
        corp, rank, brand, jun, jul = m.groups()
        b = brand.strip()
        if any(b == t or b.startswith(t + " ") for t in TARGETS):
            rows.append({"page": pno, "company": corp.strip(), "rank_in_company": int(rank), "brand": b, "sv_jun_2026_rs_mn": float(jun), "sv_jul_2026_rs_mn": float(jul)})
seen = set()
uniq = []
for r in rows:
    k = (r["company"], r["brand"])
    if k not in seen:
        seen.add(k)
        uniq.append(r)
for r in uniq:
    print(r)
with open(OUT, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["page", "company", "rank_in_company", "brand", "sv_jun_2026_rs_mn", "sv_jul_2026_rs_mn"])
    w.writeheader()
    w.writerows(uniq)
print("rows:", len(uniq))
