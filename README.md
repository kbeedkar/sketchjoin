# SketchJoin
## Installation
### Requirements

```pip install numpy pandas scikit-learn```
## Directory Structure <br>
``` . <br>
├── preprocessing/ <br>
│   ├── cms_construction.py        # Build CMS for each column <br>
│   └── minhash_construction.py    # Generate MinHash signatures <br>
├── index/
│   ├── lsh_index.py               # Build LSH index <br>
│   └── lsh_utils.py               # LSH utilities <br>
├── discovery/
│   └── LinearScan.py              # Query processing and evaluation <br>
├── utils/
│   ├── cms_utils.py               # CMS implementation <br>
│   ├── minhash_utils.py           # MinHash utilities <br>
│   └── utils.py                   # Configuration and helpers <br>
└── README.md
```
## Input Format 
### Dataset Format 
The system expects datasets as  comma-separated CSVs  in the following format:
``` dataset_folder/
├── file1.csv
├── file2.csv
├── file3.csv
└── ... ```
### Query Format
Query files follow the same CSV format, and we specify the query column via   **-- query_column** parameter.
### Query Command 
```python discovery/LinearScan.py \
    --query_file query.csv \
    --query_column column_name \
    --dataset_path dataset_location \
    --dataset_name Name```
This searches for all columns in the given dataset , having jaccard similarity greater or equal to the threshold set in **utils.py** to the "location" column in query.csv.
# Module Description

