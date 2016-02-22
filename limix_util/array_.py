import numpy as np

def isint_alike(arr):
    return np.all(arr == np.asarray(arr, int))
