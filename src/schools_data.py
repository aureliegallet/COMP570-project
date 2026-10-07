import urllib.request
import pandas as pd
import json
import argparse
from pathlib import Path
from borough_identifier import BoroughIdentifier
import matplotlib.pyplot as plt
import numpy as np

BOROUGHS = [
    "Ahuntsic-Cartierville", 
    "Anjou", 
    "Côte-des-Neiges-Notre-Dame-de-Grâce", 
    "Lachine",
    "LaSalle",
    "Le Plateau-Mont-Royal",
    "Le Sud-Ouest",
    "L'Île-Bizard-Sainte-Geneviève",
    "Mercier-Hochelaga-Maisonneuve",
    "Montréal-Nord",
    "Outremont",
    "Pierrefonds-Roxboro",
    "Rivière-des-Prairies-Pointe-aux-Trembles",
    "Rosemont-La Petite-Patrie",
    "Saint-Laurent",
    "Saint-Léonard",
    "Verdun",
    "Ville-Marie",
    "Villeray-Saint-Michel-Parc-Extension"
]

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
    
    df.to_csv(default_data_path / 'raw' / 'schools.csv')

    lengths = [len(df)]
    print("Total number of rows upon loading:", lengths[-1])

    # Convert coordinates to borough and save it in new column
    bi = BoroughIdentifier()
    df['borough'] = df.apply(lambda row: bi.match_WSG84_to_borough(longitude_x=row['COORD_X_LL84_IMM'], latitude_y=row['COORD_Y_LL84_IMM']), axis=1)

    # Remove schools with no borough. These are usually schools from Westmount or other non-boroughs.
    df = df[~df['borough'].isna()]
    lengths.append(len(df))
    print("Number of schools removed due to not being in a borough:", lengths[-2] - lengths[-1])
    
    # missing values
    empty_df = df.isna()
    empty_values = empty_df.sum()
    print("\n ------------------ \n")
    print("Missing values per column in returned dataset.")
    print(empty_values)
    print("\n ------------------ \n")

    missing_counts = pd.DataFrame()
    for borough in BOROUGHS:
        missing_counts[borough] = df[df["borough"] == borough].isna().sum()
    print("Missing values per borough.")
    print(missing_counts)
    missing_counts.insert(0, "Column", df.columns) # Absent in CSV without this line
    missing_counts.to_csv(default_data_path / "checks/schools_missing.csv", index=False)
    print("\n ------------------ \n")
    

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

    counts_df = df.groupby(["borough", "TYPE_CS"]).size().unstack(fill_value=0)

    labels = counts_df.index.to_numpy()
    anglo_schools = counts_df["Anglo"]
    french_schools = counts_df["Franco"]

    x = np.arange(len(labels))
    width = 0.25

    fig, ax = plt.subplots()
    ax.bar(x - width/2, anglo_schools, width, label='Anglo')
    ax.bar(x + width/2, french_schools, width, label='Franco')

    ax.set_title('School languages per borough')
    ax.set_xticks(x)
    plt.xticks(rotation='vertical')
    ax.set_xticklabels(labels)
    ax.legend()

    fig.tight_layout()

    plt.savefig(default_data_path / "checks/schools_per_language.png")

    bias_checks = pd.DataFrame({
        'borough': counts_df.index.to_numpy(),
        'anglo_school_count': counts_df['Anglo'],
        'franco_school_count': counts_df['Franco']
    })
    bias_checks["english_speaker_pct"] = bias_checks['borough'].map(lambda brgh: 
        (census_df[brgh]['Anglais seulement'] + census_df[brgh]['Français et anglais'].iloc[0]) / census_df[brgh]["Total - Connaissance des langues officielles pour la population totale à l'exclusion des résidents d'un établissement institutionnel"]
    )
    bias_checks["french_speaker_pct"] = bias_checks['borough'].map(lambda brgh: 
        (census_df[brgh]['Français seulement'] + census_df[brgh]['Français et anglais'].iloc[0]) / census_df[brgh]["Total - Connaissance des langues officielles pour la population totale à l'exclusion des résidents d'un établissement institutionnel"]
    )
    bias_checks['num_children'] = bias_checks['borough'].map(lambda brgh: census_df[brgh]['0 à 14 ans']["0 à 14 ans"].iloc[0])
    bias_checks["english_students_per_school"] = (bias_checks["num_children"] * bias_checks["english_speaker_pct"]) / bias_checks["anglo_school_count"]
    bias_checks["french_students_per_school"] = (bias_checks["num_children"] * bias_checks["french_speaker_pct"]) / bias_checks["franco_school_count"]

    bias_checks.to_csv(default_data_path / "checks/schools_language_bias.csv")


if __name__ == "__main__":
    main()