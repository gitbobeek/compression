def run_length_encode(data: bytes, outf, M: int) -> None:
    if len(data) == 0:
        return

    symbol_size = M // 8  # Размер символа в байтах
    i = 0
    while i < len(data):
        repeat_length = 1
        current_symbol = data[i:i + symbol_size]
        while i + (repeat_length + 1) * symbol_size <= len(data) and data[i + repeat_length * symbol_size:i + (repeat_length + 1) * symbol_size] == current_symbol:
            repeat_length += 1

        if repeat_length > 1:
            # Записываем повторяющуюся последовательность
            # Ограничиваем длину 127, чтобы управляющий байт был в диапазоне 0-255
            while repeat_length > 0:
                chunk_length = min(repeat_length, 127)
                outf.write(bytes([chunk_length]) + current_symbol)
                i += chunk_length * symbol_size
                repeat_length -= chunk_length
        else:
            # Находим длину неповторяющейся последовательности
            non_repeat_length = 1
            while i + (non_repeat_length + 1) * symbol_size <= len(data) and (
                i + (non_repeat_length + 2) * symbol_size > len(data) or data[i + non_repeat_length * symbol_size:i + (non_repeat_length + 1) * symbol_size] != data[i + (non_repeat_length + 1) * symbol_size:i + (non_repeat_length + 2) * symbol_size]
            ):
                non_repeat_length += 1

            # Записываем неповторяющуюся последовательность
            # Ограничиваем длину 127, чтобы управляющий байт был в диапазоне 0-255
            while non_repeat_length > 0:
                chunk_length = min(non_repeat_length, 127)
                outf.write(bytes([0x80 | chunk_length]) + data[i:i + chunk_length * symbol_size])
                i += chunk_length * symbol_size
                non_repeat_length -= chunk_length


def decode(data: bytes, M: int) -> bytes:
    decoded = bytearray()
    symbol_size = M // 8  # Размер символа в байтах
    i = 0
    while i < len(data):
        control_byte = data[i]
        if control_byte & 0x80:  # Неповторяющаяся последовательность
            length = control_byte & 0x7F
            decoded.extend(data[i + 1:i + 1 + length * symbol_size])
            i += 1 + length * symbol_size
        else:  # Повторяющаяся последовательность
            length = control_byte
            symbol = data[i + 1:i + 1 + symbol_size]
            decoded.extend(symbol * length)
            i += 1 + symbol_size
    return bytes(decoded)


# Чтение данных из файла
with open('test_image.txt', 'rb') as f:
    input_data = f.read()

# Параметры
M = 8  # Длина кода символов в битах (1 байт)

# Кодирование
out = open('test_output_file', 'wb')
run_length_encode(input_data, out, M)
out.close()

# Декодирование
encoded_data = open('test_output_file', 'rb').read()
decoded_data = decode(encoded_data, M)

# Запись декодированных данных в файл
with open('test_decoded_file', 'wb') as f:
    f.write(decoded_data)

# Проверка
print("Decoded data matches original:", input_data == decoded_data)
