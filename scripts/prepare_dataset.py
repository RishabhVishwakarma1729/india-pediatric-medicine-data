"""Clean + classify the crawled products into one dataset. Applies: India-only sources, 12-month recency, five target formulations.

Output: raw_pages/dataset_clean.csv (kept rows) and raw_pages/dataset_excluded.csv (rows dropped, with reason).
"""
import glob
import json
import re
import sys
from datetime import date, datetime

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
B = r"C:\Users\RISHABH\Desktop\Pediatric_Medicine_India\raw_pages"
TODAY = date(2026, 10, 31)
CUTOFF = date(2025, 10, 31)  # data must be from the last 12 months

rows = []
for f in glob.glob(B + r"\products_*.jsonl"):
    for line in open(f, encoding="utf-8"):
        rows.append(json.loads(line))
df = pd.DataFrame(rows)
for col in ("manufacturer_address", "price_valid_until", "marketer_address", "marketer", "other_packs", "page_updated", "rating_raw", "available", "sale_price", "dosage_form", "molecule"):
    if col not in df.columns:
        df[col] = None


def cell(r, k):
    v = r.get(k)
    return None if (v is None or (isinstance(v, float) and pd.isna(v))) else v


# ------------------------------------------------------------------ classification helpers
def formulation(r):
    t = " ".join(str(cell(r, k) or "") for k in ("name", "pack", "dosage_form")).lower() + " " + r["url"].rsplit("/", 1)[-1].replace("-", " ").lower()
    if re.search(r"dry syrup|dry suspension|dry powder|powder for|for oral suspension|readymix|ready mix|rediuse|redimix|reconstitut", t):
        return "Dry powder for suspension (dry syrup)"
    if re.search(r"sachet", t):
        return "Sachet"
    if re.search(r"granule", t):
        return "Granules"
    if re.search(r"suspension|\bsusp\b", t):
        return "Suspension"
    if re.search(r"syrup|oral solution|oral liquid|solution", t):
        return "Syrup / oral solution"
    return None


BRAND_MOL = {
    "Calpol": "Paracetamol", "Crocin": "Paracetamol", "Dolo": "Paracetamol", "Pacimol": "Paracetamol", "Febrex Plus": "Paracetamol + cold-medicine combination",
    "Ibugesic Plus": "Ibuprofen + Paracetamol", "Brufen": "Ibuprofen", "Meftal-P": "Mefenamic acid + Paracetamol",
    "Augmentin Duo": "Amoxicillin + Clavulanic acid", "Clavam": "Amoxicillin + Clavulanic acid", "Moxikind-CV": "Amoxicillin + Clavulanic acid",
    "Megaclav": "Amoxicillin + Clavulanic acid", "Bactoclav": "Amoxicillin + Clavulanic acid", "Novamox": "Amoxicillin", "Wymox": "Amoxicillin",
    "Taxim-O": "Cefixime", "Zifi": "Cefixime", "Cefix": "Cefixime", "Mahacef": "Cefixime",
    "Cepodem": "Cefpodoxime", "Doxcef": "Cefpodoxime", "Cefakind": "Cefpodoxime", "Ceftum": "Cefuroxime", "Zocef": "Cefuroxime",
    "Azithral": "Azithromycin", "Azee": "Azithromycin", "Zithromax": "Azithromycin", "Aziwok": "Azithromycin",
    "Ascoril": "Cough/cold combination", "Alex": "Cough/cold combination", "Grilinctus": "Cough/cold combination", "Benadryl": "Cough/cold combination",
    "Chericof": "Cough/cold combination", "Tusq": "Cough/cold combination", "Corex": "Cough/cold combination", "Honitus": "Cough/cold combination",
    "Cetzine": "Cetirizine", "Okacet": "Cetirizine", "Alerid": "Cetirizine", "Levocet": "Levocetirizine", "Xyzal": "Levocetirizine",
    "Montair": "Montelukast + Levocetirizine", "Montek": "Montelukast + Levocetirizine",
    "Emeset": "Ondansetron", "Ondem": "Ondansetron", "Domstal": "Domperidone", "Vomistop": "Domperidone",
    "Electral": "Oral rehydration salts", "ORSL": "Oral rehydration salts", "Enerzal": "Oral rehydration salts",
    "Zinconia": "Zinc (syrup form)", "Z&D": "Zinc (syrup form)", "Zincovit": "Multivitamin + zinc",
    "Econorm": "Probiotic", "Sporlac": "Probiotic", "Bifilac": "Probiotic",
    "Duphalac": "Lactulose", "Looz": "Lactulose", "Cremaffin": "Laxative (milk of magnesia + liquid paraffin)", "Cyclopam": "Dicyclomine combination",
    "Zentel": "Albendazole", "Bandy": "Albendazole", "Asthalin": "Salbutamol", "Ventorlin": "Salbutamol",
    "Practin": "Cyproheptadine (appetite)", "Dexorange": "Iron + folic acid + B12 (hematinic)",
}


