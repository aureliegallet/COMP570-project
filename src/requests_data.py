from loader import Loader
from pathlib import Path
import pandas as pd
import json
import utils

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
    
    for index, path in enumerate(output_dirs):
        # Filtered download of 311 that only takes non-null arrondissement entries, a specific nature, and in the year of 2021
        loader = Loader()
        df = pd.DataFrame()
        cumulative_df = pd.DataFrame()
        cumulative_df_non_matching = pd.DataFrame()
        cumulative_df_actions = pd.DataFrame()
        last_id = '0'
        first_go = True
        loop_counter = 0

        print("Processing " + natures[index])
        while True:
            first_go = False

            path = """https://www.donneesquebec.ca/recherche/api/3/action/datastore_search_sql?sql=SELECT * from "dbfc05f8-b939-4639-ae52-2e77f738e43f" where ("ARRONDISSEMENT" is not null or "ARRONDISSEMENT_GEO" is not null) and "NATURE" = '""" + natures[index] + """' and "DDS_DATE_CREATION" > '2021-01-01 00:00:00' and "ID_UNIQUE" > '""" + last_id + """' ORDER BY "ID_UNIQUE" LIMIT """ + hard_limit
            print(path)
            data = loader.load(path)

            df = pd.DataFrame(data)
            df = utils.str_to_num(df)

            if len(df) == 0:
                break
            
            last_id = df['ID_UNIQUE'].iat[-1]
            print(last_id)

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

            # First do matching columns
            target_df = matching_df

            print(target_df['ARRONDISSEMENT_GEO'].unique())

            borough_count = target_df[target_df['ARRONDISSEMENT_GEO'].isin(boroughs)]['ARRONDISSEMENT_GEO'].value_counts()
            resulting_df = borough_count.reset_index()
            resulting_df.columns = ['Borough', 'Count']

            not_borough_count = (~target_df['ARRONDISSEMENT_GEO'].isin(boroughs)).sum()
            resulting_df.loc[len(resulting_df)] = ['Not-Borough', not_borough_count]

            print(resulting_df)

            targeted_index = index * 2
            processed_output_path = completed_datasets[targeted_index]

            if cumulative_df.empty:
                cumulative_df = resulting_df
            else:
                resulting_df = resulting_df.rename(columns={'Count': 'ToAdd'})
                cumulative_df = pd.merge(cumulative_df, resulting_df, on='Borough', how='outer')
                cumulative_df['ToAdd'] = cumulative_df['ToAdd'].fillna(value=0)
                cumulative_df['Count'] = cumulative_df['Count'] + cumulative_df['ToAdd']
                cumulative_df = cumulative_df.drop(columns='ToAdd')

            cumulative_df.to_csv(processed_output_path, index=False)

            # Then do non-matching columns
            target_df = non_matching_df

            print(target_df['ARRONDISSEMENT_GEO'].unique())

            borough_count = target_df[target_df['ARRONDISSEMENT_GEO'].isin(boroughs)]['ARRONDISSEMENT_GEO'].value_counts()
            resulting_df = borough_count.reset_index()
            resulting_df.columns = ['Borough', 'Count']

            not_borough_count = (~target_df['ARRONDISSEMENT_GEO'].isin(boroughs)).sum()
            resulting_df.loc[len(resulting_df)] = ['Not-Borough', not_borough_count]

            print(resulting_df)

            targeted_index = index * 2 + 1
            processed_output_path = completed_datasets[targeted_index]

            if cumulative_df_non_matching.empty:
                cumulative_df_non_matching = resulting_df
            else:
                resulting_df = resulting_df.rename(columns={'Count': 'ToAdd'})
                cumulative_df_non_matching = pd.merge(cumulative_df_non_matching, resulting_df, on='Borough', how='outer')
                cumulative_df_non_matching['ToAdd'] = cumulative_df_non_matching['ToAdd'].fillna(value=0)
                cumulative_df_non_matching['Count'] = cumulative_df_non_matching['Count'] + cumulative_df_non_matching['ToAdd']
                cumulative_df_non_matching = cumulative_df_non_matching.drop(columns='ToAdd')

            cumulative_df_non_matching.to_csv(processed_output_path, index=False)

            # Tally most common action

            most_common_action = df[df['ARRONDISSEMENT_GEO'].isin(boroughs)]
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

        cumulative_df_actions = cumulative_df_actions.sort_values(by=['Count'], ascending=False)
        cumulative_df_actions = cumulative_df_actions.drop_duplicates(subset=['ARRONDISSEMENT_GEO']) # Drops all other mentions of the same arrondissement except the first
        cumulative_df_actions = cumulative_df_actions.reset_index(drop=True)

        print(cumulative_df_actions)

        processed_output_path2 = action_datasets[index]

        cumulative_df_actions.to_csv(processed_output_path2, index=False)

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