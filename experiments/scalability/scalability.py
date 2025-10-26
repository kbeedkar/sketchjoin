import pandas as pd
import os
import argparse
import csv
import random
import pickle
import time
from utils.cms_utils import CountMinSketch, CMS_WIDTH, CMS_DEPTH
from utils.minhash_utils import minhash_signature_weighted, cms_minhash_jaccard_similarity
from utils.utils import HASH_FUNCTIONS_PER_ROW, THRESHOLD, PROBABILITY_OF_ERROR_LSH, TOTAL_HASH_FUNCTIONS
from utils.lsh_utils import find_optimal_bands, build_lsh_index, find_similar_signatures


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

    input_minhash_folder = f'./minhash_signatures/{dataset_name}'

    query_data = pd.read_csv(f'{dataset_path}/{query_file}', header=0, low_memory=False)[query_column].values
    query_cms = CountMinSketch(CMS_WIDTH, CMS_DEPTH)
    for value in query_data:
        if pd.isna(value) or value == "": continue
        else:
            query_cms.add(value)
    
    query_signature = minhash_signature_weighted(query_cms, HASH_FUNCTIONS_PER_ROW, CMS_WIDTH, CMS_DEPTH)

    cms_minhash_lsh_times = []
    sampling_fractions = [0.25,0.5,0.75,1.0]
    total_columns_processed = [0,0,0,0]
    for i, sampling_fraction in enumerate(sampling_fractions):
        cms_minhash_lsh_time = 0
        minhash_signatures = {}

        file_id = 1
        for file in sorted(os.listdir(dataset_path)):
            file_path = os.path.join(dataset_path, file)
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader)

            for column_id, column in enumerate(header, start=1):
                new_id = f"{file_id}_{column_id}"
                if random.random() > sampling_fraction:
                    continue
                total_columns_processed[i] += 1
                file_safe_name = os.path.splitext(os.path.basename(file))[0]
                input_filename = f"{file_safe_name}_{file_id}_{column_id}.txt"
                input_path = os.path.join(input_minhash_folder, input_filename)
                signature_b = []
                with open(input_path, 'r') as f:
                    for line in f:
                        row = list(map(int, line.strip().split()))
                        signature_b.extend(row)

                minhash_signatures[new_id] = signature_b

            file_id += 1

        num_bands = find_optimal_bands(TOTAL_HASH_FUNCTIONS, THRESHOLD, PROBABILITY_OF_ERROR_LSH)
        build_lsh_index(minhash_signatures, num_bands)
        with open(f'lsh_index_{dataset_name}.pkl', 'rb') as f:
            lsh_index = pickle.load(f)
        start_time = time.time()
        candidate_doc_ids = find_similar_signatures(query_signature, num_bands, lsh_index)
        cms_minhash_lsh_time += time.time() - start_time

        for id in candidate_doc_ids:
            start_time = time.time()
            cms_minhash_lsh_jaccard_similarity = cms_minhash_jaccard_similarity(query_signature, minhash_signatures[id])
            cms_minhash_lsh_time += time.time() - start_time

