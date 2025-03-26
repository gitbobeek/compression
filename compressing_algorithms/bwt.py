def bwt_transform(data: bytes) -> bytes:
    if not data:
        return b""

    data = data + b"\x00"  # хуйня чтобы не запоминать цифру другой хуйни
    suffix_array = sorted(range(len(data)), key=lambda i: data[i:])
    return bytes(data[i - 1] for i in suffix_array)


def bwt_inverse(data: bytes) -> bytes:
    if not data:
        return b""

    n = len(data)
    table = [bytearray() for _ in range(n)]

    for _ in range(n):
        table = sorted(bytes([data[i]]) + table[i] for i in range(n))

    for row in table:
        if row.endswith(b"\x00"):
            return row[:-1]
    return b""


def bwt_transform_for_big_data(data: bytes, block_size=1024 * 64):
    transformed = b""
    data_array = bytearray(data)

    for block_first_index in range(0, len(data), block_size):
        new_block = data_array[block_first_index:block_first_index + block_size]
        transformed += bwt_transform(bytes(new_block))

    return transformed


def bwt_inverse_for_big_data(data: bytes, block_size=1024 * 64):
    inversed = b""
    data_array = bytearray(data)
    extra_char = 0

    for block_first_index in range(0, len(data), block_size):
        new_block = data_array[block_first_index + extra_char:block_first_index + block_size + (extra_char + 1)]
        inversed += bwt_inverse(bytes(new_block))
        extra_char += 1

    return inversed
