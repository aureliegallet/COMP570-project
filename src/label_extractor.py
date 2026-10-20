import random
import pandas as pd
from pathlib import Path

random.seed(42)

DIRNAME = Path(__file__).parent.parent
RAW_PATH = DIRNAME / "data/raw"
ANNOTATION_PATH = DIRNAME / "data/annotation"
RAW_PATH.mkdir(parents=True, exist_ok=True)
ANNOTATION_PATH.mkdir(parents=True, exist_ok=True)

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

def main():
    processed = []
    chunk_size = 50000
    cols = ['ACTI_NOM', 'ARRONDISSEMENT', 'ARRONDISSEMENT_GEO']
    reader = pd.read_csv(RAW_PATH / 'requests.csv', usecols=cols, chunksize=chunk_size, dtype=str)
    for chunk in reader:
        processed.append(chunk)

    # Preprocessing and filtering
    df = pd.concat(processed, ignore_index=True)
    df["ARRONDISSEMENT_GEO"] = df["ARRONDISSEMENT_GEO"].fillna(df["ARRONDISSEMENT"]) # Resolving borough
    df = df[~df["ARRONDISSEMENT_GEO"].isna()]
    df.drop(columns=["ARRONDISSEMENT"])
    df = df[df["ARRONDISSEMENT_GEO"].isin(BOROUGHS)]
    print(f"Dataframe length: {len(df)}")

    # extracting the distinct request category labels that appear in it, 
    # together with the number of requests carrying each one 
    # and the number of boroughs in which each one appears
    print(f"Number of unique labels: {df["ACTI_NOM"].nunique()}")
    labels = df["ACTI_NOM"].value_counts().reset_index(name="occurences")
    labels["percentage"] = labels["occurences"] / len(df)
    labels["cum_pct"] = labels["percentage"].cumsum()
    labels["represented_boroughs"] = labels["ACTI_NOM"].map(lambda name: len(df[df["ACTI_NOM"]==name]["ARRONDISSEMENT_GEO"].unique()))
    print(f"Percentage of total requests that sits in labels that only one or two boroughs use: {labels[labels["represented_boroughs"].astype(int)<3]["percentage"].sum()*100:.2f}%.")

    # Make head and tail
    tail = labels[labels["cum_pct"]>=0.9503]
    tail_sample = tail.sample(n=50, random_state=42)
    head = labels[labels["cum_pct"]<0.9503]

    # Sample double annotation set EQUALLY FOR BOROUGHS and 75-25 for volume representation
    boroughs = df["ARRONDISSEMENT_GEO"].value_counts().reset_index(name="occurences")
    boroughs["labels_head"] = boroughs["ARRONDISSEMENT_GEO"].map( # for every borough, get all unique actions that are in head
        lambda borough: 
            set(df[df["ARRONDISSEMENT_GEO"]==borough]["ACTI_NOM"].unique())
            .intersection(set(head["ACTI_NOM"].unique()))
    )
    boroughs["labels_tail"] = boroughs["ARRONDISSEMENT_GEO"].map( # for every borough, get all unique actions that are in tail
        lambda borough: 
            set(df[df["ARRONDISSEMENT_GEO"]==borough]["ACTI_NOM"].unique())
            .intersection(set(tail_sample["ACTI_NOM"].unique()))
    )

    tail_set = []
    for _, borough in boroughs.iterrows():
        selected = random.sample(sorted(borough["labels_tail"]), 3)
        tail_set.extend(selected)
    tail_set = set(tail_set)

    head_set = []
    for _, borough in boroughs.iterrows():
        selected = random.sample(sorted(borough["labels_head"]), 5)
        head_set.extend(selected)
    head_set = set(head_set)
    unused_head = set(head['ACTI_NOM']) - head_set 
    head_set.update(random.sample(sorted(unused_head), 75 - len(head_set)))

    double_annotation = head_set | tail_set
    print(len(double_annotation))

    # Saving to file
    with open(ANNOTATION_PATH / "double_annotate.txt", "w", encoding="utf-8") as file:
        for element in double_annotation:
            file.write(f"{element}\n")

    # TAKE REMAINING
    head_remaining = set(head["ACTI_NOM"]) - head_set
    tail_remaining = set(tail["ACTI_NOM"]) - tail_set

    boroughs["labels_tail_remaining"] = boroughs["ARRONDISSEMENT_GEO"].map( # for every borough, get all unique actions that are in remaining tail
        lambda borough: 
            set(df[df["ARRONDISSEMENT_GEO"]==borough]["ACTI_NOM"].unique())
            .intersection(tail_remaining)
    )

    tail_set_remaining = []
    for _, borough in boroughs.iterrows():
        selected = random.sample(sorted(borough["labels_tail_remaining"]), 4)
        tail_set_remaining.extend(selected)
    tail_set_remaining = set(tail_set_remaining)
    unused_tail_remaining = tail_remaining - tail_set_remaining 
    tail_set_remaining.update(random.sample(sorted(unused_tail_remaining), 140 - len(head_remaining) - len(tail_set_remaining)))

    open_coding_set = head_remaining | tail_set_remaining
    print(len(open_coding_set))

    # Saving to file
    with open(ANNOTATION_PATH / "open_coding.txt", "w", encoding="utf-8") as file:
        for element in open_coding_set:
            file.write(f"{element}\n")


if __name__ == "__main__":
    main()
