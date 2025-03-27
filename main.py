from numpy.ma.core import compressed

from compressors.lz78_ha import *


if __name__ == "__main__":
    input_file = "test_files/gs.raw"
    compressed_file = "tests/compressed_files/gs_photo/LZ78_HA_compressed.bin"
    decompressed_file = "tests/decompressed_files/gs_photo/LZ78_HA_decompressed.txt"

    # Сжатие
    lz78_huffman_compress(input_file, compressed_file)

    # Распаковка
    lz78_huffman_decompress(compressed_file, decompressed_file)

    # Проверка
    with open(input_file, 'rb') as f1, open(decompressed_file, 'rb') as f2, open(compressed_file, 'rb') as f3:
        original = f1.read()
        decompressed = f2.read()
        compressed = f3.read()
        print(len(original) / len(compressed))
        print("Проверка целостности:", "OK" if original == decompressed else "FAILED")