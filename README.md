# India pediatric liquid medicines (ages 2-12): market data from Indian pharmacy platforms

Dataset of syrups, suspensions, dry-powder suspensions (dry syrups), sachets and granules sold in India,
collected from 1mg, PharmEasy, Apollo Pharmacy and Netmeds on 31 Oct 2026.

**Output:** `India_Pediatric_Liquid_Medicines_Oct2026.xlsx`
- `1_Most_Sold_High_Demand`: 30 brand families with a demand figure, ranked by evidence quality.
- `2_Most_Pediatric_Relevant`: ranked by India's NLEM 2022 (National List of Essential Medicines).
- Supporting sheets: README, NLEM evidence, Pharmarack sales, all data, excluded rows, coverage and gaps.

## Rules
- India-only sources. Data from the last 12 months (since 31 Oct 2025). NLEM 2022 is older but is still India's current list.
- Only pages allowed by each site's robots.txt, at each site's crawl delay. Search pages are disallowed, so products are found through the public sitemaps.
- MedPlus is not covered: it returns HTTP 403 to automated requests and the block was not worked around.
- Nothing is invented. Missing data is labelled "Not shown" or "Not publicly available".

## Known limits
- No public source ranks pediatric syrups by sales. National evidence is Pharmarack brand-level sales (all dosage forms) via a BOBCAPS report; platform evidence is 1mg's "people bought recently" count.
- No public state/city demand data.
- Netmeds listings are often stale (expired price-valid-until dates), so most are dropped by the 12-month rule.
- The brand list is a selection of well-known pediatric brands, not a census of the market.

## Reproduce
Python 3.10+, `requests`, `pandas`, `openpyxl`, `pypdf`. Run from `scripts/` in this order:
1. `discover_urls.py`, `discover_urls2.py`, `discover_1mg_rest.py`: read public sitemaps.
2. `build_master.py`, `select_crawl_set.py` (`cap_netmeds.py` for Netmeds): choose pages.
3. `fetch_products.py [site ...]`: fetch product pages into `raw_pages/products_*.jsonl`.
4. `nlem_scan.py` (needs the NLEM 2022 PDF in `raw_pages/evidence_docs/`), `build_evidence.py`, `extract_pharmarack_rows.py`.
5. `prepare_dataset.py`, `build_workbook.py`, `validate_workbook.py`.

Large or third-party files (raw HTML samples, the NLEM PDF, full sitemap URL lists) are not in this repo.
