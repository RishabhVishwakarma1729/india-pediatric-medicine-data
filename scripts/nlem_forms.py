"""Read the NLEM 2022 list body (PDF page = list page + 240) for each target molecule and print the dosage-form lines."""
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
text = open(r"C:\Users\RISHABH\Desktop\Pediatric_Medicine_India\raw_pages\evidence_docs\nlem_text.txt", encoding="utf-8").read()
pages = {int(m.group(1)): m.group(2) for m in re.finditer(r"=====PAGE (\d+)=====\n(.*?)(?=\n=====PAGE |\Z)", text, re.S)}
OFFSET = 240

INDEX = {
    "Paracetamol": [7, 16], "Ibuprofen": [7, 16], "Mefenamic": [7], "Amoxicillin": [19], "Azithromycin": [21, 32], "Cefixime": [20], "Cefuroxime": [21],
    "Cefadroxil": [20], "Cetirizine": [9], "Ondansetron": [44, 60], "Domperidone": [60], "Oral rehydration": [62], "Zinc": [62], "Albendazole": [18],
    "Lactulose": [43, 62], "Salbutamol": [79], "Montelukast": [79], "Co-trimoxazole": [22, 35], "Metronidazole": [25, 33], "Ferrous": [45], "Clarithromycin": [22, 24],
}
for mol, lps in INDEX.items():
    print("=" * 72)
    print(mol, "-> list pages", lps, "-> PDF pages", [lp + OFFSET for lp in lps])
    for lp in lps:
        pp = lp + OFFSET
        body = pages.get(pp, "")
        lines = [ln.rstrip() for ln in body.splitlines()]
        hits = [i for i, ln in enumerate(lines) if re.search(mol, ln, re.I)]
        if not hits:
            print(f"  (PDF p{pp}: no line with '{mol}'; first lines: {' / '.join(l.strip() for l in lines[:3])[:120]})")
        for i in hits[:3]:
            snippet = " ".join(x.strip() for x in lines[i : i + 7] if x.strip())
            print(f"  PDF p{pp} (list p{lp}): {snippet[:430]}")
