import random

def generate_file(filename, width, height, ratio_w=90, ratio_b=10):
    with open(filename, 'w') as f:
        for _ in range(height):
            line = ''.join(random.choices(['W', 'B'], weights=[ratio_w, ratio_b], k=width))
            f.write(line + '\n')

generate_file('test_image.txt', 300, 600)