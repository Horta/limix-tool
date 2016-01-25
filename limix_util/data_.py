import numpy as np
import numba
import random

@numba.jit
def cross_parents(X, parents, block_size=1000):
    nblocks = X.shape[1] / block_size
    rest = X.shape[1] - nblocks * block_size

    child = np.empty(nblocks * block_size + rest, float)

    cross_parents_inplace(X, parents, child, block_size=block_size)
    return child

@numba.jit('void(double[:,:], int64[:], double[:], int64)')
def cross_parents_inplace(X, parents, child, block_size=1000):
    # nblocks = X.shape[1] / block_size
    # if X.shape[1] % block_size > 0:
    #     nblocks += 1
    # parent = np.random.choice(parents, nblocks, replace=True)

    i = 0
    while i < X.shape[1]:
        ni = i + block_size
        ni = min(ni, X.shape[1])
        j = random.randint(0, len(parents)-1)
        child[i:ni] = X[parents[j], i:ni]
        i = ni

def kinship_estimation(X):
    X = np.asarray(X, float)
    assert np.isfinite(X).all()
    s = np.std(X, 0)
    ok = s > 0
    X = X[:, ok]
    X = (X - np.mean(X, 0)) / np.std(X, 0)
    K = np.dot(X, X.T)
    K = K / K.diagonal().mean()
    return K
