"""Extract the archived Montreal profile and build borough housing indicators.

Run from any directory: python3 src/housing.py
Python standard library only. No JavaScript from the source is executed.
"""

import csv
import hashlib
import io
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/housing/raw"
TABLES = {
    "01_renter_monthly_housing_costs.csv": ("csvLoyerData", "loca_total"),
    "02_renter_housing_cost_burden.csv": ("csvEffortData", "loca_total"),
    "03_renter_household_income.csv": ("csvRevenuData", "loca_total"),
    "04_renter_costs_by_bedrooms.csv": ("csvLoyerChambresData", "loc"),
    "05_renter_household_counts.csv": ("csvData", "loca_total"),
}
ALIASES = {
    "Plateau-Mont-Royal": "Le Plateau-Mont-Royal",
    "Sud-Ouest": "Le Sud-Ouest",
    "Île-Bizard-Sainte-Geneviève": "L'Île-Bizard-Sainte-Geneviève",
    "Villeray-Saint-Michel-Parc Extension": "Villeray-Saint-Michel-Parc-Extension",
}
BUDGETS_CAD = (2000, 3000)


def household_growth_pct(previous, current):
    """Five-year percentage change; undefined when the baseline is zero."""
    if previous < 0 or current < 0:
        raise ValueError("Household counts cannot be negative")
    return round(100 * (current - previous) / previous, 2) if previous else None


def extract_table(html, variable, key):
    obj = re.search(r"const " + variable + r"\s*=\s*\{(.*?)\n\s*\};", html, re.S)
    if obj is None:
        raise ValueError(f"Missing source variable: {variable}")
    match = re.search(r"\b" + key + r"\s*:\s*`([^`]*)`", obj[1])
    if match is None or "${" in match[1]:
        raise ValueError(f"Missing or unsupported template: {variable}.{key}")
    escapes = {"n": "\n", "r": "\r", "t": "\t", "\\": "\\", '"': '"', "'": "'"}
    def decode(match):
        if match[1] not in escapes:
            raise ValueError(f"Unsupported escape: {match[0]}")
        return escapes[match[1]]
    return re.sub(r"\\(.)", decode, match[1])


def indexed(text):
    rows = list(csv.DictReader(io.StringIO(text)))
    result = {}
    for row in rows:
        geo = row["Géographie"]
        key = ALIASES.get(geo, geo)
        if key in result:
            raise ValueError(f"Duplicate geography: {key}")
        result[key] = row
    if len(result) != 20 or "Ville de Montréal" not in result:
        raise ValueError("Expected 19 boroughs plus one city total")
    del result["Ville de Montréal"]
    return result


def main():
    snapshot = RAW / "official_city_housing_profile.html"
    html = snapshot.read_text(encoding="utf-8")
    tables = {}
    for filename, (variable, key) in TABLES.items():
        text = extract_table(html, variable, key)
        # Preserve the original downloaded CSVs and verify extraction agrees.
        path = RAW / filename
        if path.exists() and path.read_text(encoding="utf-8") != text:
            raise ValueError(f"Archived CSV differs from source HTML: {filename}")
        path.write_text(text, encoding="utf-8")
        tables[filename] = indexed(text)

    costs = tables["04_renter_costs_by_bedrooms.csv"]
    for filename, rows in tables.items():
        if rows.keys() != costs.keys():
            raise ValueError(f"Geography mismatch: {filename}")
    boundaries = json.loads((ROOT / "data/borough_limits.geojson").read_text())
    expected = {f["properties"]["NOM"] for f in boundaries["features"]
                if f["properties"]["TYPE"] == "Arrondissement"}
    if set(costs) != expected:
        raise ValueError(f"Borough mismatch: {set(costs) ^ expected}")

    output = []
    for borough, row in sorted(costs.items()):
        two, three = int(row["2 chambres"]), int(row["3 chambres"])
        burden = float(tables["02_renter_housing_cost_burden.csv"][borough]["Tous_les_menages_30pct"])
        households = tables["05_renter_household_counts.csv"][borough]
        previous, current = int(households["N_2016"]), int(households["N_2021"])
        if min(two, three) <= 0:
            raise ValueError(f"Invalid housing costs for {borough}")
        if not math.isfinite(burden) or not 0 <= burden <= 100:
            raise ValueError(f"Invalid burden percentage for {borough}")
        output.append({"borough": borough, "census_year": 2021,
                       "median_monthly_shelter_cost_2br_cad": two,
                       "median_monthly_shelter_cost_3br_cad": three,
                       "renter_households_spending_30pct_or_more_pct": burden})
        for bedrooms, median in [(2, two), (3, three)]:
            for budget in BUDGETS_CAD:
                output[-1][f"budget_{budget}_minus_median_{bedrooms}br_cad"] = budget - median
        output[-1].update({
            "renter_households_2016": previous,
            "renter_households_2021": current,
            "renter_household_growth_2016_2021_pct": household_growth_pct(previous, current),
        })
    target = ROOT / "data/housing_dataset.csv"
    with target.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)
    audit = {
        "source_html_sha256": hashlib.sha256(snapshot.read_bytes()).hexdigest(),
        "source_rows_per_table": 20, "city_total_rows_removed_per_table": 1,
        "borough_rows": len(output), "duplicate_boroughs": 0,
        "unmatched_boundary_boroughs": [], "missing_2br_costs": 0,
        "missing_3br_costs": 0,
        "missing_burden_percentages": 0,
        "budget_endpoints_cad_per_month": list(BUDGETS_CAD),
        "undefined_household_growth_rows": sum(r["renter_household_growth_2016_2021_pct"] is None for r in output),
        "source_limitations": ["mean rent", "2–3-bedroom rental count in price range",
                                             "2–3-bedroom rental percentage in price range"],
    }
    (ROOT / "data/housing/validation.json").write_text(
        json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Created {target.name}: {len(output)} boroughs, {len(output[0])} columns.")


if __name__ == "__main__":
    main()
