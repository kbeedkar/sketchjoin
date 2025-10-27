import argparse
import pandas as pd
from collections import Counter
import os
from utils.utils import actual_jaccard_similarity 
from utils.minhash_vs_cms_utils import (
    CountMinSketch,
    weighted_jaccard_similarity,
    minhash_signature_weighted,
    estimate_jaccard,
    calculate_size
    
)
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare CMS and MinHash performance")
    parser.add_argument("--file1", type=str, required=True, help="Path to first CSV file")
    parser.add_argument("--column1", type=str, required=True, help="Column name in first file")
    parser.add_argument("--file2", type=str, required=True, help="Path to second CSV file")
    parser.add_argument("--column2", type=str, required=True, help="Column name in second file")
    parser.add_argument("--output", type=str, default="results.csv", help="Output results file")
    args = parser.parse_args()

    data1 = pd.read_csv(args.file1, low_memory=False)[args.col1].values
    data2 = pd.read_csv(args.file2, low_memory=False)[args.col2].values
    
    minhash_configs=[50,100,200,300,400,500,600,700,800,900,1000,1100,1200,1300,1400,1500,1600,1700,1800,1900,2000]
    cms_configs=[(25,2),(50,2),(100,2),(150,2),(200,2),(250,2),(300,2),(350,2),(400,2),(450,2),(500,2),(550,2),(600,2),(650,2),(700,2),(750,2),(800,2),(850,2),(900,2),(950,2),(1000,2)]
    size= 0
    actual_jaccard=actual_jaccard_similarity(data1, data2)
    size_minhash=[]
    size_cms=[]
    time_minhash=[]  
    time_cms=[]
    results=[]
    
    for i in range(0, len(minhash_configs)):
        ms1 = minhash_signature_weighted(Counter(data1), minhash_configs[i])
        ms2 = minhash_signature_weighted(Counter(data2), minhash_configs[i])
        
        minhash_estimate_jaccard,minhash_time=estimate_jaccard(ms1, ms2)
        results.append({

            "method": "MinHash",
            "minhash_depth": minhash_configs[i],
            "cms_width": None,
            "cms_depth": None,
            "size_minhash": minhash_configs[i]*4,  # Assuming each hash is 4 bytes
            "size_cms": None,
            "time_minhash": minhash_time,
            "time_cms": None,
            "error_minhash": abs(minhash_estimate_jaccard - actual_jaccard),
            "error_cms": None,
            "jaccard_similarity": actual_jaccard
    })
        
        

   
  

    for i in range(len(cms_configs)):  
        size=0

        cms_1 = CountMinSketch(cms_configs[i][0], cms_configs[i][1])
        cms_2 = CountMinSketch(cms_configs[i][0], cms_configs[i][1])
        for item in data1:
            if pd.isna(item) or item == "":
                continue
            size+=1
            cms_1.add(item)
        for item in data2:
            if pd.isna(item) or item == "":
                continue
            size+=1
            cms_2.add(item)
        print(size)
        cms_weighted_jaccard , time2=weighted_jaccard_similarity( cms_1, cms_2)
        results.append({

            "method": "CountMinSketch",
            "minhash_depth": None,
            "cms_width": cms_configs[i][0],
            "cms_depth": cms_configs[i][1],
            "size_minhash": None,
            "size_cms": max(calculate_size(cms_1),calculate_size(cms_2)),
            "time_minhash": None,
            "time_cms": time2,
            "error_minhash": None,
            "error_cms": abs(cms_weighted_jaccard - actual_jaccard),
            "jaccard_similarity": actual_jaccard
    })
        
    filename="results.csv"

    df = pd.DataFrame(columns=[ "method","minhash_depth","cms_width", "cms_depth","size_minhash", "size_cms" ,"time_minhash","time_cms","error_minhash","error_cms","jaccard_similarity"])
    df=pd.DataFrame(results)
    df.to_csv(filename, index=False)