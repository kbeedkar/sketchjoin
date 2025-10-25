import os
import argparse
import csv
from utils.lsh_utils import build_lsh_index, find_optimal_bands
from utils.utils import TOTAL_HASH_FUNCTIONS, PROBABILITY_OF_ERROR_LSH, THRESHOLD


def create_lsh_index(total_hash_functions, dataset_name, probability_of_error_lsh, threshold):
    input_folder_minhash = f'minhash_signatures/{dataset_name}'
    minhash_signatures = {}
    file_id = 1
    for file in sorted(os.listdir(dataset_path)):
        file_path = os.path.join(dataset_path, file)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader)
            if header is not None:
                num_columns = len(header)
            else:
                num_columns = 0
            for column_id in range(1, num_columns + 1):
                new_id = f"{file_id}_{column_id}"

                file_safe_name = os.path.splitext(os.path.basename(file))[0]
                input_filename = f"{file_safe_name}_{file_id}_{column_id}.txt"

                # read minhash signatures from file
                input_path = os.path.join(input_folder_minhash, input_filename)
                signature = []
                with open(input_path, 'r') as f:
                    for line in f:
                        row = list(map(int, line.strip().split()))
                        signature.extend(row)
                
                #store minhash signatures in a dict to build lsh index
                minhash_signatures[new_id] = signature
            file_id += 1
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            file_id += 1
            continue

    num_bands = find_optimal_bands(total_hash_functions, threshold, probability_of_error_lsh)
    build_lsh_index(minhash_signatures, num_bands)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset_path", type=str, default="./nyc_cleaned/nyc_cleaned", help="Path to the dataset without / at the end")
    parser.add_argument("--dataset_name", type=str, default="nyc", help="Name of the dataset")
    args = parser.parse_args()

    dataset_path = args.dataset_path
    dataset_name = args.dataset_name

    create_lsh_index(TOTAL_HASH_FUNCTIONS, dataset_name, PROBABILITY_OF_ERROR_LSH, THRESHOLD)