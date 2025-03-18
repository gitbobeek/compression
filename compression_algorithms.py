import heapq
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
        count, byte = data[i], data[i + 1]
        decompressed.extend(byte.to_bytes(1, 'big') * count)

    return bytes(decompressed)


class LZ77Node:
    def __init__(self, offset: int, length: int, next_byte: int):
        self.offset = offset
        self.length = length
        self.next_byte = next_byte


def lz77_compress(data: bytes, window_size: int = 4096) -> list:
    compressed = []
    pos = 0

    while pos < len(data):
        match_offset, match_length = 0, 0

        search_start = max(0, pos - window_size)
        buffer = data[search_start:pos]

        for length in range(1, min(len(data) - pos, window_size)):
            substring = data[pos:pos + length]
            index = buffer.rfind(substring)

            if index != -1:
                match_offset = pos - (search_start + index)
                match_length = length
            else:
                break

        next_byte = data[pos + match_length] if pos + match_length < len(data) else None
        compressed.append(LZ77Node(match_offset, match_length, next_byte))
        pos += match_length + 1

    return compressed


def lz77_decompress(compressed: list) -> bytes:
    decompressed = bytearray()

    for node in compressed:
        if node.length > 0:
            start = len(decompressed) - node.offset
            for i in range(node.length):
                decompressed.append(decompressed[start + i])

        if node.next_byte is not None:
            decompressed.append(node.next_byte)

    return bytes(decompressed)


class LZ78Node:
    def __init__(self, pos: int, next_byte: int):
        self.pos = pos
        self.next_byte = next_byte


def lz78_compress(data: bytes) -> list:
    dictionary = {}
    compressed = []
    buffer = bytearray()
    dict_size = 1

    for byte in data:
        new_buffer = bytes(buffer) + bytes([byte])
        if new_buffer in dictionary:
            buffer.append(byte)
        else:
            pos = dictionary.get(bytes(buffer), 0)
            compressed.append(LZ78Node(pos, byte))
            dictionary[new_buffer] = dict_size
            dict_size += 1
            buffer.clear()

    if buffer:
        last_ch = buffer.pop()
        pos = dictionary.get(bytes(buffer), 0)
        compressed.append(LZ78Node(pos, last_ch))

    return compressed


def lz78_decompress(compressed: list) -> bytes:
    dictionary = [b""]
    decompressed = bytearray()

    for node in compressed:
        word = dictionary[node.pos] + bytes([node.next_byte])
        decompressed.extend(word)
        dictionary.append(word)

    return bytes(decompressed)


def bwt_transform(data: bytes) -> bytes:
    n = len(data)
    rotations = [data[i:] + data[:i] for i in range(n)]
    rotations.sort()
    return bytes(row[-1] for row in rotations)


def bwt_inverse(data: bytes) -> bytes:
    n = len(data)
    table = [b"" for _ in range(n)]

    for _ in range(n):
        table = sorted(data[i:i + 1] + table[i] for i in range(n))

    for row in table:
        if len(row) > 0 and row[-1] == 0:
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
    heap = []
    for byte, f in freq.items():
        heapq.heappush(heap, HuffmanNode(f, byte))

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        parent = HuffmanNode(left.freq + right.freq, None, left, right)
        heapq.heappush(heap, parent)

    return heap[0]


def generate_huffman_codes(node, prefix=""):
    codes = {}
    if node is None:
        return codes
    if node.byte is not None:
        codes[node.byte] = prefix
    codes.update(generate_huffman_codes(node.left, prefix + "0"))
    codes.update(generate_huffman_codes(node.right, prefix + "1"))
    return codes


def huffman_compress(data: bytes):
    if not data:
        return b"", None

    root = build_huffman_tree(data)
    codebook = generate_huffman_codes(root)

    encoded_data = "".join(codebook[byte] for byte in data)

    padding = 8 - len(encoded_data) % 8
    encoded_data += "0" * padding

    padded_info = f"{padding:08b}"

    compressed = []
    for i in range(0, len(encoded_data), 8):
        byte = padded_info + encoded_data[i:i+8]
        compressed.append(int(byte, 2))

    final_compressed = []
    for number in compressed:
        final_compressed.append(number & 0xFF)

    return bytes(final_compressed), root


def huffman_decompress(compressed: bytes, root):
    if not compressed or root is None:
        return b""

    bitstring = "".join(f"{byte:08b}" for byte in compressed)
    padding = int(bitstring[:8], 2)
    bitstring = bitstring[8:-padding]

    node = root
    decoded_bytes = bytearray()
    for bit in bitstring:
        node = node.left if bit == "0" else node.right
        if node.byte is not None:
            decoded_bytes.append(node.byte)
            node = root

    return bytes(decoded_bytes)


def mtf_compress(data: bytes) -> bytes:
    alphabet = list(set(data))
    result = []
    for byte in data:
        index = alphabet.index(byte)
        result.append(index)
        alphabet.insert(0, alphabet.pop(index))
    return bytes(result)


def mtf_decompress(compressed_data: bytes, alphabet: bytes) -> bytes:
    result = []
    alphabet = list(alphabet)
    for index in compressed_data:
        byte = alphabet[index]
        result.append(byte)
        alphabet.insert(0, alphabet.pop(index))
    return bytes(result)


