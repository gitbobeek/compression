import sys
import time
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


def print_progress(iteration, total, prefix='', suffix='', length=50, fill='█'):
    """Выводит progress bar в терминал"""
    percent = f"{100 * (iteration / float(total)):.1f}"
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    sys.stdout.write(f'\r{prefix} |{bar}| {percent}% {suffix}')
    sys.stdout.flush()
    if iteration == total:
        print()


def lz77_compress(data, buffer_size=1024, max_length=255, show_progress=True):
    """LZ77 компрессия с прогресс-баром"""
    encoded = bytearray()
    i = 0
    n = len(data)

    while i < n:
        if show_progress:
            print_progress(i, n, prefix='LZ77 Сжатие:', suffix=f'{i}/{n} байт')

        best_offset = 0
        best_len = 0
        window_start = max(0, i - buffer_size)

        for j in range(window_start, i):
            current_len = 0
            while (current_len < max_length and
                   i + current_len < n and
                   data[j + current_len] == data[i + current_len]):
                current_len += 1

            if current_len > best_len:
                best_len = current_len
                best_offset = i - j

        if best_len > 0:
            encoded.extend(struct.pack('>H', best_offset))
            encoded.extend(struct.pack('>H', best_len))
            i += best_len
        else:
            encoded.extend(b'\x00\x00\x00\x00')
            encoded.append(data[i])
            i += 1

    if show_progress:
        print_progress(n, n, prefix='LZ77 Сжатие:', suffix=f'Готово {n}/{n} байт')
    return bytes(encoded)


def lz77_decompress(encoded, show_progress=True):
    """Исправленная версия LZ77 декомпрессора"""
    decoded = bytearray()
    i = 0
    n = len(encoded)

    while i + 4 <= n:
        if show_progress:
            print_progress(i, n, prefix='LZ77 Распаковка:', suffix=f'{i}/{n} байт')

        # Читаем offset и length (по 2 байта каждый)
        offset = (encoded[i] << 8) | encoded[i + 1]
        length = (encoded[i + 2] << 8) | encoded[i + 3]
        i += 4

        if offset == 0 and length == 0:
            # Литерал
            if i >= n:
                break
            decoded.append(encoded[i])
            i += 1
        else:
            # Проверка корректности offset
            if offset > len(decoded):
                # Если offset превышает текущую длину - копируем с начала буфера
                start = 0
            else:
                start = len(decoded) - offset

            # Копируем данные с учётом возможного перекрытия
            for _ in range(length):
                if start >= len(decoded):
                    break
                decoded.append(decoded[start])
                start += 1

    if show_progress:
        print_progress(n, n, prefix='LZ77 Распаковка:', suffix=f'Готово {n}/{n} байт')
    return bytes(decoded)

def build_huffman_tree(freq):
    """Построение дерева Хаффмана"""
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
    """Построение таблицы кодирования"""
    if code_map is None:
        code_map = {}
    if root.char is not None:
        code_map[root.char] = path
        return code_map
    build_code_map(root.left, path + "0", code_map)
    build_code_map(root.right, path + "1", code_map)
    return code_map


def huffman_compress(data, show_progress=True):
    """Huffman компрессия"""
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
    """Huffman декомпрессия"""
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
    """Полный алгоритм LZ77 + Huffman"""
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
    """Распаковка LZ77 + Huffman"""
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


