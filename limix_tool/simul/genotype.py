import numpy as np
import numba

@numba.jit
def cross_parents(X, parents, block_size=1000):
    nblocks = X.shape[1] / block_size
    rest = X.shape[1] - nblocks * block_size

    child = np.empty(nblocks * block_size + rest, float)

    cross_parents_inplace(X, parents, child, block_size=block_size)
    return child

@numba.jit('void(float64[:,:], int64[:], float64[:], int64)', nopython=True,
           nogil=True)
def cross_parents_inplace(X, parents, child, block_size=1000):
    i = 0
    j = 0
    nparents = len(parents)
    while i < X.shape[1]:
        ni = i + block_size
        ni = min(ni, X.shape[1])
        child[i:ni] = X[parents[j % nparents], i:ni]
        i = ni
        j += 1
