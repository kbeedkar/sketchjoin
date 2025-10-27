import numpy as np
from sklearn.utils import murmurhash3_32
import pandas as pd
from collections import Counter
import time
import math
import os


class CountMinSketch:
    def __init__(self, width, depth):
        self.width = width
        self.depth = depth
        self.table = np.zeros((depth, width), dtype=int)
        self.hash_functions = [lambda x, seed=i: murmurhash3_32(str(x), seed=seed) % width for i in range(depth)]
 
    def add(self, key, count=1):
        for i, h in enumerate(self.hash_functions):
            self.table[i][h(key)] += count
 
    def query(self, key):
        return min(self.table[i][h(key)] for i, h in enumerate(self.hash_functions))
   
    def max_union(self, other):
        assert self.width == other.width and self.depth == other.depth
        total = 0
        for i in range(self.depth):
            for j in range(self.width):
                total += max(self.table[i][j], other.table[i][j])
        return total
 
    def min_intersection(self, other):
        assert self.width == other.width and self.depth == other.depth
        total = 0
        for i in range(self.depth):
            for j in range(self.width):
                total += min(self.table[i][j], other.table[i][j])
        return total
    def intersection_union(self, other):
        assert self.width == other.width and self.depth == other.depth
        total_intersection = 0
        total_union = 0
        union =0
       
        arr1 = np.ascontiguousarray(self.table.ravel())
        arr2 = np.ascontiguousarray(other.table.ravel())
        time1 = time.time()
        for i in range(len(arr1)):
            a = arr1[i]
            b = arr2[i]
            if a < b:
                total_intersection += a
            else:
                total_intersection += b
        time2 = time.time() - time1
        time2=f"{time2:.6f}"
        total_union = self.depth*(size)-total_intersection
        return total_intersection ,total_union ,time2

def weighted_jaccard_similarity(cms_a, cms_b):

    numerator , denominator ,time1= cms_a.intersection_union(cms_b)
    print(f"Weighted Jaccard similarity: {numerator} / {denominator} ")
    return numerator / denominator if denominator > 0 else 0.0 , time1

def minhash_signature_weighted(counts, num_hashes):
   
    signature = []
    for i in range(num_hashes):
        hash_vals = []
        for elem, weight in counts.items():
            if pd.isna(elem) or elem == "":
                continue
            for j in range(weight):
                hash_vals.append(murmurhash3_32(f"{elem}_{j}", seed=i))
        min_val = min(hash_vals) if hash_vals else float("inf")
        signature.append(min_val)
    return signature
 
def estimate_jaccard(sig1, sig2):
    matches =0
   
    sig1 = np.ascontiguousarray(sig1)
    sig2 = np.ascontiguousarray(sig2)
    time1=time.time()
    for i in range(len(sig1)):
        a=sig1[i]
        b=sig2[i]
        if a == b:
            matches += 1
     
    time2=time.time()-time1
    time2=f"{time2:.6f}"
    print(f"MinHash Jaccard similarity: {matches} / {len(sig1)} : jaccard = {matches / len(sig1)}")
    return matches / len(sig1) ,time2

def calculate_size(cms):
    count=0
    for i in range(cms.depth):
        for j in range(cms.width):
            if cms.table[i][j] > 0:
                count += 1
    zeroes = cms.depth * cms.width - count
    bits= zeroes + count *4 *8  # Assuming each count is 4 bytes
    no_bytes= math.ceil(bits / 8)
    return  no_bytes # Assuming each count is 4 bytes
def actual_jaccard_similarity(set_a, set_b):
    set_a = [value for value in set_a if pd.notna(value) and value != ""]
    set_b = [value for value in set_b if pd.notna(value) and value != ""]
    freq_a = Counter(set_a)
    freq_b = Counter(set_b)
   
    union_keys = set(freq_a.keys()).union(set(freq_b.keys()))
   
    numerator = sum(min(freq_a.get(key,0), freq_b.get(key,0)) for key in union_keys)
    denominator = sum(max(freq_a.get(key, 0), freq_b.get(key, 0)) for key in union_keys)
   
    return numerator / denominator if denominator > 0 else 0.0
 
def read_data(filename,query_column):
    query_data = pd.read_csv(filename, low_memory=False,header=0)[query_column].values
    return query_data
# --------------------------------------------------Main Code--------------------------------------------------------------------------
minhash_error=[]
cms_error=[]
num_minhashes=[50,100,200,300,400,500,600,700,800,900,1000,1100,1200,1300,1400,1500,1600,1700,1800,1900,2000]
num_cms_hashes=[(25,2),(50,2),(100,2),(150,2),(200,2),(250,2),(300,2),(350,2),(400,2),(450,2),(500,2),(550,2),(600,2),(650,2),(700,2),(750,2),(800,2),(850,2),(900,2),(950,2),(1000,2)]

file1="file1.csv" 
column1="column1"
data1 = read_data(file1,column1)
file2="file2.csv" 
column2="column2"
data2 = read_data(file2,column2)

size= 0
actual_jaccard=actual_jaccard_similarity(data1, data2)
print(f"Actual Jaccard similarity: {actual_jaccard}") 
estimated_errors=[]
size_minhash=[]
size_cms=[]
time_minhash=[]
results=[]
# ----------------------------------------------------------------------------minhash--------------------------------------------------------------------------
for i in range(0, len(num_minhashes)):
    ms1 = minhash_signature_weighted(Counter(data1), num_minhashes[i])
    ms2 = minhash_signature_weighted(Counter(data2), num_minhashes[i])
    
    minhash_estimate_jaccard,minhash_time=estimate_jaccard(ms1, ms2)
    results.append({

        "method": "MinHash",
        "minhash_depth": num_minhashes[i],
        "cms_width": None,
        "cms_depth": None,
        "size_minhash": num_minhashes[i]*4,  # Assuming each hash is 4 bytes
        "size_cms": None,
        "time_minhash": minhash_time,
        "time_cms": None,
        "error_minhash": abs(minhash_estimate_jaccard - actual_jaccard),
        "error_cms": None,
        "jaccard_similarity": actual_jaccard
 })
    
    

# ----------------------------------------------------------------------------CountMinSketch--------------------------------------------------------------------------
time_cms=[]

for i in range(len(num_cms_hashes)):  
    size=0

    cms_1 = CountMinSketch(num_cms_hashes[i][0], num_cms_hashes[i][1])
    cms_2 = CountMinSketch(num_cms_hashes[i][0], num_cms_hashes[i][1])
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
        "cms_width": num_cms_hashes[i][0],
        "cms_depth": num_cms_hashes[i][1],
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
