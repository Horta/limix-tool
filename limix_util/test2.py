import numpy as np
import h5py
import dask.array as da
from limix_misc.report import BeginEnd
from limix_misc import hdf5_

import os

n = 1000
p = 50000

chroms = ['chrom%02d' % i for i in range(1, 2)]

random = np.random.RandomState(53)
with h5py.File('test-chrom-col.hdf5', 'w') as f:
    for chrom in chroms:
        G = np.random.randn(n, p)
        f.create_dataset(chrom, data=G, shuffle=True, compression="lzf")

def good_column_chunk(dataset, size=10*1024**2/8.):
    shape = dataset.shape
    if hasattr(dataset, 'chunks'):
        chunks = dataset.chunks
        n = size // (shape[0] * chunks[1])
        n = max(n, 1)
        return (shape[0], min(int(n*chunks[1]), shape[1]))

    n = size // (shape[0] * 1)
    n = max(n, 1)
    return (shape[0], min(int(n), shape[1]))

def dot_(filepath, path):
    with h5py.File(filepath, 'r') as f:
        G = f[path]
        print(good_column_chunk(G))
        G = da.from_array(G, chunks=good_column_chunk(G))
        G.dot(G.T).compute().shape

dot_('test-chrom-col.hdf5', 'chrom01')
# from limix_misc.dask_ import hstack_row_read, hstack_col_read
#
#
# with h5py.File('test-chrom-row.hdf5', 'r') as f:
#     Xs = [f['chrom01'], f['chrom02']]
#     X = hstack_row_read(Xs)
#     with BeginEnd('Tipo row'):
#         X.dot(X.T).compute()
#
# with h5py.File('test-chrom-col.hdf5', 'r') as f:
#     Xs = [f['chrom01'], f['chrom02']]
#     X = hstack_col_read(Xs)
#     with BeginEnd('Tipo col'):
#         X.dot(X.T).compute()
#
# with h5py.File('test-chrom-row.hdf5', 'r') as f:
#     Xs = [f['chrom01'], f['chrom02']]
#     X = hstack_row_read(Xs)
#     with BeginEnd('Tipo row'):
#         X.std().compute()
#
# with h5py.File('test-chrom-col.hdf5', 'r') as f:
#     Xs = [f['chrom01'], f['chrom02']]
#     X = hstack_col_read(Xs)
#     with BeginEnd('Tipo col'):
#         X.std().compute()
