from compressing_algorithms.lz77 import *

def test_algorithm(input_file, compressed_file, output_file):
    with open(input_file, 'rb') as file:
        data = file.read()
    compressed_data = lz77_compress(data)
    with open(compressed_file, 'wb') as file:
        file.write(compressed_data)
    decompressed_data = lz77_decompress(compressed_data)
    with open(output_file, 'wb') as file:
        file.write(decompressed_data)

    print(data == decompressed_data)
    print(format(len(data) / len(compressed_data), '.3f'))


# def test_compressor(input_file, compressed_file, output_file):
#     lz77_huffman_compress(input_file, compressed_file)
#     lz77_huffman_decompress(compressed_file, output_file)


if __name__ == "__main__":
    input_file = "test_files/enwik7.txt"
    compressed_file = "tests/compressed_files/enwik7/LZ77_compressed.bin"
    output_file = "tests/decompressed_files/enwik7/LZ77_decompressed.txt"

    test_algorithm(input_file, compressed_file, output_file)