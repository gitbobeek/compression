input_string = open('test_file.txt', 'rb').read()


def letter(hexcode: str):
    return chr(int(hexcode, 16))


def word(hexword: list):
    word_ = ''
    for i in range(len(hexword)):
        word_ += letter(hexword[i])
    return word_


def BWT(s):
    matrix = [
         s[n:] + s[:n] for n in range(len(s))
    ]

    matrix.sort()

    print(matrix)


BWT(input_string)