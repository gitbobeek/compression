from compression_algorithms import *
import time
import os


def lz78_huffman_compress(data: bytes):
    # Сжатие данных с помощью LZ78
    lz78_encoded_data = lz78_compress(data)

    # Сжатие результата LZ78 с помощью Хаффмана
    huffman_compressed_data, huffman_codes = huffman_compress(lz78_encoded_data)

    return huffman_compressed_data, huffman_codes


def lz78_huffman_decompress(compressed_data: bytes, huffman_codes: dict) -> bytes:
    # Декомпрессия Хаффмана
    huffman_decompressed_data = huffman_decompress(compressed_data, huffman_codes)

    # Декомпрессия LZ78
    lz78_decoded_data = lz78_decompress(huffman_decompressed_data)

    return lz78_decoded_data


def process_file_with_lz78_huffman(file_path, output_compressed, output_decompressed):
    start_time = time.time()

    # Чтение исходных данных
    with open(file_path, "rb") as f:
        data = f.read()
    original_size = len(data)
    print(f"Исходный размер данных: {original_size} байт")

    # Сжатие данных с использованием LZ78 и Хаффмана
    compressed_bytes, huffman_codes = lz78_huffman_compress(data)
    compressed_size = len(compressed_bytes)
    print(f"Размер сжатых данных: {compressed_size} байт")

    # Запись сжатых данных и кодов Хаффмана
    with open(output_compressed, "wb") as file:
        file.write(compressed_bytes)

    with open(output_compressed + '_codes', 'w') as code_file:
        for symbol, code in huffman_codes.items():
            code_file.write(f"{symbol}:{code}\n")

    # Чтение сжатых данных и декомпрессия
    with open(output_compressed, "rb") as f:
        compressed_data = f.read()

    huffman_codes = read_huffman_codes(output_compressed + '_codes')
    decompressed_data = lz78_huffman_decompress(compressed_data, huffman_codes)
    decompressed_size = len(decompressed_data)
    print(f"Размер после декомпрессии: {decompressed_size} байт")

    # Вычисление коэффициента сжатия
    compression_ratio = original_size / compressed_size
    print(f"Коэффициент сжатия: {compression_ratio:.2f}")

    # Вычисление энтропии и средней длины кода
    entropy = calculate_entropy(data)
    avg_code_length = calculate_average_code_length(huffman_codes, data)
    print(f"Энтропия: {entropy:.2f} бит/символ")
    print(f"Средняя длина кода: {avg_code_length:.2f} бит/символ \n")

    # Запись декомпрессированных данных
    with open(output_decompressed, "wb") as file:
        file.write(decompressed_data)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Время выполнения: {elapsed_time:.2f} секунд \n")


