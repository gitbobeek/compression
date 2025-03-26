from count_symb import count_symb
import math

def calculate_entropy(data: bytes) -> float:
    counter = count_symb(data)
    total_symbols = len(data)
    entropy = 0.0

    for count in counter:
        if count > 0:
            probability = count / total_symbols
            entropy -= probability * math.log2(probability)

    return entropy