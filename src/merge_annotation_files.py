from pathlib import Path
import pandas as pd


LABELLING_PATH = Path(__file__).resolve().parent.parent / "data" / "annotation" / "labelling"
OUTPUT_NAME = "all_annotated_labels.csv"
ANON_OUTPUT_NAME = "all_annotated_labels_anon.csv"
FILES = [
    "double_annotation_merge_r2_arbitrated.csv",
    "open_coding_second_iteration.csv",
    "single_annotation.csv",
    "rest_gpt_annotated.csv",
]
TOPIC_MAP = {
    'traffic engineering / parking': 'topic_1',
    'maintenance / city works': 'topic_2',
    'sanitation / cleanliness': 'topic_3',
    'quieteness / living comfort': 'topic_4',
    'transaction': 'topic_5',
    'other': 'topic_6',
}
def main():
    i=0
    df_list = []
    for file in FILES:
        df = pd.read_csv(LABELLING_PATH / file, encoding='utf-8')
        if i==0:
            df['annotator'] = "double annotated by Andrew and Aurélie, adjudicated by Harry"
            df['from_double_annotation'] = True
            df['adjudicator_ruling_task_3'] = df['adjudicator_ruling_task_3'].str.lower()
            df['annotator_1_task_3'] = df['annotator_1_task_3'].str.lower()
            df['annotator_2_task_3'] = df['annotator_2_task_3'].str.lower()
        else:
            if i==1:
                df['annotator'] = "Harry"
            elif i==2:
                df['annotator'] = "Andrew"
            else:
                df['annotator'] = "ChatGPT"
            df['from_double_annotation'] = False
            df['task_3'] = df['task_3'].str.lower()
            df['task_3_anon'] = df['task_3'].map(TOPIC_MAP)
        df['set'] = file.split('_')[0]
        df_list.append(df)
        i += 1
    output = pd.concat(df_list, ignore_index=True)
    output_anon = output.drop(columns="task_3") 
    output_anon.rename(columns={"task_3_anon": "task_3"})
    output = output.drop(columns="task_3_anon")
    output.to_csv(LABELLING_PATH / OUTPUT_NAME, encoding='utf-8', index=False)
    output_anon.to_csv(LABELLING_PATH / ANON_OUTPUT_NAME, encoding='utf-8', index=False)
if __name__ == "__main__":
    main()