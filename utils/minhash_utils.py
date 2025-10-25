from sklearn.utils import murmurhash3_32
import os


def minhash_signature_weighted(cms, num_hashes, width, depth):
    signatures = []
    for j in range(depth):
        signature = []
        for i in range(num_hashes):
            hash_vals = []
            for elem in range(1, width + 1):
                weight = cms.table[j][elem - 1]
                for k in range(weight):
                    hash_vals.append(murmurhash3_32(f"{elem}_{k}", seed=i))
            
            min_val = min(hash_vals) if hash_vals else 0  # Avoid empty case
            signature.append(min_val)
        signatures.append(signature)
    return signatures


def reduce_signature_size(input_minhash_folder, output_minhash_folder, sz):
    os.makedirs(output_minhash_folder, exist_ok=True)
    for filename in os.listdir(input_minhash_folder):
        if not filename.endswith('.txt'):
            continue
        
        input_path = os.path.join(input_minhash_folder, filename)
        output_path = os.path.join(output_minhash_folder, filename)

        with open(input_path, 'r') as f:
            lines = f.readlines()

        reduced_signature = []
        for line in lines[:]:
            nums = list(map(int, line.strip().split()))
            reduced_signature.append(nums[:sz])

        with open(output_path, 'w') as f:
            for row in reduced_signature:
                f.write(' '.join(map(str, row)) + '\n')


def cms_minhash_jaccard_similarity(sig1, sig2):
    matches = 0
    for j in range(len(sig1)):
        if(sig1[j]==sig2[j]):
            matches+=1
    return matches/len(sig1)
