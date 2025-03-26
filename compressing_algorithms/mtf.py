def mtf_compress(data: bytes) -> bytes:
    alphabet = list(range(256))
    result = bytearray()

    for byte in data:
        index = alphabet.index(byte)
        result.append(index)
        alphabet.pop(index)
        alphabet.insert(0, byte)

    return bytes(result)


def mtf_decompress(compressed_data: bytes) -> bytes:
    alphabet = list(range(256))
    result = bytearray()

    for index in compressed_data:
        byte = alphabet[index]
        result.append(byte)
        alphabet.pop(index)
        alphabet.insert(0, byte)

    return bytes(result)