import urllib.request
import pandas as pd
import json
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        prog='parks_data',
        description='Pulls, cleans, annotates and saves data about parks in each borough.',
    )

    current_dir = Path(__file__).resolve().parent
    default_data_path = current_dir.parent / "data"

    parser.add_argument('-i', '--input-url', default="https://donnees.montreal.ca/api/3/action/datastore_search")
    parser.add_argument('-r', '--input-resource', default="f34c3555-c285-4ef3-a55c-f0f5c440ad2d")
    parser.add_argument('-o', '--output', type=Path, default=default_data_path)

    args = parser.parse_args()

    if args.output.suffix.lower() == ".csv":
        output_path = args.output  
    elif args.output.is_dir():
        output_path = args.output / 'parks_dataset.csv'
    else:
        raise("output should be either a directory in which parks_dataset.csv will be saved, a csv file path.")

    # Pull data from donnees montreal
    base_url = args.input_url
    resource_id = args.input_resource
    filters = {}

    query_params = urllib.parse.urlencode(
        {"resource_id": resource_id, "filters": filters, "limit": 5000}
    )
    url = f"{base_url}?{query_params}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as response:
        data_dict = json.loads(response.read().decode('utf-8'))
    df = pd.DataFrame(data_dict["result"]["records"])


    # Remove rows with no park name and private parks
    df = df[df['Nom'].notna()]
    df = df[df['COMPETENCE'] != "Privé"]

    # Remove parks that have no borough or are not handled by a borough
    not_boroughs = ['Autre', 'Commission scolaire', 'Service des grands parcs, du Mont-Royal et des sports', 'Westmount']
    df = df[~df['GESTION'].isin(not_boroughs)]
    df = df[df['GESTION'].notna()]

    census_df = pd.read_excel(default_data_path / "DONNÉES DU RECENSEMENT DE 2021_AGGLOMÉRATION DE MONTRÉAL_TOTAUX ET POURCENTAGES_0.XLSX", skiprows=(0,1,2), index_col=0)
    census_df.columns = census_df.columns.str.replace("Arrondissement de ", "")
    census_df.columns = census_df.columns.str.replace("Arrondissement d'", "")
    census_df.columns = census_df.columns.str.replace("Arrondissement du", "Le")
    census_df.columns = census_df.columns.str.replace("–", "-")

    # Compute output with borough, total population in that borough, total green area in that borough, and percentage of overall green area in that borough
    output = {
        'borough': df['GESTION'].unique(),
    }
    output_df = pd.DataFrame(output)
    output_df['total_area (ha)'] = output_df['borough'].map(lambda brgh: census_df[brgh]['Superficie (en km2)']) * 100  
    output_df['green_area (ha)'] = output_df['borough'].map(lambda brgh: df[df['GESTION']==brgh]['SUPERFICIE'].astype(float).sum())
    output_df['green_area (%)'] = output_df['green_area (ha)'] / output_df['total_area (ha)'] * 100

    # Save output to csv
    output_df.to_csv(output_path, index=False)
    print(f"Succesfully saved {len(output_df)} lines to {output_path}.")


if __name__ == "__main__":
    main()