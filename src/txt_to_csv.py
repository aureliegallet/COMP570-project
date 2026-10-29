import pandas as pd
from pathlib import Path

DATA_ANNOTATION_PATH = Path(__file__).parent.parent / "data/annotation"

with open(DATA_ANNOTATION_PATH / "double_annotate.txt", "r") as file:
    labels = [line.strip() for line in file]
df = pd.DataFrame(labels, columns=["label"])
df[["annotator_1_task_1", 
    "annotator_2_task_1", 
    "annotator_1_task_2", 
    "annotator_2_task_2", 
    "annotator_1_task_3", 
    "annotator_2_task_3"
    ]] = [None, None, None, None, None, None]
df.to_csv(DATA_ANNOTATION_PATH / "double_annotate.csv", index=False)

with open(DATA_ANNOTATION_PATH / "open_coding.txt", "r") as file:
    labels = [line.strip() for line in file]
df = pd.DataFrame(labels, columns=["label"])
df[["task_1", "task_2", "task_3"]] = [None, None, None]
df.to_csv(DATA_ANNOTATION_PATH / "open_coding.csv", index=False)





