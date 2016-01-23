import numpy as np

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
