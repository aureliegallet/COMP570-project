from loader import Loader
from pathlib import Path
import pandas as pd
import json
import utils
import time

COMPLAINTS_PROCESSED = Path(__file__).resolve().parent.parent / "data/requests" / "output_complaints_processed.csv"
COMPLAINTS_PROCESSED_NON_MATCHING = Path(__file__).resolve().parent.parent / "data/requests" / "output_complaints_processed_non_matching.csv"
COMPLAINTS_ACTIONS = Path(__file__).resolve().parent.parent / "data/requests" / "output_complaints_actions.csv"

REQUESTS_PROCESSED = Path(__file__).resolve().parent.parent / "data/requests" / "output_requests_processed.csv"
REQUESTS_PROCESSED_NON_MATCHING = Path(__file__).resolve().parent.parent / "data/requests" / "output_requests_processed_non_matching.csv"
REQUESTS_ACTIONS = Path(__file__).resolve().parent.parent / "data/requests" / "output_requests_actions.csv"

COMPLETED_DATASETS = [COMPLAINTS_PROCESSED, COMPLAINTS_PROCESSED_NON_MATCHING, REQUESTS_PROCESSED, REQUESTS_PROCESSED_NON_MATCHING]
COMPLETED_DATASET_NAMES = ["Complaints", "Adjusted Complaints", "Requests", "Adjusted Requests"]

ACTION_DATASETS = [COMPLAINTS_ACTIONS, REQUESTS_ACTIONS]
ACTION_DATASET_NAMES = ["Most Common Complaint", "Most Common Requests"]

COMPLAINTS_OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data/requests" / "output_complaints.csv"
REQUESTS_OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data/requests" / "output_requests.csv"
OUTPUT_DIRS = [COMPLAINTS_OUTPUT_DIR, REQUESTS_OUTPUT_DIR]

NATURES = ["Plainte", "Requete"]

HARD_LIMIT = '30000'

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

def caculate_missing(loader):
    length = 0
    empty_values = pd.Series()
    rows_with_missing = 0

    page = 0
    page_size = 30000
    load_more = True
    missing_counts = pd.DataFrame()
    number_timeouts = 0
    while load_more:
        path = (
            """https://www.donneesquebec.ca/recherche/api/3/action/datastore_search_sql?"""
            'sql=SELECT * from "dbfc05f8-b939-4639-ae52-2e77f738e43f"'
            """where "DDS_DATE_CREATION" > '2021-01-01 00:00:00'"""
            f"""LIMIT {page_size} OFFSET {page_size * page}"""
        )
        try: 
            data = loader.load(path)
        except Exception as e:
            print("\n ------------------ \n")
            print(f"Dataset stopped loading at {page_size * page} because of error {e}.")
            break

        if data is None and number_timeouts < 2:
            number_timeouts += 1
            time.sleep(5)
        elif data is None and number_timeouts >= 2:
            print("Gateway time out twice, stopped run.")
            break
        else:
            number_timeouts = 0

            if len(data) < page_size:
                load_more = False
            else: 
                page += 1

            df = pd.DataFrame(data)
            df = utils.str_to_num(df)
            df['ARRONDISSEMENT_GEO'] = df['ARRONDISSEMENT_GEO'].fillna("Not-Borough").str.replace(' ', '')

            length += len(df)
            empty_values = empty_values.add(df.isna().sum(), fill_value = 0)

            normal_length = len(df)
            temp = df.dropna()
            removed_length = len(temp)
            rows_with_missing += normal_length - removed_length

            for borough in BOROUGHS:
                if borough in missing_counts.columns:
                    missing_counts[borough] = missing_counts[borough] + df[df["ARRONDISSEMENT_GEO"] == borough].isna().sum()
                else:
                    missing_counts[borough] = df[df["ARRONDISSEMENT_GEO"] == borough].isna().sum()

            print("Loop " + str(page))


    print("\n ------------------ \n")
    print(f"Total length of reported dataset: {length}")
    print(f"Empty values per column")
    print(empty_values.sort_values(ascending = False))
    print(f"Total rows with missing values: {rows_with_missing}")
    print("Missing values per borough")
    print(missing_counts)
    missing_counts.insert(0, "Column", df.columns) # Absent in CSV without this line
    missing_counts.to_csv(Path(__file__).resolve().parent.parent / "data/checks/requests_missing.csv", index=False)
    

