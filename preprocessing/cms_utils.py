import numpy as np
from sklearn.utils import murmurhash3_32

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

    
def cms_jaccard_similarity(cms_a, cms_b, depth, width):
    numerator = 0
    denominator = 0
    for i in range(depth):
        for j in range(width):
            numerator += min(cms_a.table[i][j], cms_b.table[i][j])
            denominator += max(cms_a.table[i][j], cms_b.table[i][j])
    return numerator / denominator if denominator > 0 else 0.0


def cms_sampling_jaccard_similarity(cms_a, cms_b, depth, width, sampling_ratio):
    numerator = 0
    denominator = 0
    for i in range(depth):
        for j in range(int(sampling_ratio*width)):
            numerator += min(cms_a.table[i][j], cms_b.table[i][j])
            denominator += max(cms_a.table[i][j], cms_b.table[i][j])
    return numerator / denominator if denominator > 0 else 0.0


def cms_earlystopping_jaccard_similarity(cms_a, cms_b, depth, width, threshold1):
        union = 0
        intersection = 0
        for i in range(depth):
            for j in range(int(width * 0.05)):
                union += max(cms_a.table[i][j], cms_b.table[i][j])
                intersection += min(cms_a.table[i][j], cms_b.table[i][j])
        initial_jaccard = intersection / union if union > 0 else 0.0
        if initial_jaccard < threshold1:
            return initial_jaccard
        union = 0
        intersection = 0
        for i in range(depth):
            for j in range(width):
                union += max(cms_a.table[i][j], cms_b.table[i][j])
                intersection += min(cms_a.table[i][j], cms_b.table[i][j])
        
        return intersection / union if union > 0 else 0.0
