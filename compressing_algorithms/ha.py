from util import count_symb as cs
import queue


class Node:
    def __init__(self, symbol=None, counter=None, left=None, right=None, parent=None):
        self.symbol = symbol
        self.counter = counter
        self.left = left
        self.right = right
        self.parent = parent

    def __lt__(self, other):
        return self.counter < other.counter


def read_huffman_codes(codes_file):
    huffman_codes = {}
    with open(codes_file, 'r') as f:
        for line in f:
            symbol, code = line.strip().split(':')
            huffman_codes[int(symbol)] = code
    return huffman_codes


def huffman_compress(data: bytes):
    C = cs.count_symb(data)
    list_of_leafs = []
    Q = queue.PriorityQueue()

    for i in range(256):
        if C[i] != 0:
            leaf = Node(symbol=i, counter=C[i])
            list_of_leafs.append(leaf)
            Q.put(leaf)

    while Q.qsize() >= 2:
        left_node = Q.get()
        right_node = Q.get()
        parent_node = Node(left=left_node, right=right_node)
        left_node.parent = parent_node
        right_node.parent = parent_node
        parent_node.counter = left_node.counter + right_node.counter
        Q.put(parent_node)

    codes = {}
    for leaf in list_of_leafs:
        node = leaf
        code = ""
        while node.parent is not None:
            if node.parent.left == node:
                code = "0" + code
            else:
                code = "1" + code
            node = node.parent
        codes[leaf.symbol] = code

    coded_message = ""
    for byte in data:
        coded_message += codes[byte]

    padding = 8 - len(coded_message) % 8
    coded_message += '0' * padding
    coded_message = f"{padding:08b}" + coded_message

    bytes_string = bytearray()
    for i in range(0, len(coded_message), 8):
        byte = coded_message[i:i + 8]
        bytes_string.append(int(byte, 2))

    return bytes(bytes_string), codes


def huffman_decompress(compressed_data: bytes, huffman_codes: dict) -> bytes:
    padding = compressed_data[0]
    coded_message = ""
    for byte in compressed_data[1:]:
        coded_message += f"{byte:08b}"

    if padding > 0:
        coded_message = coded_message[:-padding]

    reverse_codes = {v: k for k, v in huffman_codes.items()}
    current_code = ""
    decoded_data = bytearray()

    for bit in coded_message:
        current_code += bit
        if current_code in reverse_codes:
            decoded_data.append(reverse_codes[current_code])
            current_code = ""

    return bytes(decoded_data)