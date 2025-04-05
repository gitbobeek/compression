from compressing_algorithms.bwt_sa import *
from compressing_algorithms.rle import *

import time
import os
import struct

BLOCK_SIZE = 1024 * 64

def compare_files_in_chunks(file1_path, file2_path, chunk_size=4096):
    try:
        with open(file1_path, 'rb') as file1, open(file2_path, 'rb') as file2:
            while True:
                chunk1 = file1.read(chunk_size)
                chunk2 = file2.read(chunk_size)

                if chunk1 != chunk2:
                    return False

                if not chunk1 and not chunk2:
                    return True
    except IOError as e:
        print(f"Ошибка при работе с файлами: {e}")
        return False


filepath = "../test_files/Master.txt"
outfile = "../tests/decompressed_files/master/BWT_RLE_decompressed.txt"
compressed_file = "../tests/compressed_files/master/BWT_RLE_compressed.txt"

original_size = os.path.getsize(filepath)

start_time = time.time()

with open(filepath, "rb") as file, open(compressed_file, "wb") as comp:
    while True:
        text = file.read(BLOCK_SIZE)
        if not text:
            break
        print("Блок обрабатывается")
        bwt_data = bwt_from_suffix_array(text)
        compressed_block = rle_compress(bwt_data)
        comp.write(struct.pack(">I", len(compressed_block)))
        comp.write(compressed_block)


with open(compressed_file, "rb") as comp, open(outfile, "wb") as out:
    while True:
        len_bytes = comp.read(4)
        if not len_bytes:
            break
        block_len = struct.unpack(">I", len_bytes)[0]
        compressed_block = comp.read(block_len)
        if not compressed_block:
            break
        bwt_data = rle_decompress(compressed_block)
        original_block = ibwt(bwt_data)
        out.write(original_block)

final_time = time.time() - start_time
print(f"bwt + rle time: {final_time:.2f} seconds")

compressed_size = os.path.getsize(compressed_file)
compression_ratio = original_size / compressed_size
print(f"Коэффициент сжатия: {compression_ratio:.2f}")

print(compare_files_in_chunks(filepath, outfile, BLOCK_SIZE))