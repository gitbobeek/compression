import queue, struct, math
import numpy as np

def rle_compress(data: bytes) -> bytes:
    encoded = []
    i = 0
    while i < len(data):
        run_length = 1
        while i + run_length < len(data) and data[i] == data[i + run_length] and run_length < 255:
            run_length += 1

        if run_length > 1:
            encoded.append(run_length)
            encoded.append(data[i])
            i += run_length
        else:
            non_repeat_length = 1
            while (i + non_repeat_length < len(data) and
                   non_repeat_length < 255 and
                   (i + non_repeat_length + 1 >= len(data) or
                    data[i + non_repeat_length] != data[i + non_repeat_length + 1])):
                non_repeat_length += 1

            encoded.append(non_repeat_length)
            encoded.append(0x80)
            encoded.extend(data[i:i + non_repeat_length])
            i += non_repeat_length

    return bytes(encoded)


def read_huffman_codes(codes_file):
    huffman_codes = {}
    with open(codes_file, 'r') as f:
        for line in f:
            symbol, code = line.strip().split(':')
            huffman_codes[int(symbol)] = code
    return huffman_codes

def rle_decompress(data: bytes) -> bytes:
    decoded = []
    i = 0
    while i < len(data):
        run_length = data[i]
        if i + 1 < len(data) and data[i + 1] == 0x80:
            length = run_length
            decoded.extend(data[i + 2:i + 2 + length])
            i += 2 + length
        else:
            decoded.extend([data[i + 1]] * run_length)
            i += 2
    return bytes(decoded)


def lz77_compress(data: bytes, buffer_size: int) -> bytes:
    encoded_data = bytearray()  # Используем bytearray для накопления результата
    i = 0
    while i < len(data):
        # Определяем границы поиска
        search_start = max(0, i - buffer_size)
        search_end = i
        search_buffer = data[search_start:search_end]
        # Ищем максимальное совпадение
        max_length = 0
        max_offset = 0
        for length in range(1, min(len(data) - i, buffer_size) + 1):
            substring = data[i:i + length]
            offset = search_buffer.rfind(substring)
            if offset != -1:
                max_length = length
                max_offset = len(search_buffer) - offset
        if max_length > 0:
            # Кодируем offset и length в два байта каждый
            encoded_data.append((max_offset >> 8) & 0xFF)  # Старший байт offset
            encoded_data.append(max_offset & 0xFF)         # Младший байт offset
            encoded_data.append((max_length >> 8) & 0xFF)  # Старший байт length
            encoded_data.append(max_length & 0xFF)         # Младший байт length
            i += max_length
        else:
            # Если совпадений нет, кодируем как символ
            encoded_data.append(0)  # offset = 0 (старший байт)
            encoded_data.append(0)  # offset = 0 (младший байт)
            encoded_data.append(0)  # length = 0 (старший байт)
            encoded_data.append(0)  # length = 0 (младший байт)
            encoded_data.append(data[i])  # символ (1 байт)
            i += 1

    return bytes(encoded_data)

def lz77_decompress(encoded_data: bytes) -> bytes:
    decoded_data = bytearray()
    i = 0
    while i < len(encoded_data):
        try:
            if i + 4 > len(encoded_data):
                raise ValueError("Недостаточно данных для чтения offset и length.")
            # Читаем offset и length (по два байта каждый)
            offset = (encoded_data[i] << 8) | encoded_data[i + 1]
            length = (encoded_data[i + 2] << 8) | encoded_data[i + 3]
            i += 4

            if offset == 0 and length == 0:
                # Это символ
                if i >= len(encoded_data):
                    raise ValueError("Недостаточно данных для чтения символа.")
                decoded_data.append(encoded_data[i])
                i += 1
            else:
                # Это ссылка
                start = len(decoded_data) - offset
                if start < 0 or start + length > len(decoded_data):
                    raise ValueError(f"Некорректные offset или length: offset={offset}, length={length}.")

                for _ in range(length):
                    decoded_data.append(decoded_data[start])
                    start += 1

        except Exception as e:
            print(f"Ошибка декодирования на шаге {i}: {e}")
            break

    return bytes(decoded_data)

