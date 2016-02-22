import importlib
import gzip
import cPickle
import os
import path_
from progress import ProgressBar
from misc import BeginEnd
import object_
from os.path import join
from os.path import isdir
import md5
import collections
import subprocess

class PickleByName(object):
    def __init__(self):
        self._signature_only_attrs = set()

    def set_signature_only_attr(self, attr_name):
        self._signature_only_attrs.add(attr_name)

    def __getstate__(self):
        d = self.__dict__.copy()
        for attr_name in self._signature_only_attrs:
            o = getattr(self, attr_name)
            d[attr_name + '_fullname'] = object_.fullname(o)
            d[attr_name + '_init_dict'] = o.init_dict()
            del d[attr_name]
        return d

    def __setstate__(self, d):

        for attr_name in self._signature_only_attrs:
            fn = d[attr_name + '_fullname']
            k = fn.rfind(".")
            module_name, class_name = fn[:k], fn[k+1:]
            init_dict = d[attr_name + '_init_dict']
            mod = importlib.import_module(module_name)
            class_ = getattr(mod, class_name)
            o = class_(**init_dict)
            d[attr_name] = o
            del d[attr_name + '_fullname']
            del d[attr_name + '_init_dict']

        self.__dict__.update(d)

class SlotPickleMixin(object):
    """Top-class that allows mixing of classes with and without slots.

    Takes care that instances can still be pickled with the lowest
    protocol. Moreover, provides a generic `__dir__` method that
    lists all slots.

    """

    # We want to allow weak references to the objects
    __slots__ = ['__weakref__']

    def _get_all_slots(self):
        """Returns all slots as set"""
        all_slots = (getattr(cls, '__slots__', [])
                         for cls in self.__class__.__mro__)
        return set(slot for slots in all_slots for slot in slots)

    def __getstate__(self):
        if hasattr(self, '__dict__'):
            # We don't require that all sub-classes also define slots,
            # so they may provide a dictionary
            statedict = self.__dict__.copy()
        else:
            statedict = {}
        # Get all slots of potential parent classes
        for slot in self._get_all_slots():
            try:
                value = getattr(self, slot)
                statedict[slot] = value
            except AttributeError:
                pass
        # Pop slots that cannot or should not be pickled
        statedict.pop('__dict__', None)
        statedict.pop('__weakref__', None)
        return statedict

    def __setstate__(self, state):
        for key, value in state.items():
            setattr(self, key, value)

    def __dir__(self):
        result = dir(self.__class__)
        result.extend(self._get_all_slots())
        if hasattr(self, '__dict__'):
            result.extend(self.__dict__.keys())
        return result

# with gzip.open('file.txt.gz', 'rb') as f:
#     file_content = f.read()

def pickle(obj, filepath):
    with gzip.open(filepath, 'wb', compresslevel=4) as f:
        cPickle.dump(obj, f, -1)

def unpickle(filepath):
    with gzip.open(filepath, 'rb', compresslevel=4) as f:
        return cPickle.load(f)

# def unpickle(filepath):
#     try:
#         with gzip.open(filepath, 'rb', compresslevel=4) as f:
#             return cPickle.load(f)
#     except Exception as e:
#         print e
#         return _old_unpickle(filepath)


# def _old_pickle(obj, filepath):
#     import lz4
#     data = cPickle.dumps(obj)
#     with open(filepath, 'wb') as f:
#         f.write(lz4.dumps(data))

# def _old_unpickle(filepath):
#     import lz4
#     with open(filepath, 'rb') as f:
#         return cPickle.loads(lz4.loads(f.read()))

def _lastmodif_hash_folder(folder, exclude_files=None):
    if exclude_files is None:
        exclude_files = []
    out = subprocess.check_output('md5deep -r %s' % folder, shell=True)
    lines = sorted(out.strip('\n').split('\n'))

    m = md5.new()
    for line in lines:
        hash_ = line[0:32]
        fp = line[34:]
        if os.path.basename(fp) not in exclude_files:
            m.update(hash_)
    return m.hexdigest()

# def _lastmodif_hash(file_list):
#     m = md5.new()
#     for f in file_list:
#         m.update(ctime(getmtime(f)))
#     return m.hexdigest()

# def _has_valid_cache(folder, file_list):
#     fc = join(folder, '.h5merge_cache')
#     if not os.path.exists(fc):
#         return False
#     with open(fc, 'r') as f:
#         hprev = f.read()
#
#     hnext = _lastmodif_hash(file_list)
#
#     return hprev == hnext

def _has_valid_cache_folder(folder):
    fc = join(folder, '.merge_cache')
    if not os.path.exists(fc):
        return False
    with open(fc, 'r') as f:
        hprev = f.read()

    hnext = _lastmodif_hash_folder(folder, ['all.pkl', '.merge_cache'])

    return hprev == hnext

def _save_cache(folder, lastmodif_hash):
    fpath = join(folder, '.merge_cache')
    with open(fpath, 'w') as f:
        f.write(lastmodif_hash)

def _get_file_list(folder):
    file_list = []
    for (dir_, _, files) in os.walk(folder):
        if dir_ == folder:
            continue
        for f in files:
            fpath = join(dir_, f)
            if fpath.endswith('pkl') and os.path.basename(fpath) != 'all.pkl':
                file_list.append(fpath)
    return file_list

def _merge(file_list):
    pbar = ProgressBar(len(file_list))
    out = dict()
    for (i, fpath) in enumerate(file_list):
        d = unpickle(fpath)
        if isinstance(d, collections.Iterable):
            out.update(d)
        else:
            key = os.path.basename(fpath).split('.')[0]
            out[int(key)] = d
        pbar.update(i+1)
    pbar.finish()
    return out

def pickle_merge(folder, verbose=True):
    file_list = _get_file_list(folder)

    if len(file_list) == 0:
        print('   There is nothing to merge because no file'+
              ' has been found in %s.' % folder)
        return

    exist = os.path.exists(join(folder, 'all.pkl'))

    if exist and _has_valid_cache_folder(folder):
        if verbose:
            print("   Nothing to do because there is a valid cache.")
        return join(folder, 'all.pkl')

    with BeginEnd('Computing hashes'):
        h = _lastmodif_hash_folder(folder, ['all.pkl', '.merge_cache'])

    subfolders = [d for d in os.listdir(folder) if isdir(join(folder, d))]

    with path_.temp_folder() as tf:
        for sf in subfolders:
            path_.make_sure_path_exists(join(tf, sf))
            path_.cp(join(folder, sf), join(tf, sf))
        file_list = _get_file_list(tf)

        with BeginEnd('Merging pickles'):
            out = _merge(file_list)

    with BeginEnd('Storing pickles'):
        pickle(out, join(folder, 'all.pkl'))
    _save_cache(folder, h)

    return join(folder, 'all.pkl')
