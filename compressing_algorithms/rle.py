def rle_compress(data: bytes) -> bytes:
    encoded = []
    i = 0
    while i < len(data):
        run_length = 1
        while i + run_length < len(data) and data[i] == data[i + run_length] and run_length < 255:
            run_length += 1

        if run_length > 1:
            encoded.append(run_length)
            encoded.append(data[i])
            i += run_length
        else:
            non_repeat_length = 1
            while (i + non_repeat_length < len(data) and
                   non_repeat_length < 255 and
                   (i + non_repeat_length + 1 >= len(data) or
                    data[i + non_repeat_length] != data[i + non_repeat_length + 1])):
                non_repeat_length += 1

            encoded.append(non_repeat_length)
            encoded.append(0x80)
            encoded.extend(data[i:i + non_repeat_length])
            i += non_repeat_length

    return bytes(encoded)


def rle_decompress(data: bytes) -> bytes:
    decoded = []
    i = 0
    while i < len(data):
        run_length = data[i]
        if i + 1 < len(data) and data[i + 1] == 0x80:
            length = run_length
            decoded.extend(data[i + 2:i + 2 + length])
            i += 2 + length
        else:
            decoded.extend([data[i + 1]] * run_length)
            i += 2
    return bytes(decoded)