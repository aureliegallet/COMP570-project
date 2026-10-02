import pathlib
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
    parser.add_argument('-o', '--output', type=pathlib.Path, default=default_data_path)

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


    # Convert coordinates to borough and save it in new column
    bi = BoroughIdentifier()
    df['borough'] = df.apply(lambda row: bi.match_WSG84_to_borough(longitude_x=row['COORD_X_LL84_IMM'], latitude_y=row['COORD_Y_LL84_IMM']), axis=1)

    # Remove schools intended for adult learning
    df = df[~df['ORDRE_ENS'].str.contains('adultes')]
    df = df[~df['ORDRE_ENS'].str.contains('professionnelle')]

    # Group lines with same school name in the same borough to avoid duplicate records for the same establishment
    df = df.groupby(['NOM_OFFCL_ORGNS', 'borough'], as_index=False).agg(lambda x: ', '.join(x.dropna().astype(str).unique()))

    # Borough population records according to https://ville.montreal.qc.ca/pls/portal/docs/PAGE/MTL_STATS_FR/MEDIA/DOCUMENTS/CARTE_POPULATION%20ET%20SUPERFICIE%202021.PDF
    total_pop = {
        'Côte-des-Neiges-Notre-Dame-de-Grâce': 170583, 
        'Ville-Marie': 104944,
        'Montréal-Nord': 88471,
        'Mercier-Hochelaga-Maisonneuve': 140627,
        'Pierrefonds-Roxboro': 70382,
        'Rivière-des-Prairies-Pointe-aux-Trembles': 107941,
        'Lachine': 46428,
        'Saint-Laurent': 102104,
        'Rosemont-La Petite-Patrie': 141813,
        'Ahuntsic-Cartierville': 135336,
        'Le Plateau-Mont-Royal': 105813,
        'Verdun': 70377,
        'LaSalle': 82235,
        'Villeray-Saint-Michel-Parc-Extension': 145090,
        'Anjou': 43243,
        'Le Sud-Ouest': 84553,
        'L\'Île-Bizard-Sainte-Geneviève': 18885,
        'Saint-Léonard': 79495,
        'Outremont': 24629
    }

    # Compute output with borough, total population in that borough, number of schools in that borough, and number of residents per school
    output = {
        'borough': df['borough'].unique(),
    }
    output_df = pd.DataFrame(output)
    output_df['total_pop'] = output_df['borough'].map(total_pop)
    output_df['num_schools'] = output_df['borough'].map(lambda brgh: len(df[df['borough']==brgh]))
    output_df['residents_per_school'] = output_df['total_pop'] / output_df['num_schools']

    # Save output to csv
    output_df.to_csv(output_path, index=False)
    print(f"Succesfully saved {len(output_df)} lines to {output_path}.")


if __name__ == "__main__":
    main()