import pandas as pd
import os
import argparse
from utils.cms_utils import CountMinSketch, CMS_WIDTH, CMS_DEPTH
from utils.minhash_utils import cms_minhash_jaccard_similarity, minhash_signature_weighted
from utils.lsh_utils import find_similar_signatures, find_optimal_bands
from utils.utils import actual_jaccard_similarity, THRESHOLD, HASH_FUNCTIONS_PER_ROW, TOTAL_HASH_FUNCTIONS, PROBABILITY_OF_ERROR_LSH
import pickle


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

    input_minhash_folder = f"./minhash_signatures/{dataset_name}"

    query_data = pd.read_csv(f'{dataset_path}/{query_file}', header=0, low_memory=False)[query_column].values
    query_cms = CountMinSketch(CMS_WIDTH, CMS_DEPTH)
    for value in query_data:
        if pd.isna(value) or value == "": continue
        else:
            query_cms.add(value)

    query_signature = minhash_signature_weighted(query_cms, HASH_FUNCTIONS_PER_ROW, CMS_WIDTH, CMS_DEPTH)

    all_docs_id = []
    actual_doc_id = []
    cms_minhash_lsh_doc_id = []

    minhash_signatures = {}
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
                
                # cms minhash jaccard similarity
                # read minhash signatures from file
                file_safe_name = os.path.splitext(os.path.basename(file))[0]
                input_filename = f"{file_safe_name}_{file_id}_{column_id}.txt"
                input_path = os.path.join(input_minhash_folder, input_filename)

                signature_b = []
                with open(input_path, 'r') as f:
                    for line in f:
                        row = list(map(int, line.strip().split()))
                        signature_b.extend(row)

                minhash_signatures[new_id] = signature_b
                column_id += 1
            file_id += 1
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            file_id += 1
            continue

    with open(f'lsh_index_{dataset_name}.pkl', 'rb') as f:
        lsh_index = pickle.load(f)
    num_bands = find_optimal_bands(TOTAL_HASH_FUNCTIONS, THRESHOLD, PROBABILITY_OF_ERROR_LSH)
    candidate_doc_ids = find_similar_signatures(query_signature, num_bands, lsh_index)
    for id in candidate_doc_ids:
        estimated_jaccard_similarity = cms_minhash_jaccard_similarity(query_signature, minhash_signatures[id])
        if estimated_jaccard_similarity > THRESHOLD:
            cms_minhash_lsh_doc_id.append(id)

    print("\nSummary of Results:")
    print("###################################### sketchjoin")
    estimated_set = set(cms_minhash_lsh_doc_id)
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
    print (f"True Positives: {TP}")
    print (f"False Positives: {FP}")    
    print (f"False Negatives: {FN}")
    print (f"True Negatives: {TN}")
    print (f"Precision: {precision:.6f}")
    print (f"Recall: {recall:.6f}")
    print (f"F1 Score: {f1:.6f}")
    print (f"Accuracy: {accuracy:.6f}")
