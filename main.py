def run_length_encode(data: bytes, outf) -> None:
    if len(data) == 0:
        return

    counter = 1
    for i in range(1, len(data)):
        if data[i-1] == data[i]:
            counter += 1
        else:
            outf.write(hex(counter).encode('ascii') + b' ' + hex(data[i-1]).encode('utf-8') + b' ')
            counter = 1
    outf.write(hex(counter).encode('ascii') + b' ' + hex(data[i-1]).encode('utf-8') + b' ')


def decode(data: bytes) -> bytes:
    decoded = bytearray()
    text_bytes = data.split(b' ')
    i = 0
    while i < len(text_bytes) - 1:
        count = int(text_bytes[i], 16)
        byte = int(text_bytes[i + 1], 16)
        decoded.extend([byte] * count)
        i += 2
    return bytes(decoded)


def get_encoded_size(data: str) -> int:
    counter = 0
    for i in data:
        if i == ' ':
            counter += 1
    return counter


f = open('test_input_file', 'rb').read()
original_size = len(f)

out = open('test_output_file', 'wb')
run_length_encode(f, out)
out.close()

encoded_data = open('test_output_file', 'rb').read()
encoded_size = get_encoded_size(str(encoded_data))

decoded_data = decode(encoded_data)

out = open('test_decoded_file', 'wb')
out.write(decoded_data)
out.close()

compression_ratio = original_size / encoded_size if encoded_size != 0 else 0
print(f"Original size: {original_size} bytes")
print(f"Encoded size: {encoded_size} bytes")
print(f"Compression ratio: {compression_ratio:.2f}")
