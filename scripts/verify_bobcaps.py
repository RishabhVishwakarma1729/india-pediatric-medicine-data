import re
import sys

from pypdf import PdfReader

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
PDF = r"C:\Users\RISHABH\.claude\projects\c--Users-RISHABH-Desktop\fd1e8231-44b4-4015-9320-c6f47b2326e6\tool-results\webfetch-1793439858854-5steps.pdf"
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
