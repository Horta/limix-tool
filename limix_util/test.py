import numpy as np
import h5py
import dask.array as da

from limix_misc import hdf5_

import os

with h5py.File('test-new.hdf5', 'w') as f:
    g = f.create_group('group')
    g.create_dataset('data1', data=np.random.randn(100, 34), compression="gzip")
    g.create_dataset('data2', data=np.random.randn(100, 111), compression="gzip")

with h5py.File('test-ref.hdf5', 'w') as f:
    g = f.create_group('group1').create_group('group2')
    g['data1'] = h5py.ExternalLink('test-new.hdf5', '/group/data1')

# with h5py.File('test-new.hdf5', 'r') as f:
#     g = f['group']
#     print g['data1'].chunks
#
# with h5py.File('test-new.hdf5', 'r+') as f:
#     convert_matrices_to_row_layout(f)
#
# with h5py.File('test-new.hdf5', 'r') as f:
#     g = f['group']
#     print g['data1'].chunks

hdf5_.tree('test-ref.hdf5')
with h5py.File('test-ref.hdf5', 'r') as f:
    print(f['group1/group2/data1'].chunks)

with h5py.File('test-ref.hdf5', 'r+') as f:
    convert_matrices_to_row_layout(f)

hdf5_.tree('test-ref.hdf5')
with h5py.File('test-ref.hdf5', 'r') as f:
    print(f['group1/group2/data1'].chunks)

# with h5py.File('test.hdf5', 'r') as f:
#     ds1 = f['data1']
#     ds2 = f['data2']
#
#
#     da1 = da.from_array(ds1, chunks=good_chunk(ds1))
#     da2 = da.from_array(ds2, chunks=good_chunk(ds2))
#
#     with h5py.File('test-row.hdf5', 'w') as fn:
#         ds1n = fn.create_dataset('data1', shape=da1.shape, chunks=(1, da1.shape[1]),
#                                  compression='gzip', dtype=float)
#         da.store(da1, ds1n)
#
#         ds2n = fn.create_dataset('data2', shape=da2.shape, chunks=(1, da2.shape[1]),
#                                  compression='gzip', dtype=float)
#         da.store(da2, ds2n)
#
#
# f = h5py.File('test.hdf5', 'r')
# fn = h5py.File('test-row.hdf5', 'r')
#
# np.testing.assert_allclose(f['data1'][:], fn['data1'][:])
# np.testing.assert_allclose(f['data2'][:], fn['data2'][:])
