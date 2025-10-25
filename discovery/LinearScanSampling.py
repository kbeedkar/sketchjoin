import numpy as np
import pandas as pd
import os
import argparse
from utils.cms_utils import CountMinSketch, CMS_WIDTH, CMS_DEPTH, CMS_SAMPLE_RATIO, cms_sampling_jaccard_similarity
from utils.utils import actual_jaccard_similarity, THRESHOLD


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--query_file", type=str, required=True, help="Name of the query file")
    parser.add_argument("--query_column", type=str, required=True, help="Name of the query column")
    parser.add_argument("--dataset_path", type=str, default="./nyc_cleaned/nyc_cleaned", help="Path to the dataset without / at the end")
    parser.add_argument("--dataset_name", type=str, default="nyc", help="Name of the dataset")
    args = parser.parse_args()
    
    query_file = args.query_file
    query_column = args.query_column
    dataset_path = args.dataset_path
    dataset_name = args.dataset_name

    input_cms_folder = f"./cms_sketch/{dataset_name}"

    query_data = pd.read_csv(f'{dataset_path}/{query_file}', header=0, low_memory=False)[query_column].values
    query_cms = CountMinSketch(CMS_WIDTH, CMS_DEPTH)
    for value in query_data:
        if pd.isna(value) or value == "": continue
        else:
            query_cms.add(value)

    all_docs_id = []
    actual_doc_id = []
    cms_sampling_doc_id = []

    file_id = 1
    for file in sorted(os.listdir(dataset_path)):
        file_path = os.path.join(dataset_path, file)
        try:
            df = pd.read_csv(file_path, header=0, low_memory=False)
            column_id = 1
            for column in df.columns:
                new_id = f"{file_id}_{column_id}"
                all_docs_id.append(new_id)
                set_b = df[column].values

                #actual dataset jaccard similarity
                actual_jaccard = actual_jaccard_similarity(query_data, set_b)
                if actual_jaccard >= THRESHOLD:
                    actual_doc_id.append(new_id)

                # cms sketch jaccard similarity
                # read cms sketch from file
                cms_b = CountMinSketch(CMS_WIDTH, CMS_DEPTH)
                file_safe_name = os.path.splitext(os.path.basename(file))[0]
                input_filename = f"{file_safe_name}_{file_id}_{column_id}.txt"
                input_path = os.path.join(input_cms_folder, input_filename)

                with open(input_path, 'r') as f:
                    for i, line in enumerate(f):
                        cms_b.table[i] = np.array(list(map(int, line.strip().split())))
                
                # cms sampling jaccard similarity
                cms_sampling_jaccard = cms_sampling_jaccard_similarity(query_cms, cms_b, CMS_DEPTH, CMS_WIDTH, CMS_SAMPLE_RATIO)
                if cms_sampling_jaccard >= THRESHOLD:
                    cms_sampling_doc_id.append(new_id)

                column_id += 1
            file_id += 1
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            file_id += 1
            continue

    print("\nSummary of Results:")
    print("###################################### cms sampling")
    estimated_set = set(cms_sampling_doc_id)
    actual_set = set(actual_doc_id)
    TP = len(estimated_set & actual_set)
    FP = len(estimated_set - actual_set)
    FN = len(actual_set - estimated_set)
    all_doc_ids = set(all_docs_id)
    TN = len(all_doc_ids - (estimated_set | actual_set))

    precision = TP / (TP + FP) if (TP + FP) > 0 else 0.0
    recall = TP / (TP + FN) if (TP + FN) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    accuracy = (TP + TN) / (TP + FP + FN + TN) if (TP + FP + FN + TN) > 0 else 0.0