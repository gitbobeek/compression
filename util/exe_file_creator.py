import os

def generate_test_file(filename: str, size_mb: int = 1):
    size = size_mb * 1024 * 1024
    with open(filename, 'wb') as f:
        f.write(os.urandom(size))


generate_test_file("../test_files/test_data.bin", 1)