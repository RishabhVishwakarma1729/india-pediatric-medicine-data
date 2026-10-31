"""Build the India-only pediatric-relevance evidence table from NLEM 2022 (Government of India): exact list row + PDF page per molecule."""
import csv
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
B = r"C:\Users\RISHABH\Desktop\Pediatric_Medicine_India\raw_pages\evidence_docs"
NLEM_URL = "https://www.cspc.in/pdf2023/Essential_Drugs_National.pdf"
NLEM_OFFICIAL = "https://www.cdsco.gov.in/opencms/resources/UploadCDSCOWeb/2018/UploadPublic_NoticesFiles/reportnlem2022.pdf"

text = open(B + r"\nlem_text.txt", encoding="utf-8").read()
nlem = {int(m.group(1)): m.group(2) for m in re.finditer(r"=====PAGE (\d+)=====\n(.*?)(?=\n=====PAGE |\Z)", text, re.S)}
FORMS = re.compile(r"(Oral liquid|Dry Syrup|Granules|Sachet|Suspension|Syrup|Oral solution|As licensed|Dispersible)", re.I)

# molecule key -> NLEM row-name regex
MOL = {
    "Paracetamol": r"Paracetamol\*\*",
    "Ibuprofen": r"Ibuprofen\*",
    "Mefenamic acid": r"Mefenamic acid",
    "Amoxicillin": r"Amoxicillin P,S,T",
    "Amoxicillin + Clavulanic acid": r"Amoxicillin \(A\) \+ Clavulanic acid \(B\)",
    "Cefixime": r"Cefixime S,T",
    "Cefuroxime": r"Cefuroxime P,S,T",
    "Cefadroxil": r"Cefadroxil",
    "Azithromycin": r"Azithromycin\* P,S,T",
    "Clarithromycin": r"Clarithromycin\*\* S,T",
    "Cetirizine": r"Cetirizine P,S,T",
    "Ondansetron": r"Ondansetron\*+ S,T",
    "Domperidone": r"Domperidone P,S,T",
    "Oral rehydration salts": r"Oral rehydration salts\*\* P,S,T",
    "Zinc sulphate": r"Zinc Sulphate P,S,T",
    "Albendazole": r"Albendazole\* P,S,T",
    "Lactulose": r"Lactulose\* S,T",
    "Salbutamol": r"Salbutamol P,S,T",
    "Montelukast": r"Montelukast S,T",
    "Prednisolone": r"Prednisolone\*\*\* P,S,T",
    "Co-trimoxazole": r"Co-trimoxazole \[Sulphamethoxazole",
    "Metronidazole": r"Metronidazole\*\* P,S,T",
    "Ferrous salt (+folic acid)": r"Ferrous Salt \(A\)\+ Folic acid",
    "Chlorpheniramine": r"Chlorpheniramine P,S,T",
}

rows = []
for mol, pat in MOL.items():
    hit = None
    for pg in sorted(nlem):
        if pg < 177 or pg > 302:
            continue
        flat = re.sub(r"\s+", " ", nlem[pg])
        m = re.search(pat, flat)
        if m and FORMS.search(flat[m.start() : m.start() + 300]):
            head = re.search(r"Page \d+ of \d+", nlem[pg])
            hit = (pg, head.group(0) if head else "", flat[m.start() : m.start() + 300])
            break
    rows.append({
        "molecule": mol,
        "nlem_2022_row": hit[2] if hit else "Not found in NLEM 2022 list text",
        "nlem_pdf_page": hit[0] if hit else "",
        "nlem_printed_page": hit[1] if hit else "",
        "nlem_doc_url_read": NLEM_URL if hit else "",
        "nlem_official_url": NLEM_OFFICIAL if hit else "",
    })
for r in rows:
    print(f"{r['molecule']:30s} p{r['nlem_pdf_page']!s:4s} {r['nlem_2022_row'][:80]}")
with open(r"C:\Users\RISHABH\Desktop\Pediatric_Medicine_India\raw_pages\evidence_table.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print("rows:", len(rows))
