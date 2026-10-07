# Housing data

`data/housing_dataset.csv` has one row for each of Montréal’s 19 boroughs. It can be joined to the other datasets using `borough` (called `BOROUGH` in the crime file).

## Source

[Montréal housing profiles](https://donnees.montreal.ca/dataset/profils-menages-logements/resource/3cd96534-40c5-4f6b-a0b2-9b70ac155e4d), published by Ville de Montréal using the 2021 Census from Statistics Canada. Downloaded September 28, 2026. Licence: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

## Columns

- `borough`: borough name (text).
- `census_year`: 2021 (integer).
- `median_monthly_shelter_cost_2br_cad`: median monthly housing cost for renters in 2-bedroom homes (whole CAD).
- `median_monthly_shelter_cost_3br_cad`: the same measure for 3-bedroom homes (whole CAD).
- `renter_households_spending_30pct_or_more_pct`: percentage of renters spending at least 30% of income on housing (decimal, 0–100).

The housing-cost burden percentage covers all bedroom sizes. It describes existing renter households, not the fixed-income target family. Median household income and its reference year are excluded because the project assumes a fixed target income. The original income table is retained only as an archived source. The percentage excludes households with zero or negative income, following the source’s definition.

## Added calculations

- `budget_2000_minus_median_2br_cad` and `budget_3000_minus_median_2br_cad`: monthly budget minus the 2021 two-bedroom median cost (integer CAD/month).
- `budget_2000_minus_median_3br_cad` and `budget_3000_minus_median_3br_cad`: the same calculation for three bedrooms (integer CAD/month).
- `renter_households_2016` and `renter_households_2021`: source counts from `N_2016` and `N_2021` in `05_renter_household_counts.csv` (integer households, all bedroom sizes). These are supporting inputs, not per-capita comparison indicators.
- `renter_household_growth_2016_2021_pct`: `100 * (N_2021 - N_2016) / N_2016`, rounded to two decimals. This is total five-year growth, not annual growth. The denominator is the borough's 2016 renter household count. A zero baseline produces a blank, not zero growth.

Positive budget differences mean the budget exceeds the historical median; negative differences mean it is below. They are not estimates of available listings, actual savings, or the percentage of homes within budget. The $2,000 and $3,000 endpoints are project assumptions and are not inflation-adjusted. Growth is calculated from the published counts, which are rounded, so it may differ slightly from the source's published `Variation_pct`.

The CSV now has 19 rows and 12 columns. The four budget differences were checked against the bedroom-cost table, and all 19 growth calculations were checked against the household counts.

## Processing

The script selects renters (`Locataires`), removes the city-total row, fixes four borough names to match the project, and combines the columns by borough. The three selected indicators come directly from the source. The added budget differences and household growth are calculated as described above.

All 57 selected indicator values were checked against the originals. There are no missing values, and all 19 borough names match the parks, schools and crime files.

Run `python3 src/housing.py` from the repository root to rebuild the CSV. Original files are in `data/housing/raw/`; check results are in `data/housing/validation.json`.

These are historical housing costs, including applicable utilities, not current advertised rents. The source does not tell us how many homes fall within a specific rent range.

AI assistance: Used only for documentation.
