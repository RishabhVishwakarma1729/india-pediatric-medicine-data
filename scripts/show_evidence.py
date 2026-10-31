import csv
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
for r in csv.DictReader(open(r"C:\Users\RISHABH\Desktop\Pediatric_Medicine_India\raw_pages\evidence_table.csv", encoding="utf-8")):
    print("=" * 78)
    print(r["molecule"])
    print("  NLEM p%s (%s): %s" % (r["nlem_pdf_page"], r["nlem_printed_page"], r["nlem_2022_row"][:300]))
    print("  WHO  p%s: %s" % (r["who_pdf_page"], r["who_eml_2025_row"][:260]))
