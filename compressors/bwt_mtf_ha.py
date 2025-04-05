from compressing_algorithms.bwt_sa import *
from compressing_algorithms.mtf import mtf_compress, mtf_decompress
from compressing_algorithms.ha import huffman_compress, huffman_decompress

BLOCK_SIZE = 1024


def bwt_mtf_huffman_compress(input_data: bytes):
    bwt_transformed_blocks = bytearray()
    for i in range(0, len(input_data), BLOCK_SIZE):
        block = input_data[i:i + BLOCK_SIZE]
        bwt_transformed = bwt_from_suffix_array(block)
        bwt_transformed_blocks.extend(bwt_transformed)

    mtf_transformed = mtf_compress(bwt_transformed_blocks)
    compressed_data, encoding_map = huffman_compress(mtf_transformed)

    return compressed_data, encoding_map


def bwt_mtf_huffman_decompress(compressed_data: bytes, encoding_map) -> bytes:
    huffman_decompressed = huffman_decompress(compressed_data, encoding_map)
    mtf_decompressed = mtf_decompress(huffman_decompressed)

    decompressed_data = bytearray()
    for i in range(0, len(mtf_decompressed), BLOCK_SIZE):
        block = mtf_decompressed[i:i + BLOCK_SIZE]
        original_block = ibwt(block)
        decompressed_data.extend(original_block)

    return decompressed_data