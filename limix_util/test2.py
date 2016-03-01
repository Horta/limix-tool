import numpy as np
import h5py
import dask.array as da

from limix_misc import hdf5_

import os

n = 1000
p = 5000

chroms = ['chrom%02d' % i for i in range(1, 23)]

random = np.random.RandomState(53)
with h5py.File('test-chrom-row.hdf5', 'w') as f:
    for chrom in chroms:
        f.create_dataset(chrom, data=G, chunks=(1, G.shape[1]), shuffle=True,
                         compression="lzf")

random = np.random.RandomState(53)
with h5py.File('test-chrom-col.hdf5', 'w') as f:
    for chrom in chroms:
        f.create_dataset(chrom, data=G, chunks=(G.shape[0], 1), shuffle=True,
                         compression="lzf")

def conc(x):
    return np.concatenate(x)

from limix_misc.dask_ import hstack_row_read, hstack_col_read
from limix_misc.report import BeginEnd

with h5py.File('test-chrom-row.hdf5', 'r') as f:
    Xs = [f['chrom01'], f['chrom02']]
    X = hstack_row_read(Xs)
    with BeginEnd('Tipo row'):
        X.dot(X.T).compute()

with h5py.File('test-chrom-col.hdf5', 'r') as f:
    Xs = [f['chrom01'], f['chrom02']]
    X = hstack_col_read(Xs)
    with BeginEnd('Tipo col'):
        X.dot(X.T).compute()

with h5py.File('test-chrom-row.hdf5', 'r') as f:
    Xs = [f['chrom01'], f['chrom02']]
    X = hstack_row_read(Xs)
    with BeginEnd('Tipo row'):
        X.std().compute()

with h5py.File('test-chrom-col.hdf5', 'r') as f:
    Xs = [f['chrom01'], f['chrom02']]
    X = hstack_col_read(Xs)
    with BeginEnd('Tipo col'):
        X.std().compute()
