from compressing_algorithms.bwt_sa import bwt_from_suffix_array, ibwt
from compressing_algorithms.mtf import mtf_compress, mtf_decompress
from compressing_algorithms.rle import rle_compress, rle_decompress
from compressing_algorithms.ha import huffman_compress, huffman_decompress

BLOCK_SIZE = 1024 * 1024


def bwt_mtf_rle_huffman_compress(input_data: bytes):
    compressed_blocks = bytearray()
    encoding_map = None
    for i in range(0, len(input_data), BLOCK_SIZE):
        block = input_data[i:i + BLOCK_SIZE]
        bwt_transformed = bwt_from_suffix_array(block)
        mtf_transformed = mtf_compress(bwt_transformed)
        rle_transformed = rle_compress(mtf_transformed)
        huffman_compressed, encoding_map = huffman_compress(rle_transformed)
        compressed_blocks.extend(huffman_compressed)

    return compressed_blocks, encoding_map


def bwt_mtf_rle_huffman_decompress(compressed_data: bytes, encoding_map) -> bytes:
    decompressed_blocks = bytearray()
    i = 0

    while i < len(compressed_data):
        huffman_decompressed = huffman_decompress(compressed_data[i:i + BLOCK_SIZE], encoding_map)
        i += len(huffman_decompressed)

        rle_decompressed = rle_decompress(huffman_decompressed)

        mtf_decompressed = mtf_decompress(rle_decompressed)
        original_block = ibwt(mtf_decompressed)
        decompressed_blocks.extend(original_block)

    return decompressed_blocks
