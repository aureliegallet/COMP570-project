from pathlib import Path
import pandas as pd
import argparse

DATA_PATH = Path(__file__).parent.parent / "data"
DATA_ANNOTATION_PATH = DATA_PATH / "annotation"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', type=str, required=True, help="CSV file with annotations for every label (must be located in /data/annotation)")
    parser.add_argument('-i', type=str, required=True, help="CSV file with 311 requests (must be located in /data)")
    parser.add_argument('-l', type=str, default='label', help="Label column name. Default: 'label'")
    parser.add_argument('-t', type=str, nargs='+', default=['task_1'], help="Annotation column names. Default: 'task_1'")
    parser.add_argument('-o', type=str, required=True, help="CSV output file for annotated 311 requests (will save in /data/annotation)")
    args = parser.parse_args()

    label_col = args.l
    topic_col = args.t
    input_file = DATA_PATH / args.i
    output_file = DATA_ANNOTATION_PATH / args.o
    annotations_file = DATA_ANNOTATION_PATH / args.a
    annotations = pd.read_csv(annotations_file, dtype=str)
    
    processed = []
    chunk_size = 50000
    reader = pd.read_csv(input_file, chunksize=chunk_size, dtype=str)
    is_first_chunk = True
    for chunk in reader:
        chunk.rename(columns={"ACTI_NOM": label_col}, inplace=True)
        for topic in topic_col:
            topic_lookup = dict(zip(annotations[label_col], annotations[topic]))
            chunk[topic] = chunk[label_col].map(topic_lookup)
        chunk.to_csv(output_file, mode='a', index=False, header=is_first_chunk)
        is_first_chunk = False

    
if __name__ == "__main__":
    main()