import matplotlib.pyplot as plt
import numpy as np
import sys
import time

def print_progress(iteration: int, total: int, prefix: str = '', suffix: str = '', length: int = 50, fill: str = '█'):
    percent = f"{100 * (iteration / float(total)):.1f}"
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    sys.stdout.write(f'\r{prefix} |{bar}| {percent}% {suffix}')
    sys.stdout.flush()
    if iteration == total:
        print()

def lz77_compress(data: bytes, buffer_size: int = 1024, max_length: int = 255, show_progress: bool = False) -> bytes:
    encoded_data = bytearray()
    i = 0
    n = len(data)
    last_update = 0

    while i < n:
        if show_progress and time.time() - last_update > 0.1:
            print_progress(i, n, prefix='Прогресс:', suffix=f'Обработано {i}/{n} байт')
            last_update = time.time()

        search_start = max(0, i - buffer_size)
        search_end = i
        max_match_length = 0
        best_offset = 0

        max_possible_length = min(max_length, n - i)
        lookahead = min(4, max_possible_length)
        substring_start = data[i:i + lookahead]

        pos = data.rfind(substring_start, search_start, search_end)

        if pos != -1:
            offset = search_end - pos
            match_length = lookahead

            while (match_length < max_possible_length and
                   i + match_length < n and
                   data[pos + (match_length % (search_end - pos))] == data[i + match_length]):
                match_length += 1

            if match_length > max_match_length:
                max_match_length = match_length
                best_offset = offset

        if max_match_length > 0:
            encoded_data.append((best_offset >> 8) & 0xFF)
            encoded_data.append(best_offset & 0xFF)
            encoded_data.append((max_match_length >> 8) & 0xFF)
            encoded_data.append(max_match_length & 0xFF)
            i += max_match_length
        else:
            encoded_data.extend([0, 0, 0, 0])
            encoded_data.append(data[i])
            i += 1

    return bytes(encoded_data)

def calculate_compression_ratio(original_size, compressed_size):
    return original_size / compressed_size if compressed_size > 0 else float('inf')


with open("../test_files/enwik5.txt", "rb") as f:
    data = f.read()

original_size = len(data)
buffer_sizes = [2**i for i in range(8, 16)]  
compression_ratios = []

for buffer_size in buffer_sizes:
    compressed_data = lz77_compress(data, buffer_size=buffer_size)
    compressed_size = len(compressed_data)
    ratio = calculate_compression_ratio(original_size, compressed_size)
    compression_ratios.append(ratio)


plt.figure(figsize=(10, 6))
plt.plot(buffer_sizes, compression_ratios, marker='o', linestyle='-', color='r')
plt.xscale("log")
plt.xlabel("Размер буфера (байты)")
plt.ylabel("Коэффициент сжатия")
plt.title("Зависимость коэффициента сжатия от размера буфера для LZ77")
plt.grid(True)
plt.show()

optimal_buffer_size = buffer_sizes[np.argmax(compression_ratios)]
print(f"Оптимальный размер буфера: {optimal_buffer_size} байт")
