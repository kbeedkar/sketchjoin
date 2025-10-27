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
  
    def intersection_union(self, other,size):
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
def weighted_jaccard_similarity(cms_a, cms_b,size):

    numerator , denominator ,time1= cms_a.intersection_union(cms_b,size)
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
 