# Exact named-brand match on the START of the product name. Small look-alike brands (Azeeloyd, Cefixain ...) do not match.
STRICT = {
    "Calpol": r"^calpol\b", "Crocin": r"^crocin\b", "Dolo": r"^dolo\b", "Pacimol": r"^pacimol\b", "Febrex Plus": r"^febrex\b", "Ibugesic Plus": r"^ibugesic\b", "Brufen": r"^brufen\b",
    "Meftal-P": r"^meftal[ -]?p\b", "Augmentin Duo": r"^augmentin\b", "Clavam": r"^clavam\b", "Moxikind-CV": r"^moxikind\b", "Megaclav": r"^megaclav\b", "Bactoclav": r"^bactoclav\b",
    "Novamox": r"^novamox\b", "Wymox": r"^wymox\b", "Taxim-O": r"^taxim[ -]?o\b", "Zifi": r"^zifi\b", "Cefix": r"^cefix\b", "Mahacef": r"^mahacef\b", "Cepodem": r"^cepodem\b",
    "Doxcef": r"^doxcef\b", "Cefakind": r"^cefakind\b", "Ceftum": r"^ceftum\b", "Zocef": r"^zocef\b", "Azithral": r"^azithral\b", "Azee": r"^azee\b", "Zithromax": r"^zithromax\b",
    "Aziwok": r"^aziwok\b", "Ascoril": r"^ascoril\b", "Alex": r"^alex\b", "Grilinctus": r"^grilinctus\b", "Benadryl": r"^benadryl\b", "Chericof": r"^chericof\b", "Tusq": r"^tusq\b",
    "Corex": r"^corex\b", "Honitus": r"^honitus\b", "Cetzine": r"^cetzine\b", "Okacet": r"^okacet\b", "Alerid": r"^alerid\b", "Levocet": r"^levocet\b", "Xyzal": r"^xyzal\b",
    "Montair": r"^montair\b", "Montek": r"^montek\b", "Emeset": r"^emeset\b", "Ondem": r"^ondem\b", "Domstal": r"^domstal\b", "Vomistop": r"^vomistop\b", "Electral": r"^electral\b",
    "ORSL": r"^orsl\b", "Enerzal": r"^enerzal\b", "Zinconia": r"^zinconia\b", "Z&D": r"^z\s*(&|and)\s*d\b", "Zincovit": r"^zincovit\b", "Econorm": r"^econorm\b", "Sporlac": r"^sporlac\b",
    "Bifilac": r"^bifilac\b", "Duphalac": r"^duphalac\b", "Looz": r"^looz\b", "Cremaffin": r"^cremaffin\b", "Cyclopam": r"^cyclopam\b", "Zentel": r"^zentel\b", "Bandy": r"^bandy\b",
    "Asthalin": r"^asthalin\b", "Ventorlin": r"^ventorlin\b", "Practin": r"^practin\b", "Dexorange": r"^dexorange\b",
}
STRICT = {k: re.compile(v, re.I) for k, v in STRICT.items()}


