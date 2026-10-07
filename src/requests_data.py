from loader import Loader
from pathlib import Path
import pandas as pd
import json
import utils


BOROUGHS = [
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

def accumulate_counts(target_df, cumulative_df):
    borough_count = target_df[target_df['ARRONDISSEMENT_GEO'].isin(BOROUGHS)]['ARRONDISSEMENT_GEO'].value_counts()
    resulting_df = borough_count.reset_index()
    resulting_df.columns = ['Borough', 'Count']

    not_borough_count = (~target_df['ARRONDISSEMENT_GEO'].isin(BOROUGHS)).sum()
    resulting_df.loc[len(resulting_df)] = ['Not-Borough', not_borough_count]

    if cumulative_df.empty:
        cumulative_df = resulting_df
    else:
        resulting_df = resulting_df.rename(columns={'Count': 'ToAdd'})
        cumulative_df = pd.merge(cumulative_df, resulting_df, on='Borough', how='outer')
        cumulative_df['ToAdd'] = cumulative_df['ToAdd'].fillna(value=0)
        cumulative_df['Count'] = cumulative_df['Count'] + cumulative_df['ToAdd']
        cumulative_df = cumulative_df.drop(columns='ToAdd')
    return cumulative_df


def main():
    complaints_processed = Path(__file__).resolve().parent.parent / "data/requests" / "output_complaints_processed.csv"
    complaints_processed_non_matching = Path(__file__).resolve().parent.parent / "data/requests" / "output_complaints_processed_non_matching.csv"
    complaints_actions = Path(__file__).resolve().parent.parent / "data/requests" / "output_complaints_actions.csv"
    complaints_output_dir = Path(__file__).resolve().parent.parent / "data/requests" / "output_complaints.csv"

    requests_processed = Path(__file__).resolve().parent.parent / "data/requests" / "output_requests_processed.csv"
    requests_processed_non_matching = Path(__file__).resolve().parent.parent / "data/requests" / "output_requests_processed_non_matching.csv"
    requests_actions = Path(__file__).resolve().parent.parent / "data/requests" / "output_requests_actions.csv"
    requests_output_dir = Path(__file__).resolve().parent.parent / "data/requests" / "output_requests.csv"

    completed_datasets = [
        complaints_processed, complaints_processed_non_matching, 
        requests_processed, requests_processed_non_matching
    ]

    completed_dataset_names = [
        "Complaints", "Adjusted Complaints", 
        "Requests", "Adjusted Requests"
    ]

    action_datasets = [
        complaints_actions,
        requests_actions
    ]

    action_dataset_names = [
        "Most Common Complaint",
        "Most Common Requests"
    ]

    output_dirs = [
        complaints_output_dir, requests_output_dir
    ]

    natures = [
        "Plainte", "Requete"
    ]

    hard_limit = '30000'

    loader = Loader()

    # Get total count of 2021 rows
    request_sql = f"""SELECT COUNT(*) from "dbfc05f8-b939-4639-ae52-2e77f738e43f" where "DDS_DATE_CREATION" > '2021-01-01 00:00:00'"""
    request = loader.build_request("requests", is_sql = True, sql_command = request_sql)
    count_2021 = loader.send_request(request)
    print(f"Number of entries for 2021: {count_2021[0]['count']}")

    count_filtered_2021 = 0
    
    for index, path in enumerate(output_dirs):
        # Filtered download of 311 that only takes non-null arrondissement entries, a specific nature, and in the year of 2021
        cumulative_df_matching = pd.DataFrame()
        cumulative_df_non_matching = pd.DataFrame()
        cumulative_df_actions = pd.DataFrame()
        last_id = '0'
        loop_counter = 0

        print("\n ------------------ \n")
        print("Processing " + natures[index])
        while True:
            path = """https://www.donneesquebec.ca/recherche/api/3/action/datastore_search_sql?sql=SELECT * from "dbfc05f8-b939-4639-ae52-2e77f738e43f" where ("ARRONDISSEMENT" is not null or "ARRONDISSEMENT_GEO" is not null) and "NATURE" = '""" + natures[index] + """' and "DDS_DATE_CREATION" > '2021-01-01 00:00:00' and "ID_UNIQUE" > '""" + last_id + """' ORDER BY "ID_UNIQUE" LIMIT """ + hard_limit
            data = loader.load(path)
            df = pd.DataFrame(data)
            df = utils.str_to_num(df)

            if len(df) == 0:
                break
            
            last_id = df['ID_UNIQUE'].iat[-1]
            count_filtered_2021 += len(df)

            # Clear spacing because it is inconsistent between entries
            df['ARRONDISSEMENT'] = df['ARRONDISSEMENT'].str.replace(' ', '')
            df['ARRONDISSEMENT_GEO'] = df['ARRONDISSEMENT_GEO'].str.replace(' ', '')
            df['ACTI_NOM'] = df['ACTI_NOM'].str.replace(' ', '')

            matching_df = df[df['ARRONDISSEMENT'] == df['ARRONDISSEMENT_GEO']]
            non_matching_df = df[df['ARRONDISSEMENT'] != df['ARRONDISSEMENT_GEO']]


            # First do matching columns
            cumulative_df_matching = accumulate_counts(matching_df, cumulative_df_matching)

            # Then do non-matching columns
            cumulative_df_non_matching = accumulate_counts(non_matching_df, cumulative_df_non_matching)


            # Tally most common action
            most_common_action = df[df['ARRONDISSEMENT_GEO'].isin(BOROUGHS)]
            most_common_action = most_common_action.value_counts(['ARRONDISSEMENT_GEO', 'ACTI_NOM']).reset_index(name='Count') # Sorts with max on top

            if cumulative_df_actions.empty:
                cumulative_df_actions = most_common_action
            else:
                most_common_action = most_common_action.rename(columns={'Count': 'ToAdd'})
                cumulative_df_actions = pd.merge(cumulative_df_actions, most_common_action, on=['ARRONDISSEMENT_GEO', 'ACTI_NOM'], how='outer')
                cumulative_df_actions['ToAdd'] = cumulative_df_actions['ToAdd'].fillna(value=0)
                cumulative_df_actions['Count'] = cumulative_df_actions['Count'].fillna(value=0)
                cumulative_df_actions['Count'] = cumulative_df_actions['Count'] + cumulative_df_actions['ToAdd']
                cumulative_df_actions = cumulative_df_actions.drop(columns='ToAdd')

            loop_counter = loop_counter + 1
            print("Loop " + str(loop_counter))


        # Final processing and saving
        counts_matching_path = completed_datasets[index * 2]
        cumulative_df_matching.to_csv(counts_matching_path, index=False)

        counts_non_matching_path = completed_datasets[index * 2 + 1]
        cumulative_df_non_matching.to_csv(counts_non_matching_path, index=False)

        cumulative_df_actions = cumulative_df_actions.sort_values(by=['Count'], ascending=False)
        cumulative_df_actions = cumulative_df_actions.drop_duplicates(subset=['ARRONDISSEMENT_GEO']) # Drops all other mentions of the same arrondissement except the first
        cumulative_df_actions = cumulative_df_actions.reset_index(drop=True)
        action_output_path = action_datasets[index]
        cumulative_df_actions.to_csv(action_output_path, index=False)

    print("\n ------------------ \n")
    print(f"Total lines used: {count_filtered_2021}")

    # When all datasets are available merge them together
    if all(Path(path).exists() for path in completed_datasets) and all(Path(path).exists() for path in action_datasets):
        merged_df = pd.DataFrame()
        for index, path in enumerate(completed_datasets):
            if merged_df.empty: # This seems wrong but we never go there so let's not touch
                merged_df = pd.read_csv(path)
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

        merged_path = Path(__file__).resolve().parent.parent / "data" / "requests_dataset.csv"
        merged_df.to_csv(merged_path, index=False)

if __name__ == "__main__":
    main()