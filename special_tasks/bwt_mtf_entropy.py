import matplotlib.pyplot as plt
import numpy as np
from collections import Counter


def bwt_transform(text):
    text = text + "\0"
    rotations = sorted(text[i:] + text[:i] for i in range(len(text)))
    return "".join(row[-1] for row in rotations)


def mtf_encode(data):
    alphabet = list(set(data))
    mtf_result = []

    for symbol in data:
        index = alphabet.index(symbol)
        mtf_result.append(index)
        alphabet.insert(0, alphabet.pop(index))

    return mtf_result


def calculate_entropy(data):
    counter = Counter(data)
    total_symbols = len(data)
    entropy = -sum((count / total_symbols) * np.log2(count / total_symbols) for count in counter.values())
    return entropy


with open("test_files/enwik5.txt", "rb") as f:
    data = f.read()

data_size = len(data)
block_sizes = [2 ** i for i in range(10, 21)]
entropies = []

for block_size in block_sizes:
    block_entropies = []
    for i in range(0, data_size, block_size):
        block = data[i:i + block_size]
        if len(block) < block_size:
            break
        bwt_result = bwt_transform(block.decode(errors='ignore'))
        mtf_result = mtf_encode(bwt_result)
        entropy = calculate_entropy(mtf_result)
        block_entropies.append(entropy)

    entropies.append(np.mean(block_entropies))


plt.figure(figsize=(10, 6))
plt.plot(block_sizes, entropies, marker='o', linestyle='-', color='b')
plt.xscale("log")
plt.xlabel("Размер блока (байты)")
plt.ylabel("Энтропия")
plt.title("Зависимость энтропии от размера блока для BWT+MTF")
plt.grid(True)
plt.show()


optimal_block_size = block_sizes[np.argmin(entropies)]
print(f"Оптимальный размер блока: {optimal_block_size} байт")