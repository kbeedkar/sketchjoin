# SketchJoin
## Installation
### Requirements

```pip install numpy pandas scikit-learn```
## Directory Structure 
```
. 
├── preprocessing/ 
│   ├── cms_construction.py        # Build CMS for each column 
│   └── minhash_construction.py    # Generate MinHash signatures 
├── index/
│   ├── lsh_index.py               # Build LSH index 
│   └── lsh_utils.py               # LSH utilities 
├── discovery/
│   └── LinearScan.py              # Query processing and evaluation 
├── utils/
│   ├── cms_utils.py               # CMS implementation 
│   ├── minhash_utils.py           # MinHash utilities 
│   └── utils.py                   # Configuration and helpers 
└── README.md
```
## Input Format 
### Dataset Format 
The system expects datasets as  comma-separated CSVs  in the following format:
 ```
dataset_folder/
├── file1.csv
├── file2.csv
├── file3.csv
└── ...
``` 
### Query Format
Query files follow the same CSV format, and we specify the query column via   **-- query_column** parameter.
### Query Command 
```
python discovery/LinearScan.py \
    --query_file query.csv \
    --query_column column_name \
    --dataset_path dataset_location \
    --dataset_name Name
```
This searches for all columns in the given dataset , having jaccard similarity greater or equal to the threshold set in **utils.py** to the "location" column in query.csv.
## Module Description
1. Preprocessing Module
   ```
   preprocessing/cms_construction.py
   ```
   Reads each CSV file in the dataset directory.For each column, creates a CMS data structure Matrix (depth × width).
   Adds each non-null value to the sketch using multiple hash functions and saves CMS tables to disk as text files.
   Usage:
   ```
   python preprocessing/cms_construction.py \
     --dataset_path ./nyc_cleaned \
     --dataset_name nyc
   ```
  preprocessing/minhash_construction.py
  Reads CMS files created by cms_construction.py.For each CMS row, generates k hash functions.Implements weighted MinHash: elements with count c are hashed c times.Stores minimum hash value for each function and creates signature matrix (depth × k).
  Usage:
  ```
  python preprocessing/minhash_construction.py \
     --dataset_path ./nyc_cleaned \
     --dataset_name nyc
 ```
2. Index Module
   index/lsh_index.py
    Builds Locality-Sensitive Hashing index for fast approximate nearest neighbor search.
   Usage
   ```
   python index/lsh_index.py \
    --dataset_path ./nyc_cleaned/nyc_cleaned \
    --dataset_name nyc
   ```
   index/lsh_utils.py
    Utility functions for LSH index construction and band optimization.
   
   
3.Discovery Module 
discovery/Linearscan.py
Reads query column and builds its CMS nd then Scans all columns in dataset.
Computes both exact Jaccard and CMS-estimated Jaccard
Identifies columns above similarity threshold
Compares CMS results against ground truth
Reports precision, recall, F1, and accuracy
Usage:
```
python discovery/LinearScan.py \
    --query_file query.csv \
    --query_column city \
    --dataset_path ./nyc_cleaned/nyc_cleaned \
    --dataset_name nyc
```
4. Utils Module
   utils/cms_utils.py
   Purpose: Count-Min Sketch implementation and Jaccard similarity estimation.
   configuration:
   ```
   CMS_WIDTH = 2000  # Number of counters per hash function
CMS_DEPTH = 5        # Number of hash functions
```
utils/minhash_utils.py
Purpose: MinHash signature generation and signature size reduction.
5.Utils.py
Global configuration and helper functions.
Configuration Parameters:
```
      
ERROR = 0.05                         # Approximation error bound for MinHash


PROBABILITY_OF_ERROR_MINHASH = 0.1  # Probability of exceeding error bound


THRESHOLD = 0.7                     # Jaccard similarity threshold for retrieval


PROBABILITY_OF_ERROR_LSH = 0.05    # LSH false negative probability

# Computed parameters
CMS_DEPTH = 5  # from cms_utils
HASH_FUNCTIONS_PER_ROW = ⌈log(2/0.1) / (2*0.05²)⌉ / 5
TOTAL_HASH_FUNCTIONS = HASH_FUNCTIONS_PER_ROW × 5
```


