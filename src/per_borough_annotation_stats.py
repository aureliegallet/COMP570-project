from pathlib import Path
import pandas as pd

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


def main():
    chunk_size = 50_000
    chunk_size = 50000
    cols = ['label', 'ARRONDISSEMENT', 'ARRONDISSEMENT_GEO', 'task_3']
    processed = []
    reader = pd.read_csv(LABELLING_PATH / '311-annotated_requests.csv', usecols=cols, chunksize=chunk_size, dtype=str)
    for chunk in reader:
        processed.append(chunk)
    df = pd.concat(processed, ignore_index=True)
    df["ARRONDISSEMENT_GEO"] = df["ARRONDISSEMENT_GEO"].fillna(df["ARRONDISSEMENT"]) # Filling NA in ARRONDISSEMENT_GEO
    df = df[~df["ARRONDISSEMENT_GEO"].isna()]
    df.drop(columns=["ARRONDISSEMENT"])
    df = df[df["ARRONDISSEMENT_GEO"].isin(BOROUGHS)]

    na_count = df['task_3'].isna().sum()
    df_len = len(df)
    print(f"Percentage of rows with a topic: {((df_len - na_count) / df_len * 100):.2f}%")
    print("Rates per 10 000 habitants:")
    table = df[df["ARRONDISSEMENT_GEO"].isin(BOROUGHS)].pivot_table(
        index="ARRONDISSEMENT_GEO", 
        columns="task_3", 
        aggfunc="size", 
        fill_value=0
    )
    pop_dict = get_pop_dict()
    pop_series = pd.Series(pop_dict)
    norm_table = table.div(pop_series, axis=0) * 10000
    print(norm_table)
        
    
if __name__ == "__main__":
    main()