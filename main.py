from compression_algorithms import *


def main():

    file = open("input.txt", "rb")
    data = file.read()
    file.close()

    # Сжатие данных
    compressed, root = huffman_compress(data)
    print(f"Сжатые данные: {compressed}")


    file = open("compressed.bin", "wb")
    file.write(compressed)
    file.close()


    file = open("compressed.bin", "rb")
    compressed_data = file.read()
    file.close()


    decompressed = huffman_decompress(compressed_data, root)
    print(f"Разжаты данные: {decompressed}")


    file = open("output.txt", "wb")
    file.write(decompressed)
    file.close()


if __name__ == '__main__':
    main()