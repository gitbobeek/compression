import time
import os
import struct
import queue
from collections import defaultdict
import pickle

BLOCK_SIZE = 1024 * 64  # 64KB блоки


class HuffmanNode:
    def __init__(self, char=None, frequency=None, left=None, right=None):
        self.char = char
        self.frequency = frequency
        self.left = left
        self.right = right
        self.code = ''

    def __lt__(self, other):
        return self.frequency < other.frequency


# Улучшенная реализация BWT
def bwt_transform(s):
    n = len(s)
    s += b'\x00'  # Добавляем нулевой байт как маркер конца
    rotations = sorted([s[i:] + s[:i] for i in range(n + 1)])
    last_column = bytes([rotation[-1] for rotation in rotations])
    return last_column


def inverse_bwt(bwt):
    table = [bytearray() for _ in range(len(bwt))]
    for _ in range(len(bwt)):
        table.sort(key=lambda x: bytes(x))
        for i in range(len(bwt)):
            table[i].insert(0, bwt[i])
    for row in table:
        if row[-1] == 0:
            return bytes(row[:-1])
    return b''


# MTF преобразование
def mtf_encode(data):
    alphabet = list(range(256))
    result = bytearray()
    for byte in data:
        idx = alphabet.index(byte)
        result.append(idx)
        alphabet.pop(idx)
        alphabet.insert(0, byte)
    return bytes(result)


def mtf_decode(data):
    alphabet = list(range(256))
    result = bytearray()
    for idx in data:
        byte = alphabet[idx]
        result.append(byte)
        alphabet.pop(idx)
        alphabet.insert(0, byte)
    return bytes(result)


# RLE кодирование
def rle_encode(data):
    result = bytearray()
    i = 0
    while i < len(data):
        current = data[i]
        count = 1
        while i + count < len(data) and count < 255 and data[i + count] == current:
            count += 1
        result.append(count)
        result.append(current)
        i += count
    return bytes(result)


def rle_decode(data):
    result = bytearray()
    for i in range(0, len(data), 2):
        if i + 1 >= len(data):
            break
        count = data[i]
        byte = data[i + 1]
        result.extend([byte] * count)
    return bytes(result)


# Кодирование Хаффмана
def build_frequency_table(data):
    freq = defaultdict(int)
    for byte in data:
        freq[byte] += 1
    return freq


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


def huffman_encode(data, code_map):
    bit_string = ''.join(code_map[byte] for byte in data)
    padding = (8 - len(bit_string) % 8)
    bit_string += '0' * padding
    encoded = bytearray()
    encoded.append(padding)
    for i in range(0, len(bit_string), 8):
        byte = bit_string[i:i + 8]
    encoded.append(int(byte, 2))
    return bytes(encoded)


def huffman_decode(encoded_data, code_map):
    if not encoded_data:
        return b''

    padding = encoded_data[0]
    bit_string = ''.join(f"{byte:08b}" for byte in encoded_data[1:])
    if padding > 0:
        bit_string = bit_string[:-padding]

    reverse_map = {v: k for k, v in code_map.items()}
    current_code = ""
    result = bytearray()

    for bit in bit_string:
        current_code += bit
        if current_code in reverse_map:
            result.append(reverse_map[current_code])
            current_code = ""
    return bytes(result)


# Основные функции
def compress_file(input_path, output_path):
    start_time = time.time()
    original_size = os.path.getsize(input_path)

    with open(input_path, "rb") as fin, open(output_path, "wb") as fout:
        while True:
            block = fin.read(BLOCK_SIZE)
            if not block:
                break

            # Цепочка преобразований
            bwt_data = bwt_transform(block)
            mtf_data = mtf_encode(bwt_data)
            rle_data = rle_encode(mtf_data)

            # Кодирование Хаффмана
            freq = build_frequency_table(rle_data)
            if not freq:
                continue

            tree = build_huffman_tree(freq)
            code_map = build_code_map(tree)
            huffman_data = huffman_encode(rle_data, code_map)

            # Сохраняем дерево и данные
            tree_bytes = pickle.dumps(code_map)
            fout.write(struct.pack(">I", len(tree_bytes)))
            fout.write(tree_bytes)
            fout.write(struct.pack(">I", len(huffman_data)))
            fout.write(huffman_data)

    compressed_size = os.path.getsize(output_path)
    ratio = original_size / compressed_size if compressed_size > 0 else 0
    print(f"Compression complete. Ratio: {ratio:.2f}, Time: {time.time() - start_time:.2f}s")


def decompress_file(input_path, output_path):
    start_time = time.time()

    with open(input_path, "rb") as fin, open(output_path, "wb") as fout:
        while True:
            # Читаем дерево Хаффмана
            len_bytes = fin.read(4)
            if not len_bytes:
                break
            tree_len = struct.unpack(">I", len_bytes)[0]
            tree_bytes = fin.read(tree_len)
            if not tree_bytes:
                break
            try:
                code_map = pickle.loads(tree_bytes)
            except:
                break

            # Читаем сжатые данные
            len_bytes = fin.read(4)
            if not len_bytes:
                break
            data_len = struct.unpack(">I", len_bytes)[0]
            huffman_data = fin.read(data_len)
            if not huffman_data:
                break

            # Обратная цепочка преобразований
            rle_data = huffman_decode(huffman_data, code_map)
            if not rle_data:
                continue

            mtf_data = rle_decode(rle_data)
            bwt_data = mtf_decode(mtf_data)
            original_block = inverse_bwt(bwt_data)

            if original_block:
                fout.write(original_block)

    print(f"Decompression complete. Time: {time.time() - start_time:.2f}s")


input_file = "..compressors/enwik5.txt"
compressed_file = "tests/compressed_files/enwik7/BWT_MTF_RLE_HA_compressed.bin"
decompressed_file = "tests/decompressed_files/enwik7/BWT_MTF_RLE_HA_decompressed.txt"

# Создаем тестовый файл, если его нет
if not os.path.exists(input_file):
    with open(input_file, "w") as f:
        f.write("This is a test file for BWT+MTF+RLE+Huffman compression algorithm.")

# Сжатие
compress_file(input_file, compressed_file)

# Распаковка
decompress_file(compressed_file, decompressed_file)


# Проверка
def files_are_equal(file1, file2):
    with open(file1, "rb") as f1, open(file2, "rb") as f2:
        return f1.read() == f2.read()


print("Verification:", files_are_equal(input_file, decompressed_file))