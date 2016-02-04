import h5py
import numpy as np
import os
import tempfile
import shutil

def fetch(fp, path):
    with h5py.File(fp, 'r') as f:
        return f[path][:]

def tree(f_or_filepath, root_name='/', ret=False):
    if isinstance(f_or_filepath, str):
        with h5py.File(f_or_filepath, 'r') as f:
            _tree(f, root_name, ret)
    else:
        _tree(f_or_filepath, root_name, ret)

def _tree(f, root_name='/', ret=False):
    import asciitree

    _names = []
    def get_names(name, obj):
        if isinstance(obj, h5py._hl.dataset.Dataset):
            dtype = str(obj.dtype)
            shape = str(obj.shape)
            _names.append("%s [%s, %s]" % (name, dtype, shape))
        else:
            _names.append(name)

    f.visititems(get_names)
    class Node(object):
        def __init__(self, name, children):
            self.name = name
            self.children = children

        def __str__(self):
            return self.name
    root = Node(root_name, dict())

    def add_to_node(node, ns):
        if len(ns) == 0:
            return
        if ns[0] not in node.children:
            node.children[ns[0]] = Node(ns[0], dict())
        add_to_node(node.children[ns[0]], ns[1:])

    _names = sorted(_names)
    for n in _names:
        ns = n.split('/')
        add_to_node(root, ns)

    def child_iter(node):
        keys = node.children.keys()
        indices = np.argsort(keys)
        indices = np.asarray(indices)
        return list(np.asarray(node.children.values())[indices])

    msg = asciitree.draw_tree(root, child_iter)
    if ret:
        return msg
    print msg

def copy_memmap_h5dt(arr, dt):
    if arr.ndim > 2:
        raise Exception("I don't know how to handle arrays" +
                        " with more than 2 dimensions yet.")
    assert arr.shape == dt.shape
    if arr.ndim == 1:
        dt[:] = arr[:]
    else:
        if dt.chunks is not None:
            chunk_row = dt.chunks[0]
        else:
            chunk_row = 512
        r = 0
        while r < arr.shape[0]:
            re = r + chunk_row
            re = min(re, arr.shape[0])
            dt[r:re,:] = arr[r:re,:]
            r = re

# import gc
# def copy_h5dt_memmap(dt, arr):
#     if arr.ndim > 2:
#         raise Exception("I don't know how to handle arrays" +
#                         " with more than 2 dimensions yet.")
#     assert arr.shape == dt.shape
#     if len(dt.shape) == 1:
#         arr[:] = dt[:]
#     else:
#         if dt.chunks is not None:
#             chunk_row = dt.chunks[0]
#         else:
#             chunk_row = 512
#         r = 0
#         # mem = np.empty((chunk_row, dt.shape[1]), dtype=arr.dtype)
#         while r < dt.shape[0]:
#             re = r + chunk_row
#             re = min(re, dt.shape[0])
#
#
#             # dt.read_direct(mem, np.s_[r:re,:], np.s_[0:(re-r),:])
#
#             # arr[r:re,:] = dt[r:re,:]
#             # mem[:] = np.random.randn(mem.shape[0], mem.shape[1])
#             # arr[r:re,:] = mem[0:(re-r),:]
#             arr[r:re,:] = 1.
#
#             arr.flush()
#             # dt.file.flush()
#             gc.collect()
#
#             r = re

def copy_h5dt_memmap_filepath(dt, fp):

    arr = np.memmap(fp, mode='w+', shape=dt.shape, dtype=dt.dtype)
    if arr.ndim > 2:
        raise Exception("I don't know how to handle arrays" +
                        " with more than 2 dimensions yet.")
    assert arr.shape == dt.shape

    if len(dt.shape) == 1:
        arr[:] = dt[:]
        del arr
    else:
        if dt.chunks is not None:
            chunk_row = dt.chunks[0]
        else:
            chunk_row = 512
        r = 0
        del arr
        while r < dt.shape[0]:
            arr = np.memmap(fp, mode='r+', shape=dt.shape, dtype=dt.dtype)
            re = r + chunk_row
            re = min(re, dt.shape[0])
            s = np.s_[r:re,:]
            dt.read_direct(arr, s, s)
            r = re
            del arr

class Memmap(object):
    def __init__(self, filepath, path, readonly=True, tmp_folder=None):
        self._filepath = filepath
        self._path = path
        self._folder = None
        self._X = None
        self._readonly = readonly
        self._tmp_folder = tmp_folder

    def __enter__(self):
        self._folder = tempfile.mkdtemp(dir=self._tmp_folder)
        with h5py.File(self._filepath, 'r', libversion='latest') as f:
            dt = f[self._path]
            shape = dt.shape
            dtype = dt.dtype
            copy_h5dt_memmap_filepath(dt, os.path.join(self._folder, 'X'))

        mode = 'r' if self._readonly else 'r+'
        X = np.memmap(os.path.join(self._folder, 'X'), mode=mode,
                      shape=shape, dtype=dtype)
        self._X = X
        return X
    def __exit__(self, *args):
        del self._X
        shutil.rmtree(self._folder)
