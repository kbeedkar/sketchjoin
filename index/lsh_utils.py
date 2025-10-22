from collections import defaultdict
import hashlib
import math
import pickle

def hash_band(band):
    return hashlib.md5(str(band).encode()).hexdigest()

def build_lsh_index(signatures_dict, num_bands, dataset_name):
    lsh_index = defaultdict(set)
    for id, signature in signatures_dict.items():
        assert len(signature) % num_bands == 0, "Signature length must be divisible by num_bands"
        num_rows = len(signature) // num_bands
        for band_idx in range(num_bands):
            band = tuple(signature[band_idx*num_rows : (band_idx + 1)*num_rows])
            bucket_key = hash_band(band)
            lsh_index[bucket_key].add(id)

    with open(f'lsh_index_{dataset_name}.pkl', 'wb') as f:
        pickle.dump(lsh_index, f)


def find_optimal_bands(signature_size, threshold, probability_of_error_lsh):
    def get_divisors(signature_size):
        divisors = set()
        for i in range(1, int(signature_size**0.5) + 1):
            if signature_size % i == 0:
                divisors.add(i)
                divisors.add(signature_size // i)
        return sorted(divisors, reverse=True)
    divisors = get_divisors(signature_size)
    optimal_number_bands = signature_size
    for b in divisors:
        r = signature_size // b
        if 1 + (math.log(probability_of_error_lsh) // math.log(1-math.pow(threshold,r))) <= b:
            optimal_number_bands = b
        else:
            break
    return optimal_number_bands
