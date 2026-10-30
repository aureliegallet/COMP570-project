import pandas as pd
from pathlib import Path

DATA_ANNOTATION_PATH = Path(__file__).parent.parent / "data/annotation"


with open(DATA_ANNOTATION_PATH / "head_tail.txt", "r") as file:
    labels = [line.strip() for line in file]
df_all = pd.DataFrame(labels, columns=["label"])

with open(DATA_ANNOTATION_PATH / "double_annotate.txt", "r") as file:
    labels = [line.strip() for line in file]
df_double = pd.DataFrame(labels, columns=["label"])

df_single = df_all[~df_all["label"].isin(df_double["label"])] # If we only annotate the head + sampled tail
df_single[["task_1", "task_2", "task_3"]] = [None, None, None]
print(f"Length of single annotation set: {len(df_single)}")
df_single.to_csv(DATA_ANNOTATION_PATH / "single_annotate.csv", index=False)