def main():
    loader = Loader()

    # Get total count of 2021 rows
    request_sql = f"""SELECT COUNT(*) from "dbfc05f8-b939-4639-ae52-2e77f738e43f" where "DDS_DATE_CREATION" > '2021-01-01 00:00:00'"""
    request = loader.build_request("requests", is_sql = True, sql_command = request_sql)
    count_2021 = loader.send_request(request)
    print(f"Number of entries for 2021: {count_2021[0]['count']}")

    # Get action labels of 2021 rows
    request_action_sql = f"""SELECT COUNT(DISTINCT "ACTI_NOM") from "dbfc05f8-b939-4639-ae52-2e77f738e43f" where "DDS_DATE_CREATION" > '2021-01-01 00:00:00'"""
    request_action = loader.build_request("requests", is_sql = True, sql_command = request_action_sql)
    count_action_2021 = loader.send_request(request_action)
    print(f"Number of unique action labels 2021: {count_action_2021[0]['count']}")

    count_filtered_2021 = 0
    checks = [pd.Series(), pd.Series()]

    # Compute missing values for unfiltered 2021
    print("\n ------------------ \n")
    print(f"Missing values for unfiltered 2021 dataset.")
    caculate_missing(loader)


    # Filtered processing
    for index, path in enumerate(OUTPUT_DIRS):
        # Filtered download of 311 that only takes non-null arrondissement entries, a specific nature, and in the year of 2021
        cumulative_df_matching = pd.DataFrame()
        cumulative_df_non_matching = pd.DataFrame()
        cumulative_df_actions = pd.DataFrame()

        last_id = '0'
        loop_counter = 0
        print("\n ------------------ \n")
        print("Processing " + NATURES[index])

        while True:
            path = (
                """https://www.donneesquebec.ca/recherche/api/3/action/datastore_search_sql?"""
                'sql=SELECT * from "dbfc05f8-b939-4639-ae52-2e77f738e43f"'
                """where ("ARRONDISSEMENT" is not null or "ARRONDISSEMENT_GEO" is not null)"""
                f"""and "NATURE" = '{NATURES[index]}' and "DDS_DATE_CREATION" > '2021-01-01 00:00:00'"""
                f"""and "ID_UNIQUE" > '{last_id}' ORDER BY "ID_UNIQUE" LIMIT {HARD_LIMIT}"""
            )
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

            # Recording how often boroughs have this as a plainte or a request
            counting_bins = df[df['ACTI_NOM'] == "Collectededéchets"]["ARRONDISSEMENT_GEO"].value_counts()
            checks[index] = checks[index].add(counting_bins, fill_value = 0) # https://stackoverflow.com/questions/28353577/merging-and-sum-up-several-value-counts-series-in-pandas
        
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
        counts_matching_path = COMPLETED_DATASETS[index * 2]
        cumulative_df_matching.to_csv(counts_matching_path, index=False)

        counts_non_matching_path = COMPLETED_DATASETS[index * 2 + 1]
        cumulative_df_non_matching.to_csv(counts_non_matching_path, index=False)

        cumulative_df_actions = cumulative_df_actions.sort_values(by=['Count'], ascending=False)
        cumulative_df_actions = cumulative_df_actions.drop_duplicates(subset=['ARRONDISSEMENT_GEO']) # Drops all other mentions of the same arrondissement except the first
        cumulative_df_actions = cumulative_df_actions.reset_index(drop=True)
        action_output_path = ACTION_DATASETS[index]
        cumulative_df_actions.to_csv(action_output_path, index=False)

    print("\n ------------------ \n")
    print(f"Total lines used: {count_filtered_2021}")

    print("\n ------------------ \n")
    print("Bin collection bias")
    bin_df = pd.concat([checks[0], checks[1]], axis = 1)
    bin_df.columns = ["registered_as_complaint", "registered_as_request"]
    bin_df["proportion"] = bin_df["registered_as_complaint"] / (bin_df["registered_as_complaint"] + bin_df["registered_as_request"])
    bin_df = bin_df.sort_values(by="proportion")
    bin_df.to_csv(Path(__file__).resolve().parent.parent / "data/checks" / "collecte_dechets_counts.csv")
    print(bin_df)


    # When all datasets are available merge them together
    if all(Path(path).exists() for path in COMPLETED_DATASETS) and all(Path(path).exists() for path in ACTION_DATASETS):
        merged_df = pd.DataFrame()
        for index, path in enumerate(COMPLETED_DATASETS):
            if merged_df.empty:
                merged_df = pd.read_csv(path)
                merged_df = merged_df.rename(columns={'Count': COMPLETED_DATASET_NAMES[index]})
            else:
                merged_df = pd.merge(merged_df, pd.read_csv(path), on='Borough', how='outer')
                merged_df = merged_df.rename(columns={'Count': COMPLETED_DATASET_NAMES[index]})
                merged_df = merged_df.fillna(value=0)
                merged_df[COMPLETED_DATASET_NAMES[index]] = merged_df[COMPLETED_DATASET_NAMES[index]].astype(int)

        for index, path in enumerate(ACTION_DATASETS):
            new_df = pd.read_csv(path)
            new_df = new_df.rename(columns={'ARRONDISSEMENT_GEO': 'Borough'})
            new_df = new_df.drop(columns=['Count'])
            merged_df = pd.merge(merged_df, new_df, on='Borough', how='outer')
            merged_df = merged_df.rename(columns={'ACTI_NOM': ACTION_DATASET_NAMES[index]})

        is_not_borough = merged_df['Borough'] == 'Not-Borough'
        merged_df = pd.concat([merged_df[~is_not_borough], merged_df[is_not_borough]], ignore_index=True)

        merged_path = Path(__file__).resolve().parent.parent / "data" / "requests_dataset.csv"
        merged_df.to_csv(merged_path, index=False)

if __name__ == "__main__":
    main()