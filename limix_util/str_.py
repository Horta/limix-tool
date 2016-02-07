from __future__ import division
import numpy as np
import math

def array2string(a):
    a = np.asarray(a)
    if len(a) <= 4:
        return np.array2string(a, 43)
    left = np.array2string(a[0:2], 25)
    left = left[:-1]
    right = np.array2string(a[-2:], 25)
    right = right[2:]

    return left + ' ... ' + right

def summarize(s, n=64):
    assert n > 6
    s = str(s)
    if len(s) < n:
        return s

    return s[:int(n/2)-2] + ' ... ' + s[-int(math.ceil(n/2))+3:]

if __name__ == '__main__':
    print summarize('danilo horta danilo horta danilo horta danilo horta')
