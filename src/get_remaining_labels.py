import pandas as pd
from pathlib import Path

DIRNAME = Path(__file__).parent.parent
RAW_PATH = DIRNAME / "data/raw"
DATA_ANNOTATION_PATH = Path(__file__).parent.parent / "data/annotation"

def main():
    with open(DATA_ANNOTATION_PATH / "head_tail.txt", "r") as file:
        labels = [line.strip() for line in file]
    set_all = set(labels)

    with open(DATA_ANNOTATION_PATH / "double_annotate.txt", "r") as file:
        labels = [line.strip() for line in file]
    set_double = set(labels)

    with open(DATA_ANNOTATION_PATH / "open_coding.txt", "r") as file:
        labels = [line.strip() for line in file]
    set_open = set(labels)

    set_annotated = set_all | set_double | set_open


    processed = []
    chunk_size = 50000
    cols = ['ACTI_NOM']
    reader = pd.read_csv(RAW_PATH / 'requests.csv', usecols=cols, chunksize=chunk_size, dtype=str)
    for chunk in reader:
        processed.append(chunk)

    df = pd.concat(processed, ignore_index=True)

    all_labels = set(df["ACTI_NOM"].unique())
    to_annotate = all_labels - set_annotated
    
    with open(DATA_ANNOTATION_PATH / "rest.txt", "w", encoding="utf-8") as file:
            for element in sorted(to_annotate):
                file.write(f"{element}\n")
if __name__ == "__main__":
    main()