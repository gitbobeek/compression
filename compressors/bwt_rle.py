import time
import os
import struct

BLOCK_SIZE = 1024 * 64

def suffix_array(text):
    text += b'\x00'
    n = len(text)
    s_a = list(range(n))

    for i in range(n):
        s_a[i] = (text[i:], i)
    s_a.sort()
    return [suffix[1] for suffix in s_a]

def bwt_from_suffix_array(s):
    sa = suffix_array(s)
    s += b'\x00'
    n = len(s)
    bwt = bytes(s[(i - 1) % n] for i in sa)
    return bwt

def ibwt(bwt):
    n = len(bwt)
    freq = [0] * 256
    for byte in bwt:
        freq[byte] += 1

    start = [0] * 256
    for i in range(1, 256):
        start[i] = start[i - 1] + freq[i - 1]

    lf = [0] * n
    count = [0] * 256
    for i in range(n):
        byte = bwt[i]
        lf[i] = start[byte] + count[byte]
        count[byte] += 1

    original_data = bytearray()
    i = bwt.index(b'\x00')
    for _ in range(n - 1):
        i = lf[i]
        original_data.append(bwt[i])

    return bytes(original_data[::-1])

def rle_compress(data: bytes) -> bytes:
    compressed_data = bytearray()
    n = len(data)
    i = 0
    while i < n:
        current_byte = data[i]
        count = 1
        while i + count < n and count < 255 and data[i + count] == current_byte:
            count += 1
        compressed_data.append(count)
        compressed_data.append(current_byte)
        i += count
    return bytes(compressed_data)

def rle_decompress(compressed_data: bytes) -> bytes:
    decompressed_data = bytearray()
    n = len(compressed_data)
    i = 0
    while i < n:
        count = compressed_data[i]
        byte = compressed_data[i + 1]
        decompressed_data.extend([byte] * count)
        i += 2
    return bytes(decompressed_data)

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


filepath = "test_files/Master.txt"
outfile = "tests/decompressed_files/enwik7/BWT_RLE_decompressed.txt"
compressed_file = "tests/compressed_files/enwik7/BWT_RLE_compressed.txt"

original_size = os.path.getsize(filepath)

# Сжатие
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