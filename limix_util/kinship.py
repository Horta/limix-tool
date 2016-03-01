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

def gower_kinship_normalization(K):
    """
    Perform Gower normalizion on covariance matrix K
    the rescaled covariance matrix has sample variance of 1
    """
    n = K.shape[0]
    P = np.eye(n) - np.ones((n,n))/float(n)
    trPCP = np.trace(np.dot(P,np.dot(K,P)))
    r = (n-1) / trPCP
    return r * K

def kinship_estimation_hdf5(X):
    import dask.array as da
    if hasattr(X, 'chunks'):
        chunks = X.chunks
    else:
        chunks = X.shape
    X = da.from_array(X, chunks=chunks)
    std = X.std(0)
    ok = std > 0
    std = std[ok]
    X = X[:, ok]
    X -= X.mean(0)
    X /= std
    K = X.dot(X.T)
    return (K / da.diag(K).mean()).compute()

if __name__ == '__main__':
    import dask.array as da
    from dask.array.core import common_blockdim
    import h5py
    chunks = (10, 10)

    with h5py.File('test.hdf5', 'w') as f:
        f.create_dataset('data1', data=np.random.randn(100, 34), compression="gzip")
        f.create_dataset('data2', data=np.random.randn(100, 111), compression="gzip")

    with h5py.File('test.hdf5', 'r') as f:
        d1 = da.from_array(f['data1'], chunks=(5,3))
        d2 = da.from_array(f['data2'], chunks=(5,3))
        X = [d1, d2]
        # X = {('chrom', 0): (lambda: da.from_array(d1, chunks=chunks),),
        #      ('chrom', 1): (lambda: da.from_array(d2, chunks=chunks),)}
        # X = da.Array(X, 'genotype', chunks=chunks)
        X = da.concatenate(X, axis=1)
        print(X.compute().shape)

        pass
        pass
        pass
        pass
        pass
        pass
        pass
        pass
        pass
        pass
        pass
        pass
        pass
        pass
        pass
        pass
        pass
        pass
        pass
        pass
        pass
        pass
        pass
        pass
        pass
        pass
        pass
        pass
        pass
        pass
        pass
        pass
