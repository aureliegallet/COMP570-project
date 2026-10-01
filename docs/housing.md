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
- `median_annual_renter_household_income_before_tax_cad`: median yearly renter household income before tax (whole CAD).
- `income_reference_year`: 2020 (integer).

The income and percentage columns cover all bedroom sizes. The percentage excludes households with zero or negative income, following the source’s definition.

## Processing

The script selects renters (`Locataires`), removes the city-total row, fixes four borough names to match the project, and combines the columns by borough. The figures come directly from the source; no new estimates are calculated.

All 76 indicator values were checked against the originals. There are no missing values, and all 19 borough names match the parks, schools and crime files.

Run `python3 src/housing.py` from the repository root to rebuild the CSV. Original files are in `data/housing/raw/`; check results are in `data/housing/validation.json`.

These are historical housing costs, including applicable utilities, not current advertised rents. The source does not tell us how many homes fall within a specific rent range.

AI assistance: Used only for documentation.
