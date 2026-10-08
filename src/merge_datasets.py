from pathlib import Path
import pandas as pd

DATASETS = [
    ("crime_dataset.csv", "BOROUGH"),
    ("parks_dataset.csv", "borough"),
    ("schools_dataset.csv", "borough"),
    ("housing_dataset.csv", "borough"),
    ("requests_dataset.csv", "Borough")
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

    datasets = datasets.drop(datasets[datasets["borough"] == "Not-Borough"].index)
    datasets = datasets.drop(columns="census_year")

    # Process 311 per capita
    total_complaints = datasets["Complaints"] + datasets["Adjusted Complaints"]
    total_requests = datasets["Requests"] + datasets["Adjusted Requests"]
    datasets.insert(datasets.columns.get_loc("Adjusted Complaints") + 1, "Total Complaints", total_complaints)
    datasets.insert(datasets.columns.get_loc("Adjusted Requests") + 1, "Total Requests", total_requests)
    total_complaints_per_capita = datasets["Adjusted Complaints"] / datasets["POPULATION"]
    total_requests_per_capita = datasets["Adjusted Requests"] / datasets["POPULATION"]
    datasets.insert(datasets.columns.get_loc("Total Complaints") + 1, "Complaints per Capita", total_complaints_per_capita)
    datasets.insert(datasets.columns.get_loc("Total Requests") + 1, "Requests per Capita", total_requests_per_capita)

    datasets.to_csv(DATA_PATH / "final_dataset.csv", index = False)


if __name__ == "__main__":
    main()