def brand_key(name, fallback):
    name = re.sub(r"^(new|buy)\s+", "", str(name).strip(), flags=re.I)
    for k, pat in STRICT.items():
        if pat.search(name):
            return k
    first = re.split(r"[\s\-]+", name)[0]
    return first.title() + " (other brand)" if first else fallback


def apollo_pack(name):
    m = re.search(r"(\d+(?:\.\d+)?)\s*(ml|gm|gms|g|sachets?)\b", str(name), re.I)
    return f"{m.group(1)} {m.group(2).lower()}" if m else None


VET = re.compile(r"\bpet\b|\bpup\b|\bpuppy\b|\bdog\b|\bcat\b|veterinary|\bvet\b", re.I)


def molecule_key(r):
    """Label from the page's own listed composition first; fall back to the brand family only when the page lists no composition."""
    comp = str(cell(r, "composition") or "").lower()
    name = str(cell(r, "name") or "").lower()
    t = comp + " " + name
    has = lambda *ks: any(k in t for k in ks)
    if has("ofloxacin", "ornidazole") and has("metronidazole", "ornidazole", "cefixime", "ofloxacin"):
        return "Anti-infective combination (not on NLEM)"
    if has("amox", "moxikind", "augmentin", "clavam"):
        return "Amoxicillin + Clavulanic acid" if has("clav", "augmentin", "clavam", "moxikind", "-cv", " cv") else "Amoxicillin"
    if has("cefixime"):
        return "Cefixime"
    if has("cefpodoxime"):
        return "Cefpodoxime"
    if has("cefuroxime"):
        return "Cefuroxime"
    if has("azithromycin"):
        return "Azithromycin"
    if has("clarithromycin"):
        return "Clarithromycin"
    if has("paracetamol", "acetaminophen"):
        if has("ibuprofen"):
            return "Ibuprofen + Paracetamol"
        if has("mefenamic"):
            return "Mefenamic acid + Paracetamol"
        if has("phenylephrine", "chlorphen", "cetirizine", "caffeine", "dextromethorphan"):
            return "Paracetamol + cold-medicine combination"
        return "Paracetamol"
    if has("ibuprofen"):
        return "Ibuprofen"
    if has("mefenamic"):
        return "Mefenamic acid"
    if has("dicyclomine", "dicycloverine"):
        return "Dicyclomine combination"
    if has("lactulose"):
        return "Lactulose"
    if has("lactitol", "polyethylene glycol", "picosulfate", "liquid paraffin", "ispaghula", "milk of magnesia", "magnesium hydroxide"):
        return "Laxative (other, not on NLEM)"
    if has("ambroxol", "guaifenesin", "dextromethorphan", "levosalbutamol", "terbutaline", "bromhexine", "phenylephrine", "cough", "levocloperastine", "codeine", "triprolidine", "diphenhydramine", "ammonium chloride"):
        return "Cough/cold combination"
    if has("diastase", "pepsin", "pancreatin", "papain"):
        return "Digestive enzyme syrup (not on NLEM)"
    if has("potassium chloride", "sodium citrate") and has("sodium chloride"):
        return "Oral rehydration salts"
    if has("chlorpheniramine", "chlorphenamine"):
        return "Chlorpheniramine"
    if has("montelukast"):
        return "Montelukast + Levocetirizine"
    if has("levocetirizine"):
        return "Levocetirizine"
    if has("cetirizine"):
        return "Cetirizine"
    if has("ondansetron"):
        return "Ondansetron"
    if has("domperidone"):
        return "Domperidone"
    if has("salbutamol", "albuterol"):
        return "Salbutamol"
    if has("albendazole"):
        return "Albendazole"
    if has("lactobac", "bacillus", "saccharomyces", "streptococ", "bifidobac", "clostridium", "probiotic"):
        return "Probiotic"
    if has("rehydration", "electrolyte") or (has("sodium chloride") and has("glucose", "dextrose")):
        return "Oral rehydration salts"
    if has("zinc"):
        return "Multivitamin + zinc" if has("vitamin", "multivit") else "Zinc (syrup form)"
    if has("iron", "ferric", "ferrous"):
        return "Iron + folic acid + B12 (hematinic)"
    if has("cyproheptadine"):
        return "Cyproheptadine (appetite)"
    if not comp.strip() or comp.strip() == "nan":
        return BRAND_MOL.get(r["brand_family"], "Other (not mapped)")
    return "Other (not mapped)"


