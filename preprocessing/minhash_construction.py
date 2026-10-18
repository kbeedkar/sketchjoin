import os
import argparse
import numpy as np
import pandas as pd
import tmh_pybind
from utils.cms_utils import CountMinSketch, CMS_DEPTH, CMS_WIDTH
from utils.utils import TOTAL_HASH_FUNCTIONS


def construct_minhash_over_cms(dataset_path, dataset_name):
    input_cms_folder = f"./cms_sketch/{dataset_name}"
    output_minhash_folder = f"./minhash_signatures/{dataset_name}"
    os.makedirs(output_minhash_folder, exist_ok=True)
    file_id = 1
    for file in sorted(os.listdir(dataset_path)):
        file_path = os.path.join(dataset_path, file)
        try:
            df = pd.read_csv(file_path, header=0, low_memory=False)
            column_id = 1
            for column in df.columns:
                cms = CountMinSketch(CMS_WIDTH, CMS_DEPTH)
                file_safe_name = os.path.splitext(os.path.basename(file))[0]
                input_filename = f"{file_safe_name}_{file_id}_{column_id}.txt"
                input_path = os.path.join(input_cms_folder, input_filename)
                with open(input_path, 'r') as f:
                    for i, line in enumerate(f):
                        cms.table[i] = np.array(list(map(int, line.strip().split())))
                signature_b = tmh_pybind.build_signature_from_cms(
                    cms.table, num_hashes=TOTAL_HASH_FUNCTIONS
                )
                output_filename = input_filename
                output_path = os.path.join(output_minhash_folder, output_filename)
                with open(output_path, 'w') as f:
                    for hash_id , val in signature_b:
                        f.write(f"{hash_id}\n")

                column_id += 1
            file_id += 1
        except Exception as e:
            file_id += 1
            continue


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset_path", type=str, default="./nyc_cleaned",
                        help="Path to the dataset without / at the end")
    parser.add_argument("--dataset_name", type=str, default="nyc",
                        help="Name of the dataset")
    args = parser.parse_args()
    print("total hash functions",TOTAL_HASH_FUNCTIONS)
    construct_minhash_over_cms(args.dataset_path, args.dataset_name)