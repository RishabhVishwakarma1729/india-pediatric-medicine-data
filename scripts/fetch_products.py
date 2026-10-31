"""Fetch product pages from the crawl set and extract fields. One thread per site, per-site crawl delay, resumable.

Outputs: raw_pages/products_<site>.jsonl  (one JSON per URL, includes retrieval time and verbatim evidence snippets)
Stops a site's thread after 3 consecutive 403/429 responses (we do not push through blocks).
Usage: fetch_products.py [site ...]   (default: all four)
"""
import csv
import html as htmllib
import json
import os
import re
import sys
import threading
import time
from datetime import datetime, timezone

import requests

BASE = r"C:\Users\RISHABH\Desktop\Pediatric_Medicine_India\raw_pages"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept-Language": "en-IN,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml",
}
DELAY = {"1mg": 1.2, "PharmEasy": 1.5, "Apollo": 1.5, "Netmeds": 10.5}


def strip_tags(s):
    return htmllib.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()


def num(s):
    try:
        return float(str(s).replace(",", ""))
    except Exception:
        return None


# ----------------------------------------------------------------------------- parsers
def parse_1mg(h):
    d = {}
    t = re.search(r"<title>(.*?)</title>", h, re.S)
    title = htmllib.unescape(t.group(1)).strip() if t else ""
    d["name"] = re.sub(r"^Buy\s+|\s+Online$", "", re.split(r"\s*[:|]\s*", title)[0]).strip() if title else None
    m = re.search(r'"mrp":\{"displayText":"MRP ?","price":"[^\d]*([\d,\.]+)"', h)
    d["mrp"] = num(m.group(1)) if m else None
    m = re.search(r'"packSizes":"([^"]+)"', h)
    d["pack"] = m.group(1) if m else None
    m = re.search(r'"marketer":\{"id":\d+,"name":"([^"]+)","address":"([^"]*)"', h)
    d["marketer"] = m.group(1) if m else None
    d["marketer_address"] = m.group(2) if m else None
    m = re.search(r'"manufacturerInfo":\{"id":"[^"]*","name":"([^"]*)"', h)
    d["manufacturer"] = m.group(1) if m else None
    m = re.search(r'"salt_composition":\{"header":"Composition","display_text":"(.*?)"\}', h)
    d["composition"] = strip_tags(m.group(1).encode().decode("unicode_escape", errors="ignore")) if m else None
    m = re.search(r'"pack_form":"([^"]*)"', h)
    d["pack_form"] = m.group(1) if m else None
    m = re.search(r'"header":"([^"]+)","subHeader":"bought recently"', h)
    d["demand_text"] = f"{m.group(1)} bought recently" if m else None
    d["demand_n"] = num(re.match(r"([\d,\.]+)", m.group(1)).group(1)) if m and re.match(r"([\d,\.]+)", m.group(1)) else None
    m = re.search(r'"ratingsOverviewData":(\{.{0,400}?\}),"manufacturerInfo"', h, re.S)
    d["rating_raw"] = m.group(1)[:300] if m else None
    r = re.search(r'"(?:ratingCount|totalRatings|total_ratings|ratings_count)":(\d+)', h)
    d["rating_count"] = int(r.group(1)) if r else None
    r = re.search(r'"(?:avgRating|averageRating|average_rating|rating_value)":([\d.]+)', h)
    d["rating_value"] = num(r.group(1)) if r else None
    variants = re.findall(r'\{"id":"(\d+)","title":"([^"]+)","isSelected":(?:true|false),"isAvailable":(?:true|false),"slug":"([^"]+)","price":"[^\d]*([\d,\.]+)"\}', h)
    seen_packs = []
    for v in variants:
        item = f"{v[1]} = Rs {v[3]}"
        if item not in seen_packs:
            seen_packs.append(item)
    d["other_packs"] = "; ".join(seen_packs) or None
    d["available"] = None if '"isAvailable"' not in h else not bool(re.search(r'"isSelected":true,"isAvailable":false', h))
    return d


