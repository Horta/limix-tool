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
            return _tree(f, root_name, ret)
    else:
        return _tree(f_or_filepath, root_name, ret)

def findnth(haystack, needle, n):
    parts= haystack.split(needle, n+1)
    if len(parts)<=n+1:
        return -1
    return len(haystack)-len(parts[-1])-len(needle)

def _visititems(root, func, level=0, prefix=''):
    if root.name != '/':
        name = root.name
        eman = name[::-1]
        i1 = findnth(eman, '/', level)
        name = '/' + eman[:i1][::-1]
        func(prefix + name, root)
    if not hasattr(root, 'keys'):
        return
    for k in root.keys():
        if root.file == root[k].file:
            _visititems(root[k], func, level+1, prefix)
        else:
            _visititems(root[k], func, 0, prefix + root.name)

def _tree(f, root_name='/', ret=False):
    import asciitree

    _names = []
    def get_names(name, obj):
        if isinstance(obj, h5py._hl.dataset.Dataset):
            dtype = str(obj.dtype)
            shape = str(obj.shape)
            _names.append("%s [%s, %s]" % (name[1:], dtype, shape))
        else:
            _names.append(name[1:])

    # f.visititems(get_names)
    _visititems(f, get_names)
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

class XBuffRows(object):
    def __init__(self, X, row_indices, col_slice, buff_size=1000):
        buff_size = min(buff_size, X.shape[0])
        self._X = X
        self._row = 0
        self._row_buff = -1
        self._buff_size = buff_size
        self._row_indices = row_indices
        self._col_slice = col_slice
        ncols = len(np.empty(X.shape[1])[col_slice])
        self._Xbuff = np.empty((len(row_indices), ncols), dtype=X.dtype)

    def __iter__(self):
        return self

    def _extract_buffer(self, row_indices):
        cs = self._col_slice
        if isinstance(self._X, h5py.Dataset):
            srii = np.argsort(row_indices)
            sri = row_indices[srii]
            try:
                self._X.read_direct(self._Xbuff, np.s_[sri,cs], np.s_[srii,:])
            except TypeError:
                for (i, csi) in enumerate(cs):
                    self._X.read_direct(self._Xbuff[np.s_[srii,i]], np.s_[sri,csi],
                                        np.s_[:])
        else:
            self._Xbuff[:len(row_indices),:] = self._X[row_indices,cs]

    def next(self):
        if self._row >= len(self._row_indices):
            raise StopIteration

        if self._row_buff == -1:
            l = self._row
            r = l + self._buff_size
            r = min(r, len(self._row_indices))
            self._extract_buffer(self._row_indices[l:r])
            self._row_buff = 0

        vec = self._Xbuff[self._row_buff,:]
        self._row_buff += 1
        if self._row_buff >= self._Xbuff.shape[0]:
            self._row_buff = -1
        self._row += 1

        return vec

if __name__ == '__main__':
    import numpy as np
    random = np.random.RandomState(394873)
    X = random.randn(10, 10)

    with h5py.File('tmp.hdf5', 'w') as f:
        f.create_dataset('X', data=X)

    with h5py.File('tmp.hdf5', 'r') as f:
        X = f['X']
        row_indices = random.permutation(X.shape[0])
        col_slice = np.s_[:4]
        Xcopy = X[:][row_indices, col_slice].copy()

        Xb = XBuffRows(X, row_indices, col_slice, buff_size=5000)
        iterrows = iter(Xb)
        i = 0
        for row in iterrows:
            np.testing.assert_almost_equal(Xcopy[i,:], row)
            i += 1
    # print row.next()
    # print row.next()
    # print row.next()
    # print row.next()
    # print row.next()
    # print row.next()
    # print row.next()
    # print row.next()
    # print row.next()
    # print row.next()
    # print row.next()
    # print row.next()
    # print row.next()
