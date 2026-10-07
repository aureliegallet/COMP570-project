# Housing data

`data/housing_dataset.csv` has one row for each of Montréal’s 19 boroughs. It can be joined to the other datasets using `borough` (called `BOROUGH` in the crime file).

## Source

[Montréal housing profiles](https://donnees.montreal.ca/dataset/profils-menages-logements/resource/3cd96534-40c5-4f6b-a0b2-9b70ac155e4d), published by Ville de Montréal using the 2021 Census from Statistics Canada. Downloaded September 28, 2026. Licence: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

## Columns

- `borough`: borough name (text).
- `census_year`: 2021 (integer).
- `median_monthly_shelter_cost_2br_cad`: median monthly housing cost for renters in 2-bedroom homes (whole CAD).
- `median_monthly_shelter_cost_3br_cad`: the same measure for 3-bedroom homes (whole CAD).
- `assumed_monthly_household_income_cad`: fixed project assumption of 3000 CAD/month (integer), not observed income.
- `median_2br_cost_share_of_assumed_income_pct`: two-bedroom median monthly cost / 3000 × 100, rounded to two decimals (percent of assumed income).
- `median_3br_cost_share_of_assumed_income_pct`: the same calculation for three bedrooms.

The new percentages describe how much of a hypothetical household's income would go toward the borough median cost. They are not percentages of households. At this income, 30% is $900/month. Shares may exceed 100% and are not capped. Before-tax versus after-tax income has not been specified, so these are scenario comparisons, not official affordability statistics. The original income and burden tables remain archived but are not used as final indicators.

## Added calculations

- `budget_2000_minus_median_2br_cad` and `budget_3000_minus_median_2br_cad`: monthly budget minus the 2021 two-bedroom median cost (integer CAD/month).
- `budget_2000_minus_median_3br_cad` and `budget_3000_minus_median_3br_cad`: the same calculation for three bedrooms (integer CAD/month).
- `renter_households_2016` and `renter_households_2021`: source counts from `N_2016` and `N_2021` in `05_renter_household_counts.csv` (integer households, all bedroom sizes). These are supporting inputs, not per-capita comparison indicators.
- `renter_household_growth_2016_2021_pct`: `100 * (N_2021 - N_2016) / N_2016`, rounded to two decimals. This is total five-year growth, not annual growth. The denominator is the borough's 2016 renter household count. A zero baseline produces a blank, not zero growth.

Positive budget differences mean the budget exceeds the historical median; negative differences mean it is below. They are not estimates of available listings, actual savings, or the percentage of homes within budget. The $2,000 and $3,000 budget endpoints are retained separately from the new $3,000 income assumption. Spending those amounts would use 66.67%–100% of that income. All comparisons use historical costs without inflation adjustment. Growth is calculated from the published counts, which are rounded, so it may differ slightly from the source's published `Variation_pct`.

The CSV now has 19 rows and 14 columns. The four budget differences were checked against the bedroom-cost table, and all 19 growth calculations were checked against the household counts.

## Processing

The script selects renters (`Locataires`), removes the city-total row, fixes four borough names to match the project, and combines the columns by borough. The two median cost indicators come directly from the source. The added budget differences and household growth are calculated as described above.

All 38 selected median cost values were checked against the originals. There are no missing values, and all 19 borough names match the parks, schools and crime files.

Run `python3 src/housing.py` from the repository root to rebuild the CSV. Original files are in `data/housing/raw/`; check results are in `data/housing/validation.json`.

These are historical housing costs, including applicable utilities, not current advertised rents. The source does not tell us how many homes fall within a specific rent range.

AI assistance: Used only for documentation.
