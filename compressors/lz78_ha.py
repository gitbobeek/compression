import struct
import pickle
from collections import defaultdict
import queue


class HuffmanNode:
    def __init__(self, char=None, frequency=None, left=None, right=None):
        self.char = char
        self.frequency = frequency
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.frequency < other.frequency


def lz78_compress(data: bytes) -> bytes:
    """LZ78 компрессия с выводом (index, byte) пар"""
    dictionary = {b'': 0}
    current_string = b''
    compressed_data = bytearray()

    for byte in data:
        new_string = current_string + bytes([byte])
        if new_string in dictionary:
            current_string = new_string
        else:
            
            compressed_data.extend(dictionary[current_string].to_bytes(4, 'big'))
            compressed_data.append(byte)
            dictionary[new_string] = len(dictionary)
            current_string = b''

    if current_string:
        compressed_data.extend(dictionary[current_string].to_bytes(4, 'big'))

    return bytes(compressed_data)


def lz78_decompress(compressed_data: bytes) -> bytes:
    """LZ78 декомпрессия (index, byte) пар"""
    dictionary = {0: b''}
    decompressed_data = bytearray()
    i = 0

    while i < len(compressed_data):
        index = int.from_bytes(compressed_data[i:i + 4], 'big')
        i += 4
        byte = compressed_data[i] if i < len(compressed_data) else None
        i += 1 if byte is not None else 0

        string = dictionary[index]

        if byte is not None:
            new_string = string + bytes([byte])
            dictionary[len(dictionary)] = new_string
            decompressed_data.extend(new_string)
        else:
            decompressed_data.extend(string)

    return bytes(decompressed_data)


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
    """Построение таблицы кодирования Хаффмана"""
    if code_map is None:
        code_map = {}
    if root.char is not None:
        code_map[root.char] = path
        return code_map
    build_code_map(root.left, path + "0", code_map)
    build_code_map(root.right, path + "1", code_map)
    return code_map


def huffman_compress(data):
    """Huffman компрессия"""
    freq = defaultdict(int)
    for byte in data:
        freq[byte] += 1

    tree = build_huffman_tree(freq)
    code_map = build_code_map(tree)

    bit_stream = ''.join(code_map[byte] for byte in data)
    padding = (8 - len(bit_stream) % 8) % 8
    padded_stream = f"{padding:08b}{bit_stream}{'0' * padding}"

    compressed = bytearray()
    for i in range(0, len(padded_stream), 8):
        compressed.append(int(padded_stream[i:i + 8], 2))

    return bytes(compressed), code_map


def huffman_decompress(compressed, code_map):
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

    return bytes(output)


def lz78_huffman_compress(input_path, output_path):
    """Полный алгоритм LZ78 + Huffman"""
    with open(input_path, 'rb') as f:
        data = f.read()

    
    lz78_compressed = lz78_compress(data)

    
    huffman_compressed, code_map = huffman_compress(lz78_compressed)

    
    with open(output_path, 'wb') as f:
        
        tree_bytes = pickle.dumps(code_map)
        f.write(struct.pack('>I', len(tree_bytes)))
        f.write(tree_bytes)

        
        f.write(huffman_compressed)


def lz78_huffman_decompress(input_path, output_path):
    """Распаковка LZ78 + Huffman"""
    with open(input_path, 'rb') as f:
        
        tree_len = struct.unpack('>I', f.read(4))[0]
        tree_bytes = f.read(tree_len)
        code_map = pickle.loads(tree_bytes)

        
        huffman_compressed = f.read()

    
    lz78_compressed = huffman_decompress(huffman_compressed, code_map)

    
    data = lz78_decompress(lz78_compressed)

    
    with open(output_path, 'wb') as f:
        f.write(data)


