import pandas as pd
from pathlib import Path

DIRNAME = Path(__file__).parent.parent
RAW_PATH = DIRNAME / "data/raw"
DATA_ANNOTATION_PATH = Path(__file__).parent.parent / "data/annotation"

def main():
    single_df = pd.read_csv(DATA_ANNOTATION_PATH / 'single_annotate.csv', encoding='utf-8')
    set_single = set(single_df["label"])

    double_df = pd.read_csv(DATA_ANNOTATION_PATH / 'double_annotate.csv', encoding='utf-8')
    set_double = set(double_df["label"])

    open_df = pd.read_csv(DATA_ANNOTATION_PATH / 'open_coding.csv', encoding='utf-8')
    set_open = set(open_df["label"])

    set_annotated = set_single | set_double | set_open

    processed = []
    chunk_size = 50000
    cols = ['ACTI_NOM']
    reader = pd.read_csv(RAW_PATH / 'requests.csv', usecols=cols, chunksize=chunk_size, dtype=str)
    for chunk in reader:
        processed.append(chunk)

    df = pd.concat(processed, ignore_index=True)
    df['ACTI_NOM'] = df['ACTI_NOM'].fillna('').astype(str).str.strip()
    all_labels = set(df[df['ACTI_NOM'] != '']["ACTI_NOM"].unique())
    to_annotate = all_labels - set_annotated
    
    with open(DATA_ANNOTATION_PATH / "rest.txt", "w", encoding="utf-8") as file:
            for element in sorted(to_annotate):
                file.write(f"{element}\n")
if __name__ == "__main__":
    main()