def parse_pharmeasy(h):
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', h, re.S)
    if not m:
        return {"error": "no __NEXT_DATA__"}
    data = json.loads(m.group(1))
    pd = data.get("props", {}).get("pageProps", {}).get("productDetails") or {}
    comp = pd.get("compositions") or []
    rd = pd.get("ratingDetails") or {}
    return {
        "name": pd.get("name"),
        "brand": pd.get("consumerBrandName"),
        "mrp": num(pd.get("costPrice")),
        "sale_price": num(pd.get("salePrice")),
        "pack": pd.get("measurementUnit"),
        "pack_form": pd.get("packform"),
        "manufacturer": pd.get("manufacturer"),
        "molecule": pd.get("molecule"),
        "composition": "; ".join(c.get("name", "") for c in comp) or None,
        "strength": f"{pd.get('drugStrengthValue')} {pd.get('drugStrengthUnit')}" if pd.get("drugStrengthValue") else None,
        "dosage_form": pd.get("dosageForm"),
        "price_per_unit": pd.get("pricePerUnit"),
        "rating_value": rd.get("value"),
        "rating_count": rd.get("count"),
        "therapy": pd.get("therapy"),
        "rx_required": pd.get("isRxRequired"),
        "available": pd.get("isAvailable"),
        "page_updated": pd.get("lastUpdatedAtISO"),
        "demand_text": (f"{rd.get('count')} ratings (avg {rd.get('value')})" if rd.get("count") else None),
        "demand_n": rd.get("count") if rd.get("count") else None,
    }


def parse_apollo(h):
    d = {}
    blocks = re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', h, re.S)
    drug = None
    for b in blocks:
        try:
            j = json.loads(b)
        except Exception:
            continue
        if isinstance(j, dict) and isinstance(j.get("mainEntity"), dict) and j["mainEntity"].get("@type") == "Drug":
            drug = j["mainEntity"]
            break
    if not drug:
        return {"error": "no Drug JSON-LD"}
    d["name"] = drug.get("name") or drug.get("proprietaryName")
    d["manufacturer"] = (drug.get("manufacturer") or {}).get("legalName")
    d["dosage_form"] = drug.get("dosageForm")
    d["composition"] = drug.get("nonProprietaryName") or None
    offers = drug.get("offers") or {}
    d["sale_price"] = num(offers.get("price"))
    d["available"] = "InStock" in str(offers.get("availability", ""))
    m = re.search(r'\\"mrp\\":([\d.]+)', h)
    d["mrp"] = num(m.group(1)) if m else None
    pm = re.search(r"(\d+(?:\.\d+)?\s*(?:ml|gm|g|mg|sachets?|x\s*\d+\s*(?:gm|g|ml)))", d["name"] or "", re.I)
    d["pack"] = pm.group(1) if pm else None
    return d


