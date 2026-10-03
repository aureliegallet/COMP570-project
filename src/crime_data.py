import urllib.request
import pandas as pd
import json
import argparse
from pathlib import Path
from loader import Loader
from borough_identifier import BoroughIdentifier

def main():
    parser = argparse.ArgumentParser(
        prog='crime_data',
        description='Pulls, cleans, annotates and saves data about crime in each borough.',
    )

    current_dir = Path(__file__).resolve().parent
    default_data_path = current_dir.parent / "data"

    parser.add_argument('-i', '--input-url', default="https://www.donneesquebec.ca/recherche/api/3/action/datastore_search_sql?")
    parser.add_argument('-r', '--input-resource', default="c6f482bf-bf0f-4960-8b2f-9982c211addd")
    parser.add_argument('-o', '--output', type=pathlib.Path, default=default_data_path)

    args = parser.parse_args()

    if args.output.suffix.lower() == ".csv":
        output_path = args.output  
    elif args.output.is_dir():
        output_path = args.output / 'crime_dataset.csv'
    else:
        raise("output should be either a directory in which crime_dataset.csv will be saved, a csv file path.")
    
    loader = Loader()

    # Pull data from donnees quebec
    crime_sql = f"""sql=SELECT "_id", "CATEGORIE", "DATE", "X", "Y", "LONGITUDE", "LATITUDE" from "{args.input_resource}" where "DATE" >= '2021-01-01' AND "DATE" < '2022-01-01'"""
    path = f"""{args.input_url}{crime_sql}"""
    path = path.replace(" ", "%20")
    loader.load_to_csv(path, output_path)
    df = pd.read_csv(output_path, encoding='latin-1')

    # Remove rows with na values
    print(f"Original dataset length: {len(df)}")
    filtered_df = df.dropna(axis=0)
    print(f"Filtered dataset length: {len(filtered_df)}")

    dropped = len(df)-len(filtered_df)
    print(f"Number of rows dropped: {dropped}")
    print(f"Percentage dropped: {(dropped / len(df)) * 100:.2f}%")

    # Replace coordinates with borough using BoroughIdentifier tool
    borough_identifier = BoroughIdentifier()
    filtered_df["BOROUGH"] = filtered_df.apply(
        lambda row: borough_identifier.match_NAD83_to_borough(row["X"], row["Y"]), # Because custom function does not accept full Series
        axis = 1
    ) 
    filtered_df = filtered_df.drop(columns=["X", "Y"])

    # Count number of records of criminal acts for each borough
    counts = filtered_df["BOROUGH"].value_counts().reset_index()
    counts = counts.rename(columns={
        "count" : "criminal_acts"
    })

    # Save crime counts to csv
    counts.to_csv(output_path, index=False)
    print(f"Succesfully saved {len(counts)} lines to {output_path}.")


if __name__ == "__main__":
    main()