import json
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import argparse

"""
Inputs csv with a label and a topic column.
Finds n words with the highest TF-IDF score for each topic.
"""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', type=str, required=True, help="CSV file with annotations for every label to compute TF-IDF on (must be located in /data/annotation)")
    parser.add_argument('-l', type=str, default='label', help="Label column name. Default: 'label'")
    parser.add_argument('-t', type=str, default='topic', help="Topic column name. Default: 'topic'")
    parser.add_argument('-n', type=int, default=10, help="Number of words to return per topic")
    parser.add_argument('-o', type=str, help="JSON file in which to dump the output (will save in /data/annotation). Prints to terminal if None.")
    args = parser.parse_args()
    
    DATA_ANNOTATION_PATH = Path(__file__).parent.parent / "data/annotation"
    input_file = DATA_ANNOTATION_PATH / args.i

    label_col = args.l
    topic_col = args.t

    df = pd.read_csv(input_file, dtype=str, usecols=[label_col, topic_col])

    topics = df[topic_col].unique()
    documents = []
    for topic in topics:
        topic_subset = df[df[topic_col]==topic]
        document = ' '.join(topic_subset[label_col]).lower()
        documents.append(document)

    tfidf = TfidfVectorizer()
    result = tfidf.fit_transform(documents).toarray()

    feature_names = tfidf.get_feature_names_out()

    idx = (-result).argsort(axis=1)
    top_n = idx[:, :args.n]

    output = {}
    for i, topic in enumerate(topics):
        output[topic] = [feature_names[word_idx] for word_idx in top_n[i]]
    if args.o:
        with open(DATA_ANNOTATION_PATH / args.o, 'w') as f:
            json.dump(output, f)
    else:
        print(output)

if __name__ == "__main__":
    main()