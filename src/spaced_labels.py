from pathlib import Path
import json
import pandas as pd

DATA_PATH = Path(__file__).resolve().parent.parent / "data"

RAW_PATH = DATA_PATH / 'raw'
SPACED_REQUESTS = RAW_PATH / 'requests_space.csv'

LABELLING_PATH = DATA_PATH / "annotation" / "labelling"
ALL_LABELS_PATH = LABELLING_PATH / "all_annotated_labels.csv"

LOOKUP_JSON_PATH = DATA_PATH / "annotation" / "labels_lookup.json"

def main():
    chunk_size = 50_000
    lookup_dict = {}
    reader = pd.read_csv(SPACED_REQUESTS, usecols=["ACTI_NOM"], dtype=str, chunksize=chunk_size)

    for chunk in reader:
        chunk = chunk.dropna(subset=["ACTI_NOM"]).drop_duplicates(subset=["ACTI_NOM"])
        keys = chunk['ACTI_NOM'].str.replace(' ', '', regex=False)
        chunk_dict = dict(zip(keys, chunk['ACTI_NOM']))
        lookup_dict.update(chunk_dict)
    with open(LOOKUP_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(lookup_dict, f, ensure_ascii=False, indent=4)

    df = pd.read_csv(ALL_LABELS_PATH, encoding='utf-8')
    df['label_spaced'] = df['label'].map(lookup_dict)
    df.to_csv(ALL_LABELS_PATH, encoding='utf-8')
    
if __name__ == "__main__":
    main()