import sys
import time


def print_progress(iteration: int, total: int, prefix: str = '', suffix: str = '', length: int = 50, fill: str = '█'):
    """
    Выводит progress bar в терминал
    :param iteration: текущая итерация
    :param total: общее количество итераций
    :param prefix: текст перед progress bar
    :param suffix: текст после progress bar
    :param length: длина progress bar в символах
    :param fill: символ заполнения
    """
    percent = f"{100 * (iteration / float(total)):.1f}"
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    sys.stdout.write(f'\r{prefix} |{bar}| {percent}% {suffix}')
    sys.stdout.flush()
    if iteration == total:
        print()


def lz77_compress(data: bytes, buffer_size: int = 1024, max_length: int = 255, show_progress: bool = True) -> bytes:
    encoded_data = bytearray()
    i = 0
    n = len(data)
    last_update = 0

    if show_progress:
        print("Сжатие данных...")

    while i < n:
        if show_progress and time.time() - last_update > 0.1:
            print_progress(i, n, prefix='Прогресс:', suffix=f'Обработано {i}/{n} байт')
            last_update = time.time()

        search_start = max(0, i - buffer_size)
        search_end = i
        max_match_length = 0
        best_offset = 0

        max_possible_length = min(max_length, n - i)
        lookahead = min(4, max_possible_length)
        substring_start = data[i:i + lookahead]

        pos = data.rfind(substring_start, search_start, search_end)

        if pos != -1:
            offset = search_end - pos
            match_length = lookahead

            while (match_length < max_possible_length and
                   i + match_length < n and
                   data[pos + (match_length % (search_end - pos))] == data[i + match_length]):
                match_length += 1

            if match_length > max_match_length:
                max_match_length = match_length
                best_offset = offset

        if max_match_length > 0:
            encoded_data.append((best_offset >> 8) & 0xFF)
            encoded_data.append(best_offset & 0xFF)
            encoded_data.append((max_match_length >> 8) & 0xFF)
            encoded_data.append(max_match_length & 0xFF)
            i += max_match_length
        else:
            encoded_data.extend([0, 0, 0, 0])
            encoded_data.append(data[i])
            i += 1

    if show_progress:
        print_progress(n, n, prefix='Прогресс:', suffix=f'Обработано {n}/{n} байт')
        print(f"Сжатие завершено. Размер сжатых данных: {len(encoded_data)} байт")

    return bytes(encoded_data)


def lz77_decompress(encoded_data: bytes, show_progress: bool = True) -> bytes:
    decoded_data = bytearray()
    i = 0
    n = len(encoded_data)
    last_update = 0

    if show_progress:
        print("Распаковка данных...")

    while i + 4 <= n:
        if show_progress and time.time() - last_update > 0.1:
            print_progress(i, n, prefix='Прогресс:', suffix=f'Обработано {i}/{n} байт')
            last_update = time.time()

        offset = (encoded_data[i] << 8) | encoded_data[i + 1]
        length = (encoded_data[i + 2] << 8) | encoded_data[i + 3]
        i += 4

        if offset == 0 and length == 0:
            if i >= n:
                break
            decoded_data.append(encoded_data[i])
            i += 1
        else:
            start = len(decoded_data) - offset
            end = start + length

            if start < 0 or start >= len(decoded_data):
                raise ValueError(f"Invalid offset: {offset}")

            decoded_data.extend(decoded_data[start:end])

    if show_progress:
        print_progress(n, n, prefix='Прогресс:', suffix=f'Обработано {n}/{n} байт')
        print(f"Распаковка завершена. Размер данных: {len(decoded_data)} байт")

    return bytes(decoded_data)