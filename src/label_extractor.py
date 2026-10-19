import pandas as pd
import os.path

dirname = os.path.dirname(__file__)
raw_path = os.path.join(dirname, '..', 'data', 'raw')
annotation_path = os.path.join(dirname, '..', 'data', 'annotation')

chunk_size = 50000
cols = ['ACTI_NOM', 'ARRONDISSEMENT', 'ARRONDISSEMENT_GEO']
reader = pd.read_csv(os.path.join(raw_path, 'requests.csv'), usecols=cols, chunksize=chunk_size, dtype=str)

processed = []

for chunk in reader:
    processed.append(chunk)

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

df = pd.concat(processed, ignore_index=True)
df["ARRONDISSEMENT_GEO"] = df["ARRONDISSEMENT_GEO"].fillna(df["ARRONDISSEMENT"])
df = df[~df["ARRONDISSEMENT_GEO"].isna()]
df.drop(columns=["ARRONDISSEMENT"])
df = df[df["ARRONDISSEMENT_GEO"].isin(BOROUGHS)]
cum_pct = df["ACTI_NOM"].value_counts().cumsum() / df["ACTI_NOM"].value_counts().sum()
labels = cum_pct#[cum_pct<0.9503]
labels = pd.DataFrame({'ACTI_NOM':labels.index, 'cum_pct':labels.values})
labels["occurences"] = labels["ACTI_NOM"].map(lambda name: df["ACTI_NOM"].value_counts()[name])
labels["percentage"] = labels["occurences"] / df["ACTI_NOM"].value_counts().sum()

labels["represented_boroughs"] = labels["ACTI_NOM"].map(lambda name: len(df[df["ACTI_NOM"]==name]["ARRONDISSEMENT_GEO"].unique()))


print("Percentage of total requests that sits in labels that only one or two boroughs use: ", labels[labels["represented_boroughs"].astype(int)<3]["percentage"].sum()*100)
tail = labels[labels["cum_pct"]>=0.9503].sample(n=50, random_state=42)
head = labels[labels["cum_pct"]<0.9503]

head_double_annot = head.sample(n=75, random_state=41)
tail_double_annot = tail.sample(n=25, random_state=41)
to_double_annotate = pd.concat((head_double_annot, tail_double_annot))

to_double_annotate.to_csv(os.path.join(annotation_path, "double_annotate.csv"))

head_rest = head[~head.index.isin(head_double_annot.index)]
tail_rest = tail[~tail.index.isin(tail_double_annot.index)]

open_code = pd.concat((head_open_code, tail_open_code))
open_code.to_csv(os.path.join(annotation_path, "open_code.csv"))