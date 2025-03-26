from PIL import Image
import numpy as np
import struct
import os


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


def bw_to_raw(png_path, raw_path):
    with Image.open(png_path) as img:
        bw_img = img.convert('L')
        width, height = bw_img.size
        pixel_data = list(bw_img.getdata())

        with open(raw_path, 'wb') as raw_file:
            raw_file.write(struct.pack('<II', width, height))
            raw_file.write(bytes(pixel_data))


def raw_to_bw(raw_path, png_path):
    with open(raw_path, 'rb') as raw_file:
        width, height = struct.unpack('<II', raw_file.read(8))
        pixel_data = raw_file.read()
        img = Image.frombytes('L', (width, height), pixel_data)
        img.save(png_path)


bw_to_raw("../test_files/png/bw.png", "../test_files/bw.raw")
png_to_raw("../test_files/png/rgb.png", "../test_files/rgb.raw")
png_to_raw("../test_files/png/gs.png", "../test_files/gs.raw")