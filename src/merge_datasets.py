from pathlib import Path
import pandas as pd

DATASETS = [
    ("crime_dataset.csv", "BOROUGH"),
    ("parks_dataset.csv", "borough"),
    ("schools_dataset.csv", "borough"),
    ("housing_dataset.csv", "borough"),
    ("requests.csv", "Borough")
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

    datasets.to_csv(DATA_PATH / "final_dataset.csv", index = False)


if __name__ == "__main__":
    main()