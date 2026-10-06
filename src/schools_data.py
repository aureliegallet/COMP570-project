import urllib.request
import pandas as pd
import json
import argparse
from pathlib import Path
from borough_identifier import BoroughIdentifier

def main():
    parser = argparse.ArgumentParser(
        prog='schools_data',
        description='Pulls, cleans, annotates and saves data about schools in each borough.',
    )

    current_dir = Path(__file__).resolve().parent
    default_data_path = current_dir.parent / "data"

    parser.add_argument('-i', '--input-url', default="https://www.donneesquebec.ca/recherche/api/3/action/datastore_search")
    parser.add_argument('-r', '--input-resource', default="c6640a54-bc4b-43ec-864e-6c325dce61bc")
    parser.add_argument('-m', '--input-municipality', default="Montréal")
    parser.add_argument('-o', '--output', type=Path, default=default_data_path)

    args = parser.parse_args()

    if args.output.suffix.lower() == ".csv":
        output_path = args.output  
    elif args.output.is_dir():
        output_path = args.output / 'schools_dataset.csv'
    else:
        raise("output should be either a directory in which schools_dataset.csv will be saved, a csv file path.")

    # Pull data from donnees quebec
    base_url = args.input_url
    resource_id = args.input_resource
    filters = json.dumps({"NOM_MUNCP_GDUNO_ORGNS": args.input_municipality})

    query_params = urllib.parse.urlencode(
        {"resource_id": resource_id, "filters": filters, "limit": 5000}
    )
    url = f"{base_url}?{query_params}"
    with urllib.request.urlopen(url) as response:
        data_dict = json.loads(response.read().decode('utf-8'))
    df = pd.DataFrame(data_dict["result"]["records"])

    lengths = [len(df)]
    print("Total number of rows upon loading:", lengths[-1])

    # Convert coordinates to borough and save it in new column
    bi = BoroughIdentifier()
    df['borough'] = df.apply(lambda row: bi.match_WSG84_to_borough(longitude_x=row['COORD_X_LL84_IMM'], latitude_y=row['COORD_Y_LL84_IMM']), axis=1)

    # Remove schools intended for adult learning
    df = df[~df['ORDRE_ENS'].str.contains('adultes')]
    df = df[~df['ORDRE_ENS'].str.contains('professionnelle')]
    lengths.append(len(df))
    print("Number of adult learning schools removed:", lengths[-2] - lengths[-1])

    # Check levels remaining in dataset. Should have Préscolaire, Primaire & Secondaire.
    print("Education levels:", df['ORDRE_ENS'].unique())

    # Group lines with same school name in the same borough to avoid duplicate records for the same establishment
    df = df.groupby(['NOM_OFFCL_ORGNS', 'borough'], as_index=False).agg(lambda x: ', '.join(x.dropna().astype(str).unique()))
    lengths.append(len(df))
    print("Number of rows lost to merging schools with the same name in the same borough:", lengths[-2] - lengths[-1])

    print(f"Total number of rows removed: {lengths[0] - lengths[-1]} which is roughly equal to {((lengths[0] - lengths[-1]) / lengths[0]) * 100 :.2f}%.")

    census_df = pd.read_excel(default_data_path / "DONNÉES DU RECENSEMENT DE 2021_AGGLOMÉRATION DE MONTRÉAL_TOTAUX ET POURCENTAGES_0.XLSX", skiprows=(0,1,2), index_col=0)
    census_df.columns = census_df.columns.str.replace("Arrondissement de ", "")
    census_df.columns = census_df.columns.str.replace("Arrondissement d'", "")
    census_df.columns = census_df.columns.str.replace("Arrondissement du", "Le")
    census_df.columns = census_df.columns.str.replace("–", "-")

    # Compute output with borough, total population in that borough, number of schools in that borough, and number of residents per school
    output = {
        'borough': df['borough'].unique(),
    }
    output_df = pd.DataFrame(output)
    output_df['num_children'] = output_df['borough'].map(lambda brgh: census_df[brgh]['0 à 14 ans']["0 à 14 ans"].iloc[0])
    output_df['num_schools'] = output_df['borough'].map(lambda brgh: len(df[df['borough']==brgh]))
    output_df['children_per_school'] = output_df['num_children'] / output_df['num_schools']

    print("Children population count integrity check:")
    print("sum of borough children populations:", output_df['num_children'].sum())
    print("declared city children population:", census_df['Ville de Montréal']['0 à 14 ans']["0 à 14 ans"].iloc[0])

    # Save output to csv
    output_df.to_csv(output_path, index=False)
    print(f"Succesfully saved {len(output_df)} lines to {output_path}.")


if __name__ == "__main__":
    main()