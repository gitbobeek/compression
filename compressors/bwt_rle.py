import struct
from compressing_algorithms.rle import *


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


def bwt_rle_compress(data: bytes, block_size: int = 1024) -> bytes:
    compressed = bytearray()
    for i in range(0, len(data), block_size):
        block = data[i:i + block_size]
        bwt_block = bwt_from_suffix_array(block)
        rle_block = rle_compress(bwt_block)
        compressed.extend(struct.pack('I', len(rle_block)))
        compressed.extend(rle_block)
    return bytes(compressed)

def bwt_rle_decompress(data: bytes) -> bytes:
    decompressed = bytearray()
    i = 0
    while i < len(data):
        block_size = struct.unpack('I', data[i:i + 4])[0]
        i += 4
        rle_block = data[i:i + block_size]
        i += block_size
        bwt_block = rle_decompress(rle_block)
        decompressed.extend(ibwt(bwt_block))
    return bytes(decompressed)
