from compression_algorithms import *

if __name__ == "__main__":
    """
    process_large_file("enwik7.txt", "compressed_bwt.bin", bwt_transform)
    process_large_file("compressed_bwt.bin", "output_bwt.txt", bwt_inverse)
    """

    process_large_file("enwik7.txt", "compressed_lz77.bin", lz77_compress)
    process_large_file("compressed_lz77.bin", "output_lz77.txt", lz77_decompress)

    process_large_file("enwik7.txt", "compressed_lz78.bin", lz78_compress)
    process_large_file("compressed_lz78.bin", "output_lz78.txt", lz78_decompress)
