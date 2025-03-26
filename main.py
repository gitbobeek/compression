from compressors.bwt_rle import *

with open("test_files/test_data.bin", "rb") as file:
    data = file.read()
print(f"Длина исходного файла: {len(data)}")

compressed_data = bwt_rle_compress(data)
with open("tests/compressed_files/binary/BWT_RLE_compressed.bin", "wb") as file:
    file.write(compressed_data)
print(f"Длина сжатого файла: {len(compressed_data)}")

decompressed_data = bwt_rle_decompress(compressed_data)
with open("tests/decompressed_files/binary/BWT_RLE_compressed.txt", "wb") as file:
    file.write(decompressed_data)

print(f"Коэффициент сжатия: {format((len(data) / len(compressed_data)), '.3f')}")
print("Успех!" if decompressed_data == data else "Данные повреждены")
