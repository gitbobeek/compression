from util import count_symb as ca
import queue


class HuffmanNode:
    def __init__(self, char=None, frequency=None, left=None, right=None, parent=None):
        self.char = char
        self.frequency = frequency
        self.left = left
        self.right = right
        self.parent = parent

    def __lt__(self, other):
        return self.frequency < other.frequency


def load_huffman_codes(code_file_path):
    code_map = {}
    with open(code_file_path) as file:
        for line in file:
            char, code = line.strip().split(':')
            code_map[int(char)] = code
    return code_map


def huffman_compress(input_data):
    freq_table = ca.count_symb(input_data)
    leaf_nodes = []
    min_heap = queue.PriorityQueue()

    for char in range(256):
        if freq_table[char] > 0:
            node = HuffmanNode(char=char, frequency=freq_table[char])
            leaf_nodes.append(node)
            min_heap.put(node)

    while min_heap.qsize() > 1:
        left = min_heap.get()
        right = min_heap.get()
        merged = HuffmanNode(
            left=left,
            right=right,
            frequency=left.frequency + right.frequency
        )
        left.parent = merged
        right.parent = merged
        min_heap.put(merged)

    encoding_map = {}
    for node in leaf_nodes:
        current = node
        code_bits = []
        while current.parent:
            code_bits.insert(0, '0' if current.parent.left == current else '1')
            current = current.parent
        encoding_map[node.char] = ''.join(code_bits)

    bit_stream = ''.join(encoding_map[byte] for byte in input_data)

    pad_length = (8 - len(bit_stream) % 8)
    padded_stream = f"{pad_length:08b}{bit_stream}{'0' * pad_length}"

    compressed = bytearray()
    for i in range(0, len(padded_stream), 8):
        compressed.append(int(padded_stream[i:i + 8], 2))

    return bytes(compressed), encoding_map


def huffman_decompress(compressed_data, encoding_map):
    pad_info = compressed_data[0]
    bit_stream = ''.join(f"{byte:08b}" for byte in compressed_data[1:])

    if pad_info > 0:
        bit_stream = bit_stream[:-pad_info]

    decoding_map = {code: char for char, code in encoding_map.items()}
    buffer = ""
    output = bytearray()

    for bit in bit_stream:
        buffer += bit
        if buffer in decoding_map:
            output.append(decoding_map[buffer])
            buffer = ""

    return bytes(output)