import pandas as pd
from pathlib import Path
from sklearn.metrics import cohen_kappa_score


DATA_ANNOTATION_PATH = Path(__file__).parent.parent / "data/annotation"

df = pd.read_csv(DATA_ANNOTATION_PATH / "double_annotate.csv")

def compute_agreement(annotator1, annotator2, number_of_labels):
    agreement = (annotator1 == annotator2).sum() / number_of_labels * 100
    return agreement

def compute_kappa(annotator1, annotator2):
    kappa = cohen_kappa_score(list(annotator1), list(annotator2))
    return kappa

for task in range(1, 4):
    print(f"Task {task}:")

    if task == 1:
        annotator1 = df["annotator_1_task_1"]
        annotator2 = df["annotator_2_task_1"]
        agreement = compute_agreement(annotator1, annotator2, len(df))
    else:
        filtered_df = df[(df["annotator_1_task_1"] == "IN") & (df["annotator_2_task_1"] == "IN")] # only on labels both annotators placed in scope
        print(f"Number of labels both annotators placed in scope: {len(filtered_df)}")
        annotator1 = filtered_df[f"annotator_1_task_{task}"]
        annotator2 = filtered_df[f"annotator_2_task_{task}"]
        agreement = compute_agreement(annotator1, annotator2, len(filtered_df))

    print(f"Raw agreement rate: {agreement}%")

    kappa = compute_kappa(annotator1, annotator2)
    print(f"Cohen's Kappa: {kappa:.2f}")

    print("\n--------- \n")



"""
Report Cohen’s kappa alongside raw percentage agreement, separately for each of your three annotation dimensions: 
(1) in scope versus out of scope, 
(2) condition versus transaction, and 
(3) topic. 

Compute (2) and (3) only on labels both annotators placed in scope, and report how many labels that is. 
Then report Krippendorff’s alpha for each dimension with a bootstrapped 95 percent confidence interval over at least 1,000 resamples, stating the resampling unit you used and why. 
Report agreement per topic as well as overall, since an acceptable overall figure can conceal one topic on which annotators almost never agree, and that topic is usually the interesting one. 
If agreement is poor, revise the codebook and re-annotate, reporting both rounds; a low kappa you diagnosed and fixed is a stronger result than a high one you cannot explain. 
Adjudicate the disagreements to a gold standard under a written protocol stating who adjudicated, whether they saw the original labels, what rule broke ties, and how many items were resolved by rule rather than by judgment. 
Annotate the remaining labels using single annotation with the finalized codebook.

"""