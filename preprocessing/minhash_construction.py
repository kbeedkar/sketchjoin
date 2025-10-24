import numpy as np
import pandas as pd
import math
import os
import argparse
from utils.minhash_utils import minhash_signature_weighted
from utils.cms_utils import CountMinSketch, CMS_DEPTH, CMS_WIDTH
from utils.utils import HASH_FUNCTIONS_PER_ROW


def construct_minhash_over_cms(dataset_path, dataset_name):
    input_cms_folder = f'./cms_sketch/{dataset_name}'
    output_minhash_folder = f'./minhash_signatures/{dataset_name}'
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

                signature_b = minhash_signature_weighted(cms, HASH_FUNCTIONS_PER_ROW, CMS_WIDTH, CMS_DEPTH)

                output_filename = input_filename
                output_path = os.path.join(output_minhash_folder, output_filename)
                with open(output_path, 'w') as f:
                    for row in signature_b:
                        f.write(" ".join(map(str, row)) + "\n")

                column_id += 1
            file_id += 1
        except Exception as e:
            file_id += 1
            continue


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset_path", type=str, default="./nyc_cleaned", help="Path to the dataset without / at the end")
    parser.add_argument("--dataset_name", type=str, default="nyc", help="Name of the dataset")
    args = parser.parse_args()

    dataset_path = args.dataset_path
    dataset_name = args.dataset_name

    construct_minhash_over_cms(dataset_path, dataset_name)
