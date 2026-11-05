from pathlib import Path

import pandas as pd

WEIGHTINGS_PJCT1 = {
    "theft_acts_per_capita": 5,
    "break_in_acts_per_capita": 5,
    "misdemeanor_acts_per_capita": 5,    
    "death_acts_per_capita": 15,
    "green_area (%)": 10,
    "children_per_school": 25,
    "median_monthly_shelter_cost_2br_cad": 2.5,
    "median_monthly_shelter_cost_3br_cad": 2.5,
    "budget_2000_minus_median_2br_cad": 2.5,
    "budget_3000_minus_median_2br_cad": 2.5,
    "budget_2000_minus_median_3br_cad": 2.5,
    "budget_3000_minus_median_3br_cad": 2.5,
    "Complaints per Capita": 10,
    "Requests per Capita": 10
}

WEIGHTINGS_PJCT2 = {
    "theft_acts_per_capita": 5,
    "break_in_acts_per_capita": 5,
    "misdemeanor_acts_per_capita": 5,    
    "death_acts_per_capita": 15,
    "green_area (%)": 10,
    "children_per_school": 25,
    "median_monthly_shelter_cost_2br_cad": 2.5,
    "median_monthly_shelter_cost_3br_cad": 2.5,
    "budget_2000_minus_median_2br_cad": 2.5,
    "budget_3000_minus_median_2br_cad": 2.5,
    "budget_2000_minus_median_3br_cad": 2.5,
    "budget_3000_minus_median_3br_cad": 2.5,
    "maintenance / city works": 5,
    "other": 2.5,
    "quieteness / living comfort": 5,
    "sanitation / cleanliness": 5,
    "traffic engineering / parking": 2.5
}

DATA_PATH = Path(__file__).resolve().parent.parent / "data"
FILE_NAME_PJCT1 = "project1_normalized_dataset.csv"
FILE_NAME_PJCT2 = "project2_normalized_dataset.csv"

def main():
    print("PROJECT 1:")
    df = pd.read_csv(DATA_PATH / FILE_NAME_PJCT1)
    scores = (df.set_index('borough')[list(WEIGHTINGS_PJCT1.keys())] * WEIGHTINGS_PJCT1).sum(axis=1).sort_values(ascending=False)
    print(scores/100)

    print("\n----------\n")
    print("PROJECT 2:")
    df = pd.read_csv(DATA_PATH / FILE_NAME_PJCT2)
    scores = (df.set_index('borough')[list(WEIGHTINGS_PJCT2.keys())] * WEIGHTINGS_PJCT2).sum(axis=1).sort_values(ascending=False)
    print(scores/100)

if __name__ == "__main__":
    main()