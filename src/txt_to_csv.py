import pandas as pd
from pathlib import Path

DATA_ANNOTATION_PATH = Path(__file__).parent.parent / "data/annotation"

with open(DATA_ANNOTATION_PATH / "double_annotate.txt", "r") as file:
    labels = [line.strip() for line in file]
df = pd.DataFrame(labels, columns=["label"])
df["annotator_1"] = None
df["annotator_2"] = None
df.to_csv(DATA_ANNOTATION_PATH / "double_annotate.csv", index=False)

with open(DATA_ANNOTATION_PATH / "open_coding.txt", "r") as file:
    labels = [line.strip() for line in file]
df = pd.DataFrame(labels, columns=["label"])
df["annotation"] = None
df.to_csv(DATA_ANNOTATION_PATH / "open_coding.csv", index=False)





