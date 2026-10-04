from loader import Loader
from pathlib import Path
import pandas as pd
import json
import utils

def main():
    output_dir = Path(__file__).resolve().parent.parent / "data" / "raw_requests.csv"
    
    processed_output_path = Path(__file__).resolve().parent.parent / "data" / "output_complaints_processed.csv"
    processed_output_path2 = Path(__file__).resolve().parent.parent / "data" / "output_complaints_actions.csv"

    # Uncomment below to download dataset. Filtered download of 311 that only takes non-null arrondissement entries, "plainte" nature, and in the year of 2021
    loader = Loader()
    path = """https://www.donneesquebec.ca/recherche/api/3/action/datastore_search_sql?sql=SELECT * from "dbfc05f8-b939-4639-ae52-2e77f738e43f" where ("ARRONDISSEMENT" is not null or "ARRONDISSEMENT_GEO" is not null) and "NATURE" = 'Plainte' and "DDS_DATE_CREATION" > '2021-01-01 00:00:00'"""
    data = loader.load(path)

    df = pd.DataFrame(data)
    df = utils.str_to_num(df)

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

    print(target_df['ARRONDISSEMENT_GEO'].unique())

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


    # When all datasets are available merge them together
    complaints_processed = Path(__file__).resolve().parent.parent / "data" / "output_complaints_processed.csv"
    complaints_processed_non_matching = Path(__file__).resolve().parent.parent / "data" / "output_complaints_processed_non_matching.csv"
    complaints_actions = Path(__file__).resolve().parent.parent / "data" / "output_complaints_actions.csv"
    complaints_actions_non_matching = Path(__file__).resolve().parent.parent / "data" / "output_complaints_actions_non_matching.csv"

    requests_processed = Path(__file__).resolve().parent.parent / "data" / "output_requests_processed.csv"
    requests_processed_non_matching = Path(__file__).resolve().parent.parent / "data" / "output_requests_processed_non_matching.csv"
    requests_actions = Path(__file__).resolve().parent.parent / "data" / "output_requests_actions.csv"
    requests_actions_non_matching = Path(__file__).resolve().parent.parent / "data" / "output_requests_actions_non_matching.csv"

    comments_processed = Path(__file__).resolve().parent.parent / "data" / "output_comments_processed.csv"
    comments_processed_non_matching = Path(__file__).resolve().parent.parent / "data" / "output_comments_processed_non_matching.csv"
    comments_actions = Path(__file__).resolve().parent.parent / "data" / "output_comments_actions.csv"
    comments_actions_non_matching = Path(__file__).resolve().parent.parent / "data" / "output_comments_actions_non_matching.csv"

    completed_datasets = [
        complaints_processed, complaints_processed_non_matching, 
        requests_processed, requests_processed_non_matching, 
        comments_processed, comments_processed_non_matching
    ]

    completed_dataset_names = [
        "Complaints", "Adjusted Complaints", 
        "Requests", "Adjusted Requests", 
        "Comments", "Adjusted Comments"
    ]

    action_datasets = [
        complaints_actions, complaints_actions_non_matching,
        requests_actions, requests_actions_non_matching,
        comments_actions, comments_actions_non_matching
    ]

    action_dataset_names = [
        "Most Common Complaint", "Most Common Adjusted Complaint", 
        "Most Common Requests", "Most Common Adjusted Request", 
        "Most Common Comment", "Most Common Adjusted Comment"
    ]

    if all(Path(path).exists() for path in completed_datasets) and all(Path(path).exists() for path in action_datasets):
        merged_df = pd.DataFrame()
        for index, path in enumerate(completed_datasets):
            if merged_df.empty:
                merged_df = pd.read_csv(complaints_processed)
                merged_df = merged_df.rename(columns={'Count': completed_dataset_names[index]})
            else:
                merged_df = pd.merge(merged_df, pd.read_csv(path), on='Borough', how='outer')
                merged_df = merged_df.rename(columns={'Count': completed_dataset_names[index]})
                merged_df = merged_df.fillna(value=0)
                merged_df[completed_dataset_names[index]] = merged_df[completed_dataset_names[index]].astype(int)

        for index, path in enumerate(action_datasets):
            new_df = pd.read_csv(path)
            new_df = new_df.rename(columns={'ARRONDISSEMENT_GEO': 'Borough'})
            new_df = new_df.drop(columns=['Count'])
            merged_df = pd.merge(merged_df, new_df, on='Borough', how='outer')
            merged_df = merged_df.rename(columns={'ACTI_NOM': action_dataset_names[index]})

        is_not_borough = merged_df['Borough'] == 'Not-Borough'
        merged_df = pd.concat([merged_df[~is_not_borough], merged_df[is_not_borough]], ignore_index=True)

        merged_path = Path(__file__).resolve().parent.parent / "data" / "Harry - 311 Dataset Count.csv"
        merged_df.to_csv(merged_path, index=False)

if __name__ == "__main__":
    main()