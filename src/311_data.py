from loader import Loader
from pathlib import Path
import pandas as pd
import json

def main():
    output_path = Path(__file__).resolve().parent.parent / "data" / "output_complaints.csv"
    
    processed_output_path = Path(__file__).resolve().parent.parent / "data" / "output_complaints_processed.csv"
    processed_output_path2 = Path(__file__).resolve().parent.parent / "data" / "output_complaints_actions.csv"

    # Uncomment below to download dataset. Filtered download of 311 that only takes non-null arrondissement entries, "plainte" nature, and in the year of 2021
    # loader = Loader()
    # path = """https://www.donneesquebec.ca/recherche/api/3/action/datastore_search_sql?sql=SELECT * from "dbfc05f8-b939-4639-ae52-2e77f738e43f" where ("ARRONDISSEMENT" is not null or "ARRONDISSEMENT_GEO" is not null) and "NATURE" = 'Plainte' and "DDS_DATE_CREATION" > '2021-01-01 00:00:00'"""
    # path = path.replace(" ", "%20")
    # loader.load_to_csv(path, output_path)

    df = pd.read_csv(output_path, encoding='latin-1')

    # Clear spacing because it is inconsistent between entries
    df['ARRONDISSEMENT'] = df['ARRONDISSEMENT'].str.replace(' ', '')
    df['ARRONDISSEMENT_GEO'] = df['ARRONDISSEMENT_GEO'].str.replace(' ', '')
    df['ACTI_NOM'] = df['ACTI_NOM'].str.replace(' ', '')

    matching_df = df[df['ARRONDISSEMENT'] == df['ARRONDISSEMENT_GEO']]
    non_matching_df = df[df['ARRONDISSEMENT'] != df['ARRONDISSEMENT_GEO']]

    boroughs = [
        "Côte-des-Neiges-Notre-Dame-de-Grâce",
        "Ville-Marie",
        "Verdun",
        "Montréal-Nord",
        "LePlateau-Mont-Royal",
        "Villeray-Saint-Michel-Parc-Extension",
        "Rivière-des-Prairies-Pointe-aux-Trembles",
        "Ahuntsic-Cartierville",
        "LaSalle",
        "Outremont",
        "Mercier-Hochelaga-Maisonneuve",
        "L'Île-Bizard-Sainte-Geneviève",
        "Rosemont-LaPetite-Patrie",
        "Pierrefonds-Roxboro",
        "Anjou",
        "Lachine",
        "Saint-Léonard",
        "LeSud-Ouest",
        "Saint-Laurent"
    ]

    # Change as needed
    target_df = matching_df

    borough_count = target_df[target_df['ARRONDISSEMENT_GEO'].isin(boroughs)]['ARRONDISSEMENT_GEO'].value_counts()
    resulting_df = borough_count.reset_index()
    resulting_df.columns = ['Borough', 'Count']

    not_borough_count = (~target_df['ARRONDISSEMENT_GEO'].isin(boroughs)).sum()
    resulting_df.loc[len(resulting_df)] = ['Not-Borough', not_borough_count]

    filtered_target_df = target_df[target_df['ARRONDISSEMENT_GEO'].isin(boroughs)]
    most_common_action = filtered_target_df.value_counts(['ARRONDISSEMENT_GEO', 'ACTI_NOM'])
    most_common_action = most_common_action.reset_index(name='Count')
    most_common_action = most_common_action.drop_duplicates(subset=['ARRONDISSEMENT_GEO'])
    most_common_action = most_common_action.reset_index(drop=True)

    print(resulting_df)
    print(most_common_action)

    resulting_df.to_csv(processed_output_path, index=False)
    most_common_action.to_csv(processed_output_path2, index=False)

if __name__ == "__main__":
    main()