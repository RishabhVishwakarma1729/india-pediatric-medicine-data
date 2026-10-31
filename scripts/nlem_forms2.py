"""Search the whole NLEM text for each target molecule followed (within 500 chars) by a liquid / granule / sachet form. Print page + snippet."""
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
text = open(r"C:\Users\RISHABH\Desktop\Pediatric_Medicine_India\raw_pages\evidence_docs\nlem_text.txt", encoding="utf-8").read()
pages = {int(m.group(1)): m.group(2) for m in re.finditer(r"=====PAGE (\d+)=====\n(.*?)(?=\n=====PAGE |\Z)", text, re.S)}
FORMS = re.compile(r"(oral liquid|powder for oral|granule|sachet|suspension|syrup|oral solution|dispersible)", re.I)
MOLS = ["Paracetamol", "Ibuprofen", "Mefenamic", "Amoxicillin", "Azithromycin", "Cefixime", "Cefuroxime", "Cefadroxil", "Cetirizine", "Ondansetron", "Domperidone",
        "Oral rehydration salts", "Zinc", "Albendazole", "Lactulose", "Salbutamol", "Montelukast", "Co-trimoxazole", "Metronidazole", "Ferrous", "Clarithromycin", "Chlorpheniramine", "Prednisolone", "Cloxacillin", "Erythromycin", "Fluconazole"]
for mol in MOLS:
    print("=" * 72)
    print(mol)
    shown = 0
    for pg in sorted(pages):
        if pg < 140 or pg > 302:
            continue
        body = re.sub(r"\s+", " ", pages[pg])
        for m in re.finditer(r"\d+\.\d+(?:\.\d+)?\s+" + re.escape(mol) + r"[^|]{0,60}?(?=\s\d+\.\d+\s|$)", body):
            pass
        for m in re.finditer(re.escape(mol), body, re.I):
            window = body[m.start() : m.start() + 330]
            # only list-body rows: a row number like '27.4 Paracetamol' just before the molecule name
            before = body[max(0, m.start() - 8) : m.start()]
            if not re.search(r"\d+\.\d+\s*$", before):
                continue
            if FORMS.search(window):
                print(f"  PDF p{pg}: {window}")
                shown += 1
                break
        if shown >= 3:
            break
    if not shown:
        print("  (no list-body row with a liquid/granule/sachet form found)")
