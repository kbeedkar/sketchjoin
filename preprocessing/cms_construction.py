import pandas as pd
import os
import argparse
from cms_utils import CountMinSketch, CMS_WIDTH, CMS_DEPTH


def construct_cms_from_dataset(dataset_path, dataset_name):
    output_cms_folder = f"./cms_sketch/{dataset_name}"
    os.makedirs(output_cms_folder, exist_ok=True)

    # Parameters for Count-Min Sketch

    file_id = 1
    for file in sorted(os.listdir(dataset_path)):
        file_path = os.path.join(dataset_path, file)
        try:
            df = pd.read_csv(file_path, header=0, low_memory=False)
            column_id = 1
            for column in df.columns:
                set_b = df[column].values
                cms_b = CountMinSketch(CMS_WIDTH, CMS_DEPTH)
                # Build CMS for column B
                for value in set_b:
                    if pd.isna(value) or value == "":
                        continue
                    cms_b.add(value)
                file_safe_name = os.path.splitext(os.path.basename(file))[0]
                output_filename = f"{file_safe_name}_{file_id}_{column_id}.txt"
                output_path = os.path.join(output_cms_folder, output_filename)

                with open(output_path, 'w') as f:
                    for row in cms_b.table:
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

    construct_cms_from_dataset(dataset_path, dataset_name)