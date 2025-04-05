from PIL import Image
import numpy as np
import struct


def png_to_raw(image_path, output_path):
    image = Image.open(image_path)
    if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):
        
        image = image.convert('RGB')

    raw_pixels = np.array(image)
    raw_data = raw_pixels.tobytes()

    with open(output_path, 'wb') as f:
        f.write(raw_data)


def raw_to_png(raw_path, output_path, width=None, height=None, channels=3):
    with open(raw_path, 'rb') as f:
        raw_data = f.read()

    raw_array = np.frombuffer(raw_data, dtype=np.uint8)

    if width is None or height is None:
        if channels == 3:
            size = int(np.sqrt(len(raw_array) / 3))
            width = height = size
        else:
            width = height = int(np.sqrt(len(raw_array)))

    if channels == 3:
        image_array = raw_array.reshape((height, width, 3))
    else:
        image_array = raw_array.reshape((height, width))

    image = Image.fromarray(image_array)
    image.save(output_path)


def png_to_binary_raw(input_path, output_path, threshold=128):
    with Image.open(input_path) as img:
        gray_img = img.convert('L')

        binary_array = np.array(gray_img)
        binary_array = (binary_array > threshold).astype(np.uint8) * 255

        binary_array.tofile(output_path)


def raw_binary_to_png(input_path, output_path, width, height):
    binary_array = np.fromfile(input_path, dtype=np.uint8)

    expected_size = width * height
    if len(binary_array) != expected_size:
        raise ValueError(f"Ожидалось {expected_size} байт, получено {len(binary_array)}. Проверьте width и height.")

    img = Image.fromarray(binary_array.reshape(height, width), 'L')
    img.save(output_path)


# bw_to_raw("../test_files/png/bw.png", "../test_files/bw.raw")
# png_to_raw("../test_files/png/rgb.png", "../test_files/rgb.raw")
# png_to_raw("../test_files/png/gs.png", "../test_files/gs.raw")
# raw_to_png()

# png_to_binary_raw("../test_files/png/rgb.png", "../test_files/bw2.raw")
raw_binary_to_png("../test_files/bw2.raw", "converted.png", 1920, 1080)