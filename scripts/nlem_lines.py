"""Pull NLEM 2022 list lines (final list pages) for each target molecule: dosage forms and strengths, with page numbers."""
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
text = open(r"C:\Users\RISHABH\Desktop\Pediatric_Medicine_India\raw_pages\evidence_docs\nlem_text.txt", encoding="utf-8").read()
pages = {}
for m in re.finditer(r"=====PAGE (\d+)=====\n(.*?)(?=\n=====PAGE |\Z)", text, re.S):
    pages[int(m.group(1))] = m.group(2)

print("pages with 'Section' list markers between 296 and 308:")
for p in range(296, 309):
    t = pages.get(p, "")
    print(f"--- page {p}: {len(t)} chars; head: {t[:140].strip()!r}")

MOLS = ["Paracetamol", "Ibuprofen", "Amoxicillin", "Azithromycin", "Cefixime", "Cefuroxime", "Cefadroxil", "Cetirizine", "Ondansetron", "Domperidone",
        "Oral Rehydration", "Zinc", "Albendazole", "Lactulose", "Salbutamol", "Montelukast", "Co-trimoxazole", "Metronidazole", "Ferrous", "Clarithromycin", "Chlorpheniramine", "Prednisolone", "Mefenamic"]
for mol in MOLS:
    print("=" * 70)
    print(mol)
    for p in range(296, 309):
        t = pages.get(p, "")
        for line_i, line in enumerate(t.splitlines()):
            if re.search(mol, line, re.I):
                block = " | ".join(x.strip() for x in t.splitlines()[line_i : line_i + 4] if x.strip())
                print(f"  p{p}: {block[:260]}")
