import time
import os
import struct
import pickle
import queue
from collections import defaultdict


BLOCK_SIZE = 1024 * 64


class HuffmanNode:
    def __init__(self, char=None, frequency=None, left=None, right=None, parent=None):
        self.char = char
        self.frequency = frequency
        self.left = left
        self.right = right
        self.parent = parent

    def __lt__(self, other):
        return self.frequency < other.frequency


def count_symb(input_data):
    freq_table = defaultdict(int)
    for byte in input_data:
        freq_table[byte] += 1
    return freq_table


def suffix_array(text):
    text += b'\x00'
    n = len(text)
    s_a = list(range(n))

    for i in range(n):
        s_a[i] = (text[i:], i)
    s_a.sort()
    return [suffix[1] for suffix in s_a]


def bwt_from_suffix_array(s):
    sa = suffix_array(s)
    s += b'\x00'
    n = len(s)
    bwt = bytes(s[(i - 1) % n] for i in sa)
    return bwt


def ibwt(bwt):
    n = len(bwt)
    freq = [0] * 256
    for byte in bwt:
        freq[byte] += 1

    start = [0] * 256
    for i in range(1, 256):
        start[i] = start[i - 1] + freq[i - 1]

    lf = [0] * n
    count = [0] * 256
    for i in range(n):
        byte = bwt[i]
        lf[i] = start[byte] + count[byte]
        count[byte] += 1

    original_data = bytearray()
    i = bwt.index(0)  # Ищем нулевой байт
    for _ in range(n - 1):
        i = lf[i]
        original_data.append(bwt[i])

    return bytes(original_data[::-1])


def mtf_compress(data: bytes) -> bytes:
    alphabet = list(range(256))
    result = bytearray()

    for byte in data:
        index = alphabet.index(byte)
        result.append(index)
        alphabet.pop(index)
        alphabet.insert(0, byte)

    return bytes(result)


def mtf_decompress(compressed_data: bytes) -> bytes:
    alphabet = list(range(256))
    result = bytearray()

    for index in compressed_data:
        byte = alphabet[index]
        result.append(byte)
        alphabet.pop(index)
        alphabet.insert(0, byte)

    return bytes(result)


def huffman_compress(input_data):
    freq_table = count_symb(input_data)
    leaf_nodes = []
    min_heap = queue.PriorityQueue()

    for char in range(256):
        if freq_table.get(char, 0) > 0:
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
    if not compressed_data:
        return b''

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