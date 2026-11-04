from pathlib import Path
import pandas as pd
from paretoset import paretoset
from scipy.spatial.distance import cdist
from collections import namedtuple
import numpy as np

DATA_PATH = Path(__file__).resolve().parent.parent / "data"

RAW_PATH = DATA_PATH / 'raw'
SPACED_REQUESTS = RAW_PATH / 'requests_space.csv'

LABELLING_PATH = DATA_PATH / "annotation" / "labelling"
ALL_LABELS_PATH = LABELLING_PATH / "all_annotated_labels.csv"

LOOKUP_JSON_PATH = DATA_PATH / "annotation" / "labels_lookup.json"

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
BOROUGHS = [borough.replace(" ", "") for borough in BOROUGHS]

def get_pop_dict():
    census_df = pd.read_excel(DATA_PATH / "DONNÉES DU RECENSEMENT DE 2021_AGGLOMÉRATION DE MONTRÉAL_TOTAUX ET POURCENTAGES_0.XLSX", skiprows=(0,1,2), index_col=0)
    census_df.columns = census_df.columns.str.replace("Arrondissement de ", "")
    census_df.columns = census_df.columns.str.replace("Arrondissement d'", "")
    census_df.columns = census_df.columns.str.replace("Arrondissement du", "Le")
    census_df.columns = census_df.columns.str.replace("–", "-")
    census_df.columns = census_df.columns.str.replace(" ", "")
    pop_dict = {}
    for brg in BOROUGHS:
        pop_dict[brg] = census_df[brg]["Population totale en 2021"]
    return pop_dict

def load_df(path):
    chunk_size = 50000
    processed = []
    cols = ['label', 'ARRONDISSEMENT', 'ARRONDISSEMENT_GEO', 'task_1', 'task_2', 'task_3']
    reader = pd.read_csv(LABELLING_PATH / path, usecols=cols, chunksize=chunk_size, dtype=str)
    for chunk in reader:
        processed.append(chunk)
    df = pd.concat(processed, ignore_index=True)
    df["ARRONDISSEMENT_GEO"] = df["ARRONDISSEMENT_GEO"].fillna(df["ARRONDISSEMENT"]) # Filling NA in ARRONDISSEMENT_GEO
    df = df[~df["ARRONDISSEMENT_GEO"].isna()]
    df.drop(columns=["ARRONDISSEMENT"])
    df = df[df["ARRONDISSEMENT_GEO"].isin(BOROUGHS)]
    return df

def count_empty(df):
    counts = df['task_1'].isna().sum()
    print(f"Share of requests with coded labels {(len(df) - counts) / len(df) * 100:.2f}%")
    print(f"Share of the remainder: {counts / len(df) * 100:.2f}%\n")


def main():    
    # HUMAN ANNOTATED
    df_human = load_df("311-human_annotated_requests.csv")
    print("HUMAN ANNOTATED - TASK 1")
    count_empty(df_human)

    # ALL ANNOTATED
    df = load_df("311-annotated_requests.csv")
    print("ALL ANNOTATED - TASK 1")
    count_empty(df)

    na_count = df['task_3'].isna().sum()
    print("ALL ANNOTATED - Task 3")
    print(f"Percentage of rows with a topic: {((len(df) - na_count) / len(df) * 100):.2f}%\n")


    # Number of requests per borough and topic
    table = df[df["ARRONDISSEMENT_GEO"].isin(BOROUGHS)].pivot_table(
        index="ARRONDISSEMENT_GEO", 
        columns="task_3", 
        aggfunc="size", 
        fill_value=0
    )

    # Normalize number of requests by borough population
    print("Rates per 10 000 habitants:")
    pop_dict = get_pop_dict()
    pop_series = pd.Series(pop_dict)
    norm_table = table.div(pop_series, axis=0) * 10000
    print(norm_table)

    # Distribution of topics by borough
    print("\nDistribution of topics by borough:")
    percentage_table = table.div(table.sum(axis=1), axis=0) * 100
    print(percentage_table)

    # Condition only
    df_condition = df[df["task_2"].str.lower() == "condition"] # Condition | condition | CONDITION
    table_condition = df_condition[df_condition["ARRONDISSEMENT_GEO"].isin(BOROUGHS)].pivot_table( # Compute again for condition only
        index="ARRONDISSEMENT_GEO", 
        columns="task_3", 
        aggfunc="size", 
        fill_value=0
    )
    table_condition = table_condition.div(pop_series, axis=0) * 10000

    # https://pypi.org/project/paretoset/
    Solution = namedtuple("Solution", ["solution", "obj_value"])
    solutions = []
    for index, row in table_condition.iterrows():
        solution = index
        obj_value = list(row.to_dict().values())
        solutions.append(Solution(solution=solution, obj_value=obj_value))
    objective_values_array = np.vstack([s.obj_value for s in solutions])
    mask = paretoset(objective_values_array, sense=["min", "min",  "min",  "min",  "min"])
    efficient_solutions = [solution for (solution, m) in zip(solutions, mask) if m]
    print(len(efficient_solutions))
    print([solution.solution for solution in efficient_solutions])

    frontier_values_array = objective_values_array[mask]
    distances_to_all_frontier = cdist(objective_values_array, frontier_values_array, metric='euclidean') # euclidean distance to each point of the frontier
    distances_to_frontier = np.min(distances_to_all_frontier, axis=1) # take minimum: gives euclidean distance to closest Pareto Frontier point
    for i, dist in enumerate(distances_to_frontier):
        print(f"{solutions[i].solution} is {dist:.2f} units from the closest frontier point.")

    # Computed without other
    solutions = []
    for index, row in table_condition.iterrows():
        solution = index
        obj_value = list(row.to_dict().values())
        obj_value.pop(1) # Remove other, which appears in the 2nd column
        solutions.append(Solution(solution=solution, obj_value=obj_value))
    objective_values_array = np.vstack([s.obj_value for s in solutions])
    mask = paretoset(objective_values_array, sense=["min",  "min",  "min",  "min"])
    efficient_solutions = [solution for (solution, m) in zip(solutions, mask) if m]

    print(len(efficient_solutions))
    print([solution.solution for solution in efficient_solutions])

    frontier_values_array = objective_values_array[mask]
    distances_to_all_frontier = cdist(objective_values_array, frontier_values_array, metric='euclidean') # euclidean distance to each point of the frontier
    distances_to_frontier = np.min(distances_to_all_frontier, axis=1) # take minimum: gives euclidean distance to closest Pareto Frontier point
    for i, dist in enumerate(distances_to_frontier):
        print(f"{solutions[i].solution} is {dist:.2f} units from the closest frontier point.")
    


        
    
if __name__ == "__main__":
    main()