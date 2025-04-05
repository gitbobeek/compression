import queue
import pickle
import struct
from collections import defaultdict


class HuffmanNode:
    def __init__(self, char=None, frequency=None, left=None, right=None):
        self.char = char
        self.frequency = frequency
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.frequency < other.frequency


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


def lz77_compress(data: bytes, buffer_size: int = 1024, max_length: int = 255, show_progress: bool = True) -> bytes:
    encoded_data = bytearray()
    i = 0
    n = len(data)
    last_update = 0

    if show_progress:
        print("Сжатие данных...")

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

    if show_progress:
        print_progress(n, n, prefix='Прогресс:', suffix=f'Обработано {n}/{n} байт')
        print(f"Сжатие завершено. Размер сжатых данных: {len(encoded_data)} байт")

    return bytes(encoded_data)


def lz77_decompress(encoded_data: bytes, show_progress: bool = True) -> bytes:
    decoded_data = bytearray()
    i = 0
    n = len(encoded_data)
    last_update = 0

    if show_progress:
        print("Распаковка данных...")

    while i + 4 <= n:
        if show_progress and time.time() - last_update > 0.1:
            print_progress(i, n, prefix='Прогресс:', suffix=f'Обработано {i}/{n} байт')
            last_update = time.time()

        offset = (encoded_data[i] << 8) | encoded_data[i + 1]
        length = (encoded_data[i + 2] << 8) | encoded_data[i + 3]
        i += 4

        if offset == 0 and length == 0:
            if i >= n:
                break
            decoded_data.append(encoded_data[i])
            i += 1
        else:
            start = len(decoded_data) - offset
            end = start + length

            if start < 0 or offset > len(decoded_data):
                raise ValueError(f"Invalid offset: {offset}, decoded length: {len(decoded_data)}")

            for j in range(length):
                if start + j >= len(decoded_data):
                    raise ValueError(f"Invalid copy operation: start={start}, j={j}, length={len(decoded_data)}")
                decoded_data.append(decoded_data[start + j])

    while i < n:
        decoded_data.append(encoded_data[i])
        i += 1

    if show_progress:
        print_progress(n, n, prefix='Прогресс:', suffix=f'Обработано {n}/{n} байт')
        print(f"Распаковка завершена. Размер данных: {len(decoded_data)} байт")

    return bytes(decoded_data)

def build_huffman_tree(freq):
    heap = queue.PriorityQueue()
    for char, count in freq.items():
        heap.put(HuffmanNode(char=char, frequency=count))

    while heap.qsize() > 1:
        left = heap.get()
        right = heap.get()
        merged = HuffmanNode(frequency=left.frequency + right.frequency,
                             left=left, right=right)
        heap.put(merged)
    return heap.get()


def build_code_map(root, path="", code_map=None):
    if code_map is None:
        code_map = {}
    if root.char is not None:
        code_map[root.char] = path
        return code_map
    build_code_map(root.left, path + "0", code_map)
    build_code_map(root.right, path + "1", code_map)
    return code_map


def huffman_compress(data, show_progress=True):
    freq = defaultdict(int)
    for byte in data:
        freq[byte] += 1

    tree = build_huffman_tree(freq)
    code_map = build_code_map(tree)

    bit_stream = ''.join(code_map[byte] for byte in data)
    padding = (8 - len(bit_stream) % 8)
    padded_stream = f"{padding:08b}{bit_stream}{'0' * padding}"

    compressed = bytearray()
    for i in range(0, len(padded_stream), 8):
        compressed.append(int(padded_stream[i:i + 8], 2))

    if show_progress:
        print("Huffman сжатие завершено")
    return bytes(compressed), code_map


def huffman_decompress(compressed, code_map, show_progress=True):
    pad_info = compressed[0]
    bit_stream = ''.join(f"{byte:08b}" for byte in compressed[1:])

    if pad_info > 0:
        bit_stream = bit_stream[:-pad_info]

    reverse_map = {v: k for k, v in code_map.items()}
    buffer = ""
    output = bytearray()

    for bit in bit_stream:
        buffer += bit
        if buffer in reverse_map:
            output.append(reverse_map[buffer])
            buffer = ""

    if show_progress:
        print("Huffman распаковка завершена")
    return bytes(output)


def lz77_huffman_compress(input_path, output_path, show_progress=True):
    start_time = time.time()

    
    with open(input_path, 'rb') as f:
        data = f.read()

    
    lz77_compressed = lz77_compress(data, show_progress=show_progress)

    
    huffman_compressed, code_map = huffman_compress(lz77_compressed, show_progress=show_progress)

    
    tree_bytes = pickle.dumps(code_map)

    
    with open(output_path, 'wb') as f:
        f.write(struct.pack('>I', len(tree_bytes)))  
        f.write(tree_bytes)  
        f.write(huffman_compressed)  

    
    original_size = len(data)
    compressed_size = len(tree_bytes) + len(huffman_compressed) + 4
    ratio = original_size / compressed_size
    print(f"\nСжатие завершено. Коэффициент: {ratio:.2f}:1")
    print(f"Исходный размер: {original_size} байт")
    print(f"Сжатый размер: {compressed_size} байт")
    print(f"Время выполнения: {time.time() - start_time:.2f} сек")


def lz77_huffman_decompress(input_path, output_path, show_progress=True):
    start_time = time.time()

    
    with open(input_path, 'rb') as f:
        tree_len = struct.unpack('>I', f.read(4))[0]
        tree_bytes = f.read(tree_len)
        huffman_compressed = f.read()

    
    code_map = pickle.loads(tree_bytes)
    
    lz77_compressed = huffman_decompress(huffman_compressed, code_map, show_progress=show_progress)
    
    data = lz77_decompress(lz77_compressed, show_progress=show_progress)

    with open(output_path, 'wb') as f:
        f.write(data)

    print(f"\nРаспаковка завершена за {time.time() - start_time:.2f} сек")


