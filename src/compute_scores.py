import sys
import krippendorff 
import pandas as pd
from pathlib import Path
from sklearn.metrics import cohen_kappa_score
import argparse

"""
Report Cohen’s kappa alongside raw percentage agreement, separately for each of your three annotation dimensions: 
(1) in scope versus out of scope, 
(2) condition versus transaction, and 
(3) topic. 

Compute (2) and (3) only on labels both annotators placed in scope, and report how many labels that is. 
Then report Krippendorff’s alpha for each dimension with a bootstrapped 95 percent confidence interval over at least 1,000 resamples, stating the resampling unit you used and why. 
Report agreement per topic as well as overall, since an acceptable overall figure can conceal one topic on which annotators almost never agree, and that topic is usually the interesting one. 
"""

def compute_agreement(annotator1, annotator2, number_of_labels):
    agreement = (annotator1 == annotator2).sum() / number_of_labels * 100
    return agreement

def compute_kappa(annotator1, annotator2):
    kappa = cohen_kappa_score(list(annotator1), list(annotator2))
    return kappa

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', type=str, default="double_annotation_merge_adjudicated.csv", help="CSV file to compute scores on (must be located in /data/annotation/labelling)")
    parser.add_argument('-o', type=str, help="TXT file to save scores in (will save in /data/annotation)")
    parser.add_argument('-a1', default="annotator_1", type=str, help="Annotator 1 prefix. default: annotator_1")
    parser.add_argument('-a2', default="annotator_2", type=str, help="Annotator 1 prefix. default: annotator_2")
    args = parser.parse_args()

    DATA_ANNOTATION_PATH = Path(__file__).parent.parent / "data/annotation"
    
    if args.o:
        file_output = open(DATA_ANNOTATION_PATH / args.o, 'w')
        sys.stdout = file_output
    else:
        file_output = None

    df = pd.read_csv(DATA_ANNOTATION_PATH / 'labelling' / args.i)
    annotator1_prefix = args.a1
    annotator2_prefix = args.a2

    try:
        for task in range(1, 4):
            print(f"Task {task}:")
            if task == 1:
                annotator1 = df[f"{annotator1_prefix}_task_1"]
                annotator2 = df[f"{annotator2_prefix}_task_1"]
                agreement = compute_agreement(annotator1, annotator2, len(df))
            else:
                filtered_df = df[(df[f"{annotator1_prefix}_task_1"] == "IN") & (df[f"{annotator2_prefix}_task_1"] == "IN")] # only on labels both annotators placed in scope
                print(f"Number of labels both annotators placed in scope: {len(filtered_df)}")
                annotator1 = filtered_df[f"{annotator1_prefix}_task_{task}"]
                annotator2 = filtered_df[f"{annotator2_prefix}_task_{task}"]
                agreement = compute_agreement(annotator1, annotator2, len(filtered_df))

            print(f"Raw agreement rate: {agreement}%")

            kappa = compute_kappa(annotator1, annotator2)
            print(f"Cohen's Kappa: {kappa:.2f}")

            # https://github.com/pln-fing-udelar/fast-krippendorff
            krippen_data = [list(annotator1), list(annotator2)]
            res = krippendorff.bootstrap_ci(
                reliability_data=krippen_data,
                level_of_measurement="nominal",
                confidence_level=0.95,
                n_resamples=10000,
                random_state=42
            ) 
            print(f"Alpha: {res.alpha:.3f}")
            print(f"95% CI: [{res.ci_low:.3f}, {res.ci_high:.3f}]")
            print(f"Standard Error: {res.standard_error:.4f}\n")

            if task == 3:
                topics = list(filtered_df["adjudicator_ruling_task_3"].unique())
                for topic in topics:
                    topic_df = filtered_df[filtered_df["adjudicator_ruling_task_3"]==topic]
                    annotator1 = topic_df[f"{annotator1_prefix}_task_3"]
                    annotator2 = topic_df[f"{annotator2_prefix}_task_3"]
                    agreement = compute_agreement(annotator1, annotator2, len(topic_df))
                    print(topic)
                    print(f"Raw agreement rate: {agreement}% ({len(topic_df)} labels)")    

                    try: 
                        kappa = compute_kappa(annotator1, annotator2)
                        print(f"Cohen's Kappa: {kappa:.2f}")  
                    except: 
                        print(f"Error for Cohen's Kappa") 

                    try:
                        krippen_data = [list(annotator1), list(annotator2)]
                        res = krippendorff.bootstrap_ci(
                            reliability_data=krippen_data,
                            level_of_measurement="nominal",
                            confidence_level=0.95,
                            n_resamples=10000,
                            random_state=42
                        ) 
                        print(f"Alpha: {res.alpha:.3f}")
                        print(f"95% CI: [{res.ci_low:.3f}, {res.ci_high:.3f}]")
                        print(f"Standard Error: {res.standard_error:.4f}\n")     
                    except: 
                        print(f"Error for Krippendorff's Alpha\n")
            print("\n--------- \n")
    finally:
        if file_output:
            file_output.close()
            sys.stdout = sys.__stdout__

if __name__ == "__main__":
    main()

    

