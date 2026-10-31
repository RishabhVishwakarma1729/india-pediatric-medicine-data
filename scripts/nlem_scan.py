"""Extract text from the NLEM PDF and report which pediatric-relevant molecules appear with an oral liquid / sachet / granule form."""
import re
import sys

from pypdf import PdfReader

PDF = r"C:\Users\RISHABH\Desktop\Pediatric_Medicine_India\raw_pages\evidence_docs\Essential_Drugs_National.pdf"
OUT = r"C:\Users\RISHABH\Desktop\Pediatric_Medicine_India\raw_pages\evidence_docs\nlem_text.txt"

reader = PdfReader(PDF)
print("pages:", len(reader.pages))
pages = []
for i, page in enumerate(reader.pages, start=1):
    try:
        text = page.extract_text() or ""
    except Exception as exc:
        text = ""
    pages.append(text)
with open(OUT, "w", encoding="utf-8") as fh:
    for i, text in enumerate(pages, start=1):
        fh.write(f"\n=====PAGE {i}=====\n{text}")
total_chars = sum(len(t) for t in pages)
print("total chars:", total_chars)
print("first 600 chars of page 1:\n", pages[0][:600] if pages else "")

MOLECULES = ["paracetamol", "ibuprofen", "amoxicillin", "clavulan", "azithromycin", "cefixime", "cefpodoxime", "cefuroxime", "cefadroxil",
             "cetirizine", "levocetirizine", "ondansetron", "domperidone", "oral rehydration", "zinc", "albendazole", "lactulose",
             "salbutamol", "ambroxol", "guaifenesin", "montelukast", "phenobarbital", "valproate", "levetiracetam", "iron", "ferrous",
             "cotrimoxazole", "co-trimoxazole", "metronidazole", "chlorpheniramine", "cyproheptadine", "dextromethorphan", "multivitamin", "vitamin a", "calcium", "ranitidine", "mefenamic", "diclofenac", "dicyclomine", "racecadotril", "lactobacillus", "probiotic", "ofloxacin", "cefaclor", "erythromycin", "clarithromycin", "ciprofloxacin", "cloxacillin", "penicillin", "fluconazole", "nystatin", "prednisolone", "paediatric", "pediatric"]
for mol in MOLECULES:
    hits = [i for i, t in enumerate(pages, start=1) if re.search(mol, t, re.I)]
    print(f"{mol:18s} pages={hits[:12]}")
