def suffix_array(text):
    text += b'\x00'
    n = len(text)
    s_a = list(range(n))

    for i in range(n):
        s_a[i] = (text[i:], i)
    s_a.sort()
    return [suffix[1] for suffix in s_a]

def bwt_from_suffix_array(s):
    sa = suffix_array(s)
    s += b'\x00'
    n = len(s)
    bwt = bytes(s[(i - 1) % n] for i in sa)
    return bwt

def ibwt(bwt):
    n = len(bwt)
    freq = [0] * 256
    for byte in bwt:
        freq[byte] += 1

    start = [0] * 256
    for i in range(1, 256):
        start[i] = start[i - 1] + freq[i - 1]

    lf = [0] * n
    count = [0] * 256
    for i in range(n):
        byte = bwt[i]
        lf[i] = start[byte] + count[byte]
        count[byte] += 1

    original_data = bytearray()
    i = bwt.index(b'\x00')
    for _ in range(n - 1):
        i = lf[i]
        original_data.append(bwt[i])

    return bytes(original_data[::-1])