def parse_netmeds(h):
    d = {}
    blocks = re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', h, re.S)
    drug = None
    for b in blocks:
        try:
            j = json.loads(b)
        except Exception:
            continue
        cand = j[0] if isinstance(j, list) and j else j
        if isinstance(cand, dict) and cand.get("@type") in ("Drug", "Product"):
            drug = cand
            break
    if not drug:
        return {"error": "no Drug/Product JSON-LD"}
    d["name"] = drug.get("name")
    mf = drug.get("manufacturer") if isinstance(drug.get("manufacturer"), dict) else {}
    mm = re.search(r'"manufacturername":"([^"]*)"', h)
    d["manufacturer"] = htmllib.unescape(mf.get("name") or (mm.group(1) if mm else "")) or None
    d["manufacturer_address"] = mf.get("address")
    offers = drug.get("offers") if isinstance(drug.get("offers"), dict) else {}
    d["price_valid_until"] = offers.get("priceValidUntil")
    d["dosage_form"] = drug.get("dosageForm")
    gm = re.search(r'"genericnamewithdosage":"([^"]*)"', h)
    comp = drug.get("activeIngredient") or (gm.group(1) if gm else None)
    d["composition"] = None if (comp or "").strip().upper() in ("OTC", "") else comp
    d["category"] = drug.get("category")
    d["sale_price"] = num(offers.get("price"))
    m = re.search(r'"mrp":([\d.]+)', h)
    d["mrp"] = num(m.group(1)) if m else None
    ps = re.search(r'"packsize":"?([\d.]+)"?', h)
    pu = re.search(r'"packsizeunit":"([^"]*)"', h)
    d["pack"] = f"{ps.group(1)} {pu.group(1)}".strip() if ps else None
    r = re.search(r'"rating":([\d.]+),"rating_count":(\d+)', h)
    d["rating_value"] = num(r.group(1)) if r else None
    d["rating_count"] = int(r.group(2)) if r else None
    d["demand_text"] = f"{d['rating_count']} ratings (avg {d['rating_value']})" if d["rating_count"] else None
    d["demand_n"] = d["rating_count"] if d["rating_count"] else None
    d["available"] = ("InStock" in str(offers.get("availability", ""))) if offers else None
    return d


PARSERS = {"1mg": parse_1mg, "PharmEasy": parse_pharmeasy, "Apollo": parse_apollo, "Netmeds": parse_netmeds}


# ----------------------------------------------------------------------------- crawler
def run_site(site, rows):
    path = os.path.join(BASE, f"products_{site}.jsonl")
    done = set()
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                try:
                    done.add(json.loads(line)["url"])
                except Exception:
                    pass
    todo = [r for r in rows if r["url"] not in done]
    print(f"[{site}] {len(todo)} to fetch ({len(done)} already done)", flush=True)
    blocks = 0
    session = requests.Session()
    with open(path, "a", encoding="utf-8") as out:
        for n, rec in enumerate(todo, start=1):
            url = rec["url"]
            status, parsed, err = None, {}, None
            for attempt in (1, 2):
                try:
                    r = session.get(url, headers=HEADERS, timeout=60)
                    status = r.status_code
                except Exception as exc:
                    err = type(exc).__name__
                    time.sleep(5)
                    continue
                if status in (429, 500, 502, 503) and attempt == 1:
                    time.sleep(15)
                    continue
                break
            if status in (403, 429):
                blocks += 1
            elif status == 200:
                blocks = 0
            if status == 200:
                try:
                    parsed = PARSERS[site](r.content.decode("utf-8", errors="replace"))
                except Exception as exc:
                    parsed = {"error": f"parse {type(exc).__name__}: {exc}"}
            row = {"site": site, "url": url, "group": rec["group"], "brand_family": rec["brand_family"], "status": status, "fetch_error": err,
                   "retrieved_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), **parsed}
            out.write(json.dumps(row, ensure_ascii=False) + "\n")
            out.flush()
            if n % 25 == 0:
                print(f"[{site}] {n}/{len(todo)} last status {status}", flush=True)
            if blocks >= 3:
                print(f"[{site}] STOPPING: 3 consecutive 403/429 responses (site is blocking automated access)", flush=True)
                return
            time.sleep(DELAY[site])
    print(f"[{site}] finished {len(todo)}", flush=True)


if __name__ == "__main__":
    wanted = sys.argv[1:] or list(DELAY)
    by_site = {s: [] for s in DELAY}
    with open(os.path.join(BASE, "crawl_set.csv"), encoding="utf-8") as fh:
        for rec in csv.DictReader(fh):
            if rec["site"] in by_site:
                by_site[rec["site"]].append(rec)
    threads = [threading.Thread(target=run_site, args=(s, by_site[s]), daemon=False) for s in wanted if by_site[s]]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print("ALL DONE", flush=True)
