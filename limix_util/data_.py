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
           nogil=True, cache=True)
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

def kinship_estimation(X, out=None, inplace=False):
    std = X.std(0)
    ok = std > 0

    std = std[ok]
    X = X[:, ok]
    if inplace:
        X = (X - X.mean(0)) / std
    else:
        X -= X.mean(0)
        X /= std
    if out is None:
        K = X.dot(X.T)
        return K / K.diagonal().mean()
    if isinstance(X, np.core.memmap) and isinstance(out, np.ndarray):
        out = np.asarray(out)
    X.dot(X.T, out=out)
    out /= out.diagonal().mean()

# def ukinship_estimation(gr):
#     nchroms = gr.nchroms
#     for c in xrange(1, nchroms+1):
#         X = gr.chrom(c).SNP[:]
#     pass

if __name__ == '__main__':
    np.random.seed(9)
    X = np.random.randn(5,3)
    print kinship_estimation(X)
    K = np.empty((5,5))
    kinship_estimation(X, K)
    print K
    Xm = np.memmap('/tmp/X', mode='w+', dtype=float, shape=(5,3))
    Xm[:] = X
    kinship_estimation(Xm, K, inplace=True)
    print K
    del Xm
    import os
    os.remove('/tmp/X')
