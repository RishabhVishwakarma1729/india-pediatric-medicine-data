import re
import sys

from pypdf import PdfReader

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
# Download first: https://www.barodaetrade.com/Reports/Pharmaceuticals-SectorUpdate13Aug26-Research.pdf
PDF = r"C:\Users\RISHABH\Desktop\Pediatric_Medicine_India\raw_pages\evidence_docs\BOBCAPS_Pharma_Update_13Aug2026.pdf"
reader = PdfReader(PDF)
print("pages:", len(reader.pages))
for i, pg in enumerate(reader.pages, start=1):
    t = pg.extract_text() or ""
    flat = re.sub(r"\s+", " ", t)
    for m in re.finditer(r"(?i)(taxim|augmentin|azithral|meftal|calpol|zifi|ascoril|pharmatrac|pharmarack|iqvia)", flat):
        s = max(0, m.start() - 160)
        print(f"p{i}: ...{flat[s : m.end() + 220]}...")
        print()
        break