def lz78_compress(data: bytes) -> bytes:
    dictionary = {b'': 0}  # Инициализация словаря с пустой строкой
    current_string = b''
    encoded_data = bytearray()

    for byte in data:
        new_string = current_string + bytes([byte])
        if new_string in dictionary:
            current_string = new_string
        else:
            # Используем 4 байта для индекса
            encoded_data.extend(dictionary[current_string].to_bytes(4, 'big'))  # Индекс текущей строки
            encoded_data.append(byte)  # Новый символ
            dictionary[new_string] = len(dictionary)  # Добавляем новую строку в словарь
            current_string = b''

    if current_string:
        # Используем 4 байта для индекса
        encoded_data.extend(dictionary[current_string].to_bytes(4, 'big'))  # Индекс последней строки

    return bytes(encoded_data)


# Функция для декодирования данных с помощью алгоритма LZ78
def lz78_decompress(encoded_data: bytes) -> bytes:
    dictionary = {0: b''}  # Инициализация словаря с пустой строкой
    decoded_data = bytearray()
    i = 0

    while i < len(encoded_data):
        # Чтение индекса (4 байта)
        index = int.from_bytes(encoded_data[i:i + 4], 'big')
        i += 4
        if i < len(encoded_data):
            byte = encoded_data[i]  # Чтение нового символа
            i += 1
        else:
            byte = None

        if index in dictionary:
            string = dictionary[index]
            if byte is not None:
                new_string = string + bytes([byte])
                dictionary[len(dictionary)] = new_string
                decoded_data.extend(new_string)
            else:
                decoded_data.extend(string)
        else:
            raise ValueError("Некорректный индекс в закодированных данных")

    return bytes(decoded_data)


def bwt_transform(data: bytes) -> bytes:
    """Применяет преобразование BWT к байтовой строке."""
    n = len(data)
    rotations = sorted(data[i:] + data[:i] for i in range(n))
    last_column = bytes(row[-1] for row in rotations)
    original_index = rotations.index(data)
    return last_column + struct.pack('>I', original_index)

def bwt_inverse(transformed: bytes) -> bytes:
    """Обратное преобразование BWT."""
    last_column = transformed[:-4]
    original_index = struct.unpack('>I', transformed[-4:])[0]
    n = len(last_column)
    table = [b''] * n
    for _ in range(n):
        table = sorted(last_column[i:i+1] + table[i] for i in range(n))
    return table[original_index]

def compress_bwt(input_bytes: bytes, block_size: int = 100000) -> bytes:
    """Сжимает данные с использованием блочного BWT."""
    compressed_blocks = []
    for i in range(0, len(input_bytes), block_size):
        block = input_bytes[i:i + block_size]
        transformed_block = bwt_transform(block)
        compressed_blocks.append(transformed_block)
    return b''.join(compressed_blocks)

def decompress_bwt(compressed_bytes: bytes, block_size: int = 100000) -> bytes:
    """Декомпрессирует данные с использованием блочного BWT."""
    decompressed_blocks = []
    start = 0
    while start < len(compressed_bytes):
        block = compressed_bytes[start:start + block_size + 4]  # Учитываем 4 байта индекса
        start += block_size + 4
        restored_block = bwt_inverse(block)
        decompressed_blocks.append(restored_block)
    return b''.join(decompressed_blocks)


class Node():
    def __init__(self, symbol=None, counter=None, left=None, right=None, parent=None):
        self.symbol = symbol
        self.counter = counter
        self.left = left
        self.right = right
        self.parent = parent

    def __lt__(self, other):
        return self.counter < other.counter


# Функция для подсчета частоты символов
def count_symb(data: bytes) -> np.ndarray:
    counter = np.zeros(256, dtype=int)
    for byte in data:
        counter[byte] += 1
    return counter


# Функция для сжатия данных с помощью алгоритма Хаффмана
def huffman_compress(data: bytes) -> bytes:
    C = count_symb(data)
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


def calculate_average_code_length(huffman_codes: dict, data: bytes) -> float:
    counter = count_symb(data)
    total_symbols = len(data)
    total_length = 0.0

    for symbol, code in huffman_codes.items():
        probability = counter[symbol] / total_symbols
        total_length += probability * len(code)

    return total_length

def calculate_entropy(data: bytes) -> float:
    counter = count_symb(data)
    total_symbols = len(data)
    entropy = 0.0

    for count in counter:
        if count > 0:
            probability = count / total_symbols
            entropy -= probability * math.log2(probability)

    return entropy


class Node():
    def __init__(self, symbol=None, counter=None, left=None, right=None, parent=None):
        self.symbol = symbol
        self.counter = counter
        self.left = left
        self.right = right
        self.parent = parent

    def __lt__(self, other):
        return self.counter < other.counter



# Функция для декомпрессии данных с помощью алгоритма Хаффмана
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