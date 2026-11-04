from pathlib import Path
import pandas as pd


LABELLING_PATH = Path(__file__).resolve().parent.parent / "data" / "annotation" / "labelling"
OUTPUT_NAME = "all_annotated_labels.csv"
FILES = [
    "double_annotation_merge_r2_arbitrated.csv",
    "open_coding_second_iteration.csv",
    "single_annotation.csv",
    "rest_gpt_annotated.csv",
]

def main():
    is_first_file = True
    df_list = []
    for file in FILES:
        df = pd.read_csv(LABELLING_PATH / file, encoding='utf-8')
        if is_first_file:
            df.rename(columns={'adjudicator_ruling_task_1': 'task_1', 'adjudicator_ruling_task_2': 'task_2', 'adjudicator_ruling_task_3': 'task_3'}, inplace=True)
            df = df[['label', 'task_1', 'task_2', 'task_3']]
            is_first_file = False
        df_list.append(df)
    output = pd.concat(df_list, ignore_index=True)
    output.to_csv(LABELLING_PATH / OUTPUT_NAME, encoding='utf-8', index=False)
if __name__ == "__main__":
    main()