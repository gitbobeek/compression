import numpy as np


def count_symb(data: bytes) -> np.ndarray:
    counter = np.zeros(256, dtype=int)
    for byte in data:
        counter[byte] += 1

    return counter