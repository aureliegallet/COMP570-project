import utils
import pandas as pd
import json
import argparse
from pathlib import Path
from loader import Loader
from borough_identifier import BoroughIdentifier

CRIMES = {
    "Vol dans / sur véhicule à moteur" : "theft",
    "Introduction" : "break_in",
    "Méfait" : "misdemeanor",
    "Vol de véhicule à moteur" : "theft",
    "Vols qualifiés" : "theft",
    "Infractions entrainant la mort" : "death"
}

ACTS = ["theft", "break_in", "misdemeanor", "death"]

def check_location(df, original_nan, longitude, latitude):
    "Check for missing location"

    print("\n ------------------ \n")
    print(f"Number of missing values in the {longitude} column: {original_nan[longitude].sum()}")
    print(f"Number of missing values in the {latitude} column: {original_nan[latitude].sum()}")
    all_na_filter = (original_nan[longitude] & original_nan[latitude])
    print(f"Number of rows where both {longitude} and {latitude} are missing: {len(df[all_na_filter])}")

    if original_nan[longitude].sum() == len(df[all_na_filter]):
        print(f"When {longitude} is missing, {latitude} is also missing. There is no case of there being an {longitude} value without a {latitude}.")
    else:
        print(f"{longitude} and {latitude} values are not missing in the same rows. There is a mismatch in coordinates.")

def main():
    parser = argparse.ArgumentParser(
        prog='crime_data',
        description='Pulls, cleans, annotates and saves data about crime in each borough.',
    )

    current_dir = Path(__file__).resolve().parent
    default_data_path = current_dir.parent / "data"

    parser.add_argument('-i', '--input-url', default="https://www.donneesquebec.ca/recherche/api/3/action/datastore_search_sql?")
    parser.add_argument('-r', '--input-resource', default="c6f482bf-bf0f-4960-8b2f-9982c211addd")
    parser.add_argument('-o', '--output', type=Path, default=default_data_path)
    args = parser.parse_args()

    if args.output.suffix.lower() == ".csv":
        output_path = args.output  
    elif args.output.is_dir():
        output_path = args.output / 'crime_dataset.csv'
    else:
        raise("output should be either a directory in which crime_dataset.csv will be saved or a csv file path.")
    
    loader = Loader()

    # Pull data from donnees quebec
    crime_sql = f"""sql=SELECT * from "{args.input_resource}" where "DATE" >= '2021-01-01' AND "DATE" < '2022-01-01'"""
    path = f"""{args.input_url}{crime_sql}"""
    data = loader.load(path)

    # Make dataset
    df = pd.DataFrame(data)
    df = df.drop(columns = ["_full_text"])
    df = utils.str_to_num(df)
    df["CATEGORIE"] = df["CATEGORIE"].replace(CRIMES)
    original_nan = df.isna()
    initial_length = len(df)
    print(f"Dataframe length: {initial_length}")


    # Check for missing coordinates and converting them to boroughs
    check_location(df, original_nan, "X", "Y")
    check_location(df, original_nan, "LONGITUDE", "LATITUDE")
    all_na_filter = (original_nan["X"] & original_nan["Y"] & original_nan["LONGITUDE"] & original_nan["LATITUDE"])
    no_location = len(df[all_na_filter])
    df = df.dropna(subset = ["X", "Y", "LONGITUDE", "LATITUDE"])
    print("\n ------------------ \n")
    print(f"Number of rows where all coordinates are missing: {no_location}.")
    print(f"Percentage of dropped no coordinate rows: {(no_location / initial_length) * 100 :.2f}%.")

    
    # Replace coordinates with borough using BoroughIdentifier tool
    borough_identifier = BoroughIdentifier()
    df["BOROUGH_NAD83"] = df.apply(
        lambda row: borough_identifier.match_NAD83_to_borough(row["X"], row["Y"]), # Because custom function does not accept full Series
        axis = 1
    ) 
    df["BOROUGH_WSG84"] = df.apply(
        lambda row: borough_identifier.match_WSG84_to_borough(row["LONGITUDE"], row["LATITUDE"]), # Because custom function does not accept full Series
        axis = 1
    ) 
    df = df.drop(columns=["X", "Y", "LONGITUDE", "LATITUDE"])


    # Check for missing identified boroughs
    after_borough_na = df.isna()
    after_borough_length = len(df)
    all_na_filter = (after_borough_na["BOROUGH_NAD83"] & after_borough_na["BOROUGH_WSG84"])
    print("\n ------------------ \n")
    print(f"Number of missing values in the 'BOROUGH_NAD83' column: {after_borough_na["BOROUGH_NAD83"].sum()}")
    print(f"Number of missing values in the 'BOROUGH_WSG84' column: {after_borough_na["BOROUGH_WSG84"].sum()}")
    print(f"Number of rows where both 'BOROUGH_WSG84' and 'BOROUGH_WSG84' are missing: {len(df[all_na_filter])}")
    
    df["BOROUGH_WSG84"] = df["BOROUGH_WSG84"].fillna(df["BOROUGH_NAD83"]) # Replace the one missing value in BOROUGH_WSG84 with the BOROUGH_NAD83 value
    print(f"Number of missing values in the 'BOROUGH_WSG84' column: {df["BOROUGH_WSG84"].isna().sum()}")
    df = df.dropna(subset = ["BOROUGH_NAD83", "BOROUGH_WSG84"])
    removed_unidentified = len(df)
    print(f"Percentage of dropped no coordinate rows: {((after_borough_length - removed_unidentified) / after_borough_length) * 100 :.2f}%.")


    # Check if the boroughs are mismatched
    print("\n ------------------ \n")
    mismatching_borough = (df["BOROUGH_NAD83"] != df["BOROUGH_WSG84"])
    print(f"Number of rows where 'BOROUGH_NAD83' and 'BOROUGH_WSG84' are not the same: {len(df[mismatching_borough])}")
    df = df.drop(columns = ["BOROUGH_WSG84"]) # We prioritise BOROUGH_NAD83 as recommended by donnees Montreal
    df = df.rename(columns = {"BOROUGH_NAD83": "BOROUGH"})


    # Check if any remaining missing values
    print("\n ------------------ \n")
    print("Remaining missing values")
    print(df.isna().sum())
    print(f"Percentage of total dropped rows: {((initial_length - removed_unidentified) / initial_length) * 100 :.2f}%.")
    


    # Count number of records of criminal acts for each borough
    final = pd.DataFrame({"BOROUGH": []})
    for act in ACTS:
        counts = df[df["CATEGORIE"] == act]["BOROUGH"].value_counts().reset_index()
        counts = counts.rename(columns={
            "count" : f"{act}_acts"
        })
        counts_df = pd.DataFrame(counts)
        final = pd.merge(final, counts_df, how = "outer", on = "BOROUGH")
    final = final.fillna(int(0))
    print("\n ------------------ \n")
    print(final)

    # Save crime counts to csv
    final.to_csv(output_path, index = False)
    print("\n ------------------ \n")
    print(f"Succesfully saved {len(final)} lines to {output_path}.")


if __name__ == "__main__":
    main()