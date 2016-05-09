import numpy as np

def maf(X):
    X = np.asarray(X, float)
    u = np.unique(X)
    res = set(u).difference([0., 1., 2.])
    assert len(res) == 0, "I only accept matrices with 0, 1, 2."

    nalleles_b = np.sum(X, axis=0)
    nalleles_a = 2*X.shape[0] - nalleles_b

    mnalleles = np.minimum(nalleles_a, nalleles_b)
    mnalleles /= 2*X.shape[0]

    return mnalleles

def maf_exclusion(X, maf=0.05):
    return maf(X) > maf
