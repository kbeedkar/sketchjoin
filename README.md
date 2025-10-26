# SketchJoin
## Installation
### Requirements

```pip install numpy pandas scikit-learn pickle```
## Directory Structure 
```
. 
├── preprocessing/ 
│   ├── cms_construction.py        # Build CMS over each dataset column 
│   └── minhash_construction.py    # Generate MinHash signatures over CMS
├── index/
│   ├── lsh_index.py               # Build LSH index 
├── discovery/
│   ├── LinearScan.py              # LinearScan
│   ├── LinearScanSampling.py      # LinearScan with uniform sampling
│   ├── LinearScanEarlystopping.py # LinearScan with earlystopping
│   ├── LinearScanMinhash.py       # LinearScan with minhash sampling
│   └── SketchJoin.py              # SketchJoin
├── utils/
│   ├── cms_utils.py               # CMS utilities
│   ├── minhash_utils.py           # MinHash utilities 
│   ├── utils.py                   # Configuration and general helpers
|   └── lsh_utils.py               # LSH index utilities
├── experiments/
│   ├── run_queries.sh             # script to run multiple queries in parallel for SketchJoin
│   ├── run_scalability.sh         # script to run scalability experiment
|   └── scalability/               # scalability over dataset
|       ├── scalability.py
└── README.md
└──sketchJoin.ipynb

```
## Input Format 
### Dataset Format 
The system expects datasets as dataset CSVs in the following format:
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
python discovery/SketchJoin.py \
    --query_file query.csv \
    --query_column column_name \
    --dataset_path path \
    --dataset_name Name
```
This searches for all columns in the given dataset , having jaccard similarity greater or equal to the threshold set in **utils.py**, to the <column_name> column in query.csv.
## Module Description
**1. Preprocessing Module** <br>

   **preprocessing/cms_construction.py** <br>
  
   Creates CMS sketch (depth × width) over all dataset. Only uses non empty values for CMS construction.
   Usage:
   ```
   python preprocessing/cms_construction.py \
     --dataset_path path \
     --dataset_name name
   ```

  **preprocessing/minhash_construction.py** <br>
  
  Generates weighted minhash signature over CMS. Implements Weighted MinHash: elements with count c are hashed c times.
  **Usage:**
  ```
  python preprocessing/minhash_construction.py \
     --dataset_path path \
     --dataset_name name
 ```
**2. Index Module** <br>
   **index/lsh_index.py** <br>
    Builds LSH index for fast approximate nearest neighbor search. <br>
   Usage
   ```
   python index/lsh_index.py \
    --dataset_path path \
    --dataset_name name
   ```
   
   
**3.Discovery Module** <br>
 **discovery/SketchJoin.py** <br>
 Simulates SketchJoin, given the query dataset and search dataset.<br>
 **Usage:**
 ```
 python discoverySketchJoin.py \
     --query_file query.csv \
     --query_column column_name \
     --dataset_path path \
     --dataset_name name
 ```
**4. Utils Module** <br>
   **utils/cms_utils.py** <br>
   Utilities and parameters for CMS sketch.
   configuration:
   ```
   CMS_WIDTH = 2000  # Number of counters per hash function
   CMS_DEPTH = 5        # Number of hash functions
   ```
   **utils/minhash_utils.py** <br>
   Utility functions for Minhash signature.<br>
   
   **utils/utils.py** <br>

   Global configuration and general helper functions. <br>
   **Configuration Parameters**:<br>

   **utils/lsh_utils.py** <br>
    Utility functions for LSH index construction and band optimization.
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
## Experiments
** Usage: **
   ```
   python experiments/scalability/scalability.py \
     --query_file query.csv \
     --query_column column_name \
     --dataset_path path \
     --dataset_name name
   ```
experiments/run_queries.sh and experiments/run_scalability.sh can be used to run multiple queries in parallel.