# NLEM 2022 (India) relevance levels. Evidence rows are in evidence_table.csv (verbatim, with PDF page).
# level: 1 = oral liquid tagged '(p)' at primary-care level; 2 = '(p)' at secondary/tertiary level only; 3 = listed oral liquid / ORS without '(p)';
#        4 = molecule on NLEM only as a different form or only as separate components; 5 = not on NLEM 2022.
REL = {
    "Paracetamol": (1, "Paracetamol"), "Ibuprofen": (1, "Ibuprofen"), "Mefenamic acid": (1, "Mefenamic acid"), "Amoxicillin": (1, "Amoxicillin"),
    "Amoxicillin + Clavulanic acid": (1, "Amoxicillin + Clavulanic acid"),
    "Azithromycin": (1, "Azithromycin"), "Cefuroxime": (1, "Cefuroxime"), "Cetirizine": (1, "Cetirizine"), "Albendazole": (1, "Albendazole"),
    "Cefixime": (2, "Cefixime"), "Ondansetron": (2, "Ondansetron"), "Clarithromycin": (2, "Clarithromycin"),
    "Domperidone": (3, "Domperidone"), "Lactulose": (3, "Lactulose"), "Salbutamol": (3, "Salbutamol"), "Oral rehydration salts": (3, "Oral rehydration salts"),
    "Chlorpheniramine": (3, "Chlorpheniramine"),
    "Ibuprofen + Paracetamol": (4, "Ibuprofen"), "Mefenamic acid + Paracetamol": (4, "Mefenamic acid"), "Zinc (syrup form)": (4, "Zinc sulphate"),
    "Montelukast + Levocetirizine": (4, "Montelukast"), "Iron + folic acid + B12 (hematinic)": (4, "Ferrous salt (+folic acid)"),
    "Paracetamol + cold-medicine combination": (4, "Paracetamol"),
}
BASIS = {
    1: "Level 1: NLEM 2022 lists this molecule as an oral liquid tagged '(p)', available at primary-care level",
    2: "Level 2: NLEM 2022 lists an oral liquid tagged '(p)', but only at secondary/tertiary care level",
    3: "Level 3: NLEM 2022 lists the molecule (oral liquid or ORS 'as licensed') without a '(p)' tag",
    4: "Level 4: on NLEM 2022 only as a different dosage form or only as separate components; this exact product/combination is not listed",
    5: "Level 5: not on NLEM 2022 - no India-specific essential-list evidence found",
}

ev = {r["molecule"]: r for r in pd.read_csv(B + r"\evidence_table.csv").to_dict("records")}

