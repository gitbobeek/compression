def lz78_compress(data: bytes) -> bytes:
    dictionary = {b'': 0}
    current_string = b''
    compressed_data = bytearray()

    for byte in data:
        new_string = current_string + bytes([byte])
        if new_string in dictionary:
            current_string = new_string
        else:
            compressed_data.extend(dictionary[current_string].to_bytes(4, 'big'))
            compressed_data.append(byte)
            dictionary[new_string] = len(dictionary)
            current_string = b''

    if current_string:
        compressed_data.extend(dictionary[current_string].to_bytes(4, 'big'))

    return bytes(compressed_data)

def lz78_decompress(compressed_data: bytes) -> bytes:
    dictionary = {0: b''}
    decompressed_data = bytearray()
    i = 0

    while i < len(compressed_data):
        index = int.from_bytes(compressed_data[i:i + 4], 'big')
        i += 4
        byte = compressed_data[i] if i < len(compressed_data) else None
        i += 1 if byte is not None else 0

        string = dictionary[index]

        if byte is not None:
            new_string = string + bytes([byte])
            dictionary[len(dictionary)] = new_string
            decompressed_data.extend(new_string)
        else:
            decompressed_data.extend(string)

    return bytes(decompressed_data)