from pathlib import Path
import pandas as pd

DATASETS = [
    ("crime_dataset.csv", "BOROUGH"),
    ("parks_dataset.csv", "borough"),
    ("schools_dataset.csv", "borough"),
    ("housing_dataset.csv", "borough"),
    ("topics_dataset.csv", "Borough")
]

DATA_PATH = Path(__file__).resolve().parent.parent / "data"

def main():
    datasets = pd.DataFrame({"borough": []})
    for (dataset, borough_col) in DATASETS:
        path = DATA_PATH / dataset
        if path.exists():
            df = pd.read_csv(path)

            # Consistency accross datasets
            df = df.rename(columns={
                borough_col : "borough"
            })
            df["borough"] = df["borough"].str.replace(" ", "") 

            datasets = pd.merge(datasets, df, how = "outer", on = "borough")

    datasets = datasets.drop(columns="census_year")
    datasets.to_csv(DATA_PATH / "project2_dataset.csv", index = False)

    cols_to_normalize = list(datasets.columns)
    cols_to_normalize.remove('borough')
    cols_not_to_minimize = [
        "borough",
        "green_area (%)",
        "budget_2000_minus_median_2br_cad",
        "budget_3000_minus_median_2br_cad",
        "budget_2000_minus_median_3br_cad",
        "budget_3000_minus_median_3br_cad",
    ]
    cols_to_minimize = [x for x in list(datasets.columns) if x not in cols_not_to_minimize]
    normalized = datasets.copy()
    normalized[cols_to_normalize] = (datasets[cols_to_normalize] - datasets[cols_to_normalize].min()) / (datasets[cols_to_normalize].max() - datasets[cols_to_normalize].min())
    normalized[cols_to_minimize] = 1 - normalized[cols_to_minimize]
    normalized.to_csv(DATA_PATH / "project2_normalized_dataset.csv", index = False)
    

if __name__ == "__main__":
    main()