out, dropped = [], []
for _, row in df.iterrows():
    r = row.to_dict()
    reason = None
    if r.get("status") != 200:
        reason = f"fetch status {r.get('status')}"
    elif not cell(r, "name"):
        reason = "no product name parsed"
    elif VET.search(str(cell(r, "name"))) or VET.search(str(cell(r, "composition") or "")):
        reason = "veterinary (pet) product - not human pediatric"
    elif cell(r, "mrp") is None:
        reason = "no MRP on page"
    elif float(cell(r, "mrp")) > 3000:
        reason = f"implausible MRP shown on page (Rs {float(cell(r, 'mrp')):.0f} for a liquid/sachet product) - likely a listing error on the platform"
    else:
        pu = cell(r, "page_updated")
        if pu and datetime.fromisoformat(str(pu)[:10]).date() < CUTOFF:
            reason = f"page last updated {str(pu)[:10]} (older than 12 months)"
        pv = cell(r, "price_valid_until")
        if not reason and pv and datetime.fromisoformat(str(pv)[:10]).date() < TODAY:
            reason = f"price valid-until {str(pv)[:10]} already expired (stale listing)"
    form = formulation(r) if not reason else None
    if not reason and form is None:
        reason = "formulation not one of the five target forms"
    if reason:
        dropped.append({"site": r["site"], "url": r["url"], "name": cell(r, "name"), "reason": reason})
        continue
    mk = molecule_key(r)
    lvl, ekey = REL.get(mk, (5, None))
    e = ev.get(ekey) if ekey else None
    # demand signals
    dtext, dn = cell(r, "demand_text"), cell(r, "demand_n")
    rr = cell(r, "rating_raw")
    rcount = None
    if rr:
        m = re.search(r'"subText":"([\d,]+) ratings', rr)
        a = re.search(r'"averageRating":([\d.]+)', rr)
        if m:
            rcount = int(m.group(1).replace(",", ""))
            dtext = (dtext + "; " if dtext else "") + f"{rcount} ratings (avg {a.group(1) if a else 'n/a'}) on 1mg"
    name = str(cell(r, "name"))
    bk = brand_key(name, r["brand_family"])
    if r["site"] == "Apollo":
        r["pack"] = apollo_pack(name)
    out.append({
        "site": r["site"], "brand_family": bk, "crawl_token": r["brand_family"], "name": name, "url": r["url"], "retrieved_utc": r["retrieved_utc"],
        "composition": cell(r, "composition"), "molecule_key": mk, "formulation": form,
        "pediatric_label": "Yes" if re.search(r"paediatric|pediatric|kid|junior|child|infant|baby|little", name, re.I) else "No",
        "manufacturer": re.sub(r"^[A-Za-z]\)\s*", "", str(cell(r, "manufacturer"))).strip() if cell(r, "manufacturer") else None, "marketer": cell(r, "marketer"),
        "location": cell(r, "marketer_address") or cell(r, "manufacturer_address"),
        "mrp": cell(r, "mrp"), "pack": cell(r, "pack"), "other_packs": cell(r, "other_packs"), "available": cell(r, "available"),
        "demand_text": dtext, "bought_n": dn if (dn and "bought recently" in str(cell(r, "demand_text") or "")) else None, "rating_count": rcount or (dn if (dn and "ratings" in str(cell(r, "demand_text") or "")) else None),
        "rel_level": lvl, "rel_basis": BASIS[lvl],
        "nlem_row": e["nlem_2022_row"][:230] if e else "Not on NLEM 2022 list (searched list text)" if lvl == 5 else None,
        "nlem_pages": f"PDF p{e['nlem_pdf_page']} ({e['nlem_printed_page']})" if e else None,
    })
clean = pd.DataFrame(out)
pd.DataFrame(dropped).to_csv(B + r"\dataset_excluded.csv", index=False, encoding="utf-8-sig")
clean.to_csv(B + r"\dataset_clean.csv", index=False, encoding="utf-8-sig")
print("kept:", len(clean), "| excluded:", len(dropped))
print(clean.groupby("site").size().to_string())
print("\nformulation:\n", clean["formulation"].value_counts().to_string())
print("\nrelevance level:\n", clean["rel_level"].value_counts().sort_index().to_string())
print("\nmolecule key:\n", clean["molecule_key"].value_counts().head(30).to_string())
print("\nexclusion reasons:\n", pd.DataFrame(dropped)["reason"].str.replace(r"\d{4}-\d{2}-\d{2}", "DATE", regex=True).str.replace(r"status \d+", "status N", regex=True).value_counts().to_string())
