def bwt_transform(data: bytes) -> bytes:
    if not data:
        return b""

    data = data + b"\x00"
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