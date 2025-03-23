import heapq
import mmap
from collections import Counter


def rle_compress(data: bytes) -> bytes:
    compressed = bytearray()
    prev_byte = data[0]
    count = 1

    for byte in data[1:]:
        if byte == prev_byte and count < 255:
            count += 1
        else:
            compressed.extend((count, prev_byte))
            prev_byte = byte
            count = 1

    compressed.extend((count, prev_byte))
    return bytes(compressed)


def rle_decompress(data: bytes) -> bytes:
    decompressed = bytearray()

    for i in range(0, len(data), 2):
        if i + 1 >= len(data):
            break
        count, byte = data[i], data[i + 1]
        decompressed.extend(bytes([byte]) * count)

    return bytes(decompressed)


def lz77_compress(data: bytes, window_size: int = 4096) -> bytes:
    compressed = bytearray()
    pos = 0

    while pos < len(data):
        match_offset, match_length = 0, 0
        search_start = max(0, pos - window_size)
        buffer = data[search_start:pos]

        hash_table = {}
        for i in range(len(buffer)):
            hash_table[buffer[i:i + 3]] = i

        for length in range(3, min(len(data) - pos, window_size)):
            substring = data[pos:pos + length]
            if substring in hash_table:
                match_offset = pos - (search_start + hash_table[substring])
                match_length = length
            else:
                break

        next_byte = data[pos + match_length] if pos + match_length < len(data) else 0
        compressed.extend(match_offset.to_bytes(2, 'big'))
        compressed.extend(match_length.to_bytes(2, 'big'))
        compressed.append(next_byte)
        pos += match_length + 1

    return bytes(compressed)


def lz77_decompress(compressed_data: bytes) -> bytes:
    decompressed = bytearray()
    i = 0

    while i < len(compressed_data):
        offset = int.from_bytes(compressed_data[i:i+2], 'big')
        length = int.from_bytes(compressed_data[i+2:i+4], 'big')
        next_byte = compressed_data[i+4]
        i += 5

        if offset > 0 and length > 0:
            start = len(decompressed) - offset
            for j in range(length):
                decompressed.append(decompressed[start + j])

        if next_byte != 0:
            decompressed.append(next_byte)

    return bytes(decompressed)


class LZ78Node:
    def __init__(self, pos: int, next_byte: int):
        self.pos = pos
        self.next_byte = next_byte


def lz78_compress(data: bytes, max_dict_size: int = 4096) -> bytes:
    dictionary = {b"": 0}
    compressed = bytearray()
    buffer = bytearray()
    dict_size = 1

    for byte in data:
        buffer.append(byte)
        if bytes(buffer) not in dictionary:
            pos = dictionary.get(bytes(buffer[:-1]), 0)
            compressed.extend(pos.to_bytes(2, 'big'))
            compressed.append(buffer[-1])
            if dict_size < max_dict_size:
                dictionary[bytes(buffer)] = dict_size
                dict_size += 1
            buffer.clear()

    if buffer:
        pos = dictionary.get(bytes(buffer[:-1]), 0)
        compressed.extend(pos.to_bytes(2, 'big'))
        compressed.append(buffer[-1])

    return bytes(compressed)

def lz78_decompress(compressed_data: bytes) -> bytes:
    dictionary = [b""]
    decompressed = bytearray()

    for i in range(0, len(compressed_data), 3):
        pos = int.from_bytes(compressed_data[i:i+2], 'big')
        byte = compressed_data[i+2]
        if pos >= len(dictionary):
            raise ValueError("Invalid LZ78 compressed data")
        word = dictionary[pos] + bytes([byte])
        decompressed.extend(word)
        dictionary.append(word)

    return bytes(decompressed)


def bwt_transform(data: bytes) -> bytes:
    if not data:
        return b""

    data = data + b"\x00"  # Добавляем терминальный символ
    suffix_array = sorted(range(len(data)), key=lambda i: data[i:])
    return bytes(data[i - 1] for i in suffix_array)


def bwt_inverse(data: bytes) -> bytes:
    if not data:
        return b""

    n = len(data)
    table = [bytearray() for _ in range(n)]

    for _ in range(n):
        table = sorted(bytes([data[i]]) + table[i] for i in range(n))

    for row in table:
        if row.endswith(b"\x00"):
            return row[:-1]
    return b""


class HuffmanNode:
    def __init__(self, freq, byte=None, left=None, right=None):
        self.freq = freq
        self.byte = byte
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.freq < other.freq


def build_huffman_tree(data: bytes):
    freq = Counter(data)
    heap = [HuffmanNode(f, byte) for byte, f in freq.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        parent = HuffmanNode(left.freq + right.freq, None, left, right)
        heapq.heappush(heap, parent)

    return heap[0]


def generate_huffman_codes(node, prefix=""):
    codes = {}
    if node.byte is not None:
        codes[node.byte] = prefix
    if node.left is not None:
        codes.update(generate_huffman_codes(node.left, prefix + "0"))
    if node.right is not None:
        codes.update(generate_huffman_codes(node.right, prefix + "1"))
    return codes


def huffman_compress(data: bytes) -> tuple[bytes, HuffmanNode]:
    root = build_huffman_tree(data)
    codebook = generate_huffman_codes(root)

    encoded_data = "".join(codebook[byte] for byte in data)
    padding = 8 - len(encoded_data) % 8
    encoded_data += "0" * padding

    compressed = bytearray()
    compressed.append(padding)
    for i in range(0, len(encoded_data), 8):
        byte = encoded_data[i:i+8]
        compressed.append(int(byte, 2))

    return bytes(compressed), root

def huffman_decompress(compressed: bytes, root: HuffmanNode) -> bytes:
    if not compressed or root is None:
        return b""

    padding = compressed[0]
    bitstring = "".join(f"{byte:08b}" for byte in compressed[1:])
    bitstring = bitstring[:-padding] if padding > 0 else bitstring

    node = root
    decoded_bytes = bytearray()
    for bit in bitstring:
        node = node.left if bit == "0" else node.right
        if node.byte is not None:
            decoded_bytes.append(node.byte)
            node = root

    return bytes(decoded_bytes)


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


def process_large_file(input_file: str, output_file: str, process_function, block_size: int = 4096):
    with open(input_file, "rb") as infile, open(output_file, "wb") as outfile:
        with mmap.mmap(infile.fileno(), length=0, access=mmap.ACCESS_READ) as mmapped_file:
            pos = 0
            while pos < len(mmapped_file):
                chunk = mmapped_file[pos:pos + block_size]
                outfile.write(process_function(chunk))
                pos += block_size