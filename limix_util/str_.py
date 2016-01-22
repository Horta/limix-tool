import numpy as np

def array2string(a):
    a = np.asarray(a)
    if len(a) <= 4:
        return np.array2string(a, 43)
    left = np.array2string(a[0:2], 25)
    left = left[:-1]
    right = np.array2string(a[-2:], 25)
    right = right[2:]

    return left + ' ... ' + right
