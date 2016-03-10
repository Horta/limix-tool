from __future__ import division
import numpy as np

def kinship_estimation(X, out=None, inplace=False):
    X = X.astype(float)
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

def slow_kinship_estimation(X, out=None, inplace=False):
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

# def gower_kinship_normalization(K):
#     """
#     Perform Gower normalizion on covariance matrix K
#     the rescaled covariance matrix has sample variance of 1
#     """
#     n = K.shape[0]
#     P = np.eye(n) - np.ones((n,n))/float(n)
#     trPCP = np.trace(np.dot(P,np.dot(K,P)))
#     r = (n-1) / trPCP
#     return r * K

def gower_kinship_normalization(K):
    return gower_normalization(K)

def gower_normalization(K):
    """
    Perform Gower normalizion on covariance matrix K
    the rescaled covariance matrix has sample variance of 1
    """
    trPCP = K.trace() - K.mean(0).sum()
    r = (K.shape[0]-1) / trPCP
    return r * K
