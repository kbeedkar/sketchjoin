import pandas as pd
from collections import Counter
import math
from utils.cms_utils import CMS_DEPTH

ERROR = 0.05
PROBABILITY_OF_ERROR_MINHASH = 0.1
HASH_FUNCTIONS_PER_ROW = (math.ceil((math.log(2/PROBABILITY_OF_ERROR_MINHASH))/(2*ERROR*ERROR))+CMS_DEPTH-1)//CMS_DEPTH
TOTAL_HASH_FUNCTIONS = HASH_FUNCTIONS_PER_ROW * CMS_DEPTH
THRESHOLD = 0.7
PROBABILITY_OF_ERROR_LSH = 0.05

def actual_jaccard_similarity(set_a, set_b):
    set_a = [str(value) for value in set_a if pd.notna(value) and value != ""]
    set_b = [str(value) for value in set_b if pd.notna(value) and value != ""]
    freq_a = Counter(set_a)
    freq_b = Counter(set_b)
    
    intersection_keys = set(freq_a.keys()).intersection(set(freq_b.keys()))
    union_keys = set(freq_a.keys()).union(set(freq_b.keys()))
    
    numerator = sum(min(freq_a[key], freq_b[key]) for key in intersection_keys)
    denominator = sum(max(freq_a.get(key, 0), freq_b.get(key, 0)) for key in union_keys)
    
    return numerator / denominator if denominator > 0 else 0